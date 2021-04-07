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
    def __init__(self, id, namespace, state, name=None):
        self.id = id
        self.name = name
        self.state = state
        self.namespace = namespace

    def __repr__(self):
        return "[%s(%r)]" % (self.__class__, self.__dict__)


class VVPRestfulUtil(object):
    def __init__(self, base_url, namespaces, tokens=None) -> None:
        self.base_url = base_url
        self.token_map = {}
        self.namespaces = namespaces.split(',')
        if tokens is None:
            for ns in self.namespaces:
                self.token_map[ns] = None
        else:
            ts = tokens.split(',')
            if len(ts) != len(self.namespaces):
                raise Exception('namespaces and tokens must the same length!')
            for i in range(len(self.namespaces)):
                self.token_map[self.namespaces[i]] = ts[i]

    def get_token(self, namespace) -> []:
        return self.token_map.get(namespace)

    def get_namespaces(self)->[]:
        return self.namespaces

    def get_headers(self, token):
        return {'Authorization': '{} {}'.format('Bearer', token)}

    def list_deployments(self, namespace, token=None):
        if token is None:
            my_headers = self.get_headers(self.get_token(namespace))
        else:
            my_headers = self.get_headers(token)
        url = self.base_url + "/api/v1/namespaces/{}/deployments".format(namespace)
        response = requests.get(url=url, headers=my_headers)
        items = json.loads(response.content)['data']['items']
        result = []
        for item in items:
            result.append(DeploymentSpec(id=item['metadata']['id'],
                                         namespace=namespace,
                                         name=item['metadata']['name'],
                                         state=item['status']['state']))
        return result

    def start_deployment(self, namespace, deployment_id, token=None) -> bool:
        if token is None:
            my_headers = self.get_headers(self.get_token(namespace))
        else:
            my_headers = self.get_headers(token)
        url = self.base_url + "/api/v1/namespaces/{}/deployments/{}".format(namespace, deployment_id)
        json_content = {
            "spec": {
                "state": "RUNNING"
            }
        }
        headers = {'Content-Type': 'application/json'}
        headers.update(my_headers)
        response = requests.patch(url=url, data=json.dumps(json_content), headers=headers)
        if 200 == response.status_code:
            return True
        else:
            return False

    def stop_deployment(self, namespace, deployment_id, token=None) -> bool:
        if token is None:
            my_headers = self.get_headers(self.get_token(namespace))
        else:
            my_headers = self.get_headers(token)
        url = self.base_url + "/api/v1/namespaces/{}/deployments/{}".format(namespace, deployment_id)
        json_content = {
            "spec": {
                "state": "CANCELLED",
            }
        }
        headers = {'Content-Type': 'application/json'}
        headers.update(my_headers)
        response = requests.patch(url=url, data=json.dumps(json_content), headers=headers)
        if 200 == response.status_code:
            return True
        else:
            return False
