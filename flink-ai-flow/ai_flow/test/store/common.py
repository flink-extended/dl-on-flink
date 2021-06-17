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
import os
import time
from unittest import mock

from ai_flow.common.properties import Properties
from ai_flow.common.status import Status
from ai_flow.meta.dataset_meta import DataType, DatasetMeta, Schema
from ai_flow.meta.job_meta import State
from ai_flow.meta.metric_meta import MetricType
from ai_flow.model_center.entity.registered_model_detail import RegisteredModelDetail
from ai_flow.protobuf.message_pb2 import RESOURCE_ALREADY_EXISTS, \
    INVALID_PARAMETER_VALUE
from ai_flow.endpoint.server.exception import AIFlowException
from ai_flow.test.endpoint import random_str


class AbstractTestStore(object):

    """test dataset"""

    def test_save_dataset_get_dataset_by_id_and_name(self):
        response = self.store.register_dataset(name='dataset', data_format='csv',
                                               properties=Properties({'a': 'b'}),
                                               name_list=['a'], type_list=[DataType.STRING])
        self.assertEqual(response.name, 'dataset')
        response_id = self.store.get_dataset_by_id(response.uuid)
        self.assertEqual('dataset', response_id.name)
        response_by_name = self.store.get_dataset_by_name('dataset')
        self.assertEqual(response_by_name.name, 'dataset')

    def test_save_dataset_with_catalog_by_id_and_name(self):
        response = self.store.register_dataset_with_catalog(name='dataset',
                                                            catalog_name='catalog', catalog_type='kafka',
                                                            catalog_database='my_db',
                                                            catalog_table='my_table', catalog_connection_uri='/path')
        print(response.to_json_dict())
        response_id = self.store.get_dataset_by_id(response.uuid)
        self.assertEqual('dataset', response_id.name)
        response_by_name = self.store.get_dataset_by_name('dataset')
        self.assertEqual(response_by_name.name, 'dataset')
        print(response_by_name.to_json_dict(), response_id.to_json_dict())

    def test_double_register_dataset(self):
        dataset_1 = self.store.register_dataset(name='dataset', data_format='csv', properties=Properties({'a': 'b'}),
                                                name_list=['a'], type_list=[DataType.STRING])
        dataset_2 = self.store.register_dataset(name='dataset', data_format='csv', properties=Properties({'a': 'b'}),
                                                name_list=['a'], type_list=[DataType.STRING])
        self.assertEqual(dataset_1.uuid, dataset_2.uuid)
        self.assertEqual(dataset_1.schema.to_json_dict(), dataset_2.schema.to_json_dict())
        self.assertEqual(dataset_1.schema.to_json_dict(), dataset_2.schema.to_json_dict())
        self.assertRaises(AIFlowException, self.store.register_dataset, name='dataset',
                          data_format='csv',
                          create_time=round(time.time()), properties=Properties({'a': 'b'}),
                          name_list=['a'], type_list=[DataType.STRING])

    def test_double_register_dataset_with_catalog(self):
        dataset_1 = self.store.register_dataset_with_catalog(name='dataset',
                                                             catalog_name='catalog', catalog_type='kafka',
                                                             catalog_database='my_db',
                                                             catalog_table='my_table', catalog_connection_uri='/path')
        dataset_2 = self.store.register_dataset_with_catalog(name='dataset',
                                                             catalog_name='catalog', catalog_type='kafka',
                                                             catalog_database='my_db',
                                                             catalog_table='my_table', catalog_connection_uri='/path')
        self.assertEqual(dataset_1.uuid, dataset_2.uuid)
        self.assertEqual(dataset_1.schema.to_json_dict(), dataset_2.schema.to_json_dict())
        self.assertEqual(dataset_1.schema.to_json_dict(), dataset_2.schema.to_json_dict())
        self.assertRaises(AIFlowException, self.store.register_dataset, name='dataset',
                          data_format='csv',
                          create_time=round(time.time()), properties=Properties({'a': 'b'}),
                          name_list=['a'], type_list=[DataType.STRING])

    def test_list_datasets(self):
        self.store.register_dataset(name='dataset_1', data_format='csv', description='it is mq data',
                                    uri='mysql://', properties=Properties({'a': 'b'}), name_list=['a'],
                                    type_list=[DataType.INT32])
        self.store.register_dataset(name='dataset_2', data_format='npz', description='it is',
                                    uri='mysql://', properties=Properties({'a': 'b'}), name_list=['a'],
                                    type_list=[DataType.INT32])
        response_list = self.store.list_datasets(5, 0)
        self.assertEqual(len(response_list), 2)
        self.assertEqual('dataset_1', response_list[0].name)
        self.assertEqual('dataset_2', response_list[1].name)

    def test_save_datasets_list_datasets(self):
        schema = Schema(name_list=['a'],
                        type_list=[DataType.STRING])
        dataset_1 = DatasetMeta(name='dataset1', data_format='csv',
                                properties=Properties({'a': 'b'}), schema=schema)
        dataset_2 = DatasetMeta(name='dataset2')
        response = self.store.register_datasets([dataset_1, dataset_2])
        self.assertEqual(len(response), 2)
        self.assertEqual(1, response[0].uuid)
        self.assertEqual(2, response[1].uuid)
        response_list = self.store.list_datasets(2, 0)
        self.assertEqual(2, len(response_list))
        self.assertEqual('dataset1', response_list[0].name)
        self.assertEqual('dataset2', response_list[1].name)

    def test_delete_dataset(self):
        self.store.register_dataset(name='dataset', data_format='csv')
        self.assertEqual(Status.OK, self.store.delete_dataset_by_id(1))
        self.assertIsNone(self.store.get_dataset_by_name(dataset_name='dataset'))
        self.store.register_dataset(name='dataset', data_format='csv')
        self.assertEqual(Status.OK, self.store.delete_dataset_by_id(2))
        self.assertIsNone(self.store.get_dataset_by_name(dataset_name='dataset'))
        self.store.register_dataset(name='dataset', data_format='csv')
        self.assertEqual(Status.OK, self.store.delete_dataset_by_name('dataset'))
        self.assertIsNone(self.store.get_dataset_by_name(dataset_name='dataset'))
        self.store.register_dataset(name='another_dataset',
                                    data_format='csv')
        self.assertEqual(Status.OK, self.store.delete_dataset_by_name('another_dataset'))
        self.store.register_dataset(name='another_dataset',
                                    data_format='csv')
        self.assertEqual(Status.OK, self.store.delete_dataset_by_name('another_dataset'))
        self.assertIsNone(self.store.get_dataset_by_name(dataset_name='another_dataset'))

    def test_update_dataset(self):
        self.store.register_dataset(name='dataset', data_format='csv')
        update_dataset = self.store.update_dataset(dataset_name='dataset',
                                                   data_format='json',
                                                   description='it is a training dataset',
                                                   properties=Properties({'title': 'iris_training'}),
                                                   name_list=['a'], type_list=[DataType.FLOAT32])
        self.store.register_dataset_with_catalog(name='dataset_withcatalog',
                                                 catalog_name='my_hive', catalog_database='default',
                                                 catalog_connection_uri='/path/to/conf', catalog_type='hive',
                                                 catalog_table='my_table')
        update_dataset_1 = self.store.update_dataset(dataset_name='dataset_withcatalog',
                                                     catalog_name='my_hive', catalog_database='my_db',
                                                     catalog_connection_uri='/path/to/conf', catalog_type='hive')
        self.assertEqual(update_dataset.schema.name_list, ['a'])
        self.assertEqual(update_dataset_1.catalog_database, 'my_db')

    """test project"""

    def test_save_project_get_project_by_id_and_name(self):
        response = self.store.register_project(name='project', uri='www.code.com')
        self.assertEqual(response.uuid, 1)
        response_id = self.store.get_project_by_id(response.uuid)
        response_name = self.store.get_project_by_name('project')
        self.assertEqual('project', response_id.name)
        self.assertEqual('project', response_name.name)
        print(response_id)

    def test_double_register_project(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_project(name='project', uri='www.code.com')
        self.assertRaises(AIFlowException, self.store.register_project, name='project',
                          uri='www.code2.com')

    def test_list_project(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_project(name='project1', uri='www.code.com')
        response_list = self.store.list_project(2, 0)
        self.assertEqual(2, len(response_list))
        self.assertEqual('project', response_list[0].name)
        self.assertEqual('project1', response_list[1].name)
        print(response_list[1])

    def test_delete_project_by_id(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.store.register_model_version_relation(version='1', model_id=1,
                                                   workflow_execution_id=1)
        self.assertEqual(self.store.get_project_by_id(1).name, 'project')
        self.assertEqual(self.store.get_model_relation_by_id(1).name, 'model')
        self.assertEqual(self.store.get_workflow_execution_by_id(1).name, 'execution')
        self.assertEqual(self.store.get_model_version_relation_by_version('1', '1').version, '1')
        self.assertEqual(self.store.get_job_by_id(1).name, 'job')
        self.assertEqual(Status.OK, self.store.delete_project_by_id(1))
        self.assertIsNone(self.store.get_project_by_id(1))
        self.assertIsNone(self.store.get_model_relation_by_id(1))
        self.assertIsNone(self.store.get_workflow_execution_by_id(1))
        self.assertIsNone(self.store.get_model_version_relation_by_version('1', '1'))
        self.assertIsNone(self.store.get_job_by_id(1))
        self.assertIsNone(self.store.list_project(1, 0))
        self.assertIsNone(self.store.list_model_relation(1, 0))
        self.assertIsNone(self.store.list_workflow_execution(1, 0))
        self.assertIsNone(self.store.list_model_version_relation(1, 1, 0))
        self.assertIsNone(self.store.list_job(1, 0))
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=2)
        self.store.register_workflow_execution(name='execution', project_id=2,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=2, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.store.register_model_version_relation(version='1', model_id=2,
                                                   workflow_execution_id=2)
        self.assertEqual(Status.OK, self.store.delete_project_by_id(2))

    def test_delete_project_by_name(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.store.register_model_version_relation(version='1', model_id=1,
                                                   workflow_execution_id=1)
        self.assertEqual(self.store.get_project_by_id(1).name, 'project')
        self.assertEqual(self.store.get_model_relation_by_id(1).name, 'model')
        self.assertEqual(self.store.get_workflow_execution_by_id(1).name, 'execution')
        self.assertEqual(self.store.get_model_version_relation_by_version('1', '1').version, '1')
        self.assertEqual(self.store.get_job_by_id(1).name, 'job')
        self.assertEqual(Status.OK, self.store.delete_project_by_name('project'))
        self.assertIsNone(self.store.get_project_by_id(1))
        self.assertIsNone(self.store.get_model_relation_by_id(1))
        self.assertIsNone(self.store.get_workflow_execution_by_id(1))
        self.assertIsNone(self.store.get_model_version_relation_by_version('1', '1'))
        self.assertIsNone(self.store.get_job_by_id(1))
        self.assertIsNone(self.store.list_project(1, 0))
        self.assertIsNone(self.store.list_model_relation(1, 0))
        self.assertIsNone(self.store.list_workflow_execution(1, 0))
        self.assertIsNone(self.store.list_model_version_relation(1, 1, 0))
        self.assertIsNone(self.store.list_job(1, 0))
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=2)
        self.store.register_workflow_execution(name='execution', project_id=2,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=2, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.store.register_model_version_relation(version='1', model_id=2,
                                                   workflow_execution_id=2)
        self.assertEqual(Status.OK, self.store.delete_project_by_name('project'))

    def test_update_project(self):
        self.store.register_project(name='project', uri='www.code.com')
        update_project = self.store.update_project(project_name='project', uri='git@alibaba')
        self.assertEqual(update_project.uri, 'git@alibaba')
        self.assertIsNone(update_project.properties)

    """test workflow execution"""

    def test_save_workflow_execution_get_by_id_and_name(self):
        self.store.register_project(name='project', uri='www.code.com')
        response = self.store.register_workflow_execution(name='execution', project_id=1,
                                                          execution_state=State.INIT)
        self.assertEqual(response.name, 'execution')
        response_id = self.store.get_workflow_execution_by_id(response.uuid)
        response_name = self.store.get_workflow_execution_by_name('execution')
        self.assertEqual(response_id.name, 'execution')
        self.assertEqual(response_name.name, 'execution')

    def test_list_workflow_execution(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_workflow_execution(name='execution1', project_id=1,
                                               execution_state=State.INIT)
        response_list = self.store.list_workflow_execution(2, 0)
        self.assertEqual(2, len(response_list))
        self.assertEqual('execution', response_list[0].name)
        self.assertEqual('execution1', response_list[1].name)
        print(response_list[0])

    def test_update_workflow_execution(self):
        self.store.register_workflow_execution(name='execution',
                                               execution_state=State.INIT)
        end_time = int(time.time() * 1000)
        update_execution = self.store.update_workflow_execution(execution_name='execution',
                                                                execution_state=State.FINISHED, end_time=end_time)
        self.assertEqual(update_execution.execution_state, State.FINISHED)
        self.assertEqual(update_execution.end_time, end_time)
        self.assertIsNone(update_execution.signature)
        print(update_execution)

    def test_update_workflow_execution_end_time(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        now = int(time.time() * 1000)
        self.store.update_workflow_execution_end_time(now, 'execution')
        self.assertEqual(now, self.store.get_workflow_execution_by_name('execution').end_time)
        print(self.store.get_workflow_execution_by_name('execution'))

    def test_update_workflow_execution_state(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.assertEqual(State.INIT, self.store.get_workflow_execution_by_name('execution').execution_state)
        self.store.update_workflow_execution_state(State.FINISHED, 'execution')
        self.assertEqual(State.FINISHED, self.store.get_workflow_execution_by_name('execution').execution_state)
        print(self.store.get_workflow_execution_by_name('execution'))

    def test_delete_workflow_execution_by_id(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.assertEqual(self.store.get_workflow_execution_by_id(1).name, 'execution')
        self.assertEqual(self.store.get_job_by_id(1).name, 'job')
        self.assertEqual(Status.OK, self.store.delete_workflow_execution_by_id(1))
        self.assertIsNone(self.store.get_workflow_execution_by_name('execution'))
        self.assertIsNone(self.store.get_job_by_name('job'))
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.assertEqual(Status.OK, self.store.delete_workflow_execution_by_id(2))

    def test_delete_workflow_execution_by_name(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.assertEqual(self.store.get_workflow_execution_by_id(1).name, 'execution')
        self.assertEqual(self.store.get_job_by_id(1).name, 'job')
        self.assertEqual(Status.OK, self.store.delete_workflow_execution_by_name('execution'))
        self.assertIsNone(self.store.get_workflow_execution_by_name('execution'))
        self.assertIsNone(self.store.get_job_by_name('job'))
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.assertEqual(Status.OK, self.store.delete_workflow_execution_by_name('execution'))

    """test job"""

    def test_save_job_get_by_id_and_name(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        response = self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                           properties=Properties({'a': 'b'}))
        self.assertEqual(response.uuid, 1)
        response_id = self.store.get_job_by_id(response.uuid)
        response_name = self.store.get_job_by_name('job')
        self.assertEqual('job', response_id.name)
        self.assertEqual('job', response_name.name)
        print(response_id)
        print(self.store.get_workflow_execution_by_id(1))

    def test_list_job(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.store.register_job(name='job1', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        response_list = self.store.list_job(2, 0)
        self.assertEqual(2, len(response_list))
        self.assertEqual('job', response_list[0].name)
        self.assertEqual('job1', response_list[1].name)

    def test_update_job(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.store.update_job_state(job_state=State.FINISHED, job_name='job')
        response = self.store.get_job_by_name('job')
        self.assertEqual(State.FINISHED, response.job_state)
        now = int(time.time() * 1000)
        self.assertEqual(1, self.store.update_job_end_time(now, 'job'))
        response = self.store.get_job_by_name('job')
        self.assertEqual(response.end_time, now)
        print(response)

    def test_delete_job_by_id(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.assertEqual(self.store.get_job_by_id(1).name, 'job')
        self.assertEqual(Status.OK, self.store.delete_job_by_id(1))
        self.assertIsNone(self.store.get_job_by_id(1))
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.assertEqual(Status.OK, self.store.delete_job_by_id(2))

    def test_delete_job_by_name(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.assertEqual(self.store.get_job_by_id(1).name, 'job')
        self.assertEqual(Status.OK, self.store.delete_job_by_name('job'))
        self.assertIsNone(self.store.get_job_by_id(1))
        self.store.register_job(name='job', workflow_execution_id=1, job_state=State.STARTING,
                                properties=Properties({'a': 'b'}))
        self.assertEqual(Status.OK, self.store.delete_job_by_name('job'))

    def test_update_Job(self):
        self.store.register_workflow_execution(name='execution',
                                               execution_state=State.INIT)
        self.store.register_job(name='job', job_state=State.STARTING, properties=Properties({'a': 'b'}))
        update_job = self.store.update_job(job_name='job', job_state=State.FINISHED, workflow_execution_id=1)
        self.assertEqual(update_job.workflow_execution_id, 1)
        self.assertEqual(update_job.job_state, State.FINISHED)
        self.assertEqual(update_job.properties, Properties({'a': 'b'}))
        print(update_job)

    """test model """

    def test_save_model_get_id_and_name(self):
        self.store.register_project(name='project', uri='www.code.com')
        response = self.store.register_model_relation(name='model', project_id=1)
        self.assertEqual(response.name, 'model')
        self.assertEqual(self.store.get_model_relation_by_id(response.uuid).name, 'model')
        self.assertEqual(self.store.get_model_relation_by_name('model').name, 'model')
        print(self.store.get_model_relation_by_id(response.uuid))

    def test_list_model(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_model_relation(name='model1', project_id=1)
        self.assertEqual(2, len(self.store.list_model_relation(2, 0)))
        self.assertEqual('model', self.store.list_model_relation(2, 0)[0].name)
        self.assertEqual('model1', self.store.list_model_relation(2, 0)[1].name)

    def test_delete_model_by_id(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        response = self.store.register_model_version_relation(version='1', model_id=1, workflow_execution_id=1)
        self.assertEqual(response.version, '1')
        self.assertEqual(self.store.get_model_version_relation_by_version('1', 1).version, '1')
        self.assertEqual(self.store.get_model_relation_by_name('model').name, 'model')
        self.assertEqual(Status.OK, self.store.delete_model_relation_by_id(1))
        self.assertIsNone(self.store.get_model_version_relation_by_version('1', '1'))
        self.assertIsNone(self.store.get_model_relation_by_name('model'))
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_model_version_relation(version='1', model_id=2, workflow_execution_id=1)
        self.assertEqual(Status.OK, self.store.delete_model_relation_by_id(2))

    def test_delete_model_by_name(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        response = self.store.register_model_version_relation(version='1', model_id=1, workflow_execution_id=1)
        self.assertEqual(response.version, '1')
        self.assertEqual(self.store.get_model_version_relation_by_version('1', '1').version, '1')
        self.assertEqual(self.store.get_model_relation_by_name('model').name, 'model')
        self.assertEqual(Status.OK, self.store.delete_model_relation_by_name('model'))
        self.assertIsNone(self.store.get_model_version_relation_by_version('1', '1'))
        self.assertIsNone(self.store.get_model_relation_by_name('model'))
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_model_version_relation(version='1', model_id=2, workflow_execution_id=1)
        self.assertEqual(Status.OK, self.store.delete_model_relation_by_name('model'))

    def test_double_register_model_relation(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_model_relation(name='model', project_id=1)
        self.assertRaises(AIFlowException, self.store.register_model_relation, name='model', project_id=2)

    """test model version"""

    def test_save_model_version_get_by_version(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        response = self.store.register_model_version_relation(version='1', model_id=1, workflow_execution_id=1)
        self.assertEqual(response.version, '1')
        self.assertEqual(self.store.get_model_version_relation_by_version(version_name='1', model_id=1).version, '1')

    def test_list_model_version(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_model_version_relation(version='1', model_id=1, workflow_execution_id=1)
        self.store.register_model_version_relation(version='2', model_id=1, workflow_execution_id=1)
        self.assertEqual(len(self.store.list_model_version_relation(1, 2, 0)), 2)
        self.assertEqual(self.store.list_model_version_relation(1, 2, 0)[0].version, '1')
        self.assertEqual(self.store.list_model_version_relation(1, 2, 0)[1].version, '2')

    def test_delete_model_version_by_version(self):
        self.store.register_project(name='project', uri='www.code.com')
        self.store.register_model_relation(name='model', project_id=1)
        self.store.register_workflow_execution(name='execution', project_id=1,
                                               execution_state=State.INIT)
        self.store.register_model_version_relation(version='1', model_id=1, workflow_execution_id=1)
        self.assertEqual(self.store.get_model_version_relation_by_version('1', 1).version, '1')
        self.assertEqual(Status.OK, self.store.delete_model_version_relation_by_version('1', 1))
        self.assertIsNone(self.store.get_model_version_relation_by_version('1', 1))
        self.store.register_model_version_relation(version='1', model_id=1, workflow_execution_id=1)
        self.assertEqual(Status.OK, self.store.delete_model_version_relation_by_version('1', 1))

    """test artifact"""

    def test_register_artifact_get_and_list_artifact(self):
        artifact = self.store.register_artifact(name='artifact_result', create_time=int(time.time()), uri='../..')
        self.assertEqual(artifact.uuid, self.store.get_artifact_by_id(artifact.uuid).uuid)
        self.assertEqual(artifact.uri, self.store.get_artifact_by_name('artifact_result').uri)
        self.store.register_artifact(name='artifact_result_1', create_time=int(time.time()), uri='../..')
        self.assertEqual(2, len(self.store.list_artifact(2, 0)))
        self.assertEqual(Status.OK, self.store.delete_artifact_by_id(1))
        self.assertEqual(Status.OK, self.store.delete_artifact_by_name('artifact_result_1'))
        self.assertEqual(Status.ERROR, self.store.delete_artifact_by_name('no artifact'))
        self.assertIsNone(self.store.get_artifact_by_id(1))
        self.assertIsNone(self.store.get_artifact_by_name('artifact_result_1'))
        print(artifact.to_json_dict())

    def test_double_register_artifact(self):
        artifact_1 = self.store.register_artifact(name='artifact_result', uri='../..')
        artifact_2 = self.store.register_artifact(name='artifact_result', uri='../..')
        self.assertEqual(artifact_1.to_json_dict(), artifact_2.to_json_dict())
        self.assertRaises(AIFlowException, self.store.register_artifact, name='artifact_result',
                          create_time=int(time.time()), uri='../..')

    def test_update_artifact(self):
        artifact = self.store.register_artifact(name='artifact_result', create_time=int(time.time()), uri='../..')
        update_time = int(time.time())
        update_artifact = self.store.update_artifact(name='artifact_result', update_time=update_time)
        self.assertEqual(update_artifact.update_time, update_time)
        self.assertEqual(update_artifact.uri, artifact.uri)
        self.assertIsNone(update_artifact.properties)
        self.assertIsNone(update_artifact.artifact_type)

    def _create_registered_model(self, model_name, model_type='model type', model_desc='model desc'):
        return self.store.create_registered_model(model_name, model_type, model_desc)

    def _create_model_version(self, model_name, model_path='path/to/source', model_metric='http://localhost/metric',
                              model_flavor='{"flavor.version":1}', version_desc='model version desc'):
        return self.store.create_model_version(model_name, model_path, model_metric, model_flavor, version_desc)

    def test_create_registered_model(self):
        model_name1 = random_str() + 'ABcd'
        model_type1 = 'Checkpoint'
        model_desc1 = 'test_create_registered_model1'
        register_model1 = self._create_registered_model(model_name1, model_type1, model_desc1)
        self.assertEqual(register_model1.model_name, model_name1)

        # error on duplicate
        model_type2 = 'SavedModel'
        model_desc2 = 'test_create_registered_model2'
        with self.assertRaises(AIFlowException) as exception_context:
            self._create_registered_model(model_name1, model_type2, model_desc2)
        assert exception_context.exception.error_code == RESOURCE_ALREADY_EXISTS

        # slightly different name is ok
        for model_name2 in [model_name1 + 'extra', model_name1 + model_name1]:
            register_model2 = self._create_registered_model(model_name2, model_type2, model_desc2)
            self.assertEqual(register_model2.model_name, model_name2)

    def test_double_create_model(self):
        model_name1 = random_str() + 'ABcd'
        model_type1 = 'Checkpoint'
        model_desc1 = 'test_create_registered_model1'
        self._create_registered_model(model_name1, model_type1, model_desc1)
        model_name2 = random_str() + 'ABcd'
        model_type2 = 'Checkpoint'
        model_desc2 = 'test_create_registered_model1'
        self._create_registered_model(model_name2, model_type2, model_desc2)
        self.assertRaises(AIFlowException, self._create_registered_model, model_name2, model_type2, model_desc=' ')

    def test_update_registered_model(self):
        model_name1 = random_str() + 'ABcd'
        model_type1 = 'Checkpoint'
        model_desc1 = 'test_update_registered_model'
        register_model1 = self._create_registered_model(model_name1, model_type1, model_desc1)
        register_model_detail1 = self.store.get_registered_model_detail(register_model1)
        self.assertEqual(register_model1.model_name, model_name1)
        self.assertEqual(register_model_detail1.model_type, model_type1)

        # update model name
        register_model2 = self.store.update_registered_model(register_model1,
                                                             model_name='NewName')
        register_model_detail2 = self.store.get_registered_model_detail(register_model2)
        self.assertEqual(register_model2.model_name, 'NewName')
        self.assertEqual(register_model_detail2.model_name, 'NewName')
        self.assertEqual(register_model_detail2.model_type, model_type1)

        # update model type
        register_model3 = self.store.update_registered_model(register_model2,
                                                             model_type='SavedModel')
        register_model_detail3 = self.store.get_registered_model_detail(register_model3)
        self.assertEqual(register_model3.model_name, 'NewName')
        self.assertEqual(register_model_detail3.model_name, 'NewName')
        self.assertEqual(register_model_detail3.model_type, 'SavedModel')

        # update model description
        register_model4 = self.store.update_registered_model(register_model3,
                                                             model_desc='update_registered_model_desc')
        register_model_detail4 = self.store.get_registered_model_detail(register_model4)
        self.assertEqual(register_model4.model_name, 'NewName')
        self.assertEqual(register_model_detail4.model_name, 'NewName')
        self.assertEqual(register_model_detail4.model_desc, 'update_registered_model_desc')

        # update both model name, type and description
        register_model5 = self.store.update_registered_model(register_model4,
                                                             model_name='AnotherName',
                                                             model_type='H5',
                                                             model_desc='TEST')
        register_model_detail5 = self.store.get_registered_model_detail(register_model5)
        self.assertEqual(register_model5.model_name, 'AnotherName')
        self.assertEqual(register_model_detail5.model_name, 'AnotherName')
        self.assertEqual(register_model_detail5.model_type, 'H5')
        self.assertEqual(register_model_detail5.model_desc, 'TEST')

        # new models with old names
        self._create_registered_model(model_name1, model_type1, model_desc1)
        register_model5 = self._create_registered_model('NewName', 'SavedModel', 'update_registered_model_desc')

        # cannot rename model to conflict with an existing model
        with self.assertRaises(AIFlowException) as exception_context:
            self.store.update_registered_model(register_model5, 'AnotherName')
        assert exception_context.exception.error_code == RESOURCE_ALREADY_EXISTS

    def test_delete_registered_model(self):
        registered_model = self._create_registered_model('model_for_delete_RM')
        register_model_detail = self.store.get_registered_model_detail(registered_model)
        self.assertEqual(register_model_detail.model_name, 'model_for_delete_RM')

        # delete model
        self.store.delete_registered_model(registered_model)

    def test_list_registered_model(self):
        self._create_registered_model('M')
        registered_models = self.store.list_registered_models()
        self.assertEqual(len(registered_models), 1)
        self.assertEqual(registered_models[0].model_name, 'M')
        self.assertIsInstance(registered_models[0], RegisteredModelDetail)

        self._create_registered_model('N')
        self.assertEqual(set([registered_model.model_name for registered_model in self.store.list_registered_models()]),
                         {'M', 'N'})

        self._create_registered_model('NN')
        self._create_registered_model('NM')
        self._create_registered_model('MN')
        self._create_registered_model('NNO')
        self.assertEqual(set([rm.model_name for rm in self.store.list_registered_models()]),
                         {'M', 'N', 'NN', 'NM', 'MN', 'NNO'})

    def test_get_registered_model_detail(self):
        model_name = 'test_model'
        model_type = 'Checkpoint'
        model_desc = 'test_get_registered_model_detail'
        # use fake clock
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = 1234
            registered_model = self._create_registered_model(model_name, model_type, model_desc)
            self.assertEqual(registered_model.model_name, model_name)
        register_model_detail = self.store.get_registered_model_detail(registered_model)
        self.assertEqual(register_model_detail.model_name, model_name)
        self.assertEqual(register_model_detail.model_type, model_type)
        self.assertEqual(register_model_detail.model_desc, model_desc)
        self.assertEqual(register_model_detail.model_version, None)

    def test_create_model_version(self):
        model_name = 'test_for_create_model_version'
        self._create_registered_model(model_name)
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = 456778
            model_version1 = self._create_model_version(model_name)
            self.assertEqual(model_version1.model_name, model_name)
            self.assertEqual(model_version1.model_version, '1')

        model_version_detail1 = self.store.get_model_version_detail(model_version1)
        self.assertEqual(model_version_detail1.model_name, model_name)
        self.assertEqual(model_version_detail1.model_version, '1')
        self.assertEqual(model_version_detail1.model_path, 'path/to/source')
        self.assertEqual(model_version_detail1.model_metric, 'http://localhost/metric')
        self.assertEqual(model_version_detail1.model_flavor, '{"flavor.version":1}')
        self.assertEqual(model_version_detail1.version_desc, 'model version desc')
        self.assertEqual(model_version_detail1.version_status, 'READY')
        self.assertEqual(model_version_detail1.current_stage, 'Generated')
        self.store.update_model_version(model_version1, current_stage='Validated')
        self.assertEqual(self.store.get_latest_validated_model_version(model_name).model_version, '1')
        self.store.update_model_version(model_version1, current_stage='Deployed')
        self.assertEqual(self.store.get_deployed_model_version(model_name).model_version, '1')

        # new model versions for same name autoincrement versions
        model_version2 = self._create_model_version(model_name)
        model_version_detail2 = self.store.get_model_version_detail(model_version2)
        self.assertEqual(model_version2.model_version, '2')
        self.assertEqual(model_version_detail2.model_version, '2')

        model_version3 = self._create_model_version(model_name)
        model_version_detail3 = self.store.get_model_version_detail(model_version3)
        self.assertEqual(model_version3.model_version, '3')
        self.assertEqual(model_version_detail3.model_version, '3')

    def test_get_deployed_model_version(self):
        model_name = 'test_for_create_model_version'
        self._create_registered_model(model_name)
        model_version = self._create_model_version(model_name)
        serving_model_version = self.store.get_deployed_model_version(model_name)
        self.assertIsNone(serving_model_version)

        self.store.update_model_version(model_version=model_version,
                                        current_stage='DEPLOYED')
        serving_model_version = self.store.get_deployed_model_version(model_name)
        self.assertEqual(serving_model_version.model_version, model_version.model_version)
        self.assertRaises(AIFlowException, self.store.update_model_version,
                          model_version=model_version, current_stage='DEPLOYED')

    def test_get_latest_validated_model_version(self):
        model_name = 'test_for_get_validated_model_version'
        self._create_registered_model(model_name)
        model_version = self._create_model_version(model_name)
        serving_model_version = self.store.get_latest_validated_model_version(model_name)
        self.assertIsNone(serving_model_version)

        self.store.update_model_version(model_version=model_version,
                                        current_stage='VALIDATED')

        for i in range(10):
            model_version = self._create_model_version(model_name)
            self.store.update_model_version(model_version=model_version, current_stage='VALIDATED')
        serving_model_version = self.store.get_latest_validated_model_version(model_name)
        self.assertEqual(model_version.model_version, serving_model_version.model_version)

    def test_get_latest_generated_model_version(self):
        model_name = 'test_for_get_generated_model_version'
        self._create_registered_model(model_name)

        for i in range(10):
            model_version = self._create_model_version(model_name)
        generated_model_version = self.store.get_latest_generated_model_version(model_name)
        self.assertEqual(model_version.model_version, generated_model_version.model_version)

    def test_update_model_version(self):
        model_name = 'test_for_update_model_version'
        self._create_registered_model(model_name)
        model_version1 = self._create_model_version(model_name)
        model_version_detail1 = self.store.get_model_version_detail(model_version1)
        self.assertEqual(model_version_detail1.model_name, model_name)
        self.assertEqual(model_version_detail1.model_version, '1')
        self.assertEqual(model_version_detail1.current_stage, 'Generated')

        # update current stage
        self.store.update_model_version(model_version1, current_stage='Generated')
        model_version_detail2 = self.store.get_model_version_detail(model_version1)
        self.assertEqual(model_version_detail2.model_name, model_name)
        self.assertEqual(model_version_detail2.model_version, '1')
        self.assertEqual(model_version_detail2.current_stage, 'Generated')
        self.assertEqual(model_version_detail2.version_desc, 'model version desc')

        # update version description
        self.store.update_model_version(model_version1, version_desc='test model version')
        model_version_detail3 = self.store.get_model_version_detail(model_version1)
        self.assertEqual(model_version_detail3.model_name, model_name)
        self.assertEqual(model_version_detail3.model_version, '1')
        self.assertEqual(model_version_detail3.current_stage, 'Generated')
        self.assertEqual(model_version_detail3.version_desc, 'test model version')

        # update current stage and description
        self.store.update_model_version(model_version1, current_stage='Validated', version_desc='test version desc')
        model_version_detail4 = self.store.get_model_version_detail(model_version1)
        self.assertEqual(model_version_detail4.model_name, model_name)
        self.assertEqual(model_version_detail4.model_version, '1')
        self.assertEqual(model_version_detail4.current_stage, 'Validated')
        self.assertEqual(model_version_detail4.version_desc, 'test version desc')

        # only valid stages can be set
        with self.assertRaises(AIFlowException) as exception_context:
            self.store.update_model_version(model_version1, current_stage='unknown')
        assert exception_context.exception.error_code == INVALID_PARAMETER_VALUE

        # stages are case-insensitive and auto-corrected to system stage names
        for stage_name in ['DEPLOYED', 'deployed', 'DePloyEd']:
            self.store.update_model_version(model_version1, current_stage=stage_name)
            model_version_detail5 = self.store.get_model_version_detail(model_version1)
            self.assertEqual(model_version_detail5.current_stage, 'Deployed')

    def test_delete_model_version(self):
        model_name = 'test_delete_model_version'
        self._create_registered_model(model_name)
        model_version = self._create_model_version(model_name)
        model_version_detail = self.store.get_model_version_detail(model_version)
        self.assertEqual(model_version_detail.model_name, model_name)

        self.store.delete_model_version(model_version)

    def test_create_metric_meta(self):
        start = round(time.time())
        end = start + 1
        metric_meta = self.store.register_metric_meta(name='test_create_metric_meta_1', dataset_id=1,
                                                      model_name='metric_meta_model_1',
                                                      model_version='metric_meta_model_version_1', job_id=1,
                                                      start_time=start, end_time=end, uri='/tmp/metric',
                                                      metric_type=MetricType.DATASET,
                                                      tags='', metric_description='', properties={'a': 'a'})
        self.assertGreater(metric_meta.uuid, 0)
        metric_meta = self.store.update_metric_meta(uuid=metric_meta.uuid, job_id=2)
        get_metric_meta = self.store.get_dataset_metric_meta(dataset_id=1)
        self.assertIsNotNone(metric_meta.model_version)
        self.assertEqual(metric_meta.properties['a'], get_metric_meta.properties['a'])
        self.assertEqual(2, get_metric_meta.job_id)
        self.store.register_metric_meta(name='test_create_metric_meta_2', dataset_id=1,
                                        model_name='metric_meta_model_2',
                                        model_version='metric_meta_model_version_2', job_id=1,
                                        start_time=start, end_time=end, uri='/tmp/metric_1',
                                        metric_type=MetricType.MODEL,
                                        tags='', metric_description='', properties={'a': 'a'})
        self.store.register_metric_meta(name='test_create_metric_meta_3', dataset_id=2,
                                        model_name='metric_meta_model_2',
                                        model_version='metric_meta_model_version_2', job_id=1,
                                        start_time=start, end_time=end, uri='/tmp/metric_2',
                                        metric_type=MetricType.MODEL,
                                        tags='', metric_description='', properties={'a': 'a'})
        results = self.store.get_model_metric_meta(model_name='metric_meta_model_2',
                                                   model_version='metric_meta_model_version_2')
        self.assertEqual(2, len(results))

    def test_create_metric_summary(self):
        metric_summary = self.store.register_metric_summary(metric_id=1, metric_key='name', metric_value='value')
        self.assertGreater(metric_summary.uuid, 0)
        self.store.update_metric_summary(uuid=metric_summary.uuid, metric_value='value_2')
        metric_summary_list = self.store.get_metric_summary(metric_id=1)
        self.assertEqual(1, len(metric_summary_list))
        self.assertEqual('value_2', metric_summary_list[0].metric_value)
