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
import unittest
import os
import time
import shutil
from ai_flow import AIFlowServerRunner, init_ai_flow_context
from ai_flow.workflow.status import Status
from ai_flow_plugins.job_plugins import flink
from test_flink_processor import SinkWithAddInsertSql, SinkWithExecuteSql, Source, Sink, Transformer, Transformer2, \
    SourceSql, SinkSql
import ai_flow as af

project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class TestFlink(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config_file = project_path + '/master.yaml'
        cls.master = AIFlowServerRunner(config_file=config_file)
        cls.master.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.master.stop()
        generated = '{}/generated'.format(project_path)
        if os.path.exists(generated):
            shutil.rmtree(generated)
        temp = '{}/temp'.format(project_path)
        if os.path.exists(temp):
            shutil.rmtree(temp)

    def setUp(self):
        self.master._clear_db()
        af.current_graph().clear_graph()
        init_ai_flow_context()

    def tearDown(self):
        self.master._clear_db()

    def test_local_flink_task(self):
        flink.set_flink_env(None)
        with af.job_config('task_1'):
            input_example = af.user_define_operation(processor=Source())
            processed = af.transform(input=[input_example], transform_processor=Transformer())
            af.user_define_operation(input=[processed], processor=Sink())
            flink.set_flink_env(flink.FlinkBatchEnv())
        w = af.workflow_operation.submit_workflow(workflow_name=af.current_workflow_config().workflow_name)
        je = af.workflow_operation.start_job_execution(job_name='task_1', execution_id='1')
        je = af.workflow_operation.get_job_execution(job_name='task_1', execution_id='1')
        self.assertEqual(Status.FINISHED, je.status)

    def test_local_flink_task_with_flink_sql_processor(self):
        flink.set_flink_env(flink.FlinkStreamEnv())
        with af.job_config('task_1'):
            af.user_define_operation(processor=SourceSql())
            af.user_define_operation(processor=SinkSql())

        workflow = af.workflow_operation.submit_workflow(workflow_name=af.current_workflow_config().workflow_name)
        job_execution = af.workflow_operation.start_job_execution(job_name='task_1', execution_id='1')
        job_execution = af.workflow_operation.get_job_execution(job_name='task_1', execution_id='1')
        self.assertEqual(Status.FINISHED, job_execution.status)

    def test_stop_local_flink_task(self):
        with af.job_config('task_1'):
            input_example = af.user_define_operation(processor=Source())
            processed = af.transform(input=[input_example], transform_processor=Transformer2())
            af.user_define_operation(input=[processed], processor=Sink())
        w = af.workflow_operation.submit_workflow(workflow_name='test_flink')
        je = af.workflow_operation.start_job_execution(job_name='task_1', execution_id='1')
        time.sleep(2)
        af.workflow_operation.stop_job_execution(job_name='task_1', execution_id='1')
        je = af.workflow_operation.get_job_execution(job_name='task_1', execution_id='1')
        self.assertEqual(Status.FAILED, je.status)
        self.assertTrue('err' in je.properties)

    def test_local_flink_no_statementset_task(self):
        """
        This is a test case for issue 475.
        https://github.com/alibaba/flink-ai-extended/issues/475
        It calls 'TableEnv.execute_sql' in FlinkPythonProcessor and no need to call 
        StatementSet.execute().
        flink_run_main.py should be able to handle this case.
        """
        with af.job_config('task_1'):
            input_example = af.user_define_operation(processor=Source())
            processed = af.transform(input=[input_example], transform_processor=Transformer())
            af.user_define_operation(input=[processed], processor=SinkWithExecuteSql())
        af.workflow_operation.submit_workflow(
            workflow_name=af.current_workflow_config().workflow_name)
        af.workflow_operation.start_job_execution(job_name='task_1', execution_id='1')
        je = af.workflow_operation.get_job_execution(job_name='task_1', execution_id='1')
        self.assertEqual(Status.FINISHED, je.status)

    def test_local_flink_execute_statementset_add_insert_sql_task(self):
        """
        This is a test case for issue 475.
        https://github.com/alibaba/flink-ai-extended/issues/475
        It calls 'Statementset.add_insert_sql' in FlinkPythonProcessor and need to call 
        StatementSet.execute().
        flink_run_main.py should be able to handle this case.
        """
        with af.job_config('task_1'):
            input_example = af.user_define_operation(processor=Source())
            processed = af.transform(
                input=[input_example], transform_processor=Transformer())
            af.user_define_operation(
                input=[processed], processor=SinkWithAddInsertSql())
        af.workflow_operation.submit_workflow(
            workflow_name=af.current_workflow_config().workflow_name)
        af.workflow_operation.start_job_execution(
            job_name='task_1', execution_id='1')
        je = af.workflow_operation.get_job_execution(
            job_name='task_1', execution_id='1')
        self.assertEqual(Status.FINISHED, je.status)

    @unittest.skip("need start flink cluster")
    def test_cluster_flink_task(self):
        with af.job_config('task_2'):
            input_example = af.user_define_operation(processor=Source())
            processed = af.transform(input=[input_example], transform_processor=Transformer())
            af.user_define_operation(input=[processed], processor=Sink())
        w = af.workflow_operation.submit_workflow(workflow_name=af.current_workflow_config().workflow_name)
        je = af.workflow_operation.start_job_execution(job_name='task_2', execution_id='1')
        je = af.workflow_operation.get_job_execution(job_name='task_2', execution_id='1')
        self.assertEqual(Status.FINISHED, je.status)

    @unittest.skip("need start flink cluster")
    def test_cluster_stop_local_flink_task(self):
        with af.job_config('task_2'):
            input_example = af.user_define_operation(processor=Source())
            processed = af.transform(input=[input_example], transform_processor=Transformer2())
            af.user_define_operation(input=[processed], processor=Sink())
        w = af.workflow_operation.submit_workflow(workflow_name='test_python')
        je = af.workflow_operation.start_job_execution(job_name='task_2', execution_id='1')
        time.sleep(20)
        af.workflow_operation.stop_job_execution(job_name='task_2', execution_id='1')
        je = af.workflow_operation.get_job_execution(job_name='task_2', execution_id='1')
        self.assertEqual(Status.FAILED, je.status)
        self.assertTrue('err' in je.properties)

    @unittest.skip("need start flink cluster")
    def test_cluster_stop_local_flink_task_with_cancel(self):
        job_name = 'task_3'
        with af.job_config(job_name):
            input_example = af.user_define_operation(processor=Source())
            processed = af.transform(input=[input_example], transform_processor=Transformer2())
            af.user_define_operation(input=[processed], processor=Sink())
        w = af.workflow_operation.submit_workflow(workflow_name='test_python')
        je = af.workflow_operation.start_job_execution(job_name=job_name, execution_id='1')
        time.sleep(10)
        af.workflow_operation.stop_job_execution(job_name=job_name, execution_id='1')
        je = af.workflow_operation.get_job_execution(job_name=job_name, execution_id='1')
        self.assertEqual(Status.FAILED, je.status)
        self.assertTrue('err' in je.properties)

    @unittest.skip("need start flink cluster and run (nc -lk 9999)")
    def test_cluster_stop_local_flink_task_with_stop(self):
        job_name = 'task_4'
        flink_home = os.environ.get('FLINK_HOME')
        word_count_jar = os.path.join(flink_home, 'examples', 'streaming', 'SocketWindowWordCount.jar')
        jar_dir = os.path.join(project_path, 'dependencies', 'jar')
        if not os.path.exists(jar_dir):
            os.makedirs(jar_dir)
            shutil.copy(word_count_jar, jar_dir)

        args = ['--port', '9999']
        with af.job_config(job_name):
            af.user_define_operation(processor=flink.FlinkJavaProcessor(entry_class=None,
                                                                        main_jar_file='SocketWindowWordCount.jar',
                                                                        args=args))
        w = af.workflow_operation.submit_workflow(workflow_name=af.current_workflow_config().workflow_name)
        je = af.workflow_operation.start_job_execution(job_name=job_name, execution_id='1')
        time.sleep(10)
        af.workflow_operation.stop_job_execution(job_name=job_name, execution_id='1')
        je = af.workflow_operation.get_job_execution(job_name=job_name, execution_id='1')
        self.assertEqual(Status.FAILED, je.status)
        self.assertTrue('err' in je.properties)
        dep_dir = os.path.join(project_path, 'dependencies')
        if os.path.exists(dep_dir):
            shutil.rmtree(dep_dir)
        savepoint_path = '/tmp/savepoint_test_cluster_stop_local_flink_task_with_stop'
        self.assertTrue(os.path.exists(savepoint_path))
        shutil.rmtree(savepoint_path)

    @unittest.skip("need start flink cluster")
    def test_cluster_flink_java_task(self):
        flink_home = os.environ.get('FLINK_HOME')
        word_count_jar = os.path.join(flink_home, 'examples', 'batch', 'WordCount.jar')
        output_file = os.path.join(flink_home, 'log', 'output')
        if os.path.exists(output_file):
            os.remove(output_file)
        jar_dir = os.path.join(project_path, 'dependencies', 'jar')
        if not os.path.exists(jar_dir):
            os.makedirs(jar_dir)
            shutil.copy(word_count_jar, jar_dir)

        args = ['--input', os.path.join(flink_home, 'conf', 'flink-conf.yaml'), '--output', output_file]
        with af.job_config('task_2'):
            af.user_define_operation(processor=flink.FlinkJavaProcessor(entry_class=None,
                                                                        main_jar_file='WordCount.jar',
                                                                        args=args))
        w = af.workflow_operation.submit_workflow(workflow_name=af.current_workflow_config().workflow_name)
        je = af.workflow_operation.start_job_execution(job_name='task_2', execution_id='1')
        je = af.workflow_operation.get_job_execution(job_name='task_2', execution_id='1')
        self.assertEqual(Status.FINISHED, je.status)
        dep_dir = os.path.join(project_path, 'dependencies')
        if os.path.exists(dep_dir):
            shutil.rmtree(dep_dir)


if __name__ == '__main__':
    unittest.main()
