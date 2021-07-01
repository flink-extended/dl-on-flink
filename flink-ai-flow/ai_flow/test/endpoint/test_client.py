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
import unittest
from typing import List
from unittest import TestCase

from ai_flow.project.project_config import ProjectConfig
from notification_service.base_notification import EventWatcher

from ai_flow.common.properties import Properties
from ai_flow.common.status import Status
from ai_flow.meta.dataset_meta import DatasetMeta, DataType, Schema
from ai_flow.meta.job_meta import State
from ai_flow.meta.metric_meta import MetricType, MetricMeta, MetricSummary
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from ai_flow.protobuf.message_pb2 import RESOURCE_ALREADY_EXISTS
from ai_flow.client.ai_flow_client import AIFlowClient
from ai_flow.endpoint.server.exception import AIFlowException
from ai_flow.endpoint.server.server import AIFlowServer
from ai_flow.store.db.base_model import base
from ai_flow.test.store.test_sqlalchemy_store import _get_store

_SQLITE_DB_FILE = 'aiflow.db'
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)
_PORT = '50051'

client = None
client1 = None
client2 = None


class AIFlowClientTestCases(object):

    """test dataset"""

    def test_save_dataset_get_dataset_by_id_and_name(self):
        dataset = client.register_dataset(name='dataset', data_format='csv', description='it is mq data',
                                          uri='mysql://',
                                          properties=Properties({'a': 'b'}), name_list=['a'],
                                          type_list=[DataType.INT32])
        dataset_id = client.get_dataset_by_id(2)
        self.assertIsNone(dataset_id)
        dataset_name = client.get_dataset_by_name('dataset')
        self.assertEqual('dataset', dataset.name)
        self.assertEqual('dataset', dataset_name.name)

    def test_save_dataset_with_catalog_by_id_and_name(self):
        client.register_dataset_with_catalog(name='dataset',
                                             catalog_name='my_hive', catalog_connection_uri='/path/to/conf',
                                             catalog_type='hive', catalog_database='my_db', catalog_table='my_table')
        dataset_id = client.get_dataset_by_id(2)
        self.assertIsNone(dataset_id)
        dataset_name = client.get_dataset_by_name('dataset')
        self.assertEqual('my_hive', dataset_name.catalog_name)
        self.assertEqual('hive', dataset_name.catalog_type)
        self.assertEqual('my_db', dataset_name.catalog_database)
        self.assertEqual('my_table', dataset_name.catalog_table)
        self.assertEqual('/path/to/conf', dataset_name.catalog_connection_uri)

    def test_double_register_dataset(self):
        dataset_1 = client.register_dataset(name='dataset', data_format='csv', description='it is mq data',
                                            uri='mysql://', properties=Properties({'a': 'b'}), name_list=['a'],
                                            type_list=[DataType.INT32])

        dataset_2 = client.register_dataset(name='dataset', data_format='csv', description='it is mq data',
                                            uri='mysql://', properties=Properties({'a': 'b'}), name_list=['a'],
                                            type_list=[DataType.INT32])
        self.assertEqual(dataset_1.uuid, dataset_2.uuid)
        self.assertEqual(dataset_1.schema.to_json_dict(), dataset_2.schema.to_json_dict())
        self.assertRaises(AIFlowException, client.register_dataset, name='dataset',
                          data_format='csv',
                          description='it is not mq data', uri='mysql://',
                          properties=Properties({'a': 'b'}), name_list=['a'], type_list=[DataType.INT32])

    def test_list_datasets(self):
        client.register_dataset(name='dataset_1', data_format='csv', description='it is mq data',
                                uri='mysql://', properties=Properties({'a': 'b'}), name_list=['a'],
                                type_list=[DataType.INT32])
        client.register_dataset(name='dataset_2', data_format='npz', description='it is',
                                uri='mysql://', properties=Properties({'a': 'b'}), name_list=['a'],
                                type_list=[DataType.INT32])
        response_list = client.list_datasets(5, 0)
        self.assertEqual(len(response_list), 2)
        self.assertEqual('dataset_1', response_list[0].name)
        self.assertEqual('dataset_2', response_list[1].name)

    def test_save_datasets_list_datasets(self):
        dataset_1 = DatasetMeta(name='dataset1',
                                data_format='csv',
                                create_time=None, update_time=1000,
                                properties=Properties({'a': 'b'}))
        schema = Schema(name_list=['a', 'b'],
                        type_list=[DataType.STRING, DataType.INT32])
        dataset_2 = DatasetMeta(name='dataset2',
                                data_format='csv',
                                create_time=None, update_time=1000,
                                properties=Properties({'a': 'b'}), schema=schema)
        response = client.register_datasets([dataset_1, dataset_2])
        self.assertEqual(len(response), 2)
        self.assertEqual(1, response[0].uuid)
        self.assertEqual(2, response[1].uuid)
        response_list = client.list_datasets(2, 0)
        self.assertEqual(2, len(response_list))
        self.assertEqual('dataset1', response_list[0].name)
        self.assertEqual('dataset2', response_list[1].name)

    def test_delete_dataset(self):
        dataset = client.register_dataset(name='dataset',
                                          data_format='csv',
                                          description='it is mq data',
                                          uri='mysql://',
                                          properties=Properties({'a': 'b'}), name_list=['a'],
                                          type_list=[DataType.INT32])
        self.assertEqual(Status.OK, client.delete_dataset_by_name(dataset.name))
        self.assertIsNone(client.get_dataset_by_name(dataset.name))
        self.assertIsNone(client.list_datasets(1, 0))

    def test_update_dataset(self):
        client.register_dataset(name='dataset', data_format='csv', description='it is mq data',
                                uri='mysql://',
                                properties=Properties({'a': 'b'}), name_list=['a'], type_list=[DataType.INT32])
        now = int(time.time() * 1000)
        update_dataset = client.update_dataset(dataset_name='dataset', data_format='npz',
                                               properties=Properties({'kafka': 'localhost:9092'}),
                                               name_list=['b'], type_list=[DataType.STRING])
        dataset = client.get_dataset_by_name('dataset')
        self.assertTrue(dataset.update_time >= now)
        self.assertEqual(dataset.schema.name_list, update_dataset.schema.name_list)
        self.assertEqual(dataset.schema.type_list, update_dataset.schema.type_list)
        update_dataset_1 = client.update_dataset(dataset_name='dataset', catalog_type='hive', catalog_name='my_hive',
                                                 catalog_database='my_db', catalog_table='my_table')
        self.assertEqual(update_dataset_1.catalog_type, 'hive')
        self.assertEqual(update_dataset_1.catalog_name, 'my_hive')
        self.assertEqual(update_dataset_1.catalog_database, 'my_db')
        self.assertEqual(update_dataset_1.catalog_table, 'my_table')

    """test project"""

    def test_save_project_get_project_by_id_and_name(self):
        response = client.register_project(name='project', uri='www.code.com',)
        project_id = client.get_project_by_id(response.uuid)
        project_name = client.get_project_by_name('project')
        self.assertEqual(project_id.name, 'project')
        self.assertEqual(project_name.name, 'project')
        print(project_id)

    def test_double_register_project(self):
        client.register_project(name='project', uri='www.code.com')
        client.register_project(name='project', uri='www.code.com')
        self.assertRaises(AIFlowException, client.register_project,
                          name='project', uri='www.code2.com')

    def test_list_project(self):
        response = client.register_project(name='project', uri='www.code.com')
        client.register_project(name='project1', uri='www.code.com')
        project_list = client.list_project(2, response.uuid - 1)
        self.assertEqual(2, len(project_list))
        self.assertEqual('project', project_list[0].name)
        self.assertEqual('project1', project_list[1].name)

    def test_delete_project_by_id(self):
        project = client.register_project(name='project', uri='www.code.com')
        model = client.register_model_relation(name='model', project_id=project.uuid)

        client.register_model_version_relation(version='1', model_id=model.uuid,
                                               project_snapshot_id=None)
        self.assertEqual(client.get_project_by_id(project.uuid).name, 'project')
        self.assertEqual(client.get_model_relation_by_id(model.uuid).name, 'model')
        self.assertEqual(client.get_model_version_relation_by_version('1', 1).version, '1')
        self.assertEqual(Status.OK, client.delete_project_by_id(project.uuid))
        self.assertIsNone(client.get_project_by_id(project.uuid))
        self.assertIsNone(client.get_model_relation_by_id(model.uuid))
        self.assertIsNone(client.get_model_version_relation_by_version('1', model.uuid))
        self.assertIsNone(client.list_project(1, 0))
        self.assertIsNone(client.list_model_relation(1, 0))
        self.assertIsNone(client.list_model_version_relation(1, 1, 0))

    def test_delete_project_by_name(self):
        project = client.register_project(name='project', uri='www.code.com')
        model = client.register_model_relation(name='model', project_id=project.uuid)

        client.register_model_version_relation(version='1', model_id=model.uuid,
                                               project_snapshot_id=None)
        self.assertEqual(client.get_project_by_id(project.uuid).name, 'project')
        self.assertEqual(client.get_model_relation_by_id(model.uuid).name, 'model')
        self.assertEqual(client.get_model_version_relation_by_version('1', 1).version, '1')
        self.assertEqual(Status.OK, client.delete_project_by_id(project.uuid))
        self.assertIsNone(client.get_project_by_name('project'))
        self.assertIsNone(client.get_model_relation_by_id(model.uuid))
        self.assertIsNone(client.get_model_version_relation_by_version('1', model.uuid))
        self.assertIsNone(client.list_project(1, 0))
        self.assertIsNone(client.list_model_relation(1, 0))
        self.assertIsNone(client.list_model_version_relation(1, 1, 0))

    def test_update_project(self):
        client.register_project(name='project', uri='www.code.com')
        update_project = client.update_project(project_name='project', uri='git@alibaba.com')
        project = client.get_project_by_name('project')
        self.assertEqual(update_project.uri, project.uri)

    """test workflow"""

    def test_save_workflow_get_workflow_by_id_and_name(self):
        project_response = client.register_project(name='project', uri='www.code.com')
        self.assertEqual(project_response.uuid, 1)
        response = client.register_workflow(name='workflow',
                                            project_id=project_response.uuid,
                                            properties=Properties({'a': 'b'}))
        self.assertEqual(response.uuid, 1)
        self.assertEqual(response.properties, Properties({'a': 'b'}))
        response_by_id = client.get_workflow_by_id(response.uuid)
        response_by_name = client.get_workflow_by_name(project_response.name, response.name)
        self.assertEqual('workflow', response_by_id.name)
        self.assertEqual('workflow', response_by_name.name)
        self.assertEqual(Properties({'a': 'b'}), response_by_id.properties)
        self.assertEqual(Properties({'a': 'b'}), response_by_name.properties)

    def test_double_register_workflow(self):
        project_response = client.register_project(name='project', uri='www.code.com')
        project_response2 = client.register_project(name='project2', uri='www.code.com')
        client.register_workflow(name='workflow', project_id=project_response.uuid)
        client.register_workflow(name='workflow', project_id=project_response2.uuid)
        self.assertRaises(AIFlowException, client.register_workflow, name='workflow',
                          project_id=project_response.uuid)

    def test_list_workflows(self):
        project_response = client.register_project(name='project', uri='www.code.com')
        client.register_workflow(name='workflow1', project_id=project_response.uuid)
        client.register_workflow(name='workflow2', project_id=project_response.uuid)
        response_list = client.list_workflows(project_response.name, 2, 0)
        self.assertEqual('workflow1', response_list[0].name)
        self.assertEqual('workflow2', response_list[1].name)

    def test_delete_workflow(self):
        project_response = client.register_project(name='project', uri='www.code.com')
        response = client.register_workflow(name='workflow',
                                            project_id=project_response.uuid,
                                            properties=Properties({'a': 'b'}))
        self.assertEqual(Status.OK, client.delete_workflow_by_name(project_name=project_response.name,
                                                                   workflow_name='workflow'))
        self.assertIsNone(client.get_workflow_by_id(response.uuid))

        response = client.register_workflow(name='workflow', project_id=project_response.uuid)
        self.assertEqual(Status.OK, client.delete_workflow_by_id(response.uuid))
        self.assertIsNone(client.get_workflow_by_id(response.uuid))

    def test_update_workflow(self):
        project_response = client.register_project(name='project', uri='www.code.com')
        response = client.register_workflow(name='workflow',
                                            project_id=project_response.uuid,
                                            properties=Properties({'a': 'b'}))

        updated_workflow = client.update_workflow(project_name=project_response.name,
                                                  workflow_name='workflow',
                                                  properties=Properties({'a': 'c'}))
        self.assertEqual(updated_workflow.properties, Properties({'a': 'c'}))

    """test model"""

    def test_model_api(self):
        project = client.register_project(name='project', uri='www.code.com')
        model = client.register_model(model_name='test_register_model1',
                                      model_desc='test register model1', project_id=project.uuid)
        self.assertIsNone(client.get_model_by_name('no'))
        self.assertIsNone(client.get_model_by_id(2))
        self.assertEqual(client.get_model_by_id(model.uuid).name, 'test_register_model1')
        self.assertEqual(client.get_model_by_name('test_register_model1').name, 'test_register_model1')
        self.assertEqual(client.get_model_by_name('test_register_model1').model_desc, 'test register model1')
        client.register_model(model_name='test_register_model2',
                              model_desc='test register model2', project_id=1)
        self.assertEqual(len(client.list_model_relation(10, 0)), 2)

        client.delete_model_by_id(model.uuid)
        client.delete_model_by_name('test_register_model2')
        self.assertIsNone(client.list_model_relation(10, 0))
        self.assertEqual(len(client.list_registered_models()), 0)

    def test_get_deployed_model_version(self):
        project = client.register_project(name='project', uri='www.code.com')
        model = client.register_model(model_name='test_register_model1',
                                      model_desc='test register model1', project_id=project.uuid)
        model_version = client.register_model_version(model=model.uuid, model_path='/path/to/your/model/version')
        deployed_model_version = client.get_deployed_model_version(model_name=model.name)
        self.assertIsNone(deployed_model_version)
        client.update_model_version(model_name=model.name, model_version=model_version.version,
                                    current_stage=ModelVersionStage.DEPLOYED)
        deployed_model_version = client.get_deployed_model_version(model_name=model.name)
        self.assertEqual(deployed_model_version.version, model_version.version)
        self.assertRaises(AIFlowException,
                          client.update_model_version, model_name=model.name, model_version=model_version.version,
                          current_stage=ModelVersionStage.DEPLOYED)

    def test_save_model_get_id_and_name(self):
        project = client.register_project(name='project', uri='www.code.com')
        response = client.register_model_relation(name='model', project_id=project.uuid)
        model_id = client.get_model_relation_by_id(response.uuid)
        model_name = client.get_model_relation_by_name('model')
        self.assertEqual(model_id.name, model_name.name)
        self.assertEqual(1, len(client.list_model_relation(2, response.uuid - 1)))
        print(model_id)

    def test_list_model(self):
        project = client.register_project(name='project', uri='www.code.com')
        client.register_model_relation(name='model', project_id=project.uuid)
        client.register_model_relation(name='model1', project_id=project.uuid)
        self.assertEqual(2, len(client.list_model_relation(2, 0)))
        self.assertEqual('model', client.list_model_relation(2, 0)[0].name)
        self.assertEqual('model1', client.list_model_relation(2, 0)[1].name)

    def test_delete_model_by_id(self):
        project = client.register_project(name='project', uri='www.code.com')
        model_relation = client.register_model_relation(name='model', project_id=project.uuid)
        client.register_model_version_relation(version='1', model_id=model_relation.uuid,
                                               project_snapshot_id=None)
        self.assertEqual(client.get_model_version_relation_by_version('1', model_relation.uuid).version, '1')
        self.assertEqual(client.get_model_relation_by_name('model').name, 'model')
        self.assertEqual(Status.OK, client.delete_model_relation_by_id(model_relation.uuid))
        self.assertIsNone(client.get_model_version_relation_by_version('1', model_relation.uuid))
        self.assertIsNone(client.get_model_relation_by_name('model'))

    def test_delete_model_by_name(self):
        project = client.register_project(name='project', uri='www.code.com')
        model_relation = client.register_model_relation(name='model', project_id=project.uuid)
        client.register_model_version_relation(version='1', model_id=model_relation.uuid,
                                               project_snapshot_id=None)
        self.assertEqual(client.get_model_version_relation_by_version('1', model_relation.uuid).version, '1')
        self.assertEqual(client.get_model_relation_by_name('model').name, 'model')
        self.assertEqual(Status.OK, client.delete_model_relation_by_name('model'))
        self.assertIsNone(client.get_model_version_relation_by_version('1', model_relation.uuid))
        self.assertIsNone(client.get_model_relation_by_name('model'))

    """test model version"""

    def test_model_version_api(self):
        project = client.register_project(name='project', uri='www.code.com')
        model = client.register_model(model_name='test_register_model',
                                      model_desc='test register model', project_id=project.uuid)
        self.assertIsNone(client.get_model_version_by_version('1', model.uuid))
        self.assertEqual(client.get_model_by_id(model.uuid).name, 'test_register_model')
        self.assertEqual(client.get_model_by_name('test_register_model').name, 'test_register_model')
        response = client.register_model_version(model=model.uuid,
                                                 project_snapshot_id=None,
                                                 model_path='fs://source1.pkl',
                                                 version_desc='test model version 1',
                                                 current_stage=ModelVersionStage.GENERATED)
        self.assertEqual(response.version, '1')
        model_version_meta = client.get_model_version_by_version(response.version, model.uuid)
        self.assertEqual(model_version_meta.version, '1')
        self.assertEqual(model_version_meta.model_path, 'fs://source1.pkl')
        self.assertIsNone(model_version_meta.model_type)
        self.assertEqual(model_version_meta.version_desc, 'test model version 1')
        response = client.update_model_version(model_name=model.name, model_version='1',
                                               current_stage=ModelVersionStage.DEPLOYED)
        self.assertEqual(response.current_stage, ModelVersionStage.DEPLOYED)
        response = client.get_deployed_model_version(model.name)
        self.assertEqual(response.version, '1')

        response = client.register_model_version(model=model.uuid,
                                                 project_snapshot_id=None,
                                                 model_path='fs://source2.pkl',
                                                 model_type='{"flavor.version":2}',
                                                 version_desc='test model version 2')
        self.assertEqual(response.version, '2')
        self.assertEqual(len(client.list_model_version_relation(1, 10, 0)), 2)

        client.delete_model_version_by_version(version='2', model_id=1)
        self.assertEqual(len(client.list_model_version_relation(1, 10, 0)), 1)
        # register model version with deleted model version name
        response = client.register_model_version(model=model.uuid,
                                                 project_snapshot_id=None,
                                                 model_path='fs://source1.pkl',
                                                 version_desc='test model version 1')
        self.assertEqual(response.version, '2')
        model_version_meta = client.get_model_version_by_version(response.version, model.uuid)
        self.assertEqual(model_version_meta.version, '2')
        self.assertEqual(model_version_meta.model_path, 'fs://source1.pkl')
        self.assertIsNone(model_version_meta.model_type)
        self.assertEqual(model_version_meta.version_desc, 'test model version 1')

    def test_get_latest_model_version(self):
        project = client.register_project(name='project', uri='www.code.com')
        model = client.register_model(model_name='test_register_model',
                                      model_desc='test register model', project_id=project.uuid)
        response_1 = client.register_model_version(model=model.uuid,
                                                   project_snapshot_id=None,
                                                   model_path='fs://source1.pkl',
                                                   version_desc='test model version 1',
                                                   current_stage=ModelVersionStage.GENERATED)
        new_generated_model_version_1 = client.get_latest_generated_model_version(model.name)
        new_validated_model_version_1 = client.get_latest_validated_model_version(model.name)
        self.assertIsNone(new_validated_model_version_1)
        self.assertEqual(response_1.version, new_generated_model_version_1.version)
        client.update_model_version(model_name=model.name, model_version=response_1.version,
                                    current_stage=ModelVersionStage.VALIDATED)
        new_validated_model_version_2 = client.get_latest_validated_model_version(model.name)
        self.assertEqual(new_validated_model_version_2.version, response_1.version)
        response_2 = client.register_model_version(model=model.uuid,
                                                   project_snapshot_id=None,
                                                   model_path='fs://source1.pkl',
                                                   version_desc='test model version 1',
                                                   current_stage=ModelVersionStage.GENERATED)
        new_generated_model_version_2 = client.get_latest_generated_model_version(model.name)
        client.update_model_version(model_name=model.name, model_version=response_2.version,
                                    current_stage=ModelVersionStage.VALIDATED)
        new_validated_model_version_2 = client.get_latest_validated_model_version(model.name)
        self.assertEqual(new_validated_model_version_2.version, response_2.version)
        self.assertEqual(response_2.version, new_generated_model_version_2.version)

    def test_save_model_version_get_by_version(self):
        project = client.register_project(name='project', uri='www.code.com')
        model = client.register_model_relation(name='model', project_id=project.uuid)
        response = client.register_model_version_relation(version='1', model_id=model.uuid,
                                                          project_snapshot_id=None)
        self.assertEqual(response.version, '1')
        self.assertEqual(client.get_model_version_relation_by_version(response.version, model.uuid).version, '1')
        self.assertEqual(len(client.list_model_version_relation(model.uuid, 2, 0)), 1)
        print(client.get_model_version_relation_by_version(response.version, model.uuid))

    def test_list_model_version(self):
        project = client.register_project(name='project', uri='www.code.com')
        model = client.register_model_relation(name='model', project_id=project.uuid)
        client.register_model_version_relation(version='1', model_id=model.uuid,
                                               project_snapshot_id=None)
        client.register_model_version_relation(version='2', model_id=model.uuid,
                                               project_snapshot_id=None)
        self.assertEqual(len(client.list_model_version_relation(1, 2, 0)), 2)
        self.assertEqual(client.list_model_version_relation(1, 2, 0)[0].version, '1')
        self.assertEqual(client.list_model_version_relation(1, 2, 0)[1].version, '2')

    def test_delete_model_version_by_version(self):
        project = client.register_project(name='project', uri='www.code.com')
        model = client.register_model_relation(name='model', project_id=project.uuid)
        client.register_model_version_relation(version='1', model_id=model.uuid,
                                               project_snapshot_id=None)
        self.assertEqual(client.get_model_version_relation_by_version('1', model.uuid).version, '1')
        client.delete_model_version_relation_by_version('1', model.uuid)
        self.assertIsNone(client.get_model_version_relation_by_version('1', model.uuid))

        """test artifact"""

    def test_save_artifact_get_artifact_by_id_and_name(self):
        artifact = client.register_artifact(name='artifact', artifact_type='json', uri='./artifact.json')
        artifact_id = client.get_artifact_by_id(artifact.uuid)
        artifact_name = client.get_artifact_by_name(artifact.name)
        self.assertEqual(artifact.artifact_type, artifact_id.artifact_type)
        self.assertEqual('artifact', artifact_name.name)

    def test_double_save_artifact(self):
        artifact_1 = client.register_artifact(name='artifact', artifact_type='json', uri='./artifact.json')
        artifact_2 = client.register_artifact(name='artifact', artifact_type='json', uri='./artifact.json')
        self.assertEqual(artifact_1.to_json_dict(), artifact_2.to_json_dict())
        self.assertRaises(AIFlowException, client.register_artifact, name='artifact', artifact_type='json',
                          uri='./artifact.json', description='whatever')

    def test_save_artifact_list_artifact(self):
        client.register_artifact(name='artifact', artifact_type='json', uri='./artifact.json')
        client.register_artifact(name='artifact_1', artifact_type='json', uri='./artifact.json')
        self.assertEqual(2, len(client.list_artifact(2, 0)))

    def test_delete_artifact_by_id_and_name(self):
        client.register_artifact(name='artifact', artifact_type='json', uri='./artifact.json')
        client.register_artifact(name='artifact_1', artifact_type='json', uri='./artifact.json')
        self.assertIsNotNone(client.get_artifact_by_id(1))
        self.assertIsNotNone(client.get_artifact_by_name('artifact_1'))
        self.assertEqual(Status.OK, client.delete_artifact_by_id(1))
        self.assertEqual(Status.OK, client.delete_artifact_by_name('artifact_1'))
        self.assertEqual(Status.ERROR, client.delete_artifact_by_name('no artifact'))
        self.assertIsNone(client.get_artifact_by_id(1))
        self.assertIsNone(client.get_artifact_by_name('artifact_1'))

    def test_update_artifact(self):
        client.register_artifact(name='artifact', artifact_type='json', uri='./artifact.json')
        artifact = client.update_artifact(artifact_name='artifact', artifact_type='csv', uri='../..')
        artifact_id = client.get_artifact_by_id(artifact.uuid)
        self.assertEqual(artifact_id.artifact_type, 'csv')
        self.assertIsNotNone(artifact_id.update_time)
        self.assertEqual(artifact_id.uri, '../..')

    def test_create_registered_model(self):
        model_name = 'test_create_registered_model'
        model_desc = 'test create registered model'
        response = client.create_registered_model(model_name=model_name, model_desc=model_desc)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_desc, model_desc)

        with self.assertRaises(AIFlowException) as exception_context:
            client.create_registered_model(model_name=model_name)
        assert exception_context.exception.error_code == str(RESOURCE_ALREADY_EXISTS)

    def test_double_register_model(self):
        model_name = 'test_create_registered_model'
        model_desc = 'test create registered model'
        client.create_registered_model(model_name=model_name, model_desc=model_desc)
        client.create_registered_model(model_name=model_name, model_desc=model_desc)
        self.assertRaises(AIFlowException, client.create_registered_model, model_name=model_name,
                          model_desc='')
        project = client.register_project(name='project')
        client.register_model(model_name=model_name, project_id=project.uuid,
                              model_desc=model_desc)
        client.register_model(model_name=model_name, project_id=project.uuid,
                              model_desc=model_desc)
        self.assertRaises(AIFlowException, client.register_model, model_name=model_name,
                          project_id=project.uuid,
                          model_desc='')

    def test_update_registered_model(self):
        model_name1 = 'test_update_registered_model1'
        model_desc1 = 'test update registered model1'
        response = client.create_registered_model(model_name=model_name1,
                                                  model_desc=model_desc1)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name1)

        model_name2 = 'test_update_registered_model2'
        model_desc2 = 'test update registered model2'
        response = client.update_registered_model(model_name=model_name1, new_name=model_name2,
                                                  model_desc=model_desc2)
        self.assertEqual(response.model_name, model_name2)
        self.assertEqual(response.model_desc, model_desc2)

    def test_delete_registered_model(self):
        model_name = 'test_delete_registered_model'
        model_desc = 'test delete registered model'
        response = client.create_registered_model(model_name=model_name, model_desc=model_desc)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)

        client.delete_registered_model(model_name=model_name)
        response = client.get_registered_model_detail(model_name=model_name)
        self.assertIsNone(response)

    def test_list_registered_model(self):
        model_name1 = 'test_list_registered_model1'
        model_desc1 = 'test list registered model1'
        response = client.create_registered_model(model_name=model_name1,
                                                  model_desc=model_desc1)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name1)

        model_name2 = 'test_list_registered_model2'
        model_desc2 = 'test list registered model2'
        response = client.create_registered_model(model_name=model_name2,
                                                  model_desc=model_desc2)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name2)

        response = client.list_registered_models()
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0].model_name, model_name1)
        self.assertEqual(response[1].model_name, model_name2)

    def test_get_registered_model_detail(self):
        model_name = 'test_get_registered_model_detail'
        model_desc = 'test get registered model detail'
        response = client.create_registered_model(model_name=model_name, model_desc=model_desc)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)

        response = client.get_registered_model_detail(model_name=model_name)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_desc, model_desc)

        model_path1 = 'fs://source1.pkl'
        model_type1 = '{"flavor.version":1}'
        version_desc1 = 'test get registered model detail1'
        response = client.create_model_version(model_name=model_name, model_path=model_path1,
                                               model_type=model_type1,
                                               version_desc=version_desc1)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_version, '1')
        self.assertEqual(response.model_path, model_path1)
        self.assertEqual(response.model_type, model_type1)
        self.assertEqual(response.version_desc, version_desc1)

        response = client.get_registered_model_detail(model_name=model_name)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_desc, model_desc)
        model_version = response.latest_model_version
        self.assertEqual(model_version.model_version, '1')
        self.assertEqual(model_version.model_path, model_path1)
        self.assertEqual(model_version.model_type, model_type1)
        self.assertEqual(model_version.version_desc, version_desc1)

        model_path2 = 'fs://source2.pkl'
        model_type2 = '{"flavor.version":2}'
        version_desc2 = 'test get registered model detail2'
        response = client.create_model_version(model_name=model_name, model_path=model_path2,
                                               model_type=model_type2,
                                               version_desc=version_desc2)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_version, '2')
        self.assertEqual(response.model_path, model_path2)
        self.assertEqual(response.model_type, model_type2)
        self.assertEqual(response.version_desc, version_desc2)

        response = client.get_registered_model_detail(model_name=model_name)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_desc, model_desc)
        model_version = response.latest_model_version
        self.assertEqual(model_version.model_version, '2')
        self.assertEqual(model_version.model_path, model_path2)
        self.assertEqual(model_version.model_type, model_type2)
        self.assertEqual(model_version.version_desc, version_desc2)

    def test_create_model_version(self):
        model_name = 'test_create_model_version'
        model_desc = 'test create model version'
        response = client.create_registered_model(model_name=model_name, model_desc=model_desc)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)

        model_path1 = 'fs://source1.pkl'
        model_type1 = '{"flavor.version":1}'
        version_desc1 = 'test create model version1'
        response = client.create_model_version(model_name=model_name, model_path=model_path1,
                                               model_type=model_type1,
                                               version_desc=version_desc1)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_version, '1')
        self.assertEqual(response.model_path, model_path1)
        self.assertEqual(response.model_type, model_type1)
        self.assertEqual(response.version_desc, version_desc1)

        model_path2 = 'fs://source2.pkl'
        model_type2 = '{"flavor.version":2}'
        version_desc2 = 'test create model version2'
        response = client.create_model_version(model_name=model_name, model_path=model_path2,
                                               model_type=model_type2,
                                               version_desc=version_desc2)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_version, '2')
        self.assertEqual(response.model_path, model_path2)
        self.assertEqual(response.model_type, model_type2)
        self.assertEqual(response.version_desc, version_desc2)

    def test_update_model_version(self):
        model_name = 'test_update_model_version'
        model_desc = 'test update model version'
        response = client.create_registered_model(model_name=model_name, model_desc=model_desc)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)

        model_path1 = 'fs://source1.pkl'
        model_type1 = '{"flavor.version":1}'
        version_desc1 = 'test update model version1'
        version_stage1 = ModelVersionStage.GENERATED
        response = client.create_model_version(model_name=model_name, model_path=model_path1,
                                               model_type=model_type1,
                                               version_desc=version_desc1, current_stage=version_stage1)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_version, '1')
        self.assertEqual(response.model_path, model_path1)
        self.assertEqual(response.model_type, model_type1)
        self.assertEqual(response.version_desc, version_desc1)
        self.assertEqual(response.current_stage, version_stage1)

        model_path2 = 'fs://source2.pkl'
        model_type2 = '{"flavor.version":2}'
        version_desc2 = 'test update model version2'
        version_stage2 = ModelVersionStage.VALIDATED
        response = client.update_model_version(model_name=model_name, model_version='1',
                                               model_path=model_path2, model_type=model_type2,
                                               version_desc=version_desc2, current_stage=version_stage2)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_version, '1')
        self.assertEqual(response.model_path, model_path2)
        self.assertEqual(response.model_type, model_type2)
        self.assertEqual(response.version_desc, version_desc2)
        self.assertEqual(response.current_stage, version_stage2)

        response = client.update_model_version(model_name=model_name, model_version='1',
                                               current_stage=ModelVersionStage.DEPLOYED)
        self.assertEqual(response.current_stage, ModelVersionStage.DEPLOYED)

    def test_delete_model_version(self):
        model_name = 'test_delete_model_version'
        model_desc = 'test delete model version'
        response = client.create_registered_model(model_name=model_name, model_desc=model_desc)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)

        model_path = 'fs://source.pkl'
        model_type = '{"flavor.version":1}'
        version_desc = 'test delete model version'
        response = client.create_model_version(model_name=model_name, model_path=model_path,
                                               model_type=model_type, version_desc=version_desc)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_version, '1')
        self.assertEqual(response.model_path, model_path)
        self.assertEqual(response.model_type, model_type)
        self.assertEqual(response.version_desc, version_desc)

        client.delete_model_version(model_name, '1')
        response = client.get_model_version_detail(model_name, '1')
        self.assertIsNone(response)

    def test_get_model_version_detail(self):
        model_name = 'test_get_model_version_detail'
        model_desc = 'test get model version detail'
        response = client.create_registered_model(model_name=model_name, model_desc=model_desc)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)

        model_path = 'fs://source.pkl'
        model_type = '{"flavor.version":1}'
        version_desc = 'test get model version detail'
        response = client.create_model_version(model_name=model_name, model_path=model_path,
                                               model_type=model_type, version_desc=version_desc)
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_version, '1')
        self.assertEqual(response.model_path, model_path)
        self.assertEqual(response.model_type, model_type)
        self.assertEqual(response.version_desc, version_desc)

        response = client.get_model_version_detail(model_name, '1')
        self.assertIsNotNone(response)
        self.assertEqual(response.model_name, model_name)
        self.assertEqual(response.model_version, '1')
        self.assertEqual(response.model_path, model_path)
        self.assertEqual(response.model_type, model_type)
        self.assertEqual(response.version_desc, version_desc)

    def test_update_and_list_notification(self):
        key = 'test_publish_event_key'
        value1 = 'test_publish_event_value1'
        response = client.publish_event(key=key, value=value1)
        self.assertIsNotNone(response)
        self.assertEqual(response.key, key)
        self.assertEqual(response.value, value1)
        self.assertTrue(response.version > 0)
        notifications = client.list_events(key=key)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].key, key)
        self.assertEqual(notifications[0].value, value1)
        self.assertEqual(notifications[0].version, response.version)
        notifications = client.list_events(key=key, version=0)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].key, key)
        self.assertEqual(notifications[0].value, value1)

        value2 = 'test_publish_event_value2'
        old_response = response
        response = client.publish_event(key=key, value=value2)
        self.assertIsNotNone(response)
        self.assertEqual(response.version, old_response.version + 1)
        notifications = client.list_events(key=key)
        self.assertEqual(len(notifications), 2)
        self.assertEqual(notifications[1].key, key)
        self.assertEqual(notifications[1].value, value2)
        self.assertEqual(notifications[1].version, old_response.version + 1)
        notifications = client.list_events(key=key, version=old_response.version)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].key, key)
        self.assertEqual(notifications[0].value, value2)

        old_response = response
        response = client.publish_event(key=key, value=value2)
        self.assertIsNotNone(response)
        self.assertEqual(response.version, old_response.version + 1)
        notifications = client.list_events(key=key)
        self.assertEqual(len(notifications), 3)
        self.assertEqual(notifications[2].key, key)
        self.assertEqual(notifications[2].value, value2)
        self.assertEqual(notifications[2].version, old_response.version + 1)
        notifications = client.list_events(key=key, version=old_response.version)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].key, key)
        self.assertEqual(notifications[0].value, value2)

    def test_listen_notification(self):
        class TestWatcher(EventWatcher):

            def __init__(self, event_type, test_case: TestCase):
                super(TestWatcher, self).__init__()
                self.event_type = event_type
                self.test_case = test_case

            def process(self, notifications):
                self.test_case.assertNotEqual(len(notifications), 0)
                for notification in notifications:
                    print(notification)

        event_type1 = 'test_listen_notification1'
        key1 = 'test_listen_notification_key1'
        client.start_listen_event(key=key1,
                                  watcher=TestWatcher(event_type1, self))
        client.start_listen_event(key=key1,
                                  watcher=TestWatcher(event_type1, self))
        client1.start_listen_event(key=key1,
                                   watcher=TestWatcher(event_type1, self))
        client2.start_listen_event(key=key1,
                                   watcher=TestWatcher(event_type1, self))

        value1 = 'test_listen_notification_value1'
        client.publish_event(key=key1, value=value1)
        value2 = 'test_listen_notification_value2'
        client.publish_event(key=key1, value=value2)

        time.sleep(10)
        value3 = 'test_listen_notification_value3'
        client.publish_event(key=key1, value=value3)

        time.sleep(1)
        client.stop_listen_event(key1)
        client1.stop_listen_event(key1)
        client2.stop_listen_event(key1)

        key2 = 'test_listen_notification_key2'
        client.publish_event(key=key2, value=value1)
        client.publish_event(key=key2, value=value2)

        event_type2 = 'test_listen_notification2'
        client.start_listen_event(key=key2,
                                  watcher=TestWatcher(event_type2, self))
        client1.start_listen_event(key=key2,
                                   watcher=TestWatcher(event_type2, self))
        client2.start_listen_event(key=key2,
                                   watcher=TestWatcher(event_type2, self))

        time.sleep(10)
        client.publish_event(key=key2, value=value3)

        time.sleep(1)
        client.stop_listen_event(key2)
        client1.stop_listen_event(key2)
        client2.stop_listen_event(key2)

    # def test_submit_workflow(self):
    #
    #     def create_job(index) -> BaseJob:
    #         job: BaseJob = LocalCMDJob(exec_cmd='echo "hello {}" && sleep 1'.format(str(index)),
    #                                    job_context=JobContext(),
    #                                    job_config=BaseJobConfig(engine="cmd_line", platform="local"))
    #         job.instance_id = str(index)
    #         return job
    #
    #     def create_workflow() -> Workflow:
    #         ex_workflow = Workflow()
    #         for i in range(3):
    #             job = create_job(i)
    #             ex_workflow.add_job(job)
    #         deps = [JobControlEdge(target_node_id='0', source_node_id='2',
    #                                signal_config=SignalConfig(signal_key=generate_job_status_key('0'),
    #                                                           signal_value=State.FINISHED.value)),
    #                 JobControlEdge(target_node_id='1', source_node_id='2',
    #                                signal_config=SignalConfig(signal_key=generate_job_status_key('1'),
    #                                                           signal_value=State.FINISHED.value))]
    #         ex_workflow.add_edges("2", deps)
    #         workflow_meta = client.register_workflow_execution(name=generate_time_str(),
    #                                                            project_id=None,
    #                                                            execution_state=State.INIT,
    #                                                            workflow_json=dumps(ex_workflow))
    #         ex_workflow.workflow_id = workflow_meta.uuid
    #         return ex_workflow
    #
    #     workflow = create_workflow()
    #     res = client.submit_workflow(json_utils.dumps(workflow))
    #     self.assertEqual(0, res[0])
    #     workflow_id = res[1]
    #     res = client.stop_workflow(workflow_id=workflow_id)
    #     self.assertEqual(0, res[0])
    #     while client.is_alive_workflow(workflow_id)[1]:
    #         time.sleep(1)
    #     self.assertEqual(1, res[0])
    #     execution_meta = client.get_workflow_execution_by_id(workflow_id)
    #     self.assertEqual(State.FINISHED, execution_meta.execution_state)

    def test_dataset_metric_meta(self):
        self.register_workflow_job()

        start = round(time.time())
        end = start + 1
        res = client.register_metric_meta(name='a', dataset_id=1, model_name=None, model_version=None, job_id=1,
                                          start_time=start, end_time=end, uri='/tmp/metric_1',
                                          metric_type=MetricType.DATASET,
                                          tags='', metric_description='', properties=Properties({'a': 'a'}))
        client.update_metric_meta(uuid=res[2].uuid, job_id=5)
        metric_meta_result = client.get_dataset_metric_meta(dataset_id=1)
        self.assertTrue(isinstance(metric_meta_result[2], MetricMeta))
        self.assertEqual(5, metric_meta_result[2].job_id)

        res = client.register_metric_meta(name='b', dataset_id=1, model_name=None, model_version=None, job_id=1,
                                          start_time=start, end_time=end, uri='/tmp/metric_2',
                                          metric_type=MetricType.DATASET,
                                          tags='flink', metric_description='', properties=Properties({'b': 'b'}))
        metric_meta_result = client.get_dataset_metric_meta(dataset_id=1)
        get_metric_meta = client.get_metric_meta(name=res[2].name)

        self.assertEqual(res[2].tags, get_metric_meta[2].tags)

        self.assertTrue(isinstance(metric_meta_result[2], List))
        self.assertEqual(2, len(metric_meta_result[2]))

    @staticmethod
    def register_workflow_job():
        project = client.register_project(name='project')

        return project

    @staticmethod
    def register_model_and_version(project):
        model_name = 'test_create_registered_model'
        model_desc = 'test create registered model'
        model = client.register_model(model_name=model_name, project_id=project.uuid,
                                      model_desc=model_desc)
        version = client.register_model_version(model=model.uuid,
                                                model_path="/tmp",
                                                project_snapshot_id=None)
        return model, version

    def test_model_metric_meta(self):
        project = self.register_workflow_job()
        model, version = self.register_model_and_version(project)
        start = round(time.time())
        end = start + 1
        client.register_metric_meta(name='a', dataset_id=1, model_name=model.name,
                                    model_version=version.version, job_id=1,
                                    start_time=start, end_time=end, uri='/tmp/metric_1',
                                    metric_type=MetricType.MODEL,
                                    tags='', metric_description='', properties=Properties({'a': 'a'}))
        metric_meta_result = client.get_model_metric_meta(model_name=model.name, model_version=version.version)

        self.assertTrue(isinstance(metric_meta_result[2], MetricMeta))

        client.register_metric_meta(name='b', dataset_id=2, model_name=model.name,
                                    model_version=version.version, job_id=3,
                                    start_time=start, end_time=end, uri='/tmp/metric_2',
                                    metric_type=MetricType.MODEL,
                                    tags='', metric_description='', properties=Properties({'b': 'b'}))
        metric_meta_result = client.get_model_metric_meta(model_name=model.name, model_version=version.version)

        self.assertTrue(isinstance(metric_meta_result[2], List))
        self.assertEqual(2, len(metric_meta_result[2]))
        client.delete_metric_meta(metric_meta_result[2][0].uuid)
        metric_meta_result = client.get_model_metric_meta(model_name=model.name, model_version=version.version)
        self.assertTrue(isinstance(metric_meta_result[2], MetricMeta))

    def test_metric_summary(self):
        metric_summary_result = client.register_metric_summary(metric_id=1, metric_key='a', metric_value='1.0')
        self.assertTrue(isinstance(metric_summary_result[2], MetricSummary))

        client.update_metric_summary(uuid=metric_summary_result[2].uuid, metric_value='5.0')

        metric_summary_result = client.get_metric_summary(metric_id=1)
        self.assertTrue(isinstance(metric_summary_result[2], List))
        self.assertEqual('5.0', metric_summary_result[2][0].metric_value)

        client.register_metric_summary(metric_id=1, metric_key='b', metric_value='2.0')
        metric_summary_result = client.get_metric_summary(metric_id=1)

        self.assertEqual(2, len(metric_summary_result[2]))

        client.delete_metric_summary(metric_summary_result[2][0].uuid)
        metric_summary_result = client.get_metric_summary(metric_id=1)
        self.assertEqual(1, len(metric_summary_result[2]))


class TestAIFlowClientSqlite(AIFlowClientTestCases, unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        global client, client1, client2
        print("TestAIFlowClientSqlite setUpClass")
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)
        cls.server = AIFlowServer(store_uri=_SQLITE_DB_URI, port=_PORT)
        cls.server.run()
        client = AIFlowClient(server_uri='localhost:' + _PORT)
        client1 = AIFlowClient(server_uri='localhost:' + _PORT)
        client2 = AIFlowClient(server_uri='localhost:' + _PORT)

    @classmethod
    def tearDownClass(cls) -> None:
        client.stop_listen_event()
        client1.stop_listen_event()
        client2.stop_listen_event()
        cls.server.stop()
        os.remove(_SQLITE_DB_FILE)

    def setUp(self) -> None:
        _get_store(_SQLITE_DB_URI)

    def tearDown(self) -> None:
        store = _get_store(_SQLITE_DB_URI)
        base.metadata.drop_all(store.db_engine)


class TestAIFlowClientSqliteWithSingleHighAvailableServer(
        AIFlowClientTestCases, unittest.TestCase):
    """
    Used to ensure the high available server has the same functionality with normal server.
    """

    @classmethod
    def setUpClass(cls) -> None:
        global client, client1, client2
        print("TestAIFlowClientSqlite setUpClass")
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)
        cls.server = AIFlowServer(store_uri=_SQLITE_DB_URI, port=_PORT, enabled_ha=True,
                                  ha_server_uri='localhost:' + _PORT)
        cls.server.run()
        config = ProjectConfig()
        config.set_server_ip('localhost')
        config.set_server_port('50051')
        config.set_project_name('test_project')
        config.set_enable_ha(True)
        client = AIFlowClient(server_uri='localhost:' + _PORT, project_config=config)
        client1 = AIFlowClient(server_uri='localhost:' + _PORT, project_config=config)
        client2 = AIFlowClient(server_uri='localhost:' + _PORT, project_config=config)

    @classmethod
    def tearDownClass(cls) -> None:
        client.stop_listen_event()
        client.disable_high_availability()
        client1.stop_listen_event()
        client1.disable_high_availability()
        client2.stop_listen_event()
        client2.disable_high_availability()
        cls.server.stop()
        os.remove(_SQLITE_DB_FILE)

    def setUp(self) -> None:
        _get_store(_SQLITE_DB_URI)

    def tearDown(self) -> None:
        store = _get_store(_SQLITE_DB_URI)
        base.metadata.drop_all(store.db_engine)


if __name__ == '__main__':
    unittest.main()
