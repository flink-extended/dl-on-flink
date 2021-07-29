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
import os
import pandas as pd
import time
from typing import List
from joblib import dump, load

import ai_flow as af
from pyflink.table.udf import udf
from pyflink.table import Table, ScalarFunction, DataTypes
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from ai_flow.util.path_util import get_file_dir
from ai_flow_plugins.job_plugins.python.python_processor import ExecutionContext, PythonProcessor
from ai_flow_plugins.job_plugins import flink
from sklearn.neighbors import KNeighborsClassifier

EXAMPLE_COLUMNS = ['sl', 'sw', 'pl', 'pw', 'type']
flink.set_flink_env(flink.FlinkStreamEnv())


class DatasetReader(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        """
        Read dataset using pandas
        """
        # Gets the registered dataset meta info
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        # Read the file using pandas
        train_data = pd.read_csv(dataset_meta.uri, header=0, names=EXAMPLE_COLUMNS)
        # Prepare dataset
        y_train = train_data.pop(EXAMPLE_COLUMNS[4])
        return [[train_data.values, y_train.values]]


class ModelTrainer(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        """
        Train and save KNN model
        """
        model_meta: af.ModelMeta = execution_context.config.get('model_info')
        clf = KNeighborsClassifier(n_neighbors=5)
        x_train, y_train = input_list[0][0], input_list[0][1]
        clf.fit(x_train, y_train)

        # Save model to local
        model_path = get_file_dir(__file__) + '/saved_model'
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        model_timestamp = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())
        model_path = model_path + '/' + model_timestamp
        dump(clf, model_path)
        af.register_model_version(model=model_meta, model_path=model_path)
        return []


class ValidateDatasetReader(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        """
        Read test dataset
        """
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        x_test = pd.read_csv(dataset_meta.uri, header=0, names=EXAMPLE_COLUMNS)
        y_test = x_test.pop(EXAMPLE_COLUMNS[4])
        return [[x_test, y_test]]


class ModelValidator(PythonProcessor):

    def __init__(self, artifact):
        super().__init__()
        self.artifact = artifact

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        """
        Validate and deploy model if necessary
        """
        current_model_meta: af.ModelMeta = execution_context.config.get('model_info')
        deployed_model_version = af.get_deployed_model_version(model_name=current_model_meta.name)
        new_model_meta = af.get_latest_generated_model_version(current_model_meta.name)
        uri = af.get_artifact_by_name(self.artifact).uri
        if deployed_model_version is None:
            # If there is no deployed model for now, update the current generated model to be deployed.
            af.update_model_version(model_name=current_model_meta.name,
                                    model_version=new_model_meta.version,
                                    current_stage=ModelVersionStage.VALIDATED)
            af.update_model_version(model_name=current_model_meta.name,
                                    model_version=new_model_meta.version,
                                    current_stage=ModelVersionStage.DEPLOYED)
        else:
            x_validate = input_list[0][0]
            y_validate = input_list[0][1]
            knn = load(new_model_meta.model_path)
            scores = knn.score(x_validate, y_validate)
            deployed_knn = load(deployed_model_version.model_path)
            deployed_scores = deployed_knn.score(x_validate, y_validate)

            with open(uri, 'a') as f:
                f.write(
                    'deployed model version: {} scores: {}\n'.format(deployed_model_version.version, deployed_scores))
                f.write('generated model version: {} scores: {}\n'.format(new_model_meta.version, scores))
            if scores >= deployed_scores:
                # Deprecate current model and deploy better new model
                af.update_model_version(model_name=current_model_meta.name,
                                        model_version=deployed_model_version.version,
                                        current_stage=ModelVersionStage.DEPRECATED)
                af.update_model_version(model_name=current_model_meta.name,
                                        model_version=new_model_meta.version,
                                        current_stage=ModelVersionStage.VALIDATED)
                af.update_model_version(model_name=current_model_meta.name,
                                        model_version=new_model_meta.version,
                                        current_stage=ModelVersionStage.DEPLOYED)
        return []


class Source(flink.FlinkPythonProcessor):
    def process(self, execution_context: flink.ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        """
        Flink source reader that reads local file
        """
        data_meta = execution_context.config['dataset']
        t_env = execution_context.table_env
        t_env.execute_sql('''
            CREATE TABLE predict_source (
                sl FLOAT,
                sw FLOAT,
                pl FLOAT,
                pw FLOAT,
                type FLOAT
            ) WITH (
                'connector' = 'filesystem',
                'path' = '{uri}',
                'format' = 'csv',
                'csv.ignore-parse-errors' = 'true'
            )
        '''.format(uri=data_meta.uri))
        table = t_env.from_path('predict_source')
        return [table]


class Predictor(flink.FlinkPythonProcessor):
    def __init__(self):
        super().__init__()
        self.model_name = None

    def open(self, execution_context: flink.ExecutionContext):
        self.model_name = execution_context.config['model_info'].name

    def process(self, execution_context: flink.ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        """
        Use pyflink udf to do prediction
        """
        model_meta = af.get_deployed_model_version(self.model_name)
        model_path = model_meta.model_path
        clf = load(model_path)

        # Define the python udf

        class Predict(ScalarFunction):
            def eval(self, sl, sw, pl, pw):
                records = [[sl, sw, pl, pw]]
                df = pd.DataFrame.from_records(records, columns=['sl', 'sw', 'pl', 'pw'])
                return clf.predict(df)[0]

        # Register the udf in flink table env, so we can call it later in SQL statement
        execution_context.table_env.register_function('mypred',
                                                      udf(f=Predict(),
                                                          input_types=[DataTypes.FLOAT(), DataTypes.FLOAT(),
                                                                       DataTypes.FLOAT(), DataTypes.FLOAT()],
                                                          result_type=DataTypes.FLOAT()))
        return [input_list[0].select("mypred(sl,sw,pl,pw)")]


class Sink(flink.FlinkPythonProcessor):

    def process(self, execution_context: flink.ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        """
        Sink Flink Table produced by Predictor to local file
        """
        table_env = execution_context.table_env
        table_env.execute_sql('''
           CREATE TABLE predict_sink (
               prediction FLOAT 
           ) WITH (
               'connector' = 'filesystem',
               'path' = '{uri}',
               'format' = 'csv',
               'csv.ignore-parse-errors' = 'true'
           )
       '''.format(uri=execution_context.config['dataset'].uri))
        execution_context.statement_set.add_insert("predict_sink", input_list[0])
