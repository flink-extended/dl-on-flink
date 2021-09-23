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
import distutils.util
import os
import sys

import ai_flow as af
from ai_flow.model_center.entity.model_version_stage import ModelVersionEventType
from ai_flow_plugins.job_plugins import flink as flink_job
from ai_flow_plugins.job_plugins.flink import FlinkJavaProcessor
from cencus_stream_predict_executors import StreamPredictSource, StreamPredictExecutor, StreamPredictSink, \
    StreamPredictPreprocessSource, StreamPredictPreprocessExecutor, StreamPredictPreprocessSink
from cencus_stream_train_executors import StreamPreprocessExecutor, StreamValidateExecutor, StreamPushExecutor, \
    StreamTrainExecutor, StreamTrainSource, StreamTableEnvCreator, StreamPreprocessSource, StreamPreprocessSink
from census_batch_executors import BatchPreprocessExecutor, BatchTrainExecutor, BatchEvaluateExecutor, \
    BatchValidateExecutor


def batch_jobs():
    """Batch Jobs"""
    batch_model_info = af.get_model_by_name('wide_and_deep_base')
    with af.job_config(job_name='census_batch_preprocess'):
        batch_preprocess_channel = af.user_define_operation(input_data_list=[],
                                                            processor=BatchPreprocessExecutor(),
                                                            name='census_batch_preprocess')
    with af.job_config(job_name='census_batch_train'):
        batch_train_channel = af.train(input=[],
                                       training_processor=BatchTrainExecutor(),
                                       model_info=batch_model_info, name='census_batch_train')

    with af.job_config(job_name='census_batch_evaluate'):
        batch_evaluate_channel = af.evaluate(input=[],
                                             evaluation_processor=BatchEvaluateExecutor(),
                                             model_info=batch_model_info, name='census_batch_evaluate')
    with af.job_config(job_name='census_batch_validate'):
        batch_validate_channel = af.model_validate(input=[],
                                                   model_validation_processor=BatchValidateExecutor(),
                                                   model_info=batch_model_info, name='census_batch_validate')


def stream_train():
    """Stream Train Jobs"""
    stream_preprocess_input = af.get_dataset_by_name('stream_preprocess_input')
    stream_train_input = af.get_dataset_by_name('stream_train_input')

    stream_model_info = af.get_model_by_name('wide_and_deep')
    with af.job_config(job_name='census_stream_preprocess_train'):
        stream_preprocess_source = af.read_dataset(dataset_info=stream_preprocess_input,
                                                   read_dataset_processor=StreamPreprocessSource())
        stream_preprocess_channel = af.user_define_operation(input=[stream_preprocess_source],
                                                             processor=StreamPreprocessExecutor(),
                                                             name='census_stream_preprocess')
        af.write_dataset(input=stream_preprocess_channel,
                         dataset_info=stream_train_input,
                         write_dataset_processor=StreamPreprocessSink())

    with af.job_config(job_name='census_stream_train'):
        stream_train_source = af.read_dataset(dataset_info=stream_train_input,
                                              read_dataset_processor=StreamTrainSource())
        stream_train_channel = af.train(input=[stream_train_source],
                                        model_info=stream_model_info,
                                        training_processor=StreamTrainExecutor())

    with af.job_config(job_name='census_stream_validate'):
        stream_validate_channel = af.model_validate(input=[],
                                                    model_validation_processor=StreamValidateExecutor(),
                                                    model_info=stream_model_info, name='census_stream_validate')
    with af.job_config(job_name='census_stream_push'):
        af.push_model(pushing_model_processor=StreamPushExecutor(),
                      model_info=stream_model_info, name='census_stream_push')


def stream_prediction(use_jar_preprocess):
    """Stream Prediction Jobs"""
    stream_preprocess_input = af.get_dataset_by_name('stream_preprocess_input')
    stream_predict_input = af.get_dataset_by_name('stream_predict_input')
    stream_predict_output = af.get_dataset_by_name('stream_predict_output')

    stream_model_info = af.get_model_by_name('wide_and_deep')
    with af.job_config(job_name='census_stream_preprocess_predict'):
        if use_jar_preprocess:
            preprocess_jar_filename = "wdl-preprocess-0.1-SNAPSHOT.jar"
            check_jar_dependencies(preprocess_jar_filename)
            af.user_define_operation(processor=FlinkJavaProcessor(entry_class="org.aiflow.StreamPredictPreprocess",
                                                                  main_jar_file=preprocess_jar_filename,
                                                                  args=["localhost:9092",
                                                                        "census_input_preprocess_topic",
                                                                        "census_predict_input_topic"]))
        else:
            stream_predict_preprocess_source = af.read_dataset(dataset_info=stream_preprocess_input,
                                                               read_dataset_processor=StreamPredictPreprocessSource())
            stream_predict_preprocess_channel = af.user_define_operation(
                input=[stream_predict_preprocess_source],
                processor=StreamPredictPreprocessExecutor(),
                name='census_stream_predict_preprocess')
            af.write_dataset(input=stream_predict_preprocess_channel,
                             dataset_info=stream_predict_input,
                             write_dataset_processor=StreamPredictPreprocessSink())

    with af.job_config(job_name='census_stream_predict'):
        stream_predict_source = af.read_dataset(dataset_info=stream_predict_input,
                                                read_dataset_processor=StreamPredictSource())
        stream_predict_channel = af.predict(input=[stream_predict_source],
                                            model_info=stream_model_info,
                                            prediction_processor=StreamPredictExecutor())
        af.write_dataset(input=stream_predict_channel,
                         dataset_info=stream_predict_output,
                         write_dataset_processor=StreamPredictSink())


def check_jar_dependencies(jar_filename):
    jar_path = os.path.join(af.current_project_context().get_dependencies_path(), "jar", jar_filename)
    if not os.path.exists(jar_path):
        print("{} doesn't exist! \n"
              "Please put the jar in dependencies/jar".format(jar_path))
        exit(-1)


def run_workflow(use_jar_preprocess):
    af.init_ai_flow_context()
    flink_job.set_flink_env(env=StreamTableEnvCreator())
    batch_jobs()
    stream_train()
    stream_prediction(use_jar_preprocess)

    af.action_on_job_status(job_name='census_batch_train', upstream_job_name='census_batch_preprocess')
    af.action_on_job_status(job_name='census_batch_evaluate', upstream_job_name='census_batch_train')
    af.action_on_job_status(job_name='census_batch_validate', upstream_job_name='census_batch_evaluate')

    af.action_on_model_version_event(job_name='census_stream_train',
                                     model_name='wide_and_deep_base',
                                     namespace='default',
                                     model_version_event_type=ModelVersionEventType.MODEL_VALIDATED)

    af.action_on_model_version_event(job_name='census_stream_validate',
                                     model_name='wide_and_deep',
                                     namespace='default',
                                     model_version_event_type=ModelVersionEventType.MODEL_GENERATED)

    af.action_on_model_version_event(job_name='census_stream_push',
                                     model_name='wide_and_deep',
                                     namespace='default',
                                     model_version_event_type=ModelVersionEventType.MODEL_VALIDATED)

    af.action_on_model_version_event(job_name='census_stream_predict',
                                     model_name='wide_and_deep',
                                     namespace='default',
                                     model_version_event_type=ModelVersionEventType.MODEL_DEPLOYED)

    # Run workflow
    af.workflow_operation.stop_all_workflow_executions(af.current_workflow_config().workflow_name)
    af.workflow_operation.submit_workflow(af.current_workflow_config().workflow_name)
    workflow_execution = af.workflow_operation.start_new_workflow_execution(af.current_workflow_config().workflow_name)
    print(workflow_execution)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        use_jar_preprocess = False
    else:
        use_jar_preprocess = bool(distutils.util.strtobool(sys.argv[1]))
    run_workflow(use_jar_preprocess)
