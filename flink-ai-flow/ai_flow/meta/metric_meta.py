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
                 name: Text,
                 dataset_id: int,
                 model_name: Optional[Text],
                 model_version: Optional[Text],
                 job_id: int,
                 start_time: int,
                 end_time: int,
                 metric_type: MetricType,
                 uri: Text,
                 tags: Text,
                 metric_description: Text,
                 properties: Properties,
                 uuid: int = None,
                 ) -> None:
        super().__init__()
        self.uuid = uuid
        self.name = name
        self.dataset_id: int = dataset_id
        self.model_name: Optional[Text] = model_name
        self.model_version: Optional[Text] = model_version
        self.job_id: int = job_id
        self.start_time: int = start_time
        self.end_time: int = end_time
        self.metric_type: MetricType = metric_type
        self.uri: Text = uri
        self.tags: Text = tags
        self.metric_description: Text = metric_description
        self.properties: Properties = properties


class MetricSummary(Jsonable):
    def __init__(self,
                 metric_id: int,
                 metric_key: Text,
                 metric_value: Text,
                 uuid: int,
                 ) -> None:
        super().__init__()
        self.uuid = uuid
        self.metric_id: int = metric_id
        self.metric_key: Text = metric_key
        self.metric_value: Text = metric_value
