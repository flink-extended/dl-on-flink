#
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
#
import unittest

from ai_flow.workflow.control_edge import MeetAllEventCondition, WorkflowAction

from ai_flow.meta.workflow_meta import WorkflowMeta


class TestWorkflowMeta(unittest.TestCase):

    def test_workflow_meta_update_condition(self):
        meta = WorkflowMeta('workflow', 0)
        self.assertListEqual([], meta.get_condition(WorkflowAction.START))
        self.assertListEqual([], meta.get_condition(WorkflowAction.STOP))

        start_condition_list = [MeetAllEventCondition().add_event(event_key='k1', event_value='start')]
        stop_condition_list = [MeetAllEventCondition().add_event(event_key='k1', event_value='stop')]
        meta.update_condition(start_condition_list, WorkflowAction.START)
        meta.update_condition(stop_condition_list, WorkflowAction.STOP)
        self.assertListEqual(start_condition_list, meta.get_condition(WorkflowAction.START))
        self.assertListEqual(stop_condition_list, meta.get_condition(WorkflowAction.STOP))

        start_condition_list = [MeetAllEventCondition().add_event(event_key='k1', event_value='start'),
                                MeetAllEventCondition().add_event(event_key='k2', event_value='start')]
        meta.update_condition(start_condition_list, WorkflowAction.START)
        self.assertListEqual(start_condition_list, meta.get_condition(WorkflowAction.START))

        meta.update_condition([], WorkflowAction.START)
        self.assertListEqual([], meta.get_condition(WorkflowAction.START))

    def test_workflow_meta_last_event_version(self):
        meta = WorkflowMeta('workflow', 0)
        self.assertIsNone(meta.last_event_version)
