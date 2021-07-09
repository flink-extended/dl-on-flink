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
import enum
from typing import Text, List, Dict

from ai_flow.meta.dataset_meta import DatasetMeta
from ai_flow.graph.node import Node
from ai_flow.workflow.job import JobConfig
from ai_flow.util import serialization_utils
from ai_flow.graph.channel import Channel


class AINode(Node):
    def __init__(self,
                 processor: object = None,
                 name: Text = None,
                 output_num: int = 1,
                 config: JobConfig = None,
                 node_type: Text = 'AINode',
                 **kwargs) -> None:
        super().__init__(properties=None,
                         name=name,
                         output_num=output_num)
        self.processor: bytes = serialization_utils.serialize(processor)
        self.config: JobConfig = config
        self.node_config: Dict = kwargs
        self.node_config['name'] = name
        self.node_config['node_type'] = node_type

    def outputs(self) -> List[Channel]:
        if self.output_num > 0:
            result = []
            for i in range(self.output_num):
                result.append(Channel(node_id=self.node_id, port=i))
            return result
        else:
            return None

    def get_processor(self) -> object:
        if self.processor is None:
            return None
        else:
            return serialization_utils.deserialize(self.processor)

    def node_type(self):
        return self.node_config.get('node_type')

    def name(self):
        return self.node_config.get('name')


class ReadDatasetNode(AINode):
    def __init__(self,
                 dataset: DatasetMeta,
                 processor: object = None,
                 name: Text = None,
                 config: JobConfig = None,
                 node_type: Text = 'ReadDataNode', **kwargs) -> None:
        super().__init__(processor, name, 1, config, node_type, **kwargs)
        if dataset is None:
            raise Exception('dataset can not be None!')
        self.node_config['dataset'] = dataset

    def dataset(self):
        return self.node_config.get('dataset')


class WriteDatasetNode(AINode):
    def __init__(self,
                 dataset: DatasetMeta,
                 processor: object = None,
                 name: Text = None,
                 config: JobConfig = None,
                 node_type: Text = 'WriteDataNode', **kwargs) -> None:
        super().__init__(processor, name, 0, config, node_type, **kwargs)
        if dataset is None:
            raise Exception('dataset can not be None!')
        self.node_config['dataset'] = dataset

    def dataset(self):
        return self.node_config.get('dataset')

