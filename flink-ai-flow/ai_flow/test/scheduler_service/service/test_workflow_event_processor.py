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
import unittest
import unittest.mock as mock
from multiprocessing import Queue, Value

import cloudpickle
from ai_flow.workflow.status import Status

from ai_flow.api.context_extractor import ContextExtractor, EventContext, Broadcast, ContextList

from ai_flow.meta.workflow_meta import WorkflowMeta
from ai_flow.scheduler_service.service.workflow_event_handler import WorkflowEventHandler
from ai_flow.scheduler_service.service.workflow_execution_event_handler_state import WorkflowContextEventHandlerState
from ai_flow.workflow.control_edge import WorkflowSchedulingRule, MeetAllEventCondition, WorkflowAction

from notification_service.base_notification import BaseEvent

from ai_flow.plugin_interface.scheduler_interface import Scheduler, WorkflowExecutionInfo

from ai_flow.store.abstract_store import AbstractStore

from ai_flow.scheduler_service.service.workflow_event_processor import WorkflowEventProcessor


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

        self.queue = Queue()
        self.processor = WorkflowEventProcessor(self.queue, self.mock_store, self.mock_scheduler,
                                                workflow_event_handler_factory=mock_event_handler_factory)

        self._prepare_workflows()

    def test_run_and_stop(self):
        import time
        self.call_cnt = Value('i', 0)

        def mock__process_event(*args, **kwargs):
            self.call_cnt.value += 1

        self.processor._process_event = mock__process_event

        self.processor.start()
        event = BaseEvent('k', 'v', namespace='default')
        self.queue.put(event)

        time.sleep(1)
        self.assertEqual(1, self.call_cnt.value)

        self.processor.stop()
        self.processor.join()

    def test__process_event(self):
        self.call_cnt = 0

        def mock__handle_event_for_workflow(*args, **kwargs):
            self.call_cnt += 1

        self.processor._handle_event_for_workflow = mock__handle_event_for_workflow

        self.processor._process_event(BaseEvent('k', 'v', namespace='default'))
        self.assertEqual(2, self.call_cnt)

    def _prepare_workflows(self):
        context_extractor = MyContextExtractor()

        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v'), WorkflowAction.STOP)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1'), WorkflowAction.START)
        rule2 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k2', 'v2'), WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        w2 = WorkflowMeta('workflow2', 1, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule2])
        self.mock_store.list_workflows.return_value = [w1, w2]

    def test__get_subscribed_workflow(self):
        e = BaseEvent('k1', 'v1', namespace='default')
        workflows = self.processor._get_subscribed_workflow(e, 'default')
        self.assertEqual(1, len(workflows))
        self.assertEqual('workflow1', workflows[0].name)

        e = BaseEvent('k2', 'v2', namespace='default')
        workflows = self.processor._get_subscribed_workflow(e, 'default')
        self.assertEqual(1, len(workflows))
        self.assertEqual('workflow2', workflows[0].name)

        e = BaseEvent('k', 'v', namespace='default')
        workflows = self.processor._get_subscribed_workflow(e, 'default')
        self.assertEqual(2, len(workflows))
        self.assertIn('workflow1', [workflow.name for workflow in workflows])
        self.assertIn('workflow2', [workflow.name for workflow in workflows])

    def test__get_subscribed_workflow_without_workflow(self):
        self.mock_store.list_workflows.return_value = None
        e = BaseEvent('k2', 'v2', namespace='default')
        workflows = self.processor._get_subscribed_workflow(e, 'default')
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
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v'), WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1'), WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state
        self.mock_event_handler.handle_event.return_value = (WorkflowAction.NONE, 1)

        e = BaseEvent('k1', 'v1', namespace='default')
        self.processor._handle_event_for_workflow('project', w1, e)

        self.mock_store.update_workflow_context_event_handler_state \
            .assert_called_with('project', 'workflow1', 'context_1', None, 1)

    def test__handler_event_for_workflow_start_action(self):
        context_extractor = MyContextExtractor()
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v'), WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1'), WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state

        # Start Action
        self.mock_scheduler.start_new_workflow_execution.return_value = WorkflowExecutionInfo('execution_id')
        self.mock_event_handler.handle_event.return_value = (WorkflowAction.START, 1)
        e = BaseEvent('k1', 'v1', namespace='default')
        self.processor._handle_event_for_workflow('project', w1, e)

        self.mock_scheduler.start_new_workflow_execution.assert_called_with('project', 'workflow1', 'context_1')
        self.mock_store.update_workflow_context_event_handler_state \
            .assert_called_with('project', 'workflow1', 'context_1', 'execution_id', 1)

    def test__handler_event_for_workflow_start_with_running_workflow_execution(self):
        context_extractor = MyContextExtractor()
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v'), WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1'), WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1', '1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state

        # Start Action
        self.mock_scheduler.get_workflow_execution.return_value = WorkflowExecutionInfo('1', status=Status.RUNNING)
        self.mock_event_handler.handle_event.return_value = (WorkflowAction.START, 1)
        e = BaseEvent('k1', 'v1', namespace='default')
        self.processor._handle_event_for_workflow('project', w1, e)

        self.mock_scheduler.start_new_workflow_execution.assert_not_called()
        self.mock_store.update_workflow_context_event_handler_state \
            .assert_called_with('project', 'workflow1', 'context_1', '1', 1)

    def test__handler_event_for_workflow_start_with_non_running_workflow_execution(self):
        context_extractor = MyContextExtractor()
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v'), WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1'), WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1', '1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state

        # Start Action
        self.mock_scheduler.get_workflow_execution.return_value = WorkflowExecutionInfo('1', status=Status.FINISHED)
        self.mock_scheduler.start_new_workflow_execution.return_value = WorkflowExecutionInfo('execution_id')
        self.mock_event_handler.handle_event.return_value = (WorkflowAction.START, 1)
        e = BaseEvent('k1', 'v1', namespace='default')
        self.processor._handle_event_for_workflow('project', w1, e)

        self.mock_scheduler.start_new_workflow_execution.assert_called_with('project', 'workflow1', 'context_1')
        self.mock_store.update_workflow_context_event_handler_state \
            .assert_called_with('project', 'workflow1', 'context_1', 'execution_id', 1)


    def test__handler_event_for_workflow_stop_action(self):
        context_extractor = MyContextExtractor()
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v'), WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1'), WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state
        self.mock_event_handler.handle_event.return_value = (WorkflowAction.STOP, 1)

        e = BaseEvent('k1', 'v1', namespace='default')
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
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k', 'v'), WorkflowAction.START)
        rule1 = WorkflowSchedulingRule(MeetAllEventCondition().add_event('k1', 'v1'), WorkflowAction.START)
        w1 = WorkflowMeta('workflow1', 0, context_extractor_in_bytes=cloudpickle.dumps(context_extractor),
                          scheduling_rules=[rule, rule1])
        state = WorkflowContextEventHandlerState('project', 'workflow1', 'context_1')
        self.mock_store.get_workflow_context_event_handler_state.return_value = state

        # Start Action
        e = BaseEvent('k1', 'v1', namespace='default', event_type='exception')
        self.processor._handle_event_for_workflow('project', w1, e)
