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
from batch_train_stream_predict_executor import ExampleReader, ExampleTransformer, ModelTrainer, \
    ValidateExampleReader, ValidateTransformer, ModelValidator, ModelPusher, \
    PredictExampleReader, PredictTransformer, ModelPredictor, ExampleWriter

EXAMPLE_URI = os.path.abspath(os.path.join(__file__, "../../../..")) + '/example_data/mnist_{}.npz'


def run_workflow():
    af.init_ai_flow_context()

    artifact_prefix = af.current_project_config().get_project_name() + "."

    # the config of train job is a periodic job  which means it will
    # run every `interval`(defined in workflow_config.yaml) seconds
    with af.job_config('train'):
        # Register metadata raw training data(example) and read example(i.e. training dataset)
        train_example = af.register_dataset(name=artifact_prefix + 'train_example',
                                            uri=EXAMPLE_URI.format('train'))
        train_read_example = af.read_dataset(dataset_info=train_example,
                                             read_dataset_processor=ExampleReader())

        # Transform(preprocessing) example
        train_transform = af.transform(input=[train_read_example],
                                       transform_processor=ExampleTransformer())

        # Register model metadata and train model
        train_model = af.register_model(model_name=artifact_prefix + 'logistic-regression',
                                        model_desc='logistic regression model')
        train_channel = af.train(input=[train_transform],
                                 training_processor=ModelTrainer(),
                                 model_info=train_model)
    with af.job_config('validate'):
        # Validation of model
        # Read validation dataset and validate model before it is used to predict

        validate_example = af.register_dataset(name=artifact_prefix + 'validate_example',
                                               uri=EXAMPLE_URI.format('evaluate'))
        validate_read_example = af.read_dataset(dataset_info=validate_example,
                                                read_dataset_processor=ValidateExampleReader())
        validate_transform = af.transform(input=[validate_read_example],
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
        # Prediction(Inference)
        predict_example = af.register_dataset(name=artifact_prefix + 'predict_example',
                                              uri=EXAMPLE_URI.format('predict'))
        predict_read_example = af.read_dataset(dataset_info=predict_example,
                                               read_dataset_processor=PredictExampleReader())
        predict_transform = af.transform(input=[predict_read_example],
                                         transform_processor=PredictTransformer())
        predict_channel = af.predict(input=[predict_transform],
                                     model_info=train_model,
                                     prediction_processor=ModelPredictor())
        # Save prediction result
        write_example = af.register_dataset(name=artifact_prefix + 'write_example',
                                            uri=get_file_dir(__file__) + '/predict_result')
        af.write_dataset(input=predict_channel,
                         dataset_info=write_example,
                         write_dataset_processor=ExampleWriter())

    # Define relation graph connected by control edge:
    # Once a round of training is done, validator will be launched and
    # pusher will be launched if the new model is better.
    # Prediction will start once the first round of training is done and
    # when pusher pushes(deploys) a new model, the predictor will use the latest deployed model as well.
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
