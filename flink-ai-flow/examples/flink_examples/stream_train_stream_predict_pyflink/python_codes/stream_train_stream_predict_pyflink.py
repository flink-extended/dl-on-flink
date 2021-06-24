from ai_flow import ExecutionMode, ExampleSupportType, BaseJobConfig, PythonObjectExecutor, ModelType, \
    ArtifactMeta
from ai_flow.common.scheduler_type import SchedulerType

from ai_flow.model_center.entity.model_version_stage import ModelVersionEventType
from flink_ai_flow import FlinkPythonExecutor
from flink_ai_flow import LocalFlinkJobConfig
from stream_train_stream_predict_pyflink_executor import *

EXAMPLE_URI = os.path.abspath(os.path.join(__file__, "../../../..")) + '/example_data/iris_{}.csv'


def get_project_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_pyflink_project(project_root_path):
    af.set_project_config_file(get_project_path() + '/project.yaml')
    project_name = af.project_config().get_project_name()
    artifact_prefix = project_name + "."
    with af.global_config_file(config_path=get_project_path() + '/resources/workflow_config.yaml'):
        with af.config('train_job'):
            # Training of model
            # Register metadata raw training data(example) and read example(i.e. training dataset)
            train_example = af.register_example(name='train_example',
                                                support_type=ExampleSupportType.EXAMPLE_STREAM,
                                                stream_uri=EXAMPLE_URI.format('train'),
                                                data_format='csv')
            train_model = af.register_model(model_name='iris_model',
                                            model_type=ModelType.SAVED_MODEL,
                                            model_desc='A KNN model')
            train_read_example_channel = af.read_example(example_info=train_example,
                                                         executor=PythonObjectExecutor(
                                                             python_object=ReadTrainExample.LoadTrainExample()))
            train_channel = af.train(input_data_list=[train_read_example_channel],
                                     executor=PythonObjectExecutor(python_object=TrainModel()),
                                     model_info=train_model)
        with af.config('eval_job'):
            # Evaluation of model
            evaluate_example = af.register_example(name='evaluate_example',
                                                   support_type=ExampleSupportType.EXAMPLE_STREAM,
                                                   data_format='csv',
                                                   batch_uri=EXAMPLE_URI.format('test'),
                                                   stream_uri=EXAMPLE_URI.format('test'))
            evaluate_example_channel = af.read_example(example_info=evaluate_example,
                                                       executor=PythonObjectExecutor(python_object=TestExampleReader()))
            evaluate_result = get_file_dir(__file__) + '/evaluate_result'
            if os.path.exists(evaluate_result):
                os.remove(evaluate_result)
            evaluate_artifact: ArtifactMeta = af.register_artifact(name='evaluate_artifact',
                                                                   batch_uri=evaluate_result,
                                                                   stream_uri=evaluate_result)
            evaluate_channel = af.evaluate(input_data_list=[evaluate_example_channel], model_info=train_model,
                                           executor=PythonObjectExecutor(python_object=EvaluateModel()))

        with af.config('validate_job'):
            # Validation of model
            # Read validation dataset and validate model before it is used to predict

            validate_example = af.register_example(name='validate_example',
                                                   support_type=ExampleSupportType.EXAMPLE_STREAM,
                                                   data_format='csv',
                                                   batch_uri=EXAMPLE_URI.format('test'),
                                                   stream_uri=EXAMPLE_URI.format('test'))
            validate_example_channel = af.read_example(example_info=validate_example,
                                                       executor=PythonObjectExecutor(python_object=TestExampleReader()))
            validate_result = get_file_dir(__file__) + '/validate_result'
            if os.path.exists(validate_result):
                os.remove(validate_result)
            validate_artifact: ArtifactMeta = af.register_artifact(name='validate_artifact',
                                                                   batch_uri=validate_result,
                                                                   stream_uri=validate_result)
            validate_channel = af.model_validate(input_data_list=[validate_example_channel], model_info=train_model,
                                                 executor=PythonObjectExecutor(python_object=ValidateModel()))
        workflow_config = af.default_af_job_context().global_workflow_config
        flink_config : LocalFlinkJobConfig = workflow_config.job_configs['predict_job']
        flink_config.set_table_env_create_func(StreamTableEnvCreator())
        with af.config(config=flink_config):
            # Prediction(Inference)
            predict_example = af.register_example(name='predict_example',
                                                  support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                  batch_uri=EXAMPLE_URI.format('test'),
                                                  stream_uri=EXAMPLE_URI.format('test'),
                                                  data_format='csv')
            predict_read_example = af.read_example(example_info=predict_example,
                                                   executor=FlinkPythonExecutor(python_object=Source()))
            predict_channel = af.predict(input_data_list=[predict_read_example],
                                         model_info=train_model,
                                         executor=FlinkPythonExecutor(python_object=Transformer()))

            write_example = af.register_example(name='write_example',
                                                support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                batch_uri=get_file_dir(
                                                    __file__) + '/predict_model.csv',
                                                stream_uri=get_file_dir(
                                                    __file__) + '/predict_model.csv',
                                                data_format='csv')
            af.write_example(input_data=predict_channel,
                             example_info=write_example,
                             executor=FlinkPythonExecutor(python_object=Sink()))

        af.model_version_control_dependency(src=evaluate_channel,
                                            model_version_event_type=ModelVersionEventType.MODEL_GENERATED,
                                            dependency=train_channel, model_name=train_model.name)

        af.model_version_control_dependency(src=validate_channel,
                                            model_version_event_type=ModelVersionEventType.MODEL_GENERATED,
                                            dependency=train_channel, model_name=train_model.name)

        af.model_version_control_dependency(src=predict_channel,
                                            model_version_event_type=ModelVersionEventType.MODEL_DEPLOYED,
                                            dependency=validate_channel, model_name=train_model.name)
        # Run workflow
        project_dag = project_name
        af.deploy_to_airflow(project_root_path, dag_id=project_dag)
        af.run(project_path=project_root_path,
               dag_id=project_dag,
               scheduler_type=SchedulerType.AIRFLOW)


if __name__ == '__main__':
    project_path = os.path.dirname(get_file_dir(__file__))
    run_pyflink_project(project_path)
