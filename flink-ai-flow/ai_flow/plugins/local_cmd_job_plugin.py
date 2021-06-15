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
from abc import ABC
from typing import Text, Dict
from subprocess import Popen
from ai_flow.workflow.job_context import JobContext
from ai_flow.util.process_utils import get_all_children_pids
import psutil
import os
import logging
from pathlib import Path
import tempfile
from ai_flow.log import log_path_utils
from ai_flow.plugins.job_plugin import AISubGraph, ProjectDesc, AbstractJobPlugin, \
    AbstractJobConfig, AbstractJob, AbstractJobHandler, AbstractEngine, AbstractPlatform, job_name_to_task_id
from ai_flow.plugins.engine import CMDEngine
from ai_flow.plugins.local_platform import LocalPlatform, LocalJobHandler
from ai_flow.meta.job_meta import ExecutionMode
from ai_flow.graph.ai_nodes.executable import ExecutableNode
from ai_flow.executor.executor import CmdExecutor


class LocalCMDJobConfig(AbstractJobConfig):
    @staticmethod
    def from_dict(data: Dict, config) -> object:
        return AbstractJobConfig.from_dict(data, config)

    def __init__(self):
        super().__init__(platform=LocalPlatform.platform(), engine=CMDEngine.engine())


class LocalCMDJob(AbstractJob):
    def __init__(self,
                 exec_cmd,
                 job_context: JobContext = JobContext(),
                 job_config: AbstractJobConfig = LocalCMDJobConfig()):
        super().__init__(job_context, job_config)
        self.exec_cmd = exec_cmd


class LocalJobPlugin(AbstractJobPlugin, ABC):

    def __init__(self) -> None:
        super().__init__()
        self.job_handler_map: Dict[Text, LocalJobHandler] = {}

    def platform(self) -> type(AbstractPlatform):
        return LocalPlatform

    def stop_job(self, job: AbstractJob):
        if job.uuid is None or job.uuid not in self.job_handler_map:
            return
        logging.info('stop {} {} {}'.format(job.uuid, job.instance_id, job.job_name))
        job_handler = self.job_handler_map[job.uuid]
        if isinstance(job_handler.process_object, Popen):
            current_pid = job_handler.process_object.pid
            if current_pid is not None:
                children_pids = get_all_children_pids(current_pid)
                for pid in children_pids:
                    try:
                        p = psutil.Process(pid)
                        p.kill()
                        p.wait()
                    except psutil.NoSuchProcess as ex:
                        pass
            try:
                job_handler.process_object.kill()
                job_handler.process_object.wait()
            except psutil.NoSuchProcess:
                pass
        else:
            raise Exception("not support exec handle " + str(job_handler))


class LocalCMDJobPlugin(LocalJobPlugin):

    def __init__(self) -> None:
        super().__init__()
        self.job_handler_map: Dict[Text, LocalJobHandler] = {}

    def generate(self, sub_graph: AISubGraph, project_desc: ProjectDesc) -> AbstractJob:
        assert 1 == len(sub_graph.nodes)
        node: ExecutableNode = list(sub_graph.nodes.values())[0]
        if sub_graph.config.exec_mode == ExecutionMode.BATCH:
            context = JobContext(ExecutionMode.BATCH)
        else:
            context = JobContext(ExecutionMode.STREAM)
        executor: CmdExecutor = node.executor
        return LocalCMDJob(job_context=context, exec_cmd=executor.cmd_line, job_config=sub_graph.config)

    def generate_job_resource(self, job: AbstractJob) -> None:
        pass

    def submit_job(self, job: LocalCMDJob) -> AbstractJobHandler:
        # every job submitter need set the job log file,
        # local cmd job set log file name LocalCMDJob_{workflow_execution_id}_{stdout,stderr}.log
        if not Path(job.job_config.project_desc.project_path).exists():
            job.job_config.project_desc.project_path = tempfile.gettempdir()
        stdout_log = log_path_utils.stdout_log_path(job.job_config.project_desc.get_absolute_log_path(),
                                                    job.job_name)
        stderr_log = log_path_utils.stderr_log_path(job.job_config.project_desc.get_absolute_log_path(),
                                                    job.job_name)
        if not os.path.exists(job.job_config.project_desc.get_absolute_log_path()):
            os.mkdir(job.job_config.project_desc.get_absolute_log_path())
        with open(stdout_log, 'a') as out, open(stderr_log, 'a') as err:
            submitted_process = Popen(
                args=job.exec_cmd,
                shell=True,
                stdout=out,
                stderr=err
            )
            job.pid = submitted_process.pid
            job_handler = LocalJobHandler(job_instance_id=job.instance_id,
                                          job_uuid=job.uuid,
                                          workflow_id=job.job_context.workflow_execution_id,
                                          process_object=submitted_process)
            self.job_handler_map[job.uuid] = job_handler
            return job_handler

    def cleanup_job(self, job: AbstractJob):
        if job.uuid in self.job_handler_map:
            del self.job_handler_map[job.uuid]

    def job_type(self) -> type(AbstractJob):
        return LocalCMDJob

    def job_config_type(self) -> type(AbstractJobConfig):
        return LocalCMDJobConfig

    def engine(self) -> type(AbstractEngine):
        return CMDEngine

    def generate_code(self, op_index, job: AbstractJob):
        LOCAL_CMD_OPERATOR = """op_{0} = BashOperator(task_id='{1}', dag=dag, bash_command='{2}')\n"""
        if isinstance(job.exec_cmd, list):
            cmd = " ".join(job.exec_cmd)
        else:
            cmd = job.exec_cmd
        code_text = LOCAL_CMD_OPERATOR.format(op_index, job_name_to_task_id(job.job_name), cmd)
        return code_text
