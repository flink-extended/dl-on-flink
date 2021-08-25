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
from typing import List

from ai_flow.workflow.control_edge import MeetAllEventCondition

import ai_flow as af
from ai_flow.api.context_extractor import ContextExtractor, EventContext, ContextList
from ai_flow_plugins.job_plugins.python.python_processor import PythonProcessor, ExecutionContext
from notification_service.base_notification import BaseEvent, ANY_CONDITION


class DailyWorkflowContextExtractor(ContextExtractor):

    def extract_context(self, event: BaseEvent) -> EventContext:
        context_list = ContextList()
        if event.event_type == 'DATA_EVENT' and 'hourly_processed_data' in event.key:
            context_list.add_context(event.context)
            return context_list


class DataProcessingReader(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        day = execution_context.job_execution_info.workflow_execution.context
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        daily_dir = os.path.join(dataset_meta.uri, day)
        file_names = os.listdir(daily_dir)
        return [[os.path.join(daily_dir, file_name) for file_name in file_names]]


class DataProcessingProcessor(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List):
        file_paths = input_list[0]
        res = 0
        for file_path in file_paths:
            with open(file_path, 'r') as f:
                res += int(f.read())
        return [[res]]


class DataProcessingWriter(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        day = execution_context.job_execution_info.workflow_execution.context
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        result_dir = dataset_meta.uri
        os.makedirs(result_dir, exist_ok=True)
        with open(os.path.join(result_dir, day), 'w') as f:
            f.write(str(input_list[0][0]))
        return []


def main():
    af.init_ai_flow_context()
    with af.job_config('data_processing'):
        daily_data_meta = af.get_dataset_by_name('daily_data')
        daily_result_meta = af.get_dataset_by_name('daily_data_result')
        conn = af.read_dataset(daily_data_meta, DataProcessingReader())
        conn = af.transform(conn, transform_processor=DataProcessingProcessor())
        af.write_dataset(conn, daily_result_meta, DataProcessingWriter())

    af.set_context_extractor(DailyWorkflowContextExtractor())

    project_name = af.current_project_config().get_project_name()
    workflow_name = af.current_workflow_config().workflow_name
    af.workflow_operation.submit_workflow(workflow_name)

    condition = MeetAllEventCondition()
    for i in range(24):
        condition.add_event(namespace=project_name, event_type='DATA_EVENT',
                            event_key='hourly_processed_data_{}'.format(i), event_value='ready', sender=ANY_CONDITION)
    af.workflow_operation.start_new_workflow_execution_on_events(workflow_name, event_conditions=[condition])


if __name__ == '__main__':
    main()
