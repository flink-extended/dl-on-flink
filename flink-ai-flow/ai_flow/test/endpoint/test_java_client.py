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
import os
import subprocess
import unittest

from ai_flow.endpoint.server.server import AIFlowServer
from ai_flow.store.db.base_model import base
from ai_flow.test.store.test_sqlalchemy_store import _get_store
from notification_service.event_storage import DbEventStorage

_SQLITE_DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aiflow.db')
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)
_CONFIG_FILE_PATH = '../../java/client/src/test/resources/test.properties'


class JavaAIFlowClientTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        port = cls._get_properties(_CONFIG_FILE_PATH, 'port')
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)
        cls.server = AIFlowServer(store_uri=_SQLITE_DB_URI, port=port, start_scheduler_service=False)
        cls.server.run()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.stop()
        os.remove(_SQLITE_DB_FILE)

    def setUp(self) -> None:
        _get_store(_SQLITE_DB_URI)

    def tearDown(self) -> None:
        store = _get_store(_SQLITE_DB_URI)
        base.metadata.drop_all(store.db_engine)
        storage = DbEventStorage(db_conn=_SQLITE_DB_URI, create_table_if_not_exists=False)
        storage.clean_up()

    @staticmethod
    def _get_properties(file_path: str, key: str):
        try:
            pro_file = open(file_path, 'r')
            properties = {}
            for line in pro_file:
                if line.find('=') > 0:
                    strs = line.replace('\n', '').replace(' ', '').split('=')
                    properties[strs[0]] = strs[1]
            print(properties)
            return properties[key]
        except Exception as e:
            raise e
        finally:
            pro_file.close()

    @staticmethod
    def _run_test_with_java_client(method):
        jar_path = 'java/client/target/aiflow-client-1.0-SNAPSHOT-jar-with-dependencies.jar'
        home_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        jar_abs_path = os.path.join(home_path, jar_path)

        junit_runner = "com.aiflow.client.SingleJUnitTestRunner"
        test_class_and_method = "com.aiflow.client.AIFlowClientTest#{}".format(method)
        print(test_class_and_method)
        subprocess.check_call(["java", "-cp", jar_abs_path, junit_runner, test_class_and_method], shell=False)

    def test_register_dataset(self):
        self._run_test_with_java_client('testRegisterDataset')

    def test_register_dataset_with_catalog(self):
        self._run_test_with_java_client('testRegisterDatasetWithCatalog')

    def test_double_register_dataset(self):
        self._run_test_with_java_client('testDoubleRegisterDataset')

    def test_list_dataset(self):
        self._run_test_with_java_client('testListDataset')

    def test_save_and_list_datasets(self):
        self._run_test_with_java_client('testSaveAndListDatasets')

    def test_delete_dataset(self):
        self._run_test_with_java_client('testDeleteDataset')

    def test_update_dataset(self):
        self._run_test_with_java_client('testUpdateDataset')

    def test_register_project(self):
        self._run_test_with_java_client('testRegisterProject')

    def test_double_register_project(self):
        self._run_test_with_java_client('testDoubleRegisterProject')

    def test_list_projects(self):
        self._run_test_with_java_client('testListProjects')

    def test_delete_project(self):
        self._run_test_with_java_client('testDeleteProject')

    def test_update_project(self):
        self._run_test_with_java_client('testUpdateProject')

    def test_register_workflow(self):
        self._run_test_with_java_client('testRegisterWorkflow')

    def test_double_register_workflow(self):
        self._run_test_with_java_client('testDoubleRegisterWorkflow')

    def test_list_workflows(self):
        self._run_test_with_java_client('testListWorkflows')

    def test_delete_workflow(self):
        self._run_test_with_java_client('testDeleteWorkflow')

    def test_update_workflow(self):
        self._run_test_with_java_client('testUpdateWorkflow')

    def test_model_operations(self):
        self._run_test_with_java_client('testModelOperations')

    def test_register_model_relation(self):
        self._run_test_with_java_client('testRegisterModelRelation')

    def test_list_model_relation(self):
        self._run_test_with_java_client('testListModelRelation')

    def test_model_relation(self):
        self._run_test_with_java_client('deleteModelRelation')

    def test_model_version_operations(self):
        self._run_test_with_java_client('testModelVersionOperations')

    def test_list_model_version(self):
        self._run_test_with_java_client('testListModelVersion')

    def test_delete_model_version_by_version(self):
        self._run_test_with_java_client('testDeleteModelVersionByVersion')

    def test_register_artifact(self):
        self._run_test_with_java_client('testRegisterArtifact')

    def test_double_register_artifact(self):
        self._run_test_with_java_client('testDoubleRegisterArtifact')

    def test_list_artifacts(self):
        self._run_test_with_java_client('testListArtifacts')

    def test_delete_artifact(self):
        self._run_test_with_java_client('testDeleteArtifact')

    def test_update_artifact(self):
        self._run_test_with_java_client('testUpdateArtifact')

    def test_double_create_registered_model(self):
        self._run_test_with_java_client('testDoubleCreateRegisteredModel')

    def test_delete_registered_model(self):
        self._run_test_with_java_client('testDeleteRegisteredModel')

    def test_list_registered_model(self):
        self._run_test_with_java_client('testListRegisteredModel')

    def test_get_registered_model_detail(self):
        self._run_test_with_java_client('testGetRegisteredModelDetail')

    def test_update_model_version(self):
        self._run_test_with_java_client('testUpdateModelVersion')

    def test_delete_model_version(self):
        self._run_test_with_java_client('testDeleteModelVersion')

    def test_update_and_list_notification(self):
        self._run_test_with_java_client('testUpdateAndListNotification')

    def test_listen_notification(self):
        self._run_test_with_java_client('testListenNotification')
