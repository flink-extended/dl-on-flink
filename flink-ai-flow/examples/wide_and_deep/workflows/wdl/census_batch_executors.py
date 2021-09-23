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
from pyflink.dataset import ExecutionEnvironment

import ai_flow as af
from typing import List
import pandas as pd
from sklearn.utils import shuffle
from flink_ml_tensorflow.tensorflow_TFConfig import TFConfig
from flink_ml_tensorflow.tensorflow_on_flink_mlconf import MLCONSTANTS
from flink_ml_tensorflow.tensorflow_on_flink_table import train
from ai_flow.client.ai_flow_client import get_ai_flow_client
from ai_flow.util.path_util import get_file_dir
from ai_flow_plugins.job_plugins.flink import FlinkPythonProcessor, ExecutionContext, FlinkEnv
from ai_flow_plugins.job_plugins.python import PythonProcessor
from ai_flow_plugins.job_plugins.python.python_processor import ExecutionContext as PyExecutionContext
from pyflink.table import EnvironmentSettings, Table, BatchTableEnvironment, TableConfig
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from notification_service.base_notification import DEFAULT_NAMESPACE, BaseEvent
from census_common import get_accuracy_score


class BatchTableEnvCreator(FlinkEnv):

    def create_env(self):
        batch_env = ExecutionEnvironment.get_execution_environment()
        batch_env.set_parallelism(1)
        t_config = TableConfig()
        t_env = BatchTableEnvironment.create(
            batch_env,
            t_config
        )
        statement_set = t_env.create_statement_set()
        t_env.get_config().set_python_executable('python')
        t_env.get_config().get_configuration().set_boolean('python.fn-execution.memory.managed', True)
        return batch_env, t_env, statement_set


class BatchPreprocessExecutor(PythonProcessor):

    def process(self, execution_context: PyExecutionContext, input_list: List) -> List:
        data_path = '/tmp/census_data/adult.data'
        df = pd.read_csv(data_path, header=None)
        df = shuffle(df)
        df.to_csv('/tmp/census_data/adult.data', index=False, header=None)
        print("Preprocess Done")
        get_ai_flow_client().send_event(BaseEvent(key='wide_and_deep_base', value='BATCH_PREPROCESS',
                                                  event_type='BATCH_PREPROCESS',
                                                  namespace=DEFAULT_NAMESPACE))
        return []


class BatchTrainExecutor(FlinkPythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        work_num = 2
        ps_num = 1
        python_file = 'census_distribute.py'
        func = 'batch_map_func'
        prop = {MLCONSTANTS.PYTHON_VERSION: '', MLCONSTANTS.CONFIG_STORAGE_TYPE: MLCONSTANTS.STORAGE_ZOOKEEPER,
                MLCONSTANTS.CONFIG_ZOOKEEPER_CONNECT_STR: 'localhost:2181',
                MLCONSTANTS.CONFIG_ZOOKEEPER_BASE_PATH: '/demo',
                MLCONSTANTS.REMOTE_CODE_ZIP_FILE: 'hdfs://localhost:9000/demo/code.zip'}
        env_path = None

        input_tb = None
        output_schema = None

        tf_config = TFConfig(work_num, ps_num, prop, python_file, func, env_path)

        train(execution_context.execution_env, execution_context.table_env, execution_context.statement_set,
              input_tb, tf_config, output_schema)
        return []


class BatchEvaluateExecutor(PythonProcessor):
    def __init__(self):
        super().__init__()
        self.path = None
        self.model_version = None
        self.model_name = None

    def open(self, execution_context: PyExecutionContext):
        self.model_name = execution_context.config.get('model_info').name
        self.model_version = af.get_latest_generated_model_version(self.model_name)
        print("#### name {}".format(self.model_name))
        print("#### path {}".format(self.model_version.model_path))
        self.path = self.model_version.model_path.split('|')[1]

    def process(self, execution_context: PyExecutionContext, input_list: List) -> List:
        test_data = '/tmp/census_data/adult.evaluate'
        score = get_accuracy_score(self.path, test_data)
        path = get_file_dir(__file__) + '/batch_evaluate_result'
        with open(path, 'a') as f:
            f.write(str(score) + '  -------->  ' + self.model_version.version)
            f.write('\n')
        return []


def _write_result_to_file(path, content):
    with open(path, 'a') as f:
        f.write(content)
        f.write('\n')


class BatchValidateExecutor(PythonProcessor):
    def __init__(self):
        super().__init__()
        self.path = None
        self.model_version = None
        self.model_name = None

    def open(self, execution_context: PyExecutionContext):
        self.model_name = execution_context.config.get("model_info").name
        self.model_version = af.get_latest_generated_model_version(self.model_name)
        print("#### name {}".format(self.model_name))
        print("#### path {}".format(self.model_version.model_path))
        print("#### ver {}".format(self.model_version.version))
        self.path = self.model_version.model_path.split('|')[1]

    def process(self, execution_context: PyExecutionContext, input_list: List) -> List:
        test_data = '/tmp/census_data/adult.validate'
        score = get_accuracy_score(self.path, test_data)

        path = get_file_dir(__file__) + '/batch_validate_result'
        _write_result_to_file(path, str(score) + '  -------->  ' + self.model_version.version)
        validated_version = af.get_latest_validated_model_version(self.model_name)

        if validated_version is not None:
            validated_version_score = get_accuracy_score(validated_version.model_path.split('|')[1], test_data)
            if score > validated_version_score:
                af.update_model_version(model_name=self.model_name,
                                        model_version=validated_version.version,
                                        current_stage=ModelVersionStage.DEPRECATED)
                af.update_model_version(model_name=self.model_name,
                                        model_version=self.model_version.version,
                                        current_stage=ModelVersionStage.VALIDATED)
                print("#### old version[{}] score: {} new version[{}] score: {}".format(validated_version.version,
                                                                                        validated_version_score,
                                                                                        self.model_version.version,
                                                                                        score))
                _write_result_to_file(path, 'version {} pass validation.'.format(self.model_version.version))
            else:
                _write_result_to_file(path, 'version {} does not pass validation.'.format(self.model_version.version))
        else:
            af.update_model_version(model_name=self.model_name,
                                    model_version=self.model_version.version,
                                    current_stage=ModelVersionStage.VALIDATED)
            print("#### init version[{}]".format(self.model_version.version))
            _write_result_to_file(path, 'version {} pass validation.'.format(self.model_version.version))
        return []
