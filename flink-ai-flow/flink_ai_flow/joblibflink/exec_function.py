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
import json
import os
import sys

import oss2
import pandas as pd
from py4j.java_gateway import java_import
from pyflink.java_gateway import get_gateway
from pyflink.table import BatchTableEnvironment, EnvironmentSettings, DataTypes
from pyflink.table.udf import udf
from pyflink.util.utils import to_jarray


def get_file_dir(file):
    return os.path.dirname(os.path.abspath(file))


def download_jar():
    bucket = oss2.Bucket(oss2.Auth('xxx', 'xxx'), 'xxx', 'joblib-flink')
    bucket.get_object_to_file('joblib.jar', filename=get_file_dir(__file__) + '/joblib.jar')


def add_jar_to_context_class_loader(file_paths):
    urls = [gateway.jvm.java.io.File(path).toURI().toURL() for path in file_paths]
    classloader = gateway.jvm.java.net.URLClassLoader(to_jarray(gateway.jvm.java.net.URL, urls),
                                                      gateway.jvm.Thread.currentThread().getContextClassLoader())
    gateway.jvm.Thread.currentThread().setContextClassLoader(classloader)


gateway = get_gateway()

download_jar()
add_jar_to_context_class_loader([get_file_dir(__file__) + '/joblib.jar'])
java_import(gateway.jvm, 'org.apache.flink.joblib.TableUtil')


def _execute_func(exec_func, write_func, pickle_func):
    table_env = BatchTableEnvironment.create(
        environment_settings=EnvironmentSettings.new_instance().use_blink_planner().in_batch_mode().build())
    table = table_env.from_elements([(1, 'Joblib')])
    table_env.register_function(exec_func,
                                udf(lambda _: pickle_func[exec_func], DataTypes.BIGINT(), DataTypes.STRING()))
    table = table.select('{}(_1)'.format(exec_func))
    pd.DataFrame({'func': gateway.jvm.TableUtil.collectToList(table._j_table)[0]}, index=[0]).to_csv(write_func,
                                                                                                     index=False)


if __name__ == '__main__':
    _execute_func(sys.argv[1], sys.argv[2], json.loads(sys.argv[3]))
