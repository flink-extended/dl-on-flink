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
import time
from tempfile import NamedTemporaryFile
from typing import Text, Dict
from subprocess import PIPE, STDOUT, Popen

from ai_flow.translator.translator import JobGenerator
from ai_flow.util import serialization_utils
from ai_flow.workflow.job_config import JobConfig
from ai_flow.ai_graph.ai_graph import AISubGraph
from ai_flow.plugin_interface.job_plugin_interface import JobPluginFactory, JobHandle, JobRuntimeEnv, \
    JobController
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo
from ai_flow.workflow.job import Job
from ai_flow.workflow.status import Status
from ai_flow_plugins.job_plugins.bash.bash_job_config import BashJobConfig
from ai_flow_plugins.job_plugins.bash.bash_processor import BashProcessor


class BashJob(Job):
    """
    BashJob is the description of bash type job.
    The processors_file field stores the serialized file of the BashProcessor
    (ai_flow_plugins.job_plugins.bash.bash_processor.BashProcessor).
    """
    def __init__(self, job_config: JobConfig):
        super().__init__(job_config)
        self.processors_file = None


class BashJobHandle(JobHandle):

    def __init__(self, job: Job,
                 job_execution: JobExecutionInfo):
        super().__init__(job=job, job_execution=job_execution)
        """
        It saves the Popen object dictionary of the bash child process.
        key: node_id
        value: Popen object
        """
        self.sub_process = {}
        """It represents the serialized file of the processor."""
        self.processors_file = None
        """It saves the result dict of the bash child process."""
        self.lines = {}


class BashJobGenerator(JobGenerator):
    @staticmethod
    def _validate_sub_graph(sub_graph: AISubGraph):
        """
        Check that all the processor in sub_graph is BashProcessor
        """
        for node_name, ai_node in sub_graph.nodes.items():
            processor = ai_node.get_processor()
            if not isinstance(processor, BashProcessor):
                raise Exception("Invalid sub_graph: node {} in job {} expect to has BashProcessor but it is {}"
                                .format(node_name, sub_graph.config.job_name, type(processor)))

    def generate(self, sub_graph: AISubGraph, resource_dir: Text = None) -> Job:
        self._validate_sub_graph(sub_graph)
        bash_job_config: BashJobConfig = sub_graph.config
        job = BashJob(job_config=bash_job_config)
        processors = {}
        for k, v in sub_graph.nodes.items():
            processors[k] = v.get_processor()
        with NamedTemporaryFile(mode='w+b', dir=resource_dir, prefix='{}_bash_'.format(job.job_name),
                                delete=False) as fp:
            job.processors_file = os.path.basename(fp.name)
            fp.write(serialization_utils.serialize(processors))
        return job


class BashJobController(JobController):

    def cleanup_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        pass

    def submit_one_process(self, processor: BashProcessor, env, working_dir):

        def pre_exec():
            # Restore default signal disposition and invoke setsid
            for sig in ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ'):
                if hasattr(signal, sig):
                    signal.signal(getattr(signal, sig), signal.SIG_DFL)
            os.setsid()

        self.log.info('Running command: %s', processor.bash_command)

        sub_process = Popen(  # pylint: disable=subprocess-popen-preexec-fn
            ['bash', "-c", processor.bash_command],
            stdout=PIPE,
            stderr=STDOUT,
            cwd=working_dir,
            env=env,
            preexec_fn=pre_exec,
        )
        self.log.info('Process pid: %s', sub_process.pid)
        return sub_process

    def get_result(self, job_handle: JobHandle, blocking: bool = True) -> object:
        handle: BashJobHandle = job_handle
        if blocking:
            with open(handle.processors_file, 'rb') as f:
                processors: Dict = serialization_utils.deserialize(f.read())
            for k, v in processors.items():
                self.log.info('{} Output:'.format(k))
                sub_process = handle.sub_process.get(k)
                line = ''
                for raw_line in iter(sub_process.stdout.readline, b''):
                    line = raw_line.decode(v.output_encoding).rstrip()
                    self.log.info("%s", line)

                sub_process.wait()

                self.log.info('Command exited with return code %s', sub_process.returncode)

                if sub_process.returncode != 0:
                    raise Exception('Bash command failed. The command returned a non-zero exit code {}.'
                                    .format(sub_process.returncode))
                handle.lines[k] = line
        return handle.lines

    def get_job_status(self, job_handle: JobHandle) -> Status:
        handler: BashJobHandle = job_handle
        for sub_process in handler.sub_process.values():
            if sub_process is not None:
                if sub_process.poll() is None:
                    return Status.RUNNING
                else:
                    if sub_process.returncode != 0:
                        return Status.FAILED
            else:
                return Status.INIT
        return Status.FINISHED

    def submit_job(self, job: Job, job_runtime_env: JobRuntimeEnv) -> JobHandle:
        handler = BashJobHandle(job=job, job_execution=job_runtime_env.job_execution_info)
        bash_job: BashJob = job
        processor_file = os.path.join(job_runtime_env.generated_dir, bash_job.processors_file)
        with open(processor_file, 'rb') as f:
            processors: Dict = serialization_utils.deserialize(f.read())
        for k, v in processors.items():
            processor: BashProcessor = v
            env = os.environ.copy()
            if 'env' in job.job_config.properties:
                env.update(job.job_config.properties.get('env'))
            workflow_execution_context = job_runtime_env.job_execution_info.workflow_execution.context
            if workflow_execution_context:
                self.log.info("Setting env var WORKFLOW_EXECUTION_CONTEXT={}".format(workflow_execution_context))
                env['WORKFLOW_EXECUTION_CONTEXT'] = workflow_execution_context
            sub_process = self.submit_one_process(processor=processor,
                                                  env=env,
                                                  working_dir=job_runtime_env.working_dir)
            handler.sub_process[k] = sub_process
        handler.processors_file = processor_file
        return handler

    def stop_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv = None):
        handler: BashJobHandle = job_handle
        processor_file = handler.processors_file
        with open(processor_file, 'rb') as f:
            processors: Dict = serialization_utils.deserialize(f.read())
        for k, v in processors.items():
            self.log.info('{} Output:'.format(k))
            sub_process = handler.sub_process.get(k)
            self.log.info('Sending SIGTERM signal to bash process group')
            if sub_process and hasattr(sub_process, 'pid') and sub_process.poll() is None:
                while sub_process.poll() is None:
                    try:
                        os.killpg(os.getpgid(sub_process.pid), signal.SIGTERM)
                    except Exception as e:
                        self.log.error('Kill process {} failed! error {}'.format(sub_process.pid, str(e)))
                        time.sleep(1)


class BashJobPluginFactory(JobPluginFactory):
    def __init__(self) -> None:
        super().__init__()
        self._job_generator = BashJobGenerator()
        self._job_controller = BashJobController()

    def get_job_generator(self) -> JobGenerator:
        return self._job_generator

    def get_job_controller(self) -> JobController:
        return self._job_controller

    def job_type(self) -> Text:
        return "bash"
