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
import requests
import json


class DeploymentSpec(object):
    def __init__(self, id, name, state):
        self.id = id
        self.name = name
        self.state = state

    def __repr__(self):
        return "[%s(%r)]" % (self.__class__, self.__dict__)


class VVPRestfulUtil(object):
    def __init__(self, base_url, namespaces, token=None) -> None:
        self.base_url = base_url
        self.namespaces = namespaces
        if token is None:
            self.headers = {}
        else:
            self.headers = {'Authorization': '{} {}'.format('Bearer', token)}

    def get_namespaces(self)->[]:
        return self.namespaces.split(',')

    def list_deployments(self, namespace):
        url = self.base_url + "/api/v1/namespaces/{}/deployments".format(namespace)
        response = requests.get(url=url, headers=self.headers)
        items = json.loads(response.content)['data']['items']
        result = []
        for item in items:
            result.append(DeploymentSpec(id=item['metadata']['id'],
                                         name=item['metadata']['name'],
                                         state=item['status']['state']))
        return result

    def start_deployment(self, namespace, deployment_id) -> bool:
        url = self.base_url + "/api/v1/namespaces/{}/deployments/{}".format(namespace, deployment_id)
        json_content = {
            "spec": {
                "state": "RUNNING"
            }
        }
        headers = {'Content-Type': 'application/json'}
        headers.update(self.headers)
        response = requests.patch(url=url, data=json.dumps(json_content), headers=headers)
        if 200 == response.status_code:
            return True
        else:
            return False

    def stop_deployment(self, namespace, deployment_id) -> bool:
        url = self.base_url + "/api/v1/namespaces/{}/deployments/{}".format(namespace, deployment_id)
        json_content = {
            "spec": {
                "state": "CANCELLED",
            }
        }
        headers = {'Content-Type': 'application/json'}
        headers.update(self.headers)
        response = requests.patch(url=url, data=json.dumps(json_content), headers=headers)
        if 200 == response.status_code:
            return True
        else:
            return False
