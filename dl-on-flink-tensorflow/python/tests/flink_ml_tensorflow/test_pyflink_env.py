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
import os.path
import unittest

from dl_on_flink_framework.context import Context
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

from dl_on_flink_tensorflow.tf_cluster_config import TFClusterConfig
from dl_on_flink_tensorflow.tf_utils import train

test_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
archive_path = os.path.join(test_folder, "sample.zip")
python_file_path = os.path.join(test_folder, "file.py")
zipped_python_file_path = os.path.join(test_folder, "file.zip")
requirements_file_path = os.path.join(test_folder, "requirements.txt")


def verify_zipped_archive(context: Context):
    path = "sample.zip/sample.csv"
    print(f"checking if {os.path.abspath(path)} exists")
    assert os.path.exists(path)


def verify_added_python_file(context: Context):
    from file import my_func
    assert my_func()


def verify_sklearn_installed(context: Context):
    import sklearn
    print(sklearn.show_versions())


class TestPyFlinkEnv(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        from tests.flink_ml_tensorflow.utils import add_dl_on_flink_jar
        add_dl_on_flink_jar()
        super().setUpClass()

    def setUp(self) -> None:
        super().setUp()
        from tests.flink_ml_tensorflow.utils import find_jar_path
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.add_jars("file://{}".format(find_jar_path()))
        self.env.set_parallelism(1)
        self.t_env = StreamTableEnvironment.create(self.env)
        self.statement_set = self.t_env.create_statement_set()

    def test_add_zipped_archive(self):
        self.t_env.add_python_archive(archive_path)

        config = TFClusterConfig.new_builder().set_worker_count(1) \
            .set_node_entry(verify_zipped_archive).build()

        train(self.statement_set, config)
        self.statement_set.execute().wait()

    def test_add_python_files(self):
        self.t_env.add_python_file(python_file_path)

        config = TFClusterConfig.new_builder().set_worker_count(1) \
            .set_node_entry(verify_added_python_file).build()

        train(self.statement_set, config)
        self.statement_set.execute().wait()

    def test_add_zipped_python_file(self):
        self.t_env.add_python_file(zipped_python_file_path)

        config = TFClusterConfig.new_builder().set_worker_count(1) \
            .set_node_entry(verify_added_python_file).build()

        train(self.statement_set, config)
        self.statement_set.execute().wait()

    def test_requirements(self):
        self.t_env.set_python_requirements(requirements_file_path)

        config = TFClusterConfig.new_builder().set_worker_count(1) \
            .set_node_entry(verify_sklearn_installed).build()

        train(self.statement_set, config)
        self.statement_set.execute().wait()
