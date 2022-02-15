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

import glob
import os

from pyflink.util.java_utils import add_jars_to_context_class_loader


def find_jar_path():
    target_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "target")
    paths = glob.glob(os.path.join(target_dir, "dl-on-flink-tensorflow-*-jar-with-dependencies.jar"))
    if len(paths) < 1:
        raise RuntimeError("Cannot find dl-on-flink-tensorflow jar, please make sure you have run `mvn package`")
    elif len(paths) >= 2:
        raise RuntimeError("Found more than one dl-on-flink-tensorflow jar {}".format(paths))
    # logger.info("Found dl-on-flink-tensorflow jar at {}".format(paths[0]))
    return paths[0]


add_jars_to_context_class_loader(["file://{}".format(find_jar_path())])

import logging
import shutil
import time
import unittest

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes, Table, TableDescriptor, Schema

from flink_ml_tensorflow.tensorflow_TFConfig import TFConfig
from flink_ml_tensorflow.tensorflow_on_flink_ml import TensorflowEstimator, TensorflowModel
from flink_ml_tensorflow.tensorflow_on_flink_mlconf import MLCONSTANTS

logger = logging.getLogger(__name__)


class TestFlinkMlApi(unittest.TestCase):

    def setUp(self) -> None:
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.set_parallelism(1)
        self.env.add_jars("file://{}".format(find_jar_path()))
        self.t_env = StreamTableEnvironment.create(self.env)
        self.source_table = self.t_env.from_descriptor(TableDescriptor
                                                       .for_connector("datagen")
                                                       .schema(Schema.new_builder()
                                                               .column("x", DataTypes.INT())
                                                               .column("a", DataTypes.INT())
                                                               .build())
                                                       .option("fields.x.kind", "sequence")
                                                       .option("fields.x.start", "1")
                                                       .option("fields.x.end", "100")
                                                       .option("fields.a.kind", "sequence")
                                                       .option("fields.a.start", "101")
                                                       .option("fields.a.end", "200")
                                                       .build())

    @staticmethod
    def get_tf_config() -> TFConfig:
        work_num = 1
        ps_num = 1
        prop = {MLCONSTANTS.PYTHON_VERSION: '',
                MLCONSTANTS.ENCODING_CLASS: 'org.flinkextended.flink.ml.operator.coding.RowCSVCoding',
                MLCONSTANTS.DECODING_CLASS: 'org.flinkextended.flink.ml.operator.coding.RowCSVCoding',
                'sys:csv_encode_types': 'STRING'}
        tf_config = TFConfig(work_num, ps_num, prop, os.path.join(os.path.dirname(__file__), "add_one.py"),
                             "flink_stream_train", None)
        return tf_config

    def execute_and_verify_transformed_table(self, table: Table):
        with table.execute().collect() as results:
            for result in results:
                self.assertTrue(result[0] + 1 == int(result[2]))

    def test_tensorflow_estimator_save_load(self):
        tf_config = self.get_tf_config()
        tensorflow = TensorflowEstimator(tf_config, ["y"], [DataTypes.FLOAT()])
        estimator_save_path = os.path.join(os.path.dirname(__file__), "../estimator", str(time.time()))
        tensorflow.save(estimator_save_path)

        loaded_tensorflow = TensorflowEstimator.load(self.env, estimator_save_path)
        self.assertEqual(tensorflow, loaded_tensorflow)

        shutil.rmtree(estimator_save_path, ignore_errors=True)

    def test_fit_save_load_transform(self):
        tf_config = self.get_tf_config()
        tensorflow = TensorflowEstimator(tf_config, ["y"], [DataTypes.FLOAT()])
        model = tensorflow.fit(self.source_table)

        model_path = os.path.join(os.path.dirname(__file__), "model", str(time.time()))
        model.save(model_path)
        model.statement_set.execute().wait()
        self.assertTrue(os.path.isdir(model_path))
        self.assertTrue(os.path.isdir(os.path.join(model_path, "model_data")))

        loaded_model = TensorflowModel.load(self.env, model_path)
        self.execute_and_verify_transformed_table(loaded_model.transform(self.source_table)[0])

        shutil.rmtree(model_path, ignore_errors=True)

    def test_fit_transform(self):
        tf_config = self.get_tf_config()
        tensorflow = TensorflowEstimator(tf_config, ["y"], [DataTypes.FLOAT()])
        model = tensorflow.fit(self.source_table)
        model_path = os.path.join(os.path.dirname(__file__), "model", str(time.time()))
        model.save(model_path)
        model.statement_set.execute().wait()

        self.execute_and_verify_transformed_table(model.transform(self.source_table)[0])

        shutil.rmtree(model_path, ignore_errors=True)
