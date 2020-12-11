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
from typing import Text, Union, List
from ai_flow.common.json_utils import Jsonable
from ai_flow.common.serialization_utils import serialize


class BaseExecutor(Jsonable):
    """
    Base class of executor.
    """
    def __init__(self, executor_type: Text, node_id: Text = None) -> None:
        super().__init__()
        self.executor_type = executor_type
        self.node_id = node_id

    def get_type(self) -> Text:
        return self.executor_type


class PythonObjectExecutor(BaseExecutor):
    """
    Python Object executor.
    """
    def __init__(self, python_object: object, node_id: Text = None) -> None:
        """
        Set the user defined python object as member variables.

        :param python_object: User defined python object.
        :param node_id: Id of node.
        """
        super().__init__("python_object", node_id)
        self.python_object: bytes = serialize(python_object)


class PythonFuncExecutor(BaseExecutor):
    """
    Python function executor.
    """
    def __init__(self, python_func: object, node_id: Text = None) -> None:
        """
        Set the user defined python function as member variables.

        :param python_func: User defined python function.
        :param node_id: Id of node.
        """
        super().__init__("python_func", node_id)
        self.python_func: bytes = serialize(python_func)


class CmdExecutor(BaseExecutor):
    """
    Command line executor.
    """
    def __init__(self, cmd_line: Union[Text, List[Text]], node_id: Text = None) -> None:
        """
        Set the user defined command line as member variables.

        :param cmd_line: User defined command line function
        :param node_id: Id of node.
        """
        super().__init__("cmd", node_id)
        self.cmd_line: Union[Text, List[Text]] = cmd_line
