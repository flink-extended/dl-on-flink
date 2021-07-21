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
from ai_flow.model_center.entity.model_version_stage import ModelVersionEventType
from ai_flow.util.path_util import get_file_dir
from stream_train_stream_predict_executor import TrainDatasetReader, TrainDatasetTransformer, ModelTrainer, \
    ValidateDatasetReader, ValidateTransformer, ModelValidator, ModelPusher, PredictDatasetReader, \
    PredictTransformer, ModelPredictor, DatasetWriter

DATASET_URI = os.path.abspath(os.path.join(__file__, "../../../..")) + '/dataset_data/mnist_{}.npz'


def run_workflow():
    af.init_ai_flow_context()

    artifact_prefix = af.current_project_config().get_project_name() + "."

    with af.job_config('train'):
        # Register metadata raw training data(dataset) and read dataset(i.e. training dataset)
        train_dataset = af.register_dataset(name=artifact_prefix + 'train_dataset',
                                            uri=DATASET_URI.format('train'))
        train_read_dataset = af.read_dataset(dataset_info=train_dataset,
                                             read_dataset_processor=TrainDatasetReader())
        train_transform = af.transform(input=[train_read_dataset],
                                       transform_processor=TrainDatasetTransformer())
        train_model = af.register_model(model_name=artifact_prefix + 'logistic-regression',
                                        model_desc='logistic regression model')
        train_channel = af.train(input=[train_transform],
                                 training_processor=ModelTrainer(),
                                 model_info=train_model)
    with af.job_config('validate'):
        validate_dataset = af.register_dataset(name=artifact_prefix + 'validate_dataset',
                                               uri=DATASET_URI.format('evaluate'))
        validate_read_dataset = af.read_dataset(dataset_info=validate_dataset,
                                                read_dataset_processor=ValidateDatasetReader())
        validate_transform = af.transform(input=[validate_read_dataset],
                                          transform_processor=ValidateTransformer())
        validate_artifact_name = artifact_prefix + 'validate_artifact'
        validate_artifact = af.register_artifact(name=validate_artifact_name,
                                                 uri=get_file_dir(__file__) + '/validate_result')
        validate_channel = af.model_validate(input=[validate_transform],
                                             model_info=train_model,
                                             model_validation_processor=ModelValidator(validate_artifact_name))
    with af.job_config('push'):
        # Push model to serving
        # Register metadata of pushed model
        push_model_artifact_name = artifact_prefix + 'push_model_artifact'
        push_model_artifact = af.register_artifact(name=push_model_artifact_name,
                                                   uri=get_file_dir(__file__) + '/pushed_model')
        af.push_model(model_info=train_model, pushing_model_processor=ModelPusher(push_model_artifact_name))
    with af.job_config('predict'):
        predict_dataset = af.register_dataset(name=artifact_prefix + 'predict_dataset',
                                              uri=DATASET_URI.format('predict'))
        predict_read_dataset = af.read_dataset(dataset_info=predict_dataset,
                                               read_dataset_processor=PredictDatasetReader())
        predict_transform = af.transform(input=[predict_read_dataset],
                                         transform_processor=PredictTransformer())
        predict_channel = af.predict(input=[predict_transform],
                                     model_info=train_model,
                                     prediction_processor=ModelPredictor())
        write_dataset = af.register_dataset(name=artifact_prefix + 'export_dataset',
                                            uri=get_file_dir(__file__) + '/predict_result')
        af.write_dataset(input=predict_channel,
                         dataset_info=write_dataset,
                         write_dataset_processor=DatasetWriter())

    af.action_on_model_version_event(job_name='validate',
                                     model_version_event_type=ModelVersionEventType.MODEL_GENERATED,
                                     model_name=train_model.name)
    af.action_on_model_version_event(job_name='push',
                                     model_version_event_type=ModelVersionEventType.MODEL_VALIDATED,
                                     model_name=train_model.name)

    # Run workflow
    af.workflow_operation.submit_workflow(af.current_workflow_config().workflow_name)
    af.workflow_operation.start_new_workflow_execution(af.current_workflow_config().workflow_name)


if __name__ == '__main__':
    run_workflow()
