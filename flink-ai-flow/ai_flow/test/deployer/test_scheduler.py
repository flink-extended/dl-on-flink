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
import sys
from ai_flow.endpoint.client.aiflow_client import AIFlowClient

import ai_flow as af
from ai_flow.deployer.scheduler import EventScheduler
from ai_flow.graph.edge import JobControlEdge, MetConfig, generate_job_status_key
from ai_flow.graph.edge import TaskAction
from ai_flow.meta.job_meta import State
from ai_flow.plugins.local_cmd_job_plugin import LocalCMDJob
from ai_flow.endpoint.server.server import AIFlowServer
from ai_flow.store.db.base_model import base
from ai_flow.store.sqlalchemy_store import SqlAlchemyStore
from ai_flow.test.endpoint.test_client import _SQLITE_DB_FILE, _PORT, _SQLITE_DB_URI
from ai_flow.workflow.job import BaseJob, BaseJobConfig
from ai_flow.workflow.job_config import PeriodicConfig
from ai_flow.workflow.job_context import JobContext
from ai_flow.workflow.workflow import Workflow

client: AIFlowClient = None


class TestScheduler(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)
        cls.server = AIFlowServer(store_uri=_SQLITE_DB_URI, port=_PORT)
        cls.sc_manager = cls.server.deploy_service.scheduler_manager
        cls.server.run()
        global client
        client = AIFlowClient(server_uri='localhost:' + _PORT)
        cls.ls_manager = cls.sc_manager.listener_manager

    @classmethod
    def tearDownClass(cls) -> None:
        client.stop_listen_event()
        store = SqlAlchemyStore(_SQLITE_DB_URI)
        base.metadata.drop_all(store.db_engine)
        os.remove(_SQLITE_DB_FILE)

    def tearDown(self) -> None:
        print('tearDown')
        store = SqlAlchemyStore(_SQLITE_DB_URI)
        base.metadata.drop_all(store.db_engine)
        base.metadata.create_all(store.db_engine)
        af.default_graph().clear_graph()
        res = client.list_job(page_size=10, offset=0)
        self.assertIsNone(res)

    @staticmethod
    def create_job(index, sleep_time=5) -> BaseJob:
        job: BaseJob = LocalCMDJob(exec_cmd='echo "hello {}\n" && sleep {}'.format(str(index), str(sleep_time)))
        job.job_context = JobContext()
        job.job_context.workflow_execution_id = 1
        job.instance_id = str(index) + "_job"
        job.uuid = index
        job.job_name = job.instance_id
        return job

    @staticmethod
    def create_workflow() -> Workflow:
        workflow = Workflow()
        for i in range(3):
            job = TestScheduler.create_job(i, 1)
            workflow.add_job(job)
        deps = []
        deps.append(JobControlEdge(target_node_id='0_job', source_node_id='2_job',
                                   met_config=MetConfig(event_key=generate_job_status_key('0_job'),
                                                        event_value=State.FINISHED.value)))
        deps.append(JobControlEdge(target_node_id='1_job', source_node_id='2_job',
                                   met_config=MetConfig(event_key=generate_job_status_key('1_job'),
                                                        event_value=State.FINISHED.value)))
        workflow.add_edges("2_job", deps)
        workflow.workflow_id = 1
        return workflow

    @staticmethod
    def create_workflow_one_job() -> Workflow:
        workflow = Workflow()
        workflow.workflow_id = 1
        job = TestScheduler.create_job(0, 1)
        workflow.add_job(job)
        return workflow

    @staticmethod
    def create_stream_workflow() -> Workflow:
        workflow = Workflow()
        for i in range(3):
            job = TestScheduler.create_job(i, 5)
            workflow.add_job(job)
        deps = []
        deps.append(JobControlEdge(target_node_id='0_job', source_node_id='2_job',
                                   met_config=MetConfig(event_key=generate_job_status_key('0_job'),
                                                        event_value=State.FINISHED.value)))
        deps.append(JobControlEdge(target_node_id='1_job', source_node_id='2_job',
                                   met_config=MetConfig(event_key=generate_job_status_key('1_job'),
                                                        event_value=State.FINISHED.value)))
        workflow.add_edges("2_job", deps)
        workflow.workflow_id = 1

        job = TestScheduler.create_job(3, 1)
        workflow.add_job(job)
        dep2 = []
        dep2.append(JobControlEdge(target_node_id='0_job', source_node_id='3_job',
                                   met_config=MetConfig(event_key='key1',
                                                        event_value='value1')))
        workflow.add_edges('3_job', dep2)

        return workflow

    def test_stream_repeat_stream_job(self):
        print(sys._getframe().f_code.co_name)
        workflow = TestScheduler.create_stream_workflow()
        TestScheduler.sc_manager.schedule_workflow(workflow=workflow)
        client.publish_event(key='key1', value='value1')
        client.publish_event(key='key1', value='value1')
        TestScheduler.sc_manager.wait_finished(workflow.workflow_id)
        res = TestScheduler.sc_manager.get_schedule_result(workflow_id=workflow.workflow_id)
        self.assertEqual(0, res)
        res = client.list_job(page_size=10, offset=0)
        # self.assertEqual(5, len(res))
        self.assertEqual(State.FINISHED, res[0].job_state)

    def test_event_scheduler(self):
        print(sys._getframe().f_code.co_name)
        workflow = TestScheduler.create_workflow()
        workflow.workflow_id = 1
        event_scheduler = EventScheduler(client=client, listener_manager=TestScheduler.ls_manager, workflow=workflow)
        res = event_scheduler.schedule()
        self.assertEqual(0, res)

    def test_event_scheduler_one_job(self):
        print(sys._getframe().f_code.co_name)
        workflow = TestScheduler.create_workflow_one_job()
        workflow.workflow_id = 1
        event_scheduler = EventScheduler(client=client, listener_manager=TestScheduler.ls_manager, workflow=workflow)
        res = event_scheduler.schedule()
        self.assertEqual(0, res)

    @staticmethod
    def create_periodic_job(index, sleep_time=1) -> BaseJob:
        job: BaseJob = LocalCMDJob(exec_cmd='echo "hello {}\n" && sleep {}'.format(str(index), str(sleep_time)),
                                   job_config=BaseJobConfig(platform="local", engine="cmd_line"))
        job.uuid = index
        job.job_name = job.instance_id
        job.job_config.periodic_config = PeriodicConfig(periodic_type='interval', args={'seconds': 5})
        job.instance_id = str(index) + "_job"
        job.job_context = JobContext()
        job.job_context.workflow_execution_id = 1
        return job

    @staticmethod
    def create_periodic_workflow() -> Workflow:
        workflow = Workflow()
        for i in range(3):
            job = TestScheduler.create_periodic_job(i, 1)
            if 2 == i:
                job.job_config.periodic_config = None
            workflow.add_job(job)
        deps = []
        deps.append(JobControlEdge(target_node_id='0_job', source_node_id='2_job',
                                   met_config=MetConfig(event_key=generate_job_status_key('0_job'),
                                                        event_value=State.FINISHED.value)))
        deps.append(JobControlEdge(target_node_id='1_job', source_node_id='2_job',
                                   met_config=MetConfig(event_key=generate_job_status_key('1_job'),
                                                        event_value=State.FINISHED.value)))
        workflow.add_edges("2_job", deps)
        workflow.workflow_id = 1
        return workflow

    def run_periodic_job(self):
        print(sys._getframe().f_code.co_name)
        workflow = TestScheduler.create_periodic_workflow()
        TestScheduler.sc_manager.schedule_workflow(workflow=workflow)
        time.sleep(13)
        TestScheduler.sc_manager.stop_schedule_workflow(workflow_id=workflow.workflow_id)
        res = client.list_job(page_size=10, offset=0)
        self.assertGreater(len(res), 3)
        self.assertEqual('2_job', res[2].job_id)
        self.assertEqual('2_job', res[5].job_id)

    def test_batch_periodic_job(self):
        self.run_periodic_job()

    @staticmethod
    def create_restart_job_workflow() -> Workflow:
        workflow = Workflow()
        for i in range(2):
            job = TestScheduler.create_periodic_job(i, 4)
            workflow.add_job(job)

        job = TestScheduler.create_periodic_job(2, 20)
        job.job_config.periodic_config = None
        workflow.add_job(job)
        deps = []
        deps.append(JobControlEdge(target_node_id='0_job', source_node_id='2_job',
                                   met_config=MetConfig(event_key=generate_job_status_key('0_job'),
                                                        event_value=State.FINISHED.value,
                                                        action=TaskAction.RESTART)))
        deps.append(JobControlEdge(target_node_id='1_job', source_node_id='2_job',
                                   met_config=MetConfig(event_key=generate_job_status_key('1_job'),
                                                        event_value=State.FINISHED.value,
                                                        action=TaskAction.RESTART)))
        workflow.add_edges("2_job", deps)
        workflow.workflow_id = 1
        return workflow

    def test_restart_job(self):
        print(sys._getframe().f_code.co_name)
        workflow = TestScheduler.create_restart_job_workflow()

        TestScheduler.sc_manager.schedule_workflow(workflow=workflow)
        time.sleep(20)
        TestScheduler.sc_manager.stop_schedule_workflow(workflow_id=workflow.workflow_id)
        res = client.list_job(page_size=10, offset=0)
        print(res)
        self.assertGreater(len(res), 3)

    def test_event_scheduler_manager(self):
        print(sys._getframe().f_code.co_name)
        workflow = TestScheduler.create_workflow()
        TestScheduler.sc_manager.schedule_workflow(workflow=workflow)
        TestScheduler.sc_manager.wait_finished(workflow.workflow_id)
        res = TestScheduler.sc_manager.get_schedule_result(workflow_id=workflow.workflow_id)
        self.assertEqual(0, res)
        res = client.list_job(page_size=5, offset=0)
        self.assertEqual(3, len(res))
        self.assertEqual(State.FINISHED, res[0].job_state)

    @staticmethod
    def create_longrun_workflow() -> Workflow:
        workflow = Workflow()
        job_0 = TestScheduler.create_job(0, 10000)
        workflow.add_job(job_0)
        job_1 = TestScheduler.create_job(1, 1)
        workflow.add_job(job_1)
        deps = []
        deps.append(JobControlEdge(target_node_id='1_job', source_node_id='0_job',
                                   met_config=MetConfig(event_key='key_1',
                                                        event_value='value_1',
                                                        event_type='stop',
                                                        action=TaskAction.STOP)))

        workflow.add_edges("0_job", deps)
        workflow.workflow_id = 1
        return workflow

    def test_stop_job(self):
        print(sys._getframe().f_code.co_name)
        workflow = TestScheduler.create_longrun_workflow()

        TestScheduler.sc_manager.schedule_workflow(workflow=workflow)
        client.publish_event('key_1', 'value_1', 'stop')
        TestScheduler.sc_manager.wait_finished(workflow.workflow_id)
        res = TestScheduler.sc_manager.get_schedule_result(workflow_id=workflow.workflow_id)
        self.assertEqual(0, res)


if __name__ == '__main__':
    unittest.main()
