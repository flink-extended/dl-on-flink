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
from typing import List
from abc import ABC, abstractmethod
from ai_flow.udf.function_context import FunctionContext


class Executor(ABC):
    """
    Base class for user-defined functions.
    """
    def __init__(self) -> None:
        super().__init__()

    """
    Execute method for user-defined function. User write their code logic in this method.
    """

    @abstractmethod
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        pass

    """
    Setup method for user-defined function. It can be used for initialization work.
    By default, this method does nothing.
    """

    def setup(self, function_context: FunctionContext):
        pass

    """
    Tear-down method for user-defined function. It can be used for clean up work.
    By default, this method does nothing.
    """

    def close(self, function_context: FunctionContext):
        pass


class ExampleExecutor(Executor, ABC):
    """
    Base class for user-defined functions. ExampleExecutor is used in Example Operator.
    Inherited from Executor, add example meta to context.
    """
    def __init__(self) -> None:
        super().__init__()
        self.example_meta = None


ExecutorClass = type(Executor)

TransformerClass = type(Executor)

TrainerClass = type(Executor)

PredictorClass = type(Executor)

EvaluatorClass = type(Executor)
