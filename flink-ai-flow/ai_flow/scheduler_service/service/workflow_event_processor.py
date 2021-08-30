# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import logging
import sys
from typing import List, Callable

from ai_flow.meta.workflow_meta import WorkflowMeta
from ai_flow.plugin_interface.scheduler_interface import Scheduler
from ai_flow.scheduler_service.service.workflow_event_handler import WorkflowEventHandler
from ai_flow.scheduler_service.service.workflow_execution_event_handler_state import WorkflowContextEventHandlerState
from ai_flow.store.abstract_store import AbstractStore
from ai_flow.workflow.control_edge import WorkflowAction
from ai_flow.workflow.status import Status
from notification_service.base_notification import BaseEvent, ANY_CONDITION

WorkflowEventHandlerFactoryType = Callable[[WorkflowMeta], WorkflowEventHandler]


class EventKey:
    def __init__(self, namespace, event_type, key, sender):
        self.namespace = namespace
        self.event_type = event_type
        self.key = key
        self.sender = sender


class Poison(object):
    pass


class WorkflowEventProcessor:
    def __init__(self, conn, store: AbstractStore, scheduler: Scheduler,
                 workflow_event_handler_factory: WorkflowEventHandlerFactoryType = WorkflowEventHandler):
        super().__init__()
        self._conn = conn
        self.scheduler = scheduler
        self._workflow_event_handler_factory = workflow_event_handler_factory
        self.store = store

    def run(self) -> None:
        while True:
            try:
                event = self._conn.recv()
                if isinstance(event, Poison):
                    break
                elif isinstance(event, BaseEvent):
                    self._process_event(event)
                else:
                    logging.error("Receive unknown type of event: {}".format(type(event)))
            except EOFError as _:
                logging.info("Event channel is closed exiting")
                break
            except Exception as e:
                logging.error("Unexpected Exception", exc_info=e)

    def _process_event(self, event: BaseEvent):
        subscribed_workflow = []
        projects = self.store.list_project(sys.maxsize, 0)
        for project_name in projects:
            workflows = self._get_subscribed_workflow(event, project_name)
            if len(workflows) > 0:
                for workflow in workflows:
                    subscribed_workflow.append((project_name, workflow))

        for workflow_tuple in subscribed_workflow:
            project_name, workflow = workflow_tuple
            self._handle_event_for_workflow(project_name, workflow, event)

    def _get_subscribed_workflow(self, event, project_name):
        workflows: List[WorkflowMeta] = self.store.list_workflows(project_name=project_name)
        if workflows is None:
            subscribed_workflow = []
        else:
            subscribed_workflow = [workflow for workflow in workflows if self._is_subscribed(workflow, event)]
        return subscribed_workflow

    def _is_subscribed(self, workflow: WorkflowMeta, event: BaseEvent):
        rules = workflow.scheduling_rules
        subscribed_event_keys = [EventKey(e.namespace, e.event_type, e.event_key, e.sender)
                                 for rule in rules for e in rule.event_condition.events]
        event_key = EventKey(event.namespace, event.event_type, event.key, event.sender)
        return self._is_event_key_subscribed(event_key, subscribed_event_keys)

    @staticmethod
    def _is_event_key_subscribed(event_key: EventKey, subscribed_event_keys: List[EventKey]) -> bool:
        def match_condition(config_value, event_value) -> bool:
            if config_value == ANY_CONDITION or event_value == config_value:
                return True
            else:
                return False

        for subscribed_event_key in subscribed_event_keys:
            c_namespace = match_condition(subscribed_event_key.namespace, event_key.namespace)
            c_event_type = match_condition(subscribed_event_key.event_type, event_key.event_type)
            c_sender = match_condition(subscribed_event_key.sender, event_key.sender)
            c_key = match_condition(subscribed_event_key.key, event_key.key)
            if c_namespace and c_event_type and c_sender and c_key:
                return True
        return False

    def _handle_event_for_workflow(self, project_name, workflow: WorkflowMeta, event: BaseEvent):
        try:
            event_context = workflow.get_context_extractor().extract_context(event)
        except Exception as e:
            logging.error("Failed to call context extractor, workflow {} skips event {}".format(workflow.name, event),
                          exc_info=e)
            return
        states = self._get_workflow_execution_state(event_context, project_name, workflow.name)

        for state in states:
            event_handler = self._workflow_event_handler_factory(workflow)
            action, new_state = event_handler.handle_event(event, workflow_state=state.state)
            if action == WorkflowAction.START:
                workflow_execution = None
                if state.workflow_execution_id is not None:
                    workflow_execution = self.scheduler.get_workflow_execution(state.workflow_execution_id)

                if workflow_execution is None or workflow_execution.status != Status.RUNNING:
                    workflow_execution = self.scheduler.start_new_workflow_execution(state.project_name,
                                                                                     state.workflow_name,
                                                                                     state.context)
                if workflow_execution is not None:
                    state.workflow_execution_id = workflow_execution.workflow_execution_id
                else:
                    logging.warning("Fail to start workflow execution for project: {} workflow: {} context: {}"
                                    .format(state.project_name, state.workflow_name, state.context))
            elif action == WorkflowAction.STOP:
                # only stop if workflow execution exist
                if state.workflow_execution_id is not None:
                    self.scheduler.stop_workflow_execution(state.workflow_execution_id)

            state.state = new_state
            self.store.update_workflow_context_event_handler_state(state.project_name, state.workflow_name,
                                                                   state.context, state.workflow_execution_id,
                                                                   state.state)

    def _get_workflow_execution_state(self, event_context,
                                      project_name, workflow_name) -> List[WorkflowContextEventHandlerState]:
        states: List[WorkflowContextEventHandlerState] = []
        if event_context.is_broadcast():
            states.extend(self.store.list_workflow_context_event_handler_states(project_name, workflow_name))
        else:
            contexts = event_context.get_contexts()
            for context in contexts:
                state = self.store.get_workflow_context_event_handler_state(project_name, workflow_name, context)

                # register state for context if it is not exist
                if state is None:
                    state = self.store.register_workflow_context_event_handler_state(project_name,
                                                                                     workflow_name, context)
                states.append(state)
        return states
