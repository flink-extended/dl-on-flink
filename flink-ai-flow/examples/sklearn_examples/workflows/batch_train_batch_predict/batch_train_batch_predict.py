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
from batch_train_batch_predict_executor import ExampleReader, ExampleTransformer, ModelTrainer, EvaluateExampleReader, \
    EvaluateTransformer, ModelEvaluator, ValidateExampleReader, ValidateTransformer, ModelValidator, ModelPusher, \
    PredictExampleReader, PredictTransformer, ModelPredictor, ExampleWriter
from ai_flow.util.path_util import get_file_dir
from ai_flow_plugins.job_plugins import python

EXAMPLE_URI = os.path.abspath(os.path.join(__file__, "../../../..")) + '/example_data/mnist_{}.npz'


def run_workflow():

    af.init_ai_flow_context()
    artifact_prefix = af.current_project_config().get_project_name() + "."
    with af.job_config('train'):
        # Training of model
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

    with af.job_config('evaluate'):
        # Evaluation of model
        evaluate_example = af.register_dataset(name=artifact_prefix + 'evaluate_example',
                                               uri=EXAMPLE_URI.format('evaluate'))
        evaluate_read_example = af.read_dataset(dataset_info=evaluate_example,
                                                read_dataset_processor=EvaluateExampleReader())
        evaluate_transform = af.transform(input=[evaluate_read_example],
                                          transform_processor=EvaluateTransformer())
        # Register disk path used to save evaluate result
        evaluate_artifact_name = artifact_prefix + 'evaluate_artifact'
        evaluate_artifact = af.register_artifact(name=evaluate_artifact_name,
                                                 uri=get_file_dir(__file__) + '/evaluate_result')
        # Evaluate model
        evaluate_channel = af.evaluate(input=[evaluate_transform],
                                       model_info=train_model,
                                       evaluation_processor=ModelEvaluator(evaluate_artifact_name))

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

        # Define relation graph connected by control edge: train -> evaluate -> validate -> push -> predict
        af.action_on_job_status('evaluate', 'train')
        af.action_on_job_status('validate', 'evaluate')
        af.action_on_job_status('push', 'validate')
        af.action_on_job_status('predict', 'push')

    # Run workflow
    af.workflow_operation.submit_workflow(af.current_workflow_config().workflow_name)
    af.workflow_operation.start_new_workflow_execution(af.current_workflow_config().workflow_name)


if __name__ == '__main__':
    run_workflow()
