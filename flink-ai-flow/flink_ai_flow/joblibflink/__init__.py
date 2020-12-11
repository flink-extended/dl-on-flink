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
"""
Joblib Flink backend is extension for Joblib tools, which makes Joblib running on Flink parallelly.
"""


# Register Joblib Flink Parallel backend factory.
def register_flink():
    """
    Register Flink backend into Joblib called with parallel_backend('flink').
    """
    try:
        from .flink_backend import register
        register()
    except ImportError:
        msg = ("To use the flink distributed backend you must install the pyflink and packages."
               "Try to execute `python -m pip install apache-flink`."
               "See https://ci.apache.org/projects/flink for more information.")
        raise ImportError(msg)


__all__ = ['register_flink']
