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
import shutil
from typing import List

from ai_flow.workflow.control_edge import MeetAllEventCondition

import ai_flow as af
from ai_flow.api.context_extractor import ContextExtractor, EventContext, ContextList
from ai_flow_plugins.job_plugins.python.python_processor import PythonProcessor, ExecutionContext
from notification_service.base_notification import BaseEvent, ANY_CONDITION


class HourlyWorkflowContextExtractor(ContextExtractor):

    def extract_context(self, event: BaseEvent) -> EventContext:
        context_list = ContextList()
        if event.event_type == 'DATA_EVENT' and event.key == 'hourly_data':
            context_list.add_context(event.context)
            return context_list


class DataProcessingReader(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        filename = execution_context.job_execution_info.workflow_execution.context
        hourly_data_dir = dataset_meta.uri
        src_path = os.path.join(hourly_data_dir, filename)
        print('read {}'.format(src_path))
        with open(src_path, 'r') as f:
            return [f.read()]


class DataProcessingProcessor(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        num = int(input_list[0])
        return [-num]


class DataProcessingWriter(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        hourly_processed_data_dir = dataset_meta.uri
        filename = execution_context.job_execution_info.workflow_execution.context
        dest_path = os.path.join(hourly_processed_data_dir, filename)
        print('write {}'.format(dest_path))
        with open(dest_path, 'w') as f:
            f.write(str(input_list[0]))
        return []


class DataCpReader(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        hourly_data_dir = dataset_meta.uri
        filename = execution_context.job_execution_info.workflow_execution.context
        return [os.path.join(hourly_data_dir, filename)]


class DataCpProcessor(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        src_file_path = input_list[0]
        filename = execution_context.job_execution_info.workflow_execution.context

        day = str(int(filename) // 24)
        hour = str(int(filename) % 24)

        return [[src_file_path, day, hour]]


class DataCpWriter(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        print(input_list)
        src_file, day, hour = input_list[0]
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        daily_data_dir = dataset_meta.uri
        bucket_dir = os.path.join(daily_data_dir, day)
        os.makedirs(bucket_dir, exist_ok=True)

        dest_file = os.path.join(bucket_dir, hour)
        print('copy from {} to {}'.format(src_file, dest_file))
        shutil.copy(src_file, dest_file)

        af.get_ai_flow_client().send_event(BaseEvent(event_type='DATA_EVENT',
                                                     key='hourly_processed_data_{}'.format(hour),
                                                     value='ready', context=day))
        return []


def main():
    af.init_ai_flow_context()
    with af.job_config('data_processing'):
        hourly_data_meta = af.get_dataset_by_name('hourly_data')
        hourly_data_processed = af.get_dataset_by_name('hourly_data_processed')
        assert hourly_data_meta is not None and hourly_data_processed is not None
        channel = af.read_dataset(hourly_data_meta, DataProcessingReader())
        channel = af.transform(transform_processor=DataProcessingProcessor(), input=channel)
        af.write_dataset(channel, hourly_data_processed, DataProcessingWriter())

    with af.job_config('data_cp'):
        hourly_data_processed = af.get_dataset_by_name('hourly_data_processed')
        daily_data_meta = af.get_dataset_by_name('daily_data')
        assert hourly_data_processed is not None and daily_data_meta is not None
        channel = af.read_dataset(hourly_data_processed, DataCpReader())
        channel1 = af.user_define_operation(channel, processor=DataCpProcessor())
        af.write_dataset(channel1, daily_data_meta, DataCpWriter())

    af.action_on_job_status('data_cp', 'data_processing')
    af.set_context_extractor(HourlyWorkflowContextExtractor())

    project_name = af.current_project_config().get_project_name()
    workflow_name = af.current_workflow_config().workflow_name
    af.workflow_operation.submit_workflow(workflow_name)

    condition = MeetAllEventCondition(). \
        add_event(namespace=project_name, event_type='DATA_EVENT',
                  event_key='hourly_data', event_value='ready', sender=ANY_CONDITION)
    af.workflow_operation.start_new_workflow_execution_on_events(workflow_name, event_conditions=[condition])


if __name__ == '__main__':
    main()
