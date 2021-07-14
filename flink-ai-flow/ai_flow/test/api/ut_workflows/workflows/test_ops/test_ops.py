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
import os
from ai_flow.ai_graph.ai_node import AINode, ReadDatasetNode, WriteDatasetNode
from ai_flow.api import ops
from ai_flow.ai_graph.ai_graph import current_graph
from ai_flow.api.ai_flow_context import init_ai_flow_context
from ai_flow.context.job_context import job_config
from ai_flow.endpoint.server.server import AIFlowServer
from ai_flow.meta.dataset_meta import DatasetMeta
from ai_flow.meta.model_meta import ModelMeta
from ai_flow.workflow.control_edge import ControlEdge, TaskAction, AIFlowInternalEventType
from ai_flow.workflow.periodic_config import PeriodicConfig
from ai_flow.workflow.status import Status


_SQLITE_DB_FILE = 'aiflow.db'
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)
_PORT = '50051'


class TestOps(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:

        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)
        cls.server = AIFlowServer(store_uri=_SQLITE_DB_URI, port=_PORT,
                                  start_default_notification=False,
                                  start_meta_service=True,
                                  start_metric_service=False,
                                  start_model_center_service=False,
                                  start_scheduler_service=False)
        cls.server.run()
        init_ai_flow_context()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.stop()
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)

    def setUp(self):
        init_ai_flow_context()

    def tearDown(self):
        current_graph().clear_graph()

    def get_node_by_name(self, name) -> AINode:
        for n in current_graph().nodes.values():
            if n.name == name:
                return n
        return None

    def test_user_define_operation(self):
        with job_config('task_1'):
            o = ops.user_define_operation(processor=None, a='a', name='1')
            ops.user_define_operation(input=o, b='b', name='2')
        self.assertEqual(2, len(current_graph().nodes))
        self.assertEqual(1, len(current_graph().edges))
        node_0 = list(current_graph().nodes.values())[0]
        node_1 = list(current_graph().nodes.values())[1]
        self.assertEqual('mock', node_0.config.job_type)
        self.assertEqual('mock', node_1.config.job_type)
        self.assertEqual('a', self.get_node_by_name('1').node_config.get('a'))
        self.assertEqual('b', self.get_node_by_name('2').node_config.get('b'))

    def test_read_write_dataset(self):
        with job_config('task_1'):
            o = ops.read_dataset(read_dataset_processor=None, dataset_info=DatasetMeta(name='source'))
            ops.write_dataset(input=o, dataset_info=DatasetMeta(name='sink'))
        self.assertEqual(2, len(current_graph().nodes))
        self.assertEqual(1, len(current_graph().edges))
        node_list = list(current_graph().nodes.values())
        for node in node_list:
            if isinstance(node, ReadDatasetNode):
                self.assertEqual('source', node.node_config.get('dataset').name)
            elif isinstance(node, WriteDatasetNode):
                self.assertEqual('sink', node.node_config.get('dataset').name)
            self.assertEqual('mock', node.config.job_type)

    def test_transform(self):
        with job_config('task_1'):
            o = ops.read_dataset(read_dataset_processor=None, dataset_info=DatasetMeta(name='dataset'))
            t = ops.transform(input=o, transform_processor=None)
            ops.write_dataset(input=t, dataset_info=DatasetMeta(name='dataset'))
        self.assertEqual(3, len(current_graph().nodes))
        self.assertEqual(2, len(current_graph().edges))

    def test_train(self):
        with job_config('task_1'):
            o = ops.read_dataset(read_dataset_processor=None, dataset_info=DatasetMeta(name='dataset'))
            t = ops.train(input=o, training_processor=None, output_num=1, model_info=ModelMeta(name='model'), name='a')
            ops.write_dataset(input=t, dataset_info=DatasetMeta(name='dataset'))
        self.assertEqual(3, len(current_graph().nodes))
        self.assertEqual(2, len(current_graph().edges))
        n = self.get_node_by_name('a')
        self.assertEqual('model', n.node_config.get('model_info').name)

    def test_predict(self):
        with job_config('task_1'):
            o = ops.read_dataset(read_dataset_processor=None, dataset_info=DatasetMeta(name='dataset'))
            t = ops.predict(input=o, prediction_processor=None,
                            model_info=ModelMeta(name='model'), name='a')
            ops.write_dataset(input=t, dataset_info=DatasetMeta(name='dataset'))
        self.assertEqual(3, len(current_graph().nodes))
        self.assertEqual(2, len(current_graph().edges))
        n = self.get_node_by_name('a')
        self.assertEqual('model', n.node_config.get('model_info').name)

    def test_evaluate(self):
        with job_config('task_1'):
            o = ops.read_dataset(read_dataset_processor=None, dataset_info=DatasetMeta(name='dataset'))
            t = ops.evaluate(input=o, evaluation_processor=None,
                             model_info=ModelMeta(name='model'), name='a')
        self.assertEqual(2, len(current_graph().nodes))
        self.assertEqual(1, len(current_graph().edges))
        n = self.get_node_by_name('a')
        self.assertEqual('model', n.node_config.get('model_info').name)

    def test_dataset_validate(self):
        with job_config('task_1'):
            o = ops.read_dataset(read_dataset_processor=None, dataset_info=DatasetMeta(name='dataset'), name='a')
            ops.dataset_validate(input=o, dataset_validation_processor=None, name='b')
        self.assertEqual(2, len(current_graph().nodes))
        self.assertEqual(1, len(current_graph().edges))
        n = self.get_node_by_name('a')
        self.assertEqual('dataset', n.node_config.get('dataset').name)

    def test_model_validate(self):
        with job_config('task_1'):
            o = ops.read_dataset(read_dataset_processor=None, dataset_info=DatasetMeta(name='dataset'))
            t = ops.model_validate(input=o, model_validation_processor=None,
                                   model_info=ModelMeta(name='model'), name='a')
        self.assertEqual(2, len(current_graph().nodes))
        self.assertEqual(1, len(current_graph().edges))
        n = self.get_node_by_name('a')
        self.assertEqual('model', n.node_config.get('model_info').name)

    def test_push_model(self):
        with job_config('task_1'):
            ops.push_model(pushing_model_processor=None, model_info=ModelMeta(name='model'), name='a')
        self.assertEqual(1, len(current_graph().nodes))
        n = self.get_node_by_name('a')
        self.assertEqual('model', n.node_config.get('model_info').name)

    def test_action_on_event(self):
        with job_config('task_1'):
            o1 = ops.user_define_operation(processor=None, a='a', name='1')
        with job_config('task_2'):
            o2 = ops.user_define_operation(processor=None, b='b', name='2')
        ops.action_on_event(job_name='task_1', sender='task_2', event_key='a', event_value='a')
        self.assertEqual(1, len(current_graph().edges))
        edge: ControlEdge = current_graph().edges.get('task_1')[0]
        self.assertEqual('task_1', edge.destination)
        self.assertEqual('task_2', edge.condition_config.sender)
        self.assertEqual('a', edge.condition_config.event_key)
        self.assertEqual('a', edge.condition_config.event_value)

    def test_action_on_status(self):
        with job_config('task_1'):
            o1 = ops.user_define_operation(processor=None, a='a', name='1')
        with job_config('task_2'):
            o2 = ops.user_define_operation(processor=None, b='b', name='2')
        ops.action_on_job_status(job_name='task_1',
                                 upstream_job_name='task_2',
                                 upstream_job_status=Status.FINISHED, action=TaskAction.START)
        self.assertEqual(1, len(current_graph().edges))
        edge: ControlEdge = current_graph().edges.get('task_1')[0]
        self.assertEqual('task_1', edge.destination)
        self.assertEqual('task_2', edge.condition_config.sender)
        self.assertEqual(AIFlowInternalEventType.JOB_STATUS_CHANGED, edge.condition_config.event_type)
        self.assertEqual(TaskAction.START, edge.condition_config.action)


if __name__ == '__main__':
    unittest.main()
