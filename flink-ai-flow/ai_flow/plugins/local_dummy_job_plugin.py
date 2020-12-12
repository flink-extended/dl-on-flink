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
from typing import Dict
from ai_flow.plugins.job_plugin import AISubGraph, ProjectDesc, JobContext, AbstractJobPlugin, \
    AbstractJobConfig, AbstractJob, AbstractJobHandler, AbstractEngine, AbstractPlatform, job_name_to_task_id
from ai_flow.plugins.engine import DummyEngine
from ai_flow.plugins.local_platform import LocalPlatform, LocalJobHandler


class LocalDummyJobConfig(AbstractJobConfig):
    @staticmethod
    def from_dict(data: Dict, config) -> object:
        return AbstractJobConfig.from_dict(data, config)

    def __init__(self, operator_name: str = None):
        super().__init__(platform=LocalPlatform.platform(), engine=DummyEngine.engine())
        self.properties['operator_name'] = operator_name


class SendEventJobConfig(LocalDummyJobConfig):

    def __init__(self, uri: str, key: str, value: str, event_type: str):
        super().__init__("send_event")
        self.properties['uri'] = uri
        self.properties['event_key'] = key
        self.properties['event_value'] = value
        self.properties['event_type'] = event_type


class LocalDummyJob(AbstractJob):
    def __init__(self,
                 job_context: JobContext = JobContext(),
                 job_config: AbstractJobConfig = LocalDummyJobConfig()):
        super().__init__(job_context, job_config)


class LocalDummyJobPlugin(AbstractJobPlugin, ABC):

    def __init__(self) -> None:
        super().__init__()

    def generate(self, sub_graph: AISubGraph, project_desc: ProjectDesc) -> AbstractJob:
        return LocalDummyJob()

    def generate_job_resource(self, job: AbstractJob) -> None:
        pass

    def submit_job(self, job: AbstractJob) -> AbstractJobHandler:
        return LocalJobHandler(job_instance_id=job.instance_id, job_uuid=job.uuid,
                               workflow_id=job.job_context.workflow_execution_id)

    def cleanup_job(self, job: AbstractJob):
        pass

    def platform(self) -> type(AbstractPlatform):
        return LocalPlatform

    def stop_job(self, job: AbstractJob):
        pass

    def job_type(self) -> type(AbstractJob):
        return LocalDummyJob

    def job_config_type(self) -> type(AbstractJobConfig):
        return LocalDummyJobConfig

    def engine(self) -> type(AbstractEngine):
        return DummyEngine

    def generate_code(self, op_index, job: AbstractJob):
        DUMMY_OPERATOR = """op_{0} = DummyOperator(task_id='{1}', dag=dag)\n"""

        SEND_EVENT_OPERATOR = """op_{0} = SendEventOperator(
            task_id='{1}',
            dag=dag,
            uri='{2}',
            event=Event(key='{3}', value='{4}', event_type='{5}'))\n"""

        if "send_event" == job.job_config.properties['operator_name']:
            code_text = SEND_EVENT_OPERATOR.format(op_index,
                                                   job_name_to_task_id(job.job_name),
                                                   job.job_config.properties['uri'],
                                                   job.job_config.properties['event_key'],
                                                   job.job_config.properties['event_value'],
                                                   job.job_config.properties['event_type']
                                                   )
        else:
            code_text = DUMMY_OPERATOR.format(op_index, job_name_to_task_id(job.job_name))

        return code_text
