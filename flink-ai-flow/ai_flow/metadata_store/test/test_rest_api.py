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
import json
import subprocess
import time
import unittest
import requests

HEADER = 'http://localhost:8080'

"""
start server service first
the default server port is 50051 and the proxy port is 8080
make sure no port conflicts
"""


class Test_Rest_Api(unittest.TestCase):
    def setUp(self) -> None:
        subprocess.Popen("cd sbin && bash start_service.sh", shell=True)
        # wait the server and proxy to start
        time.sleep(3)

    def tearDown(self) -> None:
        subprocess.Popen("cd sbin && bash stop_service.sh", shell=True)

    def test_save_example_get_id_name(self):
        example = {
            "example": {
                "name": "example",
                "properties": {
                    "a": "b"
                },
                "description": "wow!",
                "supportType": "EXAMPLE_BOTH",
                "schema": {
                    "name_list": ["a", "b", "c"],
                    "type_list": ["Int32", "Int64", "String"]
                },
                "format": "csv"
            }
        }
        data = json.dumps(example)
        response = requests.post(HEADER + '/aiflow/metadata_store/dataset/save', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(int(result_data.get('uuid')), 1)

        data = '{"id":1}'
        response = requests.post(HEADER + '/aiflow/metadata_store/dataset/get/id', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('name'), 'example')

        data = '{"name":"example"}'
        response = requests.post(HEADER + '/aiflow/metadata_store/dataset/get/name', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('name'), 'example')

        examples = {
            "examples": [{
                "name": "example1"
            }, {
                "name": "example2"
            }]
        }
        data = json.dumps(examples)
        response = requests.post(HEADER + '/aiflow/metadata_store/dataset/save', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(len(result_data.get('examples')), 2)

        data = '{"pageSize":2,"offset":1}'
        response = requests.post(HEADER + '/aiflow/metadata_store/dataset/list', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(2, len(result_data.get('examples')))

    def test_project(self):
        project = {
            "project": {"name": "project"}
        }
        data = json.dumps(project)
        response = requests.post(HEADER + '/aiflow/metadata_store/project/save', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(int(result_data.get('uuid')), 1)

        data = '{"id":1}'
        response = requests.post(HEADER + '/aiflow/metadata_store/project/get/id', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('name'), 'project')

        data = '{"name":"project"}'
        response = requests.post(HEADER + '/aiflow/metadata_store/project/get/name', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('name'), 'project')

        data = '{"pageSize":2,"offset":0}'
        response = requests.post(HEADER + '/aiflow/metadata_store/project/list', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(1, len(result_data.get('projects')))

    def test_model(self):
        model = {
            "model": {"name": "model",
                      "projectId": 1}
        }
        data = json.dumps(model)
        response = requests.post(HEADER + '/aiflow/metadata_store/model/save', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(int(result_data.get('uuid')), 1)

        data = '{"id":1}'
        response = requests.post(HEADER + '/aiflow/metadata_store/model/get/id', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('name'), 'model')

        data = '{"name":"model"}'
        response = requests.post(HEADER + '/aiflow/metadata_store/model/get/name', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('name'), 'model')

        data = '{"pageSize":2,"offset":0}'
        response = requests.post(HEADER + '/aiflow/metadata_store/model/list', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(1, len(result_data.get('models')))

    def test_model_version(self):
        model_version = {
            "modelVersion": {"version": "model version",
                             "modelId": 1,
                             "workflowExecutionId": 1}
        }
        data = json.dumps(model_version)
        response = requests.post(HEADER + '/aiflow/metadata_store/modelVersion/save', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('version'), 'model version')

        data = '{"name":"model version"}'
        response = requests.post(HEADER + '/aiflow/metadata_store/modelVersion/get/version', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('version'), 'model version')

        version = '{"name":"model version"}'
        requests.post(HEADER + '/aiflow/metadata_store/modelVersion/delete/version', data=version, verify=False)

        data = '{"modelId":1, "pageSize":2,"offset":0}'
        response = requests.post(HEADER + '/aiflow/metadata_store/modelVersion/list', data=data, verify=False)
        return_code = json.loads(response.text).get('return_code')
        self.assertEqual(return_code, '2002')

    def test_workflow_execution(self):
        workflow_execution = {
            "workflowExecution": {"name": "execution",
                                  "projectId": 1}
        }
        data = json.dumps(workflow_execution)
        response = requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/save', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(int(result_data.get('uuid')), 1)

        data = '{"id":1}'
        response = requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/get/id', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('name'), 'execution')

        data = '{"name":"execution"}'
        response = requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/get/name', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('name'), 'execution')

        data = '{"pageSize":2,"offset":0}'
        response = requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/list', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(1, len(result_data.get('workflow_executions')))

    def test_job(self):
        job = {
            "job": {"name": "job",
                    "workflowExecutionId": 1}
        }
        data = json.dumps(job)
        response = requests.post(HEADER + '/aiflow/metadata_store/job/save', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(int(result_data.get('uuid')), 1)

        data = '{"id":1}'
        response = requests.post(HEADER + '/aiflow/metadata_store/job/get/id', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('name'), 'job')

        data = '{"state": "FINISHED", "name":"job"}'
        response = requests.post(HEADER + '/aiflow/metadata_store/job/update', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data, 1)

        data = '{"name":"job"}'
        response = requests.post(HEADER + '/aiflow/metadata_store/job/get/name', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        self.assertEqual(result_data.get('name'), 'job')
        self.assertEqual(result_data.get('state'), 'FINISHED')

        data = '{"id":1}'
        requests.post(HEADER + '/aiflow/metadata_store/job/delete/id', data=data, verify=False)

        job_1 = {
            "job": {"name": "job1",
                    "workflowExecutionId": 1}
        }
        data = json.dumps(job_1)
        requests.post(HEADER + '/aiflow/metadata_store/job/save', data=data, verify=False)

        data = '{"name":"job1"}'
        requests.post(HEADER + '/aiflow/metadata_store/job/delete/name', data=data, verify=False)

        data = '{"pageSize":2,"offset":0}'
        response = requests.post(HEADER + '/aiflow/metadata_store/job/list', data=data, verify=False)
        return_code = json.loads(response.text).get('return_code')
        self.assertEqual(return_code, '2002')


class Test_delete_rest_api(unittest.TestCase):

    def setUp(self) -> None:
        subprocess.Popen("cd sbin && bash start_service.sh", shell=True)
        # wait the server and proxy to start
        time.sleep(3)

    def tearDown(self) -> None:
        subprocess.Popen("cd sbin && bash stop_service.sh", shell=True)

    def test_delete_example_by_id(self):
        example = {
            "example": {
                "name": "example",
                "properties": {
                    "a": "b"
                },
                "supportType": "EXAMPLE_BOTH",
                "format": "csv"
            }
        }
        data = json.dumps(example)
        response = requests.post(HEADER + '/aiflow/metadata_store/dataset/save', data=data, verify=False)
        result_data = json.loads(json.loads(response.text).get('data'))
        uuid = int(result_data.get('uuid'))

        data = '{"id":' + str(uuid) + '}'
        requests.post(HEADER + '/aiflow/metadata_store/dataset/delete/id', data=data, verify=False)

        data = '{"id":1}'
        response = requests.post(HEADER + '/aiflow/metadata_store/dataset/get/id', data=data, verify=False)
        return_code = json.loads(response.text).get('return_code')
        self.assertEqual(return_code, '2002')

    def test_delete_example_by_name(self):
        example = {
            "example": {
                "name": "example1",
                "properties": {
                    "a": "b"
                },
                "supportType": "EXAMPLE_BOTH",
                "format": "csv"
            }
        }
        data = json.dumps(example)
        requests.post(HEADER + '/aiflow/metadata_store/dataset/save', data=data, verify=False)

        data = '{"name":"example1"}'
        requests.post(HEADER + '/aiflow/metadata_store/dataset/delete/name', data=data, verify=False)

        response = requests.post(HEADER + '/aiflow/metadata_store/dataset/get/name', data=data, verify=False)
        return_code = json.loads(response.text).get('return_code')
        self.assertEqual(return_code, '2002')

    def test_delete_project_by_id(self):
        project = {
            "project": {"name": "project"}
        }
        model = {
            "model": {"name": "model",
                      "projectId": 1}
        }
        workflow_execution = {
            "workflowExecution": {"name": "execution",
                                  "projectId": 1}
        }
        model_version = {
            "modelVersion": {"version": "model version",
                             "modelId": 1,
                             "workflowExecutionId": 1}
        }
        job = {
            "job": {"name": "job",
                    "workflowExecutionId": 1}
        }
        requests.post(HEADER + '/aiflow/metadata_store/project/save', data=json.dumps(project), verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/model/save', data=json.dumps(model), verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/save', data=json.dumps(workflow_execution),
                      verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/modelVersion/save', data=json.dumps(model_version), verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/job/save', data=json.dumps(job), verify=False)

        data = '{"id":1}'
        requests.post(HEADER + '/aiflow/metadata_store/project/delete/id', data=data, verify=False)
        self.assertEqual('2002',
                         json.loads(requests.post(HEADER + '/aiflow/metadata_store/project/get/id', data=data,
                                                  verify=False).text).get('return_code'))
        self.assertEqual('2002',
                         json.loads(requests.post(HEADER + '/aiflow/metadata_store/model/get/id', data=data,
                                                  verify=False).text).get('return_code'))
        self.assertEqual('2002',
                         json.loads(requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/get/id',
                                                  data=data, verify=False).text).get(
                             'return_code'))
        version = '{"name":"model version"}'
        self.assertEqual(
            json.loads(requests.post(HEADER + '/aiflow/metadata_store/modelVersion/get/version', data=version,
                                     verify=False).text).get(
                'return_code'), '2002')
        self.assertEqual('2002', json.loads(
            requests.post(HEADER + '/aiflow/metadata_store/job/get/id', data=data, verify=False).text).get(
            'return_code'))

    def test_delete_project_by_name(self):
        project = {
            "project": {"name": "project1"}
        }
        model = {
            "model": {"name": "model1",
                      "projectId": 2}
        }
        workflow_execution = {
            "workflowExecution": {"name": "execution1",
                                  "projectId": 2}
        }
        model_version = {
            "modelVersion": {"version": "model version1",
                             "modelId": 2,
                             "workflowExecutionId": 2}
        }
        job = {
            "job": {"name": "job1",
                    "workflowExecutionId": 2}
        }
        requests.post(HEADER + '/aiflow/metadata_store/project/save', data=json.dumps(project), verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/model/save', data=json.dumps(model), verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/save', data=json.dumps(workflow_execution),
                      verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/modelVersion/save', data=json.dumps(model_version), verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/job/save', data=json.dumps(job), verify=False)

        data = '{"name":"project1"}'
        requests.post(HEADER + '/aiflow/metadata_store/project/delete/name', data=data, verify=False)

        data = '{"id":2}'
        self.assertEqual('2002',
                         json.loads(requests.post(HEADER + '/aiflow/metadata_store/project/get/id', data=data,
                                                  verify=False).text).get('return_code'))
        self.assertEqual('2002',
                         json.loads(requests.post(HEADER + '/aiflow/metadata_store/model/get/id', data=data,
                                                  verify=False).text).get('return_code'))
        self.assertEqual('2002',
                         json.loads(requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/get/id',
                                                  data=data, verify=False).text).get(
                             'return_code'))
        version = '{"name":"model version"}'
        self.assertEqual(
            json.loads(requests.post(HEADER + '/aiflow/metadata_store/modelVersion/get/version', data=version,
                                     verify=False).text).get(
                'return_code'), '2002')
        self.assertEqual('2002', json.loads(
            requests.post(HEADER + '/aiflow/metadata_store/job/get/id', data=data, verify=False).text).get(
            'return_code'))

    def test_delete_model_by_id(self):
        model = {
            "model": {"name": "model_deleted",
                      "projectId": 1}
        }
        model_version = {
            "modelVersion": {"version": "model version deleted",
                             "modelId": 1,
                             "workflowExecutionId": 1}
        }
        requests.post(HEADER + '/aiflow/metadata_store/model/save', data=json.dumps(model), verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/modelVersion/save', data=json.dumps(model_version), verify=False)

        data = '{"id":1}'
        requests.post(HEADER + '/aiflow/metadata_store/model/delete/id', data=data, verify=False)

        model_name = '{"name": "model_deleted"}'
        self.assertEqual('2002', json.loads(
            requests.post(HEADER + '/aiflow/metadata_store/model/get/name', data=model_name, verify=False).text).get(
            'return_code'))

        version = '{"name":"model version deleted"}'
        self.assertEqual('2002', json.loads(
            requests.post(HEADER + '/aiflow/metadata_store/modelVersion/get/version', data=version,
                          verify=False).text).get(
            'return_code'))

    def test_delete_model_by_name(self):
        model = {
            "model": {"name": "model_deleted_name",
                      "projectId": 1}
        }
        model_version = {
            "modelVersion": {"version": "model version deleted name",
                             "modelId": 1,
                             "workflowExecutionId": 1}
        }
        requests.post(HEADER + '/aiflow/metadata_store/model/save', data=json.dumps(model), verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/modelVersion/save', data=json.dumps(model_version), verify=False)

        data = '{"name":"model_deleted_name"}'
        requests.post(HEADER + '/aiflow/metadata_store/model/delete/name', data=data, verify=False)

        model_name = '{"name": "model_deleted_name"}'
        self.assertEqual('2002', json.loads(
            requests.post(HEADER + '/aiflow/metadata_store/model/get/name', data=model_name, verify=False).text).get(
            'return_code'))

        version = '{"name":"model version deleted name"}'
        response = requests.post(HEADER + '/aiflow/metadata_store/modelVersion/get/version', data=version,
                                 verify=False)
        self.assertEqual('2002', json.loads(
            requests.post(HEADER + '/aiflow/metadata_store/modelVersion/get/version', data=version,
                          verify=False).text).get(
            'return_code'))

    def test_delete_workflow_execution_by_id(self):
        workflow_execution = {
            "workflowExecution": {"name": "execution_deleted_id",
                                  "projectId": 1}
        }
        model_version = {
            "modelVersion": {"version": "model version 1",
                             "modelId": 1,
                             "workflowExecutionId": 1}
        }
        job = {
            "job": {"name": "job",
                    "workflowExecutionId": 1}
        }
        requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/save', data=json.dumps(workflow_execution),
                      verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/modelVersion/save', data=json.dumps(model_version), verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/job/save', data=json.dumps(job), verify=False)
        data = '{"id":1}'
        requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/delete/id', data=data, verify=False)
        self.assertEqual('2002',
                         json.loads(requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/get/id',
                                                  data=data, verify=False).text).get(
                             'return_code'))
        version = '{"name":"model version 1"}'
        self.assertEqual('2002',
                         json.loads(
                             requests.post(HEADER + '/aiflow/metadata_store/modelVersion/get/version', data=version,
                                           verify=False).text).get(
                             'return_code'))
        self.assertEqual('2002',
                         json.loads(requests.post(HEADER + '/aiflow/metadata_store/job/get/id', data=data,
                                                  verify=False).text).get('return_code'))

    def test_delete_workflow_execution_by_name(self):
        workflow_execution = {
            "workflowExecution": {"name": "execution_deleted_name",
                                  "projectId": 1}
        }
        model_version = {
            "modelVersion": {"version": "model version 2",
                             "modelId": 1,
                             "workflowExecutionId": 1}
        }
        job = {
            "job": {"name": "job",
                    "workflowExecutionId": 1}
        }
        requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/save', data=json.dumps(workflow_execution),
                      verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/modelVersion/save', data=json.dumps(model_version), verify=False)
        requests.post(HEADER + '/aiflow/metadata_store/job/save', data=json.dumps(job), verify=False)
        data = '{"name": "execution_deleted_name"}'
        requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/delete/name', data=data, verify=False)
        self.assertEqual('2002',
                         json.loads(requests.post(HEADER + '/aiflow/metadata_store/workflowExecution/get/id',
                                                  data=data, verify=False).text).get(
                             'return_code'))
        version = '{"name":"model version 1"}'
        self.assertEqual('2002',
                         json.loads(
                             requests.post(HEADER + '/aiflow/metadata_store/modelVersion/get/version', data=version,
                                           verify=False).text).get(
                             'return_code'))
        self.assertEqual('2002',
                         json.loads(requests.post(HEADER + '/aiflow/metadata_store/job/get/id', data=data,
                                                  verify=False).text).get('return_code'))
