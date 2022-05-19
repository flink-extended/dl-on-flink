#  Copyright 2022 Deep Learning on Flink Authors
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from time import sleep
import json
import os
from dl_on_flink_framework import node_pb2
from dl_on_flink_framework import node_service_pb2_grpc


class Context(object):
    """
    The context is passed to the deep learning process via the function argument
    of the entry function.

    User can use the given context to get the information in ClusterConfig, e.g. The
    configuration of the cluster, i.e., the number of node for each node type in the
    cluster, the node type and index of the current process or any property that is
    added to the ClusterConfig.

    It can be used to interact with the Java process, e.g. notify that the
    python process is finished.
    """

    def __str__(self):
        return self.context_pb.__str__()

    def __init__(self, context, channel):
        self.mode = context.mode
        self.roleName = context.roleName
        self.index = context.index
        self.roleParallelism = context.roleParallelism
        self.properties = context.props
        self.context_pb = context

        self.userScript = context.userScript
        self.identity = context.identity
        self.funcName = context.funcName
        self.failNum = context.failNum

        self.outQueueName = context.outQueueName
        self.inQueueName = context.inQueueName
        self.outQueueMMapLen = context.outQueueMMapLen
        self.inQueueMMapLen = context.inQueueMMapLen

        self.channel = channel
        self.stub = node_service_pb2_grpc.NodeServiceStub(self.channel)

    def from_java(self):
        return "queue://" + str(self.inQueueName) + ":" + str(self.inQueueMMapLen)

    def to_java(self):
        return "queue://" + str(self.outQueueName) + ":" + str(self.outQueueMMapLen)

    def get_current_attempt_index(self):
        """
        Get the current attempt index. Attempt index starts from 0.
        """
        return self.failNum

    def get_finished_worker_nodes(self):
        """
        Get a list of finished nodes with the node type of worker.
        """
        response = self.stub.GetFinishWorker(node_pb2.NodeSimpleRequest(code=0))
        return response.workers

    def get_property(self, key):
        """
        Get the property set in ClusterConfig
        :param key: The key of the property.
        """
        return self.properties[key]

    def get_node_type_count_map(self):
        """
        Get a map from node type to the node count.
        """
        return self.roleParallelism

    def get_index(self):
        """
        Get the index of the current node.
        """
        return self.index

    def get_node_type(self):
        """
        Get the node type of the current node.
        """
        return self.roleName

    def stop_node(self):
        """
        Stop the current node.
        """
        response = self.stub.FinishJob(node_pb2.NodeSimpleRequest(code=0))

    def get_context_proto(self):
        return self.context_pb
