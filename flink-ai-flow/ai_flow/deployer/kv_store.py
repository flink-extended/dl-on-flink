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
from abc import ABCMeta, abstractmethod
import time


class BaseKVStore(metaclass=ABCMeta):

    @abstractmethod
    def update(self, key, value):
        pass

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def get_value_and_time(self, key):
        pass

    @abstractmethod
    def in_store(self, key)->bool:
        pass


class MemoryKVStore(BaseKVStore):
    def __init__(self) -> None:
        self.store = {}

    def update(self, key, value):
        self.store[key] = (value, time.time())

    def get(self, key):
        if key in self.store:
            return self.store[key][0]
        else:
            return None

    def get_value_and_time(self, key):
        if key in self.store:
            return self.store[key]
        else:
            return None

    def in_store(self, key)->bool:
        return key in self.store
