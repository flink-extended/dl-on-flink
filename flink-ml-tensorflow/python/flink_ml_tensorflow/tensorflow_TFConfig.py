#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from pyflink.java_gateway import get_gateway


class TFConfig(object):

    def __init__(self, num_worker, num_ps, properties, python_file, func, env_path):
        """

        :param num_worker: the number of TF workers
        :param num_ps: the number of TF PS
        :param properties: TF properties
        :param python_file: the python file, the entry python file
        :param func: the entry function name in the first python file
        :param env_path: the path of env
        """
        self._num_worker = num_worker
        self._num_ps = num_ps
        self._properties = properties
        self._python_file = python_file
        self._func = func
        self._env_path = env_path
        self._j_tf_config = None

    def java_config(self):
        if not self._j_tf_config:
            self._j_tf_config = get_gateway().jvm.org.flinkextended.flink.ml.tensorflow.client.TFConfig(self._num_worker,
                                                                                                        self._num_ps,
                                                                                                        self._properties,
                                                                                                        self._python_file,
                                                                                                        self._func,
                                                                                                        self._env_path)
        return self._j_tf_config

    def __eq__(self, other):
        return type(self) is type(other) \
               and self._num_worker == other._num_worker \
               and self._num_ps == other._num_ps \
               and self._properties == other._properties \
               and self._python_file == other._python_file \
               and self._func == other._func \
               and self._env_path == other._env_path
