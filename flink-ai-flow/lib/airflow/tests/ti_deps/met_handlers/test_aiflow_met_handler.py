# -*- coding: utf-8 -*-
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

import unittest
from airflow.ti_deps.met_handlers.aiflow_met_handler import *


class TestAiFlowMetHandler(unittest.TestCase):

    def test_parse_config(self):
        configs_op_5 = '[{"__af_object_type__": "jsonable", "__class__": "MetConfig", "__module__": "ai_flow.graph.edge", "action": "START", "condition": "NECESSARY", "event_key": "key_1", "event_type": "UNDEFINED", "event_value": "value_1", "life": "ONCE", "value_condition": "EQUAL"}, {"__af_object_type__": "jsonable", "__class__": "MetConfig", "__module__": "ai_flow.graph.edge", "action": "START", "condition": "NECESSARY", "event_key": "key_2", "event_type": "UNDEFINED", "event_value": "value_2", "life": "ONCE", "value_condition": "EQUAL"}]'
        res = AIFlowMetHandler.parse_configs(configs_op_5)
        self.assertEqual(2, len(res))

    def test_met_stop(self):
        configs_op = '''[
    {
        "__af_object_type__":"jsonable",
        "__class__":"MetConfig",
        "__module__":"ai_flow.graph.edge",
        "action":"STOP",
        "condition":"NECESSARY",
        "event_key":"key_1",
        "event_type":"UNDEFINED",
        "event_value":"value_1",
        "life":"ONCE",
        "value_condition":"EQUAL"
    }
]'''
        ai_ts = AiFlowTs()
        aw = ActionWrapper()
        ai_ts.event_map[('key_1', 'UNDEFINED')] = Event(key='key_1', value='value_1', event_type='UNDEFINED', create_time=1)
        res = AIFlowMetHandler(configs_op).met_sc(ai_ts, aw)
        self.assertEqual(True, res)
        self.assertEqual(TaskAction.STOP, aw.action)

    def test_met_restart(self):
        configs_op = '''[
    {
        "__af_object_type__":"jsonable",
        "__class__":"MetConfig",
        "__module__":"ai_flow.graph.edge",
        "action":"RESTART",
        "condition":"NECESSARY",
        "event_key":"key_1",
        "event_type":"UNDEFINED",
        "event_value":"value_1",
        "life":"ONCE",
        "value_condition":"EQUAL"
    }
]'''
        ai_ts = AiFlowTs()
        aw = ActionWrapper()
        ai_ts.event_map[('key_1', 'UNDEFINED')] = Event(key='key_1', value='value_1', event_type='UNDEFINED',
                                                        create_time=1)
        res = AIFlowMetHandler(configs_op).met_sc(ai_ts, aw)
        self.assertEqual(True, res)
        self.assertEqual(TaskAction.RESTART, aw.action)

