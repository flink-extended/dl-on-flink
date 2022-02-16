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
import argparse
import logging
import os
import sys
from datetime import datetime

from dl_on_flink_tensorflow.tensorflow_TFConfig import TFConfig
from dl_on_flink_tensorflow.tensorflow_on_flink_mlconf import MLCONSTANTS
from dl_on_flink_tensorflow.tensorflow_on_flink_table import train
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

logger = logging.getLogger(__file__)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format="%(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model-path',
        dest='model_path',
        required=False,
        default=f"/tmp/linear/{datetime.now().strftime('%Y%m%d%H%M')}",
        help='Where the trained model should be saved')
    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)

    model_save_path = known_args.model_path
    logger.info("Model will be saved at: {}".format(model_save_path))

    # Prepare Flink environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    t_env = StreamTableEnvironment.create(env)
    statement_set = t_env.create_statement_set()

    python_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'linear.py')

    # Create the table of samples for model training
    t_env.execute_sql("""
        CREATE TABLE src (
            x FLOAT
        ) WITH (
            'connector' = 'datagen',
            'number-of-rows' = '512000',
            'fields.x.min' = '0',
            'fields.x.max' = '1'
        )
    """)
    input_tb = t_env.sql_query("SELECT x, 2*x+1 FROM src")

    prop = {
        MLCONSTANTS.ENCODING_CLASS:
            "org.flinkextended.flink.ml.operator.coding.RowCSVCoding",
        MLCONSTANTS.DECODING_CLASS:
            "org.flinkextended.flink.ml.operator.coding.RowCSVCoding",
        'sys:csv_encode_types': 'STRING,STRING',
        'model_save_path': model_save_path,
        MLCONSTANTS.CONFIG_STORAGE_TYPE: MLCONSTANTS.STORAGE_LOCAL_FILE,
    }

    tf_config = TFConfig(num_worker=2, num_ps=0, properties=prop,
                         python_file=python_file, func="stream_train",
                         env_path=None)
    train(env, t_env, statement_set,
          input_table=input_tb, tf_config=tf_config, output_schema=None)

    # Submit the job. Note that you should call execute method on the
    # statement_set.
    job_client = statement_set.execute().get_job_client()
    if job_client is not None:
        job_client.get_job_execution_result().result()
