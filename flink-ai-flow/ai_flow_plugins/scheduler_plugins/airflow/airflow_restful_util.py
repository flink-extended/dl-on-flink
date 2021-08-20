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
import sys

import requests
import json
from requests.auth import HTTPBasicAuth
from typing import List, Text, Dict


class AirFlowRestfulUtil(object):
    def __init__(self,
                 endpoint_url: Text,
                 user_name: Text,
                 password: Text
                 ):
        self.endpoint_url = endpoint_url
        self.header = {'Content-type': 'application/json',
                       'Accept': 'application/json'}
        self.auth = HTTPBasicAuth(user_name, password)

    @classmethod
    def parse_response(cls, response):
        if 200 == response.status_code:
            result_json = json.loads(response.content)
        else:
            raise Exception(str(response.reason))
        return result_json

    def list_dags(self) -> List:
        response = requests.get(url='{}/api/v1/dags'.format(self.endpoint_url),
                                headers=self.header,
                                auth=self.auth)
        result_json = self.parse_response(response)
        dags = result_json.get('dags')
        result = []
        for dag in dags:
            result.append(dag.get('dag_id'))
        return result

    def dag_exist(self, dag_id: Text) -> bool:
        dags = set(self.list_dags())
        if dag_id in dags:
            return True
        else:
            return False

    def get_dag(self, dag_id: Text) -> Dict:
        response = requests.get(url='{}/api/v1/dags/{}'.format(self.endpoint_url, dag_id),
                                headers=self.header,
                                auth=self.auth)
        result_json = self.parse_response(response)
        return result_json

    def set_dag_is_paused(self, dag_id: Text, is_paused: bool):
        response = requests.patch(url='{}/api/v1/dags/{}'.format(self.endpoint_url, dag_id),
                                  headers=self.header,
                                  auth=self.auth,
                                  data=json.dumps({'is_paused': is_paused}))
        result_json = self.parse_response(response)
        return result_json

    def list_dagruns(self, dag_id: Text) -> Dict:
        response = requests.get(url='{}/api/v1/dags/{}/dagRuns'.format(self.endpoint_url, dag_id),
                                headers=self.header,
                                auth=self.auth,
                                params={'limit': str(sys.maxsize)})
        result_json = self.parse_response(response)
        return result_json['dag_runs']

    def get_dagrun(self, dag_id: Text, run_id: Text) -> Dict:
        response = requests.get(url='{}/api/v1/dags/{}/dagRuns/{}'.format(self.endpoint_url, dag_id, run_id),
                                headers=self.header,
                                auth=self.auth)
        try:
            result_json = self.parse_response(response)
        except Exception as e:
            result_json = None
        return result_json

    def list_task_instance(self, dag_id: Text, run_id: Text) -> List:
        response = requests.get(url='{}/api/v1/dags/{}/dagRuns/{}/taskInstances'
                                .format(self.endpoint_url, dag_id, run_id),
                                headers=self.header,
                                auth=self.auth)
        result_json = self.parse_response(response)
        return result_json.get('task_instances')

    def get_task_instance(self, dag_id: Text, run_id: Text, task_id: Text) -> Dict:
        response = requests.get(url='{}/api/v1/dags/{}/dagRuns/{}/taskInstances/{}'
                                .format(self.endpoint_url, dag_id, run_id, task_id),
                                headers=self.header,
                                auth=self.auth)
        try:
            result_json = self.parse_response(response)
        except Exception as e:
            result_json = None
        return result_json

    def list_task_execution(self, dag_id: Text, run_id: Text) -> List:
        response = requests.get(url='{}/api/v1/dags/{}/dagRuns/{}/taskExecutions'
                                .format(self.endpoint_url, dag_id, run_id),
                                headers=self.header,
                                auth=self.auth)
        result_json = self.parse_response(response)
        return result_json.get('task_executions')

    def list_task_execution_by_task_id(self, dag_id: Text, run_id: Text, task_id: Text) -> List:
        response = requests.get(url='{}/api/v1/dags/{}/dagRuns/{}/taskInstances/{}/taskExecutions'
                                .format(self.endpoint_url, dag_id, run_id, task_id),
                                headers=self.header,
                                auth=self.auth)
        result_json = self.parse_response(response)
        return result_json.get('task_executions')
