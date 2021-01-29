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
import traceback
import logging
from subprocess import Popen
from typing import Text, Any, Dict
from ai_flow.deployer.listener import JobStatusEvent
from ai_flow.meta.job_meta import State
from ai_flow.plugins.platform import AbstractPlatform, AbstractJobHandler, AbstractJobStatusListener


class LocalJobHandler(AbstractJobHandler):

    def __init__(self, job_instance_id: Text, job_uuid: int, workflow_id: int, process_object: Any = None) -> None:
        super().__init__(job_instance_id, job_uuid, workflow_id)
        self.platform = LocalPlatform.platform()
        self.process_object = process_object


class LocalPlatform(AbstractPlatform):
    @staticmethod
    def job_status_listener() -> type(AbstractJobStatusListener):
        return LocalJobStatusListener

    @staticmethod
    def platform() -> Text:
        return 'local'


class LocalJobStatusListener(AbstractJobStatusListener):
    def __init__(self, time_interval=2) -> None:
        super().__init__(platform=LocalPlatform.platform())
        self.time_interval = time_interval
        self.job_handles: Dict[int, LocalJobHandler] = {}
        # key job uuid, value State
        self.status_map = {}
        self.running = True
        self.lock = threading.Lock()
        self.started = False

    def listen(self):
        while self.running:
            self.lock.acquire()
            try:
                key_set = set()
                for handle in self.job_handles.values():
                    if isinstance(handle.process_object, Popen):
                        if handle.process_object.poll() is None:
                            status = State.RUNNING
                        else:
                            if 0 == handle.process_object.returncode:
                                status = State.FINISHED
                            elif -9 == handle.process_object.returncode:
                                logging.info("returncode {}".format(handle.process_object.returncode))
                                status = State.FAILED
                            else:
                                logging.info("returncode {}".format(handle.process_object.returncode))
                                status = State.FAILED
                    elif handle.process_object is None:
                        status = State.RUNNING
                    else:
                        raise Exception("not support exec handle " + str(handle))

                    # kill job do not send message
                    if status is None:
                        logging.info("kill job {}".format(handle.job_instance_id))
                        if handle.job_uuid in self.status_map:
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
                for k, v in self.status_map.items():
                    if v == State.FINISHED or v == State.FAILED:
                        key_set.add(k)
                for k in key_set:
                    if k in self.status_map:
                        del self.status_map[k]
            finally:
                self.lock.release()
            time.sleep(self.time_interval)

    def run(self):
        try:
            self.listen()
        except Exception as e:
            logging.error(e)
            traceback.print_exc()

    def start_listen(self):
        if not self.started:
            self.setDaemon(daemonic=True)
            self.setName(self.platform + "_listener")
            self.start()
            self.started = True
        else:
            logging.error("The LocalJobStatusListener can not be started twice! "
                          "Please check the code.")

    def stop_listen(self):
        self.running = False
        self.join()

    def register_job_listening(self, job_handler: LocalJobHandler):
        self.lock.acquire()
        try:
            self.job_handles[job_handler.job_uuid] = job_handler
        finally:
            self.lock.release()

    def stop_job_listening(self, job_uuid: int):
        self.lock.acquire()
        try:
            if job_uuid in self.job_handles:
                del self.job_handles[job_uuid]
            if job_uuid in self.status_map:
                del self.status_map[job_uuid]
        finally:
            self.lock.release()
