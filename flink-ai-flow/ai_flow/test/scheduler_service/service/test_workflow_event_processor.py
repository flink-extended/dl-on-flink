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
import multiprocessing
import unittest
import unittest.mock as mock
from multiprocessing import Queue, Value

import cloudpickle
from ai_flow.meta.project_meta import ProjectMeta

from ai_flow.workflow.status import Status

from ai_flow.api.context_extractor import ContextExtractor, EventContext, Broadcast, ContextList

from ai_flow.meta.workflow_meta import WorkflowMeta
from ai_flow.scheduler_service.service.workflow_event_handler import WorkflowEventHandler
from ai_flow.scheduler_service.service.workflow_execution_event_handler_state import WorkflowContextEventHandlerState
from ai_flow.workflow.control_edge import WorkflowSchedulingRule, MeetAllEventCondition, WorkflowAction

from notification_service.base_notification import BaseEvent

from ai_flow.plugin_interface.scheduler_interface import Scheduler, WorkflowExecutionInfo

from ai_flow.store.abstract_store import AbstractStore

from ai_flow.scheduler_service.service.workflow_event_processor import WorkflowEventProcessor, Poison


class MyContextExtractor(ContextExtractor):

    def extract_context(self, event: BaseEvent) -> EventContext:
        if event.event_type == 'exception':
            raise Exception()
        if event.event_type == 'broadcast':
            return Broadcast()

        context_list = ContextList()
        context_list.add_context(event.context)
        return context_list


class TestWorkflowEventProcessor(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_store: AbstractStore = mock.Mock()
        self.mock_scheduler: Scheduler = mock.Mock()
        self.mock_event_handler: WorkflowEventHandler = mock.Mock()

        def mock_event_handler_factory(scheduler_rule):
            return self.mock_event_handler

        self.c1, self.c2 = multiprocessing.connection.Pipe()
        self.processor = WorkflowEventProcessor(self.c1, self.mock_store, self.mock_scheduler,
                                                workflow_event_handler_factory=mock_event_handler_factory)

        self._prepare_workflows()

    def test_run_and_stop(self):
        import time
        self.call_cnt = Value('i', 0)

        def mock__process_event(*args, **kwargs):
            self.call_cnt.value += 1

        self.processor._process_event = mock__process_event
        process = multiprocessing.Process(target=self.processor.run)
        process.start()

        event = BaseEvent('k', 'v', namespace='test_namespace')
        self.c2.send(event)

        time.sleep(1)
        self.assertEqual(1, self.call_cnt.value)

        self.c2.send(Poison())

        process.join()

    def test__process_event(self):
        self.call_cnt = 0

        def mock__handle_event_for_workflow(*args, **kwargs):
            self.call_cnt += 1

        self.processor._handle_event_for_workflow = mock__handle_event_for_workflow

        self.processor._process_event(BaseEvent('k', 'v', namespace='test_namespace'))
        self.assertEqual(3, self.call_cnt)

    def _prepare_workflows(self):
        context_extractor = MyContextExtractor()

        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v', namespace='test_namespace'),
                                      WorkflowAction.STOP)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1', namespace='test_namespace'),
                                       WorkflowAction.START)
        rule2 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k2', 'v2', namespace='test_namespace'),
                                       WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        w2 = WorkflowMeta('workflow2', 1, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule2])
        w3 = WorkflowMeta('workflow3', 1, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule])

        def mock_list_workflows(project_name):
            if project_name == 'test_project1':
                return [w1]
            elif project_name == 'test_project2':
                return [w2, w3]
            else:
                return None

        self.mock_store.list_workflows = mock_list_workflows
        p1 = ProjectMeta(name='test_project1', uri='dummy')
        p2 = ProjectMeta(name='test_project2', uri='dummy')
        self.mock_store.list_projects.return_value = [p1, p2]

    def test__get_subscribed_workflow(self):
        e = BaseEvent('k1', 'v1', namespace='test_namespace')
        workflows = self.processor._get_subscribed_workflow(e, 'test_project1')
        self.assertEqual(1, len(workflows))
        self.assertEqual('workflow1', workflows[0].name)

        e = BaseEvent('k2', 'v2', namespace='test_namespace')
        workflows = self.processor._get_subscribed_workflow(e, 'test_project2')
        self.assertEqual(1, len(workflows))
        self.assertEqual('workflow2', workflows[0].name)

        e = BaseEvent('k', 'v', namespace='test_namespace')
        workflows1 = self.processor._get_subscribed_workflow(e, 'test_project1')
        workflows2 = self.processor._get_subscribed_workflow(e, 'test_project2')
        self.assertEqual(3, len(workflows1 + workflows2))
        self.assertIn('workflow1', [workflow.name for workflow in workflows1])
        self.assertIn('workflow2', [workflow.name for workflow in workflows2])
        self.assertIn('workflow3', [workflow.name for workflow in workflows2])

    def test__get_subscribed_workflow_without_workflow(self):
        e = BaseEvent('k2', 'v2', namespace='test_namespace')
        workflows = self.processor._get_subscribed_workflow(e, 'test_not_exist_project')
        self.assertEqual(0, len(workflows))

    def test__get_workflow_execution_state_register_state_if_not_exist(self):
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = None
        self.mock_store.register_workflow_context_event_handler_state.return_value = state

        context_list = ContextList()
        context_list.add_context('context_1')
        states = self.processor._get_workflow_execution_state(context_list, 'project', 'workflow1')

        self.assertEqual(1, len(states))
        self.assertEqual(state, states[0])
        self.mock_store.register_workflow_context_event_handler_state.assert_called_with('project', 'workflow1',
                                                                                         'context_1')

    def test__get_workflow_execution_state_with_context(self):
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state

        context_list = ContextList()
        context_list.add_context('context_1')
        context_list.add_context('context_2')
        states = self.processor._get_workflow_execution_state(context_list, 'project', 'workflow1')

        calls = [mock.call('project', 'workflow1', 'context_1'), mock.call('project', 'workflow1', 'context_2')]
        self.mock_store.get_workflow_context_event_handler_state.assert_has_calls(calls, any_order=True)
        self.assertEqual(2, len(states))

    def test__get_workflow_execution_state_with_broadcast(self):
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.list_workflow_context_event_handler_states.return_value = [state]

        states = self.processor._get_workflow_execution_state(Broadcast(), 'project', 'workflow1')

        self.mock_store.list_workflow_context_event_handler_states.assert_called_with('project', 'workflow1')
        self.assertEqual(1, len(states))
        self.assertEqual(state, states[0])

    def test__handler_event_for_workflow_none_action(self):
        context_extractor = MyContextExtractor()
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v', namespace='test_namespace'),
                                      WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1', namespace='test_namespace'),
                                       WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state
        self.mock_event_handler.handle_event.return_value = (WorkflowAction.NONE, 1)

        e = BaseEvent('k1', 'v1', namespace='test_namespace')
        self.processor._handle_event_for_workflow('project', w1, e)

        self.mock_store.update_workflow_context_event_handler_state \
            .assert_called_with('project', 'workflow1', 'context_1', None, 1)

    def test__handler_event_for_workflow_start_action(self):
        context_extractor = MyContextExtractor()
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v', namespace='test_namespace'),
                                      WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1', namespace='test_namespace'),
                                       WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state

        # Start Action
        self.mock_scheduler.start_new_workflow_execution.return_value = WorkflowExecutionInfo('execution_id')
        self.mock_event_handler.handle_event.return_value = (WorkflowAction.START, 1)
        e = BaseEvent('k1', 'v1', namespace='test_namespace')
        self.processor._handle_event_for_workflow('project', w1, e)

        self.mock_scheduler.start_new_workflow_execution.assert_called_with('project', 'workflow1', 'context_1')
        self.mock_store.update_workflow_context_event_handler_state \
            .assert_called_with('project', 'workflow1', 'context_1', 'execution_id', 1)

    def test__handler_event_for_workflow_start_with_running_workflow_execution(self):
        context_extractor = MyContextExtractor()
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v', namespace='test_namespace'),
                                      WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1', namespace='test_namespace'),
                                       WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1', '1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state

        # Start Action
        self.mock_scheduler.get_workflow_execution.return_value = WorkflowExecutionInfo('1', status=Status.RUNNING)
        self.mock_event_handler.handle_event.return_value = (WorkflowAction.START, 1)
        e = BaseEvent('k1', 'v1', namespace='test_namespace')
        self.processor._handle_event_for_workflow('project', w1, e)

        self.mock_scheduler.start_new_workflow_execution.assert_not_called()
        self.mock_store.update_workflow_context_event_handler_state \
            .assert_called_with('project', 'workflow1', 'context_1', '1', 1)

    def test__handler_event_for_workflow_start_with_non_running_workflow_execution(self):
        context_extractor = MyContextExtractor()
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v', namespace='test_namespace'),
                                      WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1', namespace='test_namespace'),
                                       WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1', '1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state

        # Start Action
        self.mock_scheduler.get_workflow_execution.return_value = WorkflowExecutionInfo('1', status=Status.FINISHED)
        self.mock_scheduler.start_new_workflow_execution.return_value = WorkflowExecutionInfo('execution_id')
        self.mock_event_handler.handle_event.return_value = (WorkflowAction.START, 1)
        e = BaseEvent('k1', 'v1', namespace='test_namespace')
        self.processor._handle_event_for_workflow('project', w1, e)

        self.mock_scheduler.start_new_workflow_execution.assert_called_with('project', 'workflow1', 'context_1')
        self.mock_store.update_workflow_context_event_handler_state \
            .assert_called_with('project', 'workflow1', 'context_1', 'execution_id', 1)

    def test__handler_event_for_workflow_stop_action(self):
        context_extractor = MyContextExtractor()
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v', namespace='test_namespace'),
                                      WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1', namespace='test_namespace'),
                                       WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state
        self.mock_event_handler.handle_event.return_value = (WorkflowAction.STOP, 1)

        e = BaseEvent('k1', 'v1', namespace='test_namespace')
        self.processor._handle_event_for_workflow('project', w1, e)

        self.mock_store.update_workflow_context_event_handler_state \
            .assert_called_with('project', 'workflow1', 'context_1', None, 1)

        state.workflow_execution_id = 'execution_id'
        self.processor._handle_event_for_workflow('project', w1, e)
        self.mock_scheduler.stop_workflow_execution.assert_called_with('execution_id')
        self.mock_store.update_workflow_context_event_handler_state \
            .assert_called_with('project', 'workflow1', 'context_1', 'execution_id', 1)

    def test__handler_event_for_workflow_exception(self):
        context_extractor = MyContextExtractor()
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v', namespace='test_namespace'),
                                      WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1', namespace='test_namespace'),
                                       WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state

        # Start Action
        e = BaseEvent('k1', 'v1', namespace='test_namespace', event_type='exception')
        self.processor._handle_event_for_workflow('project', w1, e)
