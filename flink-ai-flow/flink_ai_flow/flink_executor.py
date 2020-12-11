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
from typing import Text
from ai_flow.executor.executor import BaseExecutor, PythonObjectExecutor
from ai_flow.common.serialization_utils import serialize


class FlinkJavaExecutor(BaseExecutor):
    """
    Implementation of BaseExecutor. Represents the flink java executor.
    """
    def __init__(self, java_class: Text) -> None:
        """
        Construct of FlinkJavaExecutor.

        :param java_class: Class which execute the flink job.
        """
        super().__init__("flink_java")
        self.java_class: Text = java_class


class FlinkPythonExecutor(PythonObjectExecutor):
    """
    Implementation of BaseExecutor. Represents the flink python executor.
    """
    def __init__(self, python_object: object, node_id: Text = None) -> None:
        """
        Construct of FlinkPythonExecutor.

        :param python_object: Object includes the python executor.
        :param node_id: Id of node.
        """
        super().__init__(python_object=python_object, node_id=node_id)
        self.python_object: bytes = serialize(python_object)
