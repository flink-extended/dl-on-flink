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
from enum import Enum
from typing import Text, Optional
from ai_flow.common.properties import Properties
from ai_flow.util.json_utils import Jsonable


class MetricType(str, Enum):
    """
    Execution mode of the specific job. Batch or Stream.
    """
    DATASET = 'DATASET'
    MODEL = 'MODEL'

    @staticmethod
    def value_of(metric_type):
        if metric_type in ('DATASET', 'dataset'):
            return MetricType.DATASET
        elif metric_type in ('MODEL', 'model'):
            return MetricType.MODEL
        else:
            raise NotImplementedError


class MetricMeta(Jsonable):
    def __init__(self,
                 metric_name: Text,
                 metric_type: MetricType,
                 metric_desc: Optional[Text],
                 project_name: Text,
                 dataset_name: Optional[Text],
                 model_name: Optional[Text],
                 job_name: Optional[Text],
                 start_time: int,
                 end_time: int,
                 uri: Optional[Text],
                 tags: Optional[Text],
                 properties: Properties,
                 ) -> None:
        super().__init__()
        self.metric_name = metric_name
        self.metric_type = metric_type
        self.metric_desc = metric_desc
        self.project_name = project_name
        self.dataset_name = dataset_name
        self.model_name = model_name
        self.job_name = job_name
        self.start_time = start_time
        self.end_time = end_time
        self.uri = uri
        self.tags = tags
        self.properties: Properties = properties


class MetricSummary(Jsonable):
    def __init__(self,
                 uuid: int,
                 metric_name: Text,
                 metric_key: Text,
                 metric_value: Text,
                 metric_timestamp: int,
                 model_version: Optional[Text],
                 job_execution_id: Optional[Text]
                 ) -> None:
        super().__init__()
        self.uuid = uuid
        self.metric_name = metric_name
        self.metric_key = metric_key
        self.metric_value = metric_value
        self.metric_timestamp = metric_timestamp
        self.model_version = model_version
        self.job_execution_id = job_execution_id
