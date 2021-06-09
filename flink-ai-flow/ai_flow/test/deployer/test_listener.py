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
import time
import unittest

from ai_flow.endpoint.client.aiflow_client import AIFlowClient
from kubernetes import client as kube_cli

from ai_flow.common.message_queue import MessageQueue
from ai_flow.deployer.listener import EventListener, EventListenerWatcher, ListenerManager, JobStatusEvent, SimpleEvent
from ai_flow.endpoint.server.server import AIFlowServer
from ai_flow.store.db.base_model import base
from ai_flow.store.sqlalchemy_store import SqlAlchemyStore
from ai_flow.test.endpoint.test_client import _SQLITE_DB_FILE, _PORT, _SQLITE_DB_URI

client = None


class TestListener(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)
        cls.server = AIFlowServer(store_uri=_SQLITE_DB_URI, port=_PORT)
        cls.server.run()
        global client
        client = AIFlowClient(server_uri='localhost:' + _PORT)

    @classmethod
    def tearDownClass(cls) -> None:
        client.stop_listen_event()
        store = SqlAlchemyStore(_SQLITE_DB_URI)
        base.metadata.drop_all(store.db_engine)
        os.remove(_SQLITE_DB_FILE)

    def test_signal_listener(self):
        message_queue = MessageQueue()
        watcher = EventListenerWatcher(message_queue)
        event_type = "listener_name"
        event_key = "event_key"
        listener = EventListener(client=client, watcher=watcher)
        listener.start_listen(event_type=event_type, event_key=event_key)
        for i in range(3):
            client.publish_event(key=event_key, value=str(i))
        listener.stop_listen_all()
        self.assertEqual(3, message_queue.length())

    # def test_local_job_status_listener(self):
    #     message_queue = MessageQueue()
    #     listener = LocalJobStatusListener(message_queue=message_queue, time_interval=1)
    #     listener.start_listen()
    #     job: BaseJob = LocalCMDJob(exec_cmd='echo "hello" && sleep 5')
    #     job.instance_id = "1"
    #     local_cmd_job_submitter = LocalCMDSubmitter()
    #     job_handler = local_cmd_job_submitter.submit_job(job)
    #     listener.register_job_listening(job_handler)
    #
    #     event1 = message_queue.get()
    #     self.assertEqual(event1.status, State.RUNNING.value)
    #     event1 = message_queue.get()
    #     self.assertEqual(event1.status, State.FINISHED.value)
    #     message_queue.send("haha")
    #     event1 = message_queue.get()
    #     self.assertEqual("haha", event1)
    #     listener.stop_listen()
    #
    # def test_kubernetes_job_status_listener(self):
    #     # Default is None, means loading the config from ~/.kube/config, please set your own kube config file path
    #     # if needed.
    #     kubernetes_util.load_kubernetes_config(None)
    #     if not kubernetes_util.kubernetes_cluster_available:
    #         return
    #     message_queue = MessageQueue()
    #     listener = KubernetesJobStatusListener(message_queue=message_queue)
    #     listener.start_listen()
    #     instance_id = "10086"
    #     test_job_name = 'listener-test-perl-job'
    #     job_obj = create_job_object(test_job_name, instance_id)
    #     create_job(kube_cli.BatchV1Api(), job_obj)
    #     expected_status_list = ['STARTING', 'RUNNING', 'FINISHED']
    #     job_states = []
    #     while True:
    #         event: JobStatusEvent = message_queue.get_with_timeout(timeout=10)
    #         if event is None:
    #             continue
    #         print(str(event.job_id) + '-' + event.status)
    #         if event.job_id == str(instance_id):
    #             job_states.append(event.status)
    #             if event.status == State.FAILED.value or event.status == State.FINISHED.value:
    #                 break
    #     delete_job(kube_cli.BatchV1Api(), test_job_name)
    #     self.assertEqual(expected_status_list, job_states)
    #     listener.stop_listen()

    # def test_listener_manager(self):
    #     listener_manager = ListenerManager(client=client)
    #     listener_manager. \
    #         job_status_listener_manager.register('local',
    #                                              LocalJobStatusListener(message_queue=listener_manager.message_queue))
    #     listener_manager.start_job_status_listener()
    #     job: BaseJob = LocalCMDJob(exec_cmd='echo "hello" && sleep 5')
    #     job.instance_id = "1"
    #     local_cmd_job_submitter = LocalCMDSubmitter()
    #     job_handler = local_cmd_job_submitter.submit_job(job)
    #     listener_manager.register_job_handler_listening(job_handler)
    #
    #     event1 = listener_manager.get_event()
    #     self.assertEqual(event1.status, State.RUNNING.value)
    #     event1 = listener_manager.get_event()
    #     self.assertEqual(event1.status, State.FINISHED.value)
    #     listener_manager.send_event("haha")
    #     event1 = listener_manager.get_event()
    #     self.assertEqual("haha", event1)
    #
    #     listener_name = "listener_name"
    #     event_key = "event_key"
    #     listener_manager.start_listen_signal(listener_name=listener_name, event_key=event_key)
    #     for i in range(3):
    #         client.update_notification(key=event_key, value=str(i))
    #     for i in range(3):
    #         event1 = listener_manager.get_event()
    #         self.assertEqual(str(i), event1.value)
    #
    #     listener_manager.stop_listen_all_signal()
    #     listener_manager.stop_job_status_listener()

    def test_listener_manager_message_dispatcher(self):
        listener_manager = ListenerManager(client=client)
        listener_manager.start_dispatcher()
        mq_list = []
        for i in range(3):
            mq = MessageQueue()
            mq_list.append(mq)
            listener_manager.register_message_queue(i, mq)
        for i in range(3):
            j_s_event = JobStatusEvent(workflow_id=i, job_id=str(i), status="Running")
            listener_manager.send_event(j_s_event)
        self.wait_dispatch_message(listener_manager)
        for i in range(3):
            mq = listener_manager.message_dispatcher.message_queue_map[i]
            self.assertEqual(1, mq.length())
            event = mq.get()
            self.assertEqual("Running", event.status)
            self.assertEqual(str(i), event.job_id)
            self.assertEqual(i, event.workflow_id)

        for i in range(3):
            listener_manager.message_dispatcher.listen_event_key(workflow_id=i, event_key="key_{}".format(i))
        listener_manager.message_dispatcher.listen_event_key(workflow_id=0, event_key="key_{}".format(1))
        for i in range(5):
            j_s_event = SimpleEvent(key="key_{}".format(i), value="Running")
            listener_manager.send_event(j_s_event)
        self.wait_dispatch_message(listener_manager)
        for i in range(3):
            mq = listener_manager.message_dispatcher.message_queue_map[i]
            if 0 == i:
                self.assertEqual(2, mq.length())
                event = mq.get()
                self.assertEqual("key_0", event.key)
                event = mq.get()
                self.assertEqual("key_1", event.key)
            else:
                self.assertEqual(1, mq.length())
                event = mq.get()
                self.assertEqual("key_{}".format(i), event.key)

        listener_manager.stop_dispatcher()

    @staticmethod
    def wait_dispatch_message(listener_manager):
        while listener_manager.message_queue.length() != 0:
            time.sleep(1)


def create_job_object(job_name, instance_id):
    # Configureate Pod template container
    container = kube_cli.V1Container(
        name="pi",
        image="perl",
        command=["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"])
    # Create and configurate a spec section
    template = kube_cli.V1PodTemplateSpec(
        metadata=kube_cli.V1ObjectMeta(labels={"app": "pi"}, annotations={'ai-flow/watched': 'True',
                                                                          'ai-flow/job-id': str(instance_id),
                                                                          'ai-flow/workflow-id': str(1)}),
        spec=kube_cli.V1PodSpec(restart_policy="Never", containers=[container]))
    # Create the specification of deployment
    spec = kube_cli.V1JobSpec(
        template=template,
        backoff_limit=4)
    # Instantiate the job object
    job = kube_cli.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=kube_cli.V1ObjectMeta(name=job_name),
        spec=spec)

    return job


def create_job(api_instance, job):
    api_instance.create_namespaced_job(
        body=job,
        namespace="ai-flow")


def delete_job(api_instance, job_name):
    api_instance.delete_namespaced_job(
        name=job_name,
        namespace="ai-flow",
        body=kube_cli.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))


if __name__ == '__main__':
    unittest.main()
