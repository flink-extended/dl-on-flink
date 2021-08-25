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

from typing import List

from notification_service.base_notification import BaseEvent

import ai_flow as af
from ai_flow_plugins.job_plugins.python import PythonProcessor
from ai_flow_plugins.job_plugins.python.python_processor import ExecutionContext


class HourlyDataWriter(PythonProcessor):
    def __init__(self, interval=60 * 60):
        super().__init__()
        self.interval = interval

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        base_path = dataset_meta.uri
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        i = 0
        while True:
            filepath = os.path.join(base_path, str(i))
            with open(filepath, 'w') as f:
                f.write(str(i))
            af.get_ai_flow_client() \
                .send_event(BaseEvent(event_type='DATA_EVENT', key='hourly_data', value='ready', context=str(i)))
            i += 1
            time.sleep(self.interval)
        return []


def main():
    af.init_ai_flow_context()
    with af.job_config('data_produce'):
        dataset_meta = af.get_dataset_by_name('hourly_data')
        assert dataset_meta is not None
        af.write_dataset(input=None, dataset_info=dataset_meta, write_dataset_processor=HourlyDataWriter(interval=10))

    workflow_name = af.current_workflow_config().workflow_name
    af.workflow_operation.submit_workflow(workflow_name)
    af.workflow_operation.start_new_workflow_execution(workflow_name)


if __name__ == '__main__':
    main()
