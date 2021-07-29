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
import os
import signal
import sys
import time
from subprocess import Popen, PIPE, STDOUT
from tempfile import NamedTemporaryFile
from typing import Text, List

from ai_flow.ai_graph.ai_graph import AISubGraph
from ai_flow.ai_graph.ai_node import AINode
from ai_flow.log import log_path_utils
from ai_flow.plugin_interface.job_plugin_interface import JobPluginFactory, JobHandle, JobRuntimeEnv, \
    JobController
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo
from ai_flow.translator.translator import JobGenerator
from ai_flow.util import serialization_utils
from ai_flow.util.file_util import zip_file_util
from ai_flow.workflow.job import Job
from ai_flow.workflow.job_config import JobConfig
from ai_flow.workflow.status import Status
from ai_flow_plugins.job_plugins.flink.flink_env import get_global_flink_env, get_flink_env_by_job_name
from ai_flow_plugins.job_plugins.flink.flink_job_config import FlinkJobConfig
from ai_flow_plugins.job_plugins.flink.flink_processor import FlinkJavaProcessor, FlinkPythonProcessor
from ai_flow_plugins.job_plugins.utils.run_graph import RunGraph, build_run_graph


class FlinkJob(Job):
    def __init__(self, job_config: JobConfig):
        super().__init__(job_config)
        self.is_java = False
        self.stdout_log: Text = None
        self.stderr_log: Text = None
        # python flink job
        self.run_graph_file: Text = None
        self.flink_env_file: Text = None

        # java flink job
        self.processor_file: Text = None


class FlinkJobHandle(JobHandle):

    def __init__(self, job: Job,
                 job_execution: JobExecutionInfo):
        super().__init__(job=job, job_execution=job_execution)
        self.sub_process = None


class FlinkJobGenerator(JobGenerator):

    def _is_java_job(self, sub_graph: AISubGraph) -> bool:
        if len(sub_graph.nodes) == 1:
            node: AINode = list(sub_graph.nodes.values())[0]
            processor = node.get_processor()
            if isinstance(processor, FlinkJavaProcessor):
                return True
            else:
                return False
        else:
            for node in sub_graph.nodes.values():
                processor = node.get_processor()
                if isinstance(processor, FlinkPythonProcessor):
                    pass
                else:
                    raise Exception("Processor must be instance of FlinkPythonProcessor!")
            return False

    def _check_processor_validated(self, sub_graph: AISubGraph):
        if len(sub_graph.nodes) > 1:
            for node in sub_graph.nodes.values():
                processor = node.get_processor()
                if not isinstance(processor, FlinkPythonProcessor):
                    raise Exception("A job can only contains one FlinkJavaProcessor or multiple FlinkPythonProcessor.")

    def generate(self, sub_graph: AISubGraph, resource_dir: Text = None) -> Job:
        self._check_processor_validated(sub_graph=sub_graph)
        flink_job_config: FlinkJobConfig = FlinkJobConfig.from_job_config(sub_graph.config)
        job = FlinkJob(job_config=flink_job_config)
        is_java = self._is_java_job(sub_graph)
        job.is_java = is_java
        if is_java and flink_job_config.run_mode != 'cluster':
            raise Exception("Java flink job only support cluster mode!")
        if not is_java:
            run_graph: RunGraph = build_run_graph(sub_graph)
            with NamedTemporaryFile(mode='w+b', dir=resource_dir,
                                    prefix='{}_run_graph_'.format(job.job_name), delete=False) as fp:
                job.run_graph_file = os.path.basename(fp.name)
                fp.write(serialization_utils.serialize(run_graph))

            with NamedTemporaryFile(mode='w+b', dir=resource_dir,
                                    prefix='{}_flink_env_'.format(job.job_name), delete=False) as fp:
                job.flink_env_file = os.path.basename(fp.name)
                flink_env = get_flink_env_by_job_name(job_name=flink_job_config.job_name)
                if flink_env is None:
                    flink_env = get_global_flink_env()
                fp.write(serialization_utils.serialize(flink_env))
        else:
            with NamedTemporaryFile(mode='w+b', dir=resource_dir,
                                    prefix='{}_flink_processor_'.format(job.job_name), delete=False) as fp:
                job.processor_file = os.path.basename(fp.name)
                fp.write(list(sub_graph.nodes.values())[0].processor)
        return job


class FlinkJobController(JobController):

    def submit_job(self, job: Job, job_runtime_env: JobRuntimeEnv = None) -> JobHandle:
        handle = FlinkJobHandle(job=job, job_execution=job_runtime_env.job_execution_info)
        flink_job: FlinkJob = job
        job_config: FlinkJobConfig = FlinkJobConfig.from_job_config(flink_job.job_config)
        env = os.environ.copy()
        env.update(job_config.properties.get('env', {}))
        if not flink_job.is_java:
            run_graph_file = os.path.join(job_runtime_env.generated_dir, flink_job.run_graph_file)
            flink_env_file = os.path.join(job_runtime_env.generated_dir, flink_job.flink_env_file)
            # Add PYTHONPATH
            copy_path = sys.path.copy()
            copy_path.insert(0, job_runtime_env.workflow_dir)
            copy_path.insert(0, job_runtime_env.python_dep_dir)
            env['PYTHONPATH'] = ':'.join(copy_path)

            current_path = os.path.dirname(__file__)
            script_path = os.path.join(current_path, 'flink_run_main.py')
            python3_location = sys.executable
            if job_config.run_mode == 'local':
                bash_command = [python3_location, script_path, run_graph_file, job_runtime_env.working_dir, flink_env_file]
            elif job_config.run_mode == 'cluster':
                bash_command = ['flink', 'run']

                if job_config.flink_run_args is not None:
                    bash_command.extend(job_config.flink_run_args)

                bash_command.append('-pyfs')
                files = [job_runtime_env.workflow_dir]
                if os.path.exists(job_runtime_env.python_dep_dir):
                    files.append(job_runtime_env.python_dep_dir)
                bash_command.append(','.join(files))

                if os.path.exists(job_runtime_env.resource_dir):
                    zip_file_util.make_dir_zipfile(job_runtime_env.resource_dir,
                                                   os.path.join(job_runtime_env.working_dir, 'resources.zip'))
                    bash_command.extend(['-pyarch',
                                     os.path.join(job_runtime_env.working_dir, 'resources.zip#resources')])
                bash_command.extend(['-py', script_path,
                                     run_graph_file, job_runtime_env.working_dir, flink_env_file])
            else:
                raise Exception('Flink supports run_mode local or cluster, do not support {}.'
                                .format(job_config.run_mode))
        else:
            # flink java job
            bash_command = ['flink', 'run']

            if job_config.flink_run_args is not None:
                bash_command.extend(job_config.flink_run_args)

            if os.path.exists(job_runtime_env.resource_dir):
                zip_file_util.make_dir_zipfile(job_runtime_env.resource_dir,
                                               os.path.join(job_runtime_env.working_dir, 'resources.zip'))
            processor: FlinkJavaProcessor = serialization_utils.\
                read_object_from_serialized_file(os.path.join(job_runtime_env.generated_dir, flink_job.processor_file))
            if processor.entry_class is not None:
                bash_command.extend(['-c', processor.entry_class])
            bash_command.append(os.path.join(job_runtime_env.jar_dep_dir, processor.main_jar_file))
            bash_command.extend(processor.args)
        self.log.info(' '.join(bash_command))
        stdout_log = log_path_utils.stdout_log_path(job_runtime_env.log_dir, job.job_name)
        stderr_log = log_path_utils.stderr_log_path(job_runtime_env.log_dir, job.job_name)
        if not os.path.exists(job_runtime_env.log_dir):
            os.makedirs(job_runtime_env.log_dir)

        sub_process = self.submit_process(bash_command=bash_command,
                                          env=env,
                                          working_dir=job_runtime_env.working_dir,
                                          stdout_log=stdout_log,
                                          stderr_log=stderr_log)
        handle.sub_process = sub_process
        handle.stdout_log = stdout_log
        handle.stderr_log = stderr_log

        if flink_job.is_java:
            # write job_id to file.
            num = 0
            while True:
                if os.path.exists(stdout_log):
                    break
                else:
                    time.sleep(1)
                num += 1
                if 0 == num % 20:
                    self.log.info("Waiting for stdout log file created...")

            while True:
                with open(stdout_log, 'r') as f:
                    lines = f.readlines()
                if len(lines) >= 1:
                    line = lines[0]
                    if line.startswith("Job has been submitted with JobID"):
                        job_id = line.split(' ')[6][:-1]
                        with open(os.path.join(job_runtime_env.working_dir, 'job_id'), 'w') as fp:
                            fp.write(job_id)
                        self.log.info('Flink job id {}'.format(job_id))
                    break
                else:
                    time.sleep(1)

        return handle

    def stop_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv = None):
        handle: FlinkJobHandle = job_handle
        job_config: FlinkJobConfig = FlinkJobConfig.from_job_config(job_handle.job.job_config)
        if job_config.run_mode == 'cluster':
            job_id_file = os.path.join(job_runtime_env.working_dir, 'job_id')
            if os.path.exists(job_id_file):
                with open(job_id_file, 'r') as fp:
                    job_id = fp.read()
                env = os.environ.copy()
                env.update(job_config.properties.get('env', {}))
                # Add PYTHONPATH
                copy_path = sys.path.copy()
                copy_path.insert(0, job_runtime_env.python_dep_dir)
                env['PYTHONPATH'] = ':'.join(copy_path)
                bash_command = ['flink', 'stop']
                if job_config.flink_stop_args is not None:
                    bash_command.extend(job_config.flink_stop_args)
                bash_command.append(job_id)
                self.log.info(' '.join(bash_command))
                sp = Popen(bash_command,
                           stdout=PIPE,
                           stderr=STDOUT,
                           cwd=job_runtime_env.working_dir,
                           env=env)
                sp.wait()
        self.log.info('Output:')
        sub_process = handle.sub_process
        self.log.info('Sending SIGTERM signal to process group')
        if sub_process and hasattr(sub_process, 'pid') and sub_process.poll() is None:
            while sub_process.poll() is None:
                try:
                    os.killpg(os.getpgid(sub_process.pid), signal.SIGTERM)
                except Exception as e:
                    self.log.error('Kill process {} failed! error {}'.format(sub_process.pid, str(e)))
                    time.sleep(1)

    def cleanup_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv = None):
        pass

    def submit_process(self, bash_command: List, env, working_dir, stdout_log, stderr_log):

        def pre_exec():
            # Restore default signal disposition and invoke setsid
            for sig in ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ'):
                if hasattr(signal, sig):
                    signal.signal(getattr(signal, sig), signal.SIG_DFL)
            os.setsid()

        self.log.info('Running command: %s', bash_command)
        with open(stdout_log, 'a') as out, open(stderr_log, 'a') as err:
            sub_process = Popen(  # pylint: disable=subprocess-popen-preexec-fn
                bash_command,
                stdout=out,
                stderr=err,
                cwd=working_dir,
                env=env,
                preexec_fn=pre_exec,
            )
        self.log.info('Process pid: %s', sub_process.pid)
        return sub_process

    def get_result(self, job_handle: JobHandle, blocking: bool = True) -> object:
        handle: FlinkJobHandle = job_handle
        if blocking:
            handle.sub_process.wait()
            self.log.info('Command exited with return code %s', handle.sub_process.returncode)

            if handle.sub_process.returncode != 0:
                raise Exception('Flink run failed. The command returned a non-zero exit code.')
            return None
        else:
            return None

    def get_job_status(self, job_handle: JobHandle) -> Status:
        pass


class FlinkJobPluginFactory(JobPluginFactory):

    def __init__(self) -> None:
        super().__init__()
        self._job_generator = FlinkJobGenerator()
        self._job_controller = FlinkJobController()

    def get_job_generator(self) -> JobGenerator:
        return self._job_generator

    def get_job_controller(self) -> JobController:
        return self._job_controller

    def job_type(self) -> Text:
        return "flink"
