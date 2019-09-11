# Copyright 2019 The flink-ai-extended Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

from pyflink.java_gateway import get_gateway


class TFConfig(object):

    def __init__(self, num_worker, num_ps, python_file, func, properties, env_path, zk_conn, zk_base_path):
        self._num_worker = num_worker
        self._num_ps = num_ps
        self._python_file = python_file
        self._func = func
        self._properties = properties
        self._env_path = env_path
        self._zk_conn = zk_conn
        self._zk_base_path = zk_base_path

    def java_config(self):
        return get_gateway().jvm.com.alibaba.flink.ml.tensorflow.client.TFConfig(self._num_worker,
                                                                                 self._num_ps,
                                                                                 self._properties,
                                                                                 self._python_file,
                                                                                 self._func,
                                                                                 self._env_path)
