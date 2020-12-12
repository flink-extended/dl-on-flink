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
from python_ai_flow.python_job_common import BaseExampleComponent, Executor
from typing import List, Text
from python_ai_flow.example_components.rabbitmq import rabbitmq_utils
import threading
from streamz import Stream
from ai_flow.udf.function_context import FunctionContext
from ai_flow.common.args import ExecuteArgs


rabbitmq_conn_pool = {}
rabbitmq_ch_pool = {}


def get_rabbitmq_conn(conn_str):
    if conn_str not in rabbitmq_conn_pool:
        rabbitmq_conn_pool[conn_str] = rabbitmq_utils.connect(conn_str)
    return rabbitmq_conn_pool[conn_str]


def close_rabbitmq_conn(conn_str):
    if conn_str in rabbitmq_conn_pool:
        rabbitmq_utils.close(rabbitmq_conn_pool[conn_str])


def close_rabbitmq_all_conn():
    for i in rabbitmq_conn_pool:
        rabbitmq_utils.close(rabbitmq_conn_pool[i])


class RabbitMQExample(BaseExampleComponent):
    class SourceThread(threading.Thread):
        def __init__(self,
                     name,
                     conn_str,
                     queue):
            threading.Thread.__init__(self)
            self.name = name
            self.conn_str = conn_str
            self.queue = queue
            self.stream = Stream()

        def run(self) -> None:
            def callback(ch, method, propertites, body):
                self.stream.emit(body)

            conn = get_rabbitmq_conn(self.conn_str)
            ch = rabbitmq_utils.create_channel(conn)
            ch.basic_consume(on_message_callback=callback, queue=self.queue, auto_ack=True)
            ch.start_consuming()

    class SourceExecutor(Executor):

        def __init__(self,
                     file_format: Text,
                     conn_str: Text,
                     args: ExecuteArgs) -> None:
            super().__init__()
            self.file_format = file_format
            self.conn_str = conn_str
            self.kwargs = args
            self.source_thread = None

        def execute(self, context: FunctionContext, args: List = None) -> List:
            self.source_thread = RabbitMQExample.SourceThread(name="",
                                                              conn_str=self.conn_str,
                                                              queue=self.kwargs.stream_properties['queue'])
            return [self.source_thread.stream]

        def close(self, context):
            self.source_thread.start()
            self.source_thread.join()

    class SinkExecutor(Executor):

        def __init__(self,
                     file_format: Text,
                     conn_str: Text,
                     args: ExecuteArgs) -> None:
            super().__init__()
            self.file_format = file_format
            self.conn_str = conn_str
            self.kwargs = args
            self.conn = None
            self.channel = None

        def setup(self, context):
            self.conn = get_rabbitmq_conn(self.conn_str)
            self.channel = rabbitmq_utils.create_channel(self.conn)

        def execute(self, context: FunctionContext, args: List = None):
            def sink(record):
                rabbitmq_utils.send_message(self.channel, self.kwargs.stream_properties['queue'], record)

            upstream = args[0]
            upstream.sink(sink)

    def batch_executor(self) -> Executor:
        raise Exception("rabbitmq not support batch mode!")

    def stream_executor(self):
        if self.is_source:
            return RabbitMQExample.SourceExecutor(
                file_format=self.example_meta.data_format,
                conn_str=self.example_meta.stream_uri,
                args=self.example_node.execute_properties.stream_properties)
        else:
            return RabbitMQExample.SinkExecutor(
                file_format=self.example_meta.data_format,
                conn_str=self.example_meta.stream_uri,
                args=self.example_node.execute_properties.stream_properties)
