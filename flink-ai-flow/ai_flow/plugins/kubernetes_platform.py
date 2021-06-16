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
import traceback
import logging
from typing import Text, List
from kubernetes import client as k8s_cli, watch
from ai_flow.plugins.platform import AbstractPlatform, AbstractJobHandler


DEFAULT_NAMESPACE = 'ai-flow'

DEFAULT_PROJECT_PATH = '/opt/ai-flow/project'

"""
kubernetes job must has annotations:
'ai-flow/watched'
'ai-flow/job-id'
'ai-flow/job-uuid'
'ai-flow/workflow-id'
"""
ANNOTATION_PREFIX = DEFAULT_NAMESPACE
ANNOTATION_WATCHED = ANNOTATION_PREFIX + '/watched'
ANNOTATION_JOB_ID = ANNOTATION_PREFIX + '/job-id'
ANNOTATION_JOB_UUID = ANNOTATION_PREFIX + '/job-uuid'
ANNOTATION_WORKFLOW_ID = ANNOTATION_PREFIX + '/workflow-id'


class KubernetesPlatform(AbstractPlatform):

    @staticmethod
    def platform() -> Text:
        return 'kubernetes'


class KubernetesJobHandler(AbstractJobHandler):
    def __init__(self, job_instance_id: Text, job_uuid: int, workflow_id: int):
        super(KubernetesJobHandler, self).__init__(job_instance_id, job_uuid, workflow_id)
        self.platform = KubernetesPlatform.platform()


def watch_k8s_job_status(job_name):
    from airflow.exceptions import AirflowException

    v1 = k8s_cli.CoreV1Api()
    watcher = watch.Watch()
    success = False
    for event in watcher.stream(v1.list_namespaced_pod, ANNOTATION_PREFIX):
        try:
            meta = event['object'].metadata.annotations
            if meta is not None:
                phase = event['object'].status.phase
                logging.info(meta)
                logging.info(phase)
                if phase == 'Pending':
                    pass
                elif phase == 'Running':
                    pass
                elif phase == 'Succeeded':
                    success = True
                    break
                elif phase == 'Failed':
                    success = False
                    break
        except Exception as e:
            logging.warning("message: {}".format(str(event)))
            track = traceback.format_exc()
            logging.warning(track)
    watcher.stop()
    if not success:
        raise AirflowException("job: {0} failed!".format(job_name))
    else:
        logging.info("job: {0} succeed!".format(job_name))
