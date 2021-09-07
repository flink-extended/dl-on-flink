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
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Text, Any, List

from ai_flow_plugins.job_plugins.python.python_processor import PythonProcessor

from ai_flow.ai_graph.ai_graph import AISubGraph
from ai_flow.log import log_path_utils
from ai_flow.plugin_interface.job_plugin_interface import JobPluginFactory, JobHandle, JobRuntimeEnv, \
    JobController
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo
from ai_flow.translator.translator import JobGenerator
from ai_flow.util import serialization_utils
from ai_flow.workflow.job import Job
from ai_flow.workflow.job_config import JobConfig
from ai_flow.workflow.status import Status
from ai_flow_plugins.job_plugins.python.python_job_config import PythonJobConfig
from ai_flow_plugins.job_plugins.utils.run_graph import RunGraph, build_run_graph


class PythonJob(Job):
    """
    PythonJob is the description of python type job.
    The run_graph_file field stores the serialized file of the RunGraph
    (ai_flow_plugins.job_plugins.python.python_job_plugin.RunGraph).
    """
    def __init__(self, job_config: JobConfig):
        super().__init__(job_config)
        self.run_graph_file: Text = None


class PythonJobHandle(JobHandle):

    def __init__(self, job: Job,
                 job_execution: JobExecutionInfo):
        super().__init__(job=job, job_execution=job_execution)
        """It saves the Popen object of the python child process."""
        self.sub_process = None


class PythonJobGenerator(JobGenerator):

    @staticmethod
    def _validate_sub_graph(sub_graph: AISubGraph):
        """
        Check that all the processor in sub_graph is PythonProcessor
        """
        for node_name, ai_node in sub_graph.nodes.items():
            processor = ai_node.get_processor()
            if not isinstance(processor, PythonProcessor):
                raise Exception("Invalid sub_graph: node {} in job {} expect to has PythonProcessor but it is {}"
                                .format(node_name, sub_graph.config.job_name, type(processor)))

    def generate(self, sub_graph: AISubGraph, resource_dir: Text = None) -> Job:
        self._validate_sub_graph(sub_graph)
        python_job_config: PythonJobConfig = sub_graph.config
        run_graph: RunGraph = build_run_graph(sub_graph)
        job = PythonJob(job_config=python_job_config)
        with NamedTemporaryFile(mode='w+b', dir=resource_dir, prefix='{}_python_'.format(job.job_name), delete=False) as fp:
            job.run_graph_file = os.path.basename(fp.name)
            fp.write(serialization_utils.serialize(run_graph))
        return job


class PythonJobController(JobController):
    def submit_job(self, job: Job, job_runtime_env: JobRuntimeEnv = None) -> JobHandle:
        handle = PythonJobHandle(job=job, job_execution=job_runtime_env.job_execution_info)
        python_job: PythonJob = job
        run_graph_file = os.path.join(job_runtime_env.generated_dir, python_job.run_graph_file)

        env = os.environ.copy()
        if 'env' in job.job_config.properties:
            env.update(job.job_config.properties.get('env'))
        # Add PYTHONPATH
        copy_path = sys.path.copy()
        copy_path.insert(0, job_runtime_env.workflow_dir)
        copy_path.insert(0, job_runtime_env.python_dep_dir)
        env['PYTHONPATH'] = ':'.join(copy_path)

        current_path = os.path.dirname(__file__)
        script_path = os.path.join(current_path, 'python_run_main.py')
        if 'python_executable_path' in job.job_config.properties:
            python3_location = job.job_config.properties.get('python_executable_path')
        else:
            python3_location = sys.executable
        bash_command = [python3_location, script_path, run_graph_file, job_runtime_env.working_dir]

        stdout_log = log_path_utils.stdout_log_path(job_runtime_env.log_dir, job.job_name)
        stderr_log = log_path_utils.stderr_log_path(job_runtime_env.log_dir, job.job_name)
        if not os.path.exists(job_runtime_env.log_dir):
            os.makedirs(job_runtime_env.log_dir)

        sub_process = self.submit_python_process(bash_command=bash_command,
                                                 env=env,
                                                 working_dir=job_runtime_env.working_dir,
                                                 stdout_log=stdout_log,
                                                 stderr_log=stderr_log)
        handle.sub_process = sub_process
        return handle

    def stop_job(self, job_handle: JobHandle, job_runtime_env: Any = None):
        handle: PythonJobHandle = job_handle
        self.log.info('Output:')
        sub_process = handle.sub_process
        self.log.info('Sending SIGTERM signal to python process group')
        if sub_process and hasattr(sub_process, 'pid') and sub_process.poll() is None:
            while sub_process.poll() is None:
                try:
                    os.killpg(os.getpgid(sub_process.pid), signal.SIGTERM)
                except Exception as e:
                    self.log.error('Kill process {} failed! error {}'.format(sub_process.pid, str(e)))
                    time.sleep(1)

    def cleanup_job(self, job_handle: JobHandle, job_runtime_env: Any = None):
        pass

    def submit_python_process(self, bash_command: List, env, working_dir, stdout_log, stderr_log):

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
        handle: PythonJobHandle = job_handle
        if blocking:
            handle.sub_process.wait()
            self.log.info('Command exited with return code %s', handle.sub_process.returncode)

            if handle.sub_process.returncode != 0:
                raise Exception('python returned a non-zero exit code {}.'.format(handle.sub_process.returncode))
            return None
        else:
            return None

    def get_job_status(self, job_handle: JobHandle) -> Status:
        handle: PythonJobHandle = job_handle
        sub_process = handle.sub_process
        if sub_process is not None:
            if sub_process.poll() is None:
                return Status.RUNNING
            else:
                if sub_process.returncode != 0:
                    return Status.FAILED
                else:
                    return Status.FINISHED
        else:
            return Status.INIT


class PythonJobPluginFactory(JobPluginFactory):
    def __init__(self) -> None:
        super().__init__()
        self._job_generator = PythonJobGenerator()
        self._job_controller = PythonJobController()

    def get_job_generator(self) -> JobGenerator:
        return self._job_generator

    def get_job_controller(self) -> JobController:
        return self._job_controller

    def job_type(self) -> Text:
        return "python"

