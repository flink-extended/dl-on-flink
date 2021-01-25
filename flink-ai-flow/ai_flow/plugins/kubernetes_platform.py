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
import threading
import traceback
import logging
from typing import Text, List
from kubernetes import client as k8s_cli, watch
from ai_flow.deployer.listener import JobStatusEvent
from ai_flow.deployer.utils import kubernetes_util
from ai_flow.meta.job_meta import State
from ai_flow.plugins.platform import AbstractPlatform, AbstractJobStatusListener, AbstractJobHandler


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
    def job_status_listener() -> type(AbstractJobStatusListener):
        return KubernetesJobStatusListener

    @staticmethod
    def platform() -> Text:
        return 'kubernetes'


class KubernetesJobHandler(AbstractJobHandler):
    def __init__(self, job_instance_id: Text, job_uuid: int, workflow_id: int):
        super(KubernetesJobHandler, self).__init__(job_instance_id, job_uuid, workflow_id)
        self.platform = KubernetesPlatform.platform()


class KubernetesJobStatusListener(AbstractJobStatusListener):
    def __init__(self):
        super().__init__(platform='kubernetes')
        self.job_handles: List[AbstractJobHandler] = []
        self.status_map = {}
        self.running = True
        self.lock = threading.Lock()
        self.started = False

    def listen(self):

        def is_watched(annotation_meta):
            if ANNOTATION_WATCHED in annotation_meta:
                if annotation_meta[ANNOTATION_WATCHED] == 'True':
                    return True
                return False
            else:
                return False

        v1 = k8s_cli.CoreV1Api()
        watcher = watch.Watch()
        for event in watcher.stream(v1.list_namespaced_pod, ANNOTATION_PREFIX):
            if not self.running:
                watcher.stop()
            self.lock.acquire()
            try:
                meta = event['object'].metadata.annotations
                if meta is not None:
                    logging.debug(meta)
                    if is_watched(meta):
                        job_id = meta[ANNOTATION_JOB_ID]
                        job_uuid = meta[ANNOTATION_JOB_UUID]
                        phase = event['object'].status.phase
                        logging.debug(phase)
                        if phase == 'Pending':
                            status = State.STARTING
                        elif phase == 'Running':
                            status = State.RUNNING
                        elif phase == 'Succeeded':
                            status = State.FINISHED
                        elif phase == 'Failed':
                            status = State.FAILED
                        if job_uuid in self.status_map:
                            ss = self.status_map[job_uuid]
                            if ss == status:
                                continue
                        self.status_map[job_uuid] = status
                        if status == State.STARTING:
                            continue
                        workflow_id = int(meta[ANNOTATION_WORKFLOW_ID])
                        event = JobStatusEvent(job_id=job_id, status=status.value, workflow_id=workflow_id)
                        self.message_queue.send(event)
            except Exception as e:
                logging.info("message: {}".format(str(event)))
                track = traceback.format_exc()
                logging.info(track)
            finally:
                self.lock.release()

    def run(self) -> None:
        try:
            self.listen()
        except Exception as e:
            logging.info(e)
            traceback.print_exc()

    def start_listen(self):
        if not kubernetes_util.kubernetes_cluster_available:
            logging.info("Kubernetes cluster is not available.")
            return
        if not self.started:
            self.setDaemon(daemonic=True)
            self.setName(self.platform + "_listener")
            self.start()
            self.started = True
        else:
            logging.error("The LocalJobStatusListener can not be started twice! "
                          "Please check the code.")

    def stop_listen(self):
        if not kubernetes_util.kubernetes_cluster_available:
            return
        self.running = False
        # self.join()

    def register_job_listening(self, job_handler: AbstractJobHandler):
        # since the api server will push the pod status changing event to watcher, there is no need to register
        # kubernetes job listening explicitly.
        pass

    def stop_job_listening(self, job_id: Text):
        pass


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
