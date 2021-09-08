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
import ai_flow as af
from ai_flow.util.path_util import get_file_dir
from ai_flow.model_center.entity.model_version_stage import ModelVersionEventType
from flink_sql_workflow_processors import DatasetReader, ModelTrainer, Source, Sink

DATASET_URI = os.path.abspath(os.path.join(__file__, "../../../..")) + '/dataset_data/iris_{}.csv'


def run_workflow():
    # Init project
    af.init_ai_flow_context()

    artifact_prefix = af.current_project_config().get_project_name() + "."
    # Training of model
    with af.job_config('train'):
        # Register metadata of training data(dataset) and read dataset(i.e. training dataset)
        train_dataset = af.register_dataset(name=artifact_prefix + 'train_dataset',
                                            uri=DATASET_URI.format('train'))
        train_read_dataset = af.read_dataset(dataset_info=train_dataset,
                                             read_dataset_processor=DatasetReader())

        # Register model metadata and train model
        train_model = af.register_model(model_name=artifact_prefix + 'KNN',
                                        model_desc='KNN model')
        train_channel = af.train(input=[train_read_dataset],
                                 training_processor=ModelTrainer(),
                                 model_info=train_model)

    # Prediction(Inference) using flink
    with af.job_config('predict'):
        # Read test data and do prediction
        predict_dataset = af.register_dataset(name=artifact_prefix + 'predict_dataset',
                                              uri=DATASET_URI.format('test'))
        predict_read_dataset = af.read_dataset(dataset_info=predict_dataset,
                                               read_dataset_processor=Source())
        # Save prediction result
        write_dataset = af.register_dataset(name=artifact_prefix + 'write_dataset',
                                            uri=get_file_dir(__file__) + '/predict_result')
        af.write_dataset(input=None,
                         dataset_info=write_dataset,
                         write_dataset_processor=Sink(model_name=train_model.name))

    # Define relation graph connected by control edge: train -> validate -> predict
    af.action_on_model_version_event(job_name='predict',
                                     model_version_event_type=ModelVersionEventType.MODEL_GENERATED,
                                     model_name=train_model.name)
    # Submit workflow
    af.workflow_operation.submit_workflow(af.current_workflow_config().workflow_name)
    # Run workflow
    af.workflow_operation.start_new_workflow_execution(af.current_workflow_config().workflow_name)


if __name__ == '__main__':
    run_workflow()