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
from datetime import datetime, time, date

import numpy as np
from typing import List

from sklearn.preprocessing import StandardScaler
from sklearn.utils import check_random_state

from ai_flow.workflow.control_edge import MeetAllEventCondition

import ai_flow as af
from ai_flow.api.context_extractor import ContextExtractor, EventContext, ContextList, Broadcast
from ai_flow_plugins.job_plugins.bash import BashProcessor
from ai_flow_plugins.job_plugins.python.python_processor import PythonProcessor, ExecutionContext
from notification_service.base_notification import BaseEvent, ANY_CONDITION


class HourlyWorkflowContextExtractor(ContextExtractor):

    def extract_context(self, event: BaseEvent) -> EventContext:
        context_list = ContextList()
        if event.event_type == 'DATA_EVENT' and event.key == 'hourly_data':
            context_list.add_context(event.context)
            return context_list

        return Broadcast()


class DataProcessingReader(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        process_hour = execution_context.job_execution_info.workflow_execution.context
        hourly_data_dir = dataset_meta.uri

        dataset_path = os.path.join(hourly_data_dir, '{}.npz'.format(process_hour))
        print('reading {}'.format(dataset_path))

        with np.load(dataset_path) as f:
            return [[f['x_train'], f['y_train']]]


class DataProcessingProcessor(PythonProcessor):
    @staticmethod
    def preprocess_data(x_data, y_data=None):
        random_state = check_random_state(0)
        permutation = random_state.permutation(x_data.shape[0])
        if y_data is None:
            return x_data[permutation]
        else:
            return x_data[permutation], y_data[permutation]

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        x_train, y_train = self.preprocess_data(input_list[0][0], input_list[0][1])
        x_train = x_train.reshape((x_train.shape[0], -1))
        return [[StandardScaler().fit_transform(x_train), y_train]]


class DataProcessingWriter(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        hourly_processed_data_dir = dataset_meta.uri
        os.makedirs(hourly_processed_data_dir, exist_ok=True)

        process_hour = execution_context.job_execution_info.workflow_execution.context
        dataset_path = os.path.join(hourly_processed_data_dir, '{}.npz'.format(process_hour))
        print('writing {}'.format(dataset_path))

        x_train, y_train = input_list[0][0], input_list[0][1]
        np.savez_compressed(dataset_path, x_train=x_train, y_train=y_train)
        return []


class DailyDataReadyReader(PythonProcessor):
    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        return [[dataset_meta]]


class DailyDataReadySensor(PythonProcessor):
    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        dataset_meta: af.DatasetMeta = input_list[0][0]
        process_hour = execution_context.job_execution_info.workflow_execution.context
        process_date = datetime.fromisoformat(process_hour).date()
        daily_data_dir = os.path.join(dataset_meta.uri, process_date.isoformat())

        print('check if {} data is ready at {}'.format(process_date, daily_data_dir))
        for i in range(24):
            process_datatime = datetime.combine(process_date, time(hour=i)).isoformat(timespec='hours')
            file_name = "{}.npz".format(process_datatime)
            file_path = os.path.join(daily_data_dir, file_name)
            if not os.path.exists(file_path):
                print("{} not exist".format(file_path))
                return []

        print('all data for {} is ready'.format(process_date))
        af.get_ai_flow_client().send_event(BaseEvent(key='daily_data', value='ready', event_type='DATA_EVENT',
                                                     context=process_date.isoformat()))


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
        conn = af.read_dataset(hourly_data_processed, read_dataset_processor=BashProcessor("echo dummy read"))
        conn = af.user_define_operation(conn, processor=BashProcessor(bash_command="""
            set -e
            PROCESS_HOUR=${{WORKFLOW_EXECUTION_CONTEXT}}
            SRC={hourly_data_processed_dir}/${{PROCESS_HOUR}}.npz
            DEST_DIR={daily_data}/`echo ${{PROCESS_HOUR}} | cut -d'T' -f1`
            mkdir -p ${{DEST_DIR}}
            DEST=${{DEST_DIR}}/${{PROCESS_HOUR}}.npz
            echo copying from ${{SRC}} to ${{DEST}}
            cp ${{SRC}} ${{DEST}}
        """.format(hourly_data_processed_dir=hourly_data_processed.uri, daily_data=daily_data_meta.uri)))
        af.write_dataset(conn, daily_data_meta, write_dataset_processor=BashProcessor("echo dummy write"))

    with af.job_config('daily_data_ready_sensor'):
        daily_data_meta = af.get_dataset_by_name('daily_data')
        assert daily_data_meta is not None
        channel = af.read_dataset(daily_data_meta, read_dataset_processor=DailyDataReadyReader())
        af.user_define_operation(channel, processor=DailyDataReadySensor())

    af.action_on_job_status('data_cp', 'data_processing')
    af.action_on_job_status('daily_data_ready_sensor', 'data_cp')
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
