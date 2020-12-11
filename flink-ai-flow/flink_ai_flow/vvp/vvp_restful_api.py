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
import requests
import json
import os
import time
import logging
from ai_flow.common import json_utils

default_flink_image_info = {
    "flinkVersion": "1.11",
    "flinkImageRegistry": "xxx",
    "flinkImageRepository": "vvr",
    "flinkImageTag": "1.11.1-vvr-2.0.1"
}

default_resources = {
    "jobmanager": {
        "cpu": 1.0,
        "memory": "1G"
    },
    "taskmanager": {
        "cpu": 1.0,
        "memory": "2G"
    }
}

default_flink_config = {
    "metrics.reporter.promgatewayappmgr.groupingKey": "deploymentName={{deploymentName}};deploymentId={{deploymentId}};jobId={{jobId}}",
    "metrics.reporter.promgatewayappmgr.jobName": "{{deploymentName}}",
    "metrics.reporter.promgatewayappmgr.port": "9091",
    "metrics.reporters": "promgatewayappmgr",
    "metrics.reporter.promgatewayappmgr.class": "org.apache.flink.metrics.prometheus.PrometheusPushGatewayReporter",
    "metrics.reporter.promgatewayappmgr.host": "xxx"
}

default_logging = {
    "loggingProfile": "default",
    "log4jLoggers": {
        "": "INFO"
    }
}

default_kubernetes = {
    "pods": {
        "annotations": {
            "prometheus.io/scrape": 'true',
            "prometheus.io/port": '9249',
            "prometheus.io/path": "/metrics"
        },
        "labels": {},
        "nodeSelector": {},
        "securityContext": None,
        "affinity": None,
        "envVars": {
            "name": "HADOOP_USER_NAME",
            "value": "hdp-prophet-platform",
            "valueFrom": None
        }
    }
}

default_upgrade_strategy = {"kind": "STATEFUL"}


default_restore_strategy = {"kind": "LATEST_STATE", "allowNonRestoredState": False }


class DeploymentSpec(json_utils.Jsonable):
    def __init__(self, id, name, state):
        self.id = id
        self.name = name
        self.state = state

    def __repr__(self):
        return "[%s(%r)]" % (self.__class__, self.__dict__)


class VVPRestful(json_utils.Jsonable):
    def __init__(self, base_url, namespace, token) -> None:
        self.base_url = base_url
        self.namespace = namespace
        if token is None:
            self.headers = {}
        else:
            self.headers = {'Authorization': '{} {}'.format('Bearer', token)}

    def up_load_artifact(self, artifact_path) -> str:
        url = self.base_url + "/artifacts/v1/namespaces/{}/artifacts:upload".format(self.namespace)
        file_name = os.path.basename(artifact_path)
        json_content = {
            "artifact": {
                "filename": file_name,
                "content": "",
            }
        }
        files = {'file': open(artifact_path, 'rb')}
        response = requests.post(url=url, json=json_content, files=files, headers=self.headers)
        return json.loads(response.content)['data']['artifact']['uri']

    def list_artifacts(self) -> list:
        url = self.base_url + "/artifacts/v1/namespaces/{}/artifacts:list".format(self.namespace)
        response = requests.get(url=url, headers=self.headers)
        return json.loads(response.content)['data']['artifacts']

    def list_deployment_targets(self):
        url = self.base_url + "/api/v1/namespaces/{}/deployment-targets".format(self.namespace)
        response = requests.get(url=url, headers=self.headers)
        return json.loads(response.content)['data']['items']

    def list_deployments(self):
        url = self.base_url + "/api/v1/namespaces/{}/deployments".format(self.namespace)
        response = requests.get(url=url, headers=self.headers)
        items = json.loads(response.content)['data']['items']
        result = []
        for item in items:
            result.append(DeploymentSpec(id=item['metadata']['id'],
                                         name=item['metadata']['name'],
                                         state=item['status']['state']))
        return result

    def get_deployment(self, id):
        url = self.base_url + "/api/v1/namespaces/{}/deployments/{}".format(self.namespace, id)
        response = requests.get(url=url, headers=self.headers)
        if 200 == response.status_code:
            item = json.loads(response.content)['data']
            result = DeploymentSpec(id=item['metadata']['id'],
                                    name=item['metadata']['name'],
                                    state=item['status']['state'])
            return result
        else:
            logging.error('{} {}'.format(response.status_code, response.content))
            return None

    def get_deployment_target_id(self) -> str:
        targets = self.list_deployment_targets()
        for target in targets:
            if target['metadata']['namespace'] == self.namespace:
                return target['metadata']['id']
        return ''

    def create_deployment(self,
                          name,
                          jar_uri,
                          entry_class,
                          main_args="",
                          addition_dependencies=[],
                          flink_image_info=default_flink_image_info,
                          parallelism=1,
                          resources=default_resources,
                          flink_config=default_flink_config,
                          logging=default_logging,
                          upgrade_strategy=default_upgrade_strategy,
                          restore_strategy=default_restore_strategy,
                          kubernetes=default_kubernetes,
                          spec=None):
        url = self.base_url + "/api/v1/namespaces/{}/deployments".format(self.namespace)
        target_id = self.get_deployment_target_id()
        if spec is None:
            json_content = {
                "kind": "Deployment",
                "apiVersion": "v1",
                "metadata": {
                    "name": name,
                    "namespace": self.namespace,
                },
                "spec": {
                    "state": "RUNNING",
                    "upgradeStrategy": upgrade_strategy,
                    "restoreStrategy": restore_strategy,
                    "deploymentTargetId": target_id,
                    "maxSavepointCreationAttempts": 4,
                    "maxJobCreationAttempts": 4,
                    "template": {
                        "metadata": {
                            "annotations": {
                                "flink.security.ssl.enabled": "false",
                                "flink.queryable-state.enabled": "false"
                            }
                        },
                        "spec": {
                            "artifact": {
                                "kind": "JAR",
                                "jarUri": jar_uri,
                                "entryClass": entry_class,
                                "mainArgs": main_args,
                                "additionalDependencies": addition_dependencies,
                                "flinkVersion": flink_image_info['flinkVersion'],
                                "flinkImageRegistry": flink_image_info["flinkImageRegistry"],
                                "flinkImageRepository": flink_image_info["flinkImageRepository"],
                                "flinkImageTag": flink_image_info["flinkImageTag"]
                            },
                            "parallelism": parallelism,
                            "resources": resources,
                            "flinkConfiguration": flink_config,
                            "logging": logging,
                            "kubernetes": kubernetes
                        }
                    }
                }
            }
        else:
            json_content = {
                "kind": "Deployment",
                "apiVersion": "v1",
                "metadata": {
                    "name": name,
                    "namespace": self.namespace,
                },
                "spec": spec
            }
        response = requests.post(url=url, json=json_content, headers=self.headers)
        result = json.loads(response.content)
        return result['data']['metadata']['id'], result

    def start_deployment(self, deployment_id) -> bool:
        url = self.base_url + "/api/v1/namespaces/{}/deployments/{}".format(self.namespace, deployment_id)
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

    def stop_deployment(self, deployment_id) -> bool:
        url = self.base_url + "/api/v1/namespaces/{}/deployments/{}".format(self.namespace, deployment_id)
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

    def delete_deployment(self, deployment_id) -> bool:
        url = self.base_url + "/api/v1/namespaces/{}/deployments/{}".format(self.namespace, deployment_id)
        response = requests.delete(url=url, headers=self.headers)
        if 200 == response.status_code:
            return True
        else:
            return False

    def get_deployment_events(self, deployment_id):
        url = self.base_url + "/api/v1/namespaces/{}/events".format(self.namespace)
        response = requests.get(url=url, params={'deploymentId': deployment_id}, headers=self.headers)
        print(response.content)
        return json.loads(response.content)

    def get_job_events(self, job_id):
        url = self.base_url + "/api/v1/namespaces/{}/events".format(self.namespace)
        response = requests.get(url=url, params={'jobId': job_id}, headers=self.headers)
        return json.loads(response.content)

    def get_job_ids(self, deployment_id) -> list:
        url = self.base_url + "/api/v1/namespaces/{}/jobs".format(self.namespace)
        response = requests.get(url=url, params={'deploymentId': deployment_id}, headers=self.headers)
        jobs = json.loads(response.content)['data']['items']
        job_id_list = []
        for job in jobs:
            job_id_list.append(job['metadata']['id'])
        return job_id_list

    def wait_deployment_state(self, deployment_id, state=set(["CANCELLED"]), timeout=None, interval=15,
                              max_retry_num=3) -> bool:
        retry_num = 0
        if timeout is None:
            while True:
                deployment = self.get_deployment(deployment_id)
                if deployment is None and retry_num < max_retry_num:
                    time.sleep(interval)
                    retry_num += 1
                    continue
                else:
                    if deployment is None:
                        raise Exception("can not get deployment information for {} times".format(max_retry_num))
                    else:
                        retry_num = 0

                if deployment.state in state:
                    return True
                logging.debug("wait deployment: {} state: {}".format(deployment_id, state))
                time.sleep(interval)
        else:
            num = (timeout / interval) + 1
            for i in range(num):
                deployment = self.get_deployment(deployment_id)
                if deployment.state in state:
                    return True
                time.sleep(interval)
            return False

    def sync_start_deployment(self, deployment_id):
        res = self.start_deployment(deployment_id=deployment_id)
        if res:
            self.wait_deployment_state(deployment_id=deployment_id, state=set(['RUNNING']))
        else:
            raise Exception('start deployment {} failed!'.format(deployment_id))
        return True

    def sync_stop_deployment(self, deployment_id):
        res = self.stop_deployment(deployment_id=deployment_id)
        if res:
            self.wait_deployment_state(deployment_id=deployment_id, state=set(['CANCELLED', 'FINISHED']))
        else:
            raise Exception('stop deployment {} failed!'.format(deployment_id))

    def submit_job(self,
                   name,
                   artifact_path,
                   entry_class='',
                   main_args='',
                   addition_dependencies=[],
                   flink_image_info=default_flink_image_info,
                   parallelism=1,
                   resources=default_resources,
                   flink_config=default_flink_config,
                   logging=default_logging,
                   upgrade_strategy=default_upgrade_strategy,
                   restore_strategy=default_restore_strategy,
                   kubernetes=default_kubernetes,
                   spec=None,
                   job_type='java'):
        current_deployment = None
        deployments = self.list_deployments()
        for deployment in deployments:
            if deployment.name == name:
                current_deployment = deployment
                break
        if current_deployment is not None and current_deployment.state != 'CANCELLED':
            self.sync_stop_deployment(current_deployment.id)

        # artifacts = self.list_artifacts()
        #
        # def upload_artifact(package):
        #     file_name = os.path.basename(package)
        #     uri = None
        #     for artifact in artifacts:
        #         if artifact['filename'] == file_name:
        #             uri = artifact['uri']
        #             break
        #     if uri is None:
        #         uri = self.up_load_artifact(package)
        #     return uri
        #
        # artifact_uri = upload_artifact(artifact_path)
        # add_deps = []
        # for dep in addition_dependencies:
        #     add_deps.append(upload_artifact(dep))

        if current_deployment is None:
            if 'python' == job_type:
                main_class = 'org.apache.flink.client.python.PythonDriver'
            else:
                main_class = entry_class
            deployment_id, info = self.create_deployment(name=name,
                                                         jar_uri=artifact_path,
                                                         entry_class=main_class,
                                                         main_args=main_args,
                                                         addition_dependencies=addition_dependencies,
                                                         flink_image_info=flink_image_info,
                                                         parallelism=parallelism,
                                                         resources=resources,
                                                         flink_config=flink_config,
                                                         logging=logging,
                                                         upgrade_strategy=upgrade_strategy,
                                                         restore_strategy=restore_strategy,
                                                         kubernetes=kubernetes,
                                                         spec=spec)
        else:
            deployment_id = current_deployment.id

        res = self.sync_start_deployment(deployment_id)
        if res:
            job_id = self.get_job_ids(deployment_id)[0]
        else:
            raise Exception("start deployment {} failed!".format(deployment_id))
        return deployment_id, job_id

