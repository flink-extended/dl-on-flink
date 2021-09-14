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
from datetime import datetime, timedelta, date, time

import numpy as np

from typing import List

from notification_service.base_notification import BaseEvent

import ai_flow as af
from ai_flow_plugins.job_plugins.python import PythonProcessor
from ai_flow_plugins.job_plugins.python.python_processor import ExecutionContext

DATASET_URI = os.path.abspath(os.path.join(__file__, "../../../..")) + '/dataset_data/mnist_{}.npz'
HOURLY_DATA_PRODUCE_FREQUENCY_SEC = 60


class HourlyDataWriter(PythonProcessor):
    def __init__(self, interval=60 * 60, days=2):
        super().__init__()
        self.interval = interval
        self.days = days

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        base_path = dataset_meta.uri
        if not os.path.exists(base_path):
            os.mkdir(base_path)

        ai_flow_client = af.get_ai_flow_client()
        mnist_train_dataset = ai_flow_client.get_dataset_by_name('mnist_train').uri
        with np.load(mnist_train_dataset) as f:
            x_train, y_train = f['x_train'], f['y_train']
        current_time = datetime.combine(date.today(), time(0))
        one_hour = timedelta(hours=1)

        for i in range(24 * self.days):
            filepath = os.path.join(base_path, '{}.npz'.format(current_time.isoformat(timespec='hours')))
            idx = np.random.choice(np.arange(len(x_train)), 1000, replace=False)
            np.savez_compressed(filepath, x_train=x_train[idx], y_train=y_train[idx])
            ai_flow_client \
                .send_event(BaseEvent(event_type='DATA_EVENT', key='hourly_data', value='ready',
                                      context=current_time.isoformat(timespec='hours')))
            current_time += one_hour
            time.sleep(self.interval)
        return []


def main():
    af.init_ai_flow_context()
    with af.job_config('data_produce'):
        dataset_meta = af.get_dataset_by_name('hourly_data')
        assert dataset_meta is not None
        af.write_dataset(input=None,
                         dataset_info=dataset_meta,
                         write_dataset_processor=HourlyDataWriter(HOURLY_DATA_PRODUCE_FREQUENCY_SEC))

    workflow_name = af.current_workflow_config().workflow_name
    af.workflow_operation.submit_workflow(workflow_name)
    af.workflow_operation.start_new_workflow_execution(workflow_name)


if __name__ == '__main__':
    main()
