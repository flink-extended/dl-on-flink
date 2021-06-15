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
from ai_flow.util.json_utils import Jsonable


class AbstractEngine(Jsonable):
    """
    ai flow job must run by one engine, such as python bash etc.
    """

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def engine() -> Text:
        """
        :return platform name:
        """
        raise NotImplementedError("not implement engine")


class CMDEngine(AbstractEngine):
    @staticmethod
    def engine() -> Text:
        return 'cmd_line'


class DummyEngine(AbstractEngine):
    @staticmethod
    def engine() -> Text:
        return 'dummy'
