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
import time
from typing import Text, Dict
from ai_flow import State
from ai_flow.deployer.listener import JobStatusEvent
from ai_flow.plugins.platform import AbstractPlatform, AbstractJobStatusListener, AbstractJobHandler
from flink_ai_flow.vvp.vvp_restful_api import VVPRestful


class VVPJobHandler(AbstractJobHandler):

    def __init__(self,
                 vvp_restful: VVPRestful,
                 vvp_job_id: Text,
                 vvp_deployment_id: Text,
                 job_instance_id: Text,
                 job_uuid: int,
                 workflow_id: int) -> None:
        super().__init__(job_instance_id, job_uuid, workflow_id)
        self.platform = VVPPlatform.platform()
        self.vvp_restful: VVPRestful = vvp_restful
        self.vvp_job_id = vvp_job_id
        self.vvp_deployment_id = vvp_deployment_id

    def get_job_status(self) -> State:
        events = self.vvp_restful.get_job_events(self.vvp_job_id)
        for item in events['data']['items']:
            vvp_job_status = item['metadata']['name']
            if 'JOB_SUCCESSFULLY_FINISHED' == vvp_job_status:
                return State.FINISHED
            elif 'GENERAL_FAILURE' == vvp_job_status:
                return State.FAILED
        return State.RUNNING


class VVPJobStatusListener(AbstractJobStatusListener):
    def __init__(self, time_interval=10) -> None:
        super().__init__(platform="vvp")
        self.time_interval = time_interval
        self.job_handles: Dict[int, VVPJobHandler] = {}
        # key job uuid, value State
        self.status_map = {}
        self.running = True

    def listen(self):
        while self.running:
            for handle in self.job_handles.values():
                status = handle.get_job_status()

                # kill job do not send message
                if status is None:
                    if handle.job_instance_id in self.status_map:
                        del self.status_map[handle.job_uuid]
                    time.sleep(self.time_interval)
                    continue
                # send event
                if handle.job_uuid in self.status_map:
                    ss = self.status_map[handle.job_uuid]
                    if ss != status:
                        event = JobStatusEvent(workflow_id=handle.workflow_id,
                                               job_id=handle.job_instance_id,
                                               status=status.value)
                        self.status_map[handle.job_uuid] = status
                        self.message_queue.send(event)
                else:
                    event = JobStatusEvent(workflow_id=handle.workflow_id,
                                           job_id=handle.job_instance_id,
                                           status=State.RUNNING.value)
                    self.status_map[handle.job_uuid] = State.RUNNING
                    self.message_queue.send(event)
                    if status != State.RUNNING:
                        event = JobStatusEvent(workflow_id=handle.workflow_id,
                                               job_id=handle.job_instance_id,
                                               status=status.value)
                        self.status_map[handle.job_uuid] = status
                        self.message_queue.send(event)

            # clean up status_map
            key_set = set()
            for k, v in self.status_map.items():
                if v == State.FINISHED or v == State.FAILED:
                    key_set.add(k)
            for k in key_set:
                del self.status_map[k]
            time.sleep(self.time_interval)

    def run(self):
        self.listen()

    def start_listen(self):
        self.setDaemon(daemonic=True)
        self.setName(self.platform + "_listener")
        self.start()

    def stop_listen(self):
        self.running = False
        self.join()

    def register_job_listening(self, job_handler: VVPJobHandler):
        self.job_handles[job_handler.job_uuid] = job_handler

    def stop_job_listening(self, job_uuid: int):
        lock = threading.Lock()
        with lock:
            if job_uuid in self.job_handles:
                del self.job_handles[job_uuid]


class VVPPlatform(AbstractPlatform):
    @staticmethod
    def platform() -> Text:
        return 'vvp'

    @staticmethod
    def job_status_listener() -> type(AbstractJobStatusListener):
        return VVPJobStatusListener
