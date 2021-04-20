from ai_flow import ExampleSupportType, PythonObjectExecutor, ModelType
from ai_flow.common.scheduler_type import SchedulerType
from batch_train_batch_predict_executor import *
from ai_flow.plugins.local_platform import LocalPlatform
from python_ai_flow.python_engine import PythonEngine
from examples.example_utils import example_util

EXAMPLE_URI = os.path.abspath('.') + '/example_data/mnist_{}.npz'


def run_project(project_root_path):

    af.set_project_config_file(example_util.get_project_config_file(project_root_path))

    # Config python job, we set platform to local and engine to python here
    python_job_config = af.BaseJobConfig(platform=LocalPlatform.platform(), engine=PythonEngine.engine())

    # Set execution mode of this python job to BATCH,
    # which indicates jobs with this config is running in the form of batch.
    python_job_config.exec_mode = af.ExecutionMode.BATCH

    with af.config(python_job_config):
        project_name = example_util.get_parent_dir_name(__file__)
        project_meta = af.register_project(name=project_name,
                                           uri=project_root_path,
                                           project_type='local python')
        # Training of model
        # Register metadata raw training data(example) and read example(i.e. training dataset)
        train_example = af.register_example(name='train_example',
                                            support_type=ExampleSupportType.EXAMPLE_BATCH,
                                            batch_uri=EXAMPLE_URI.format('train'),
                                            data_format='npz')
        train_read_example = af.read_example(example_info=train_example,
                                             executor=PythonObjectExecutor(python_object=ExampleReader()))

        # Transform(preprocessing) example
        train_transform = af.transform(input_data_list=[train_read_example],
                                       executor=PythonObjectExecutor(python_object=ExampleTransformer()))

        # Register model metadata and train model
        train_model = af.register_model(model_name='logistic-regression',
                                        model_type=ModelType.SAVED_MODEL,
                                        model_desc='logistic regression model')
        train_channel = af.train(input_data_list=[train_transform],
                                 executor=PythonObjectExecutor(python_object=ModelTrainer()),
                                 model_info=train_model)

        # Evaluation of model
        evaluate_example = af.register_example(name='evaluate_example',
                                               support_type=ExampleSupportType.EXAMPLE_BATCH,
                                               batch_uri=EXAMPLE_URI.format('evaluate'),
                                               data_format='npz')
        evaluate_read_example = af.read_example(example_info=evaluate_example,
                                                executor=PythonObjectExecutor(python_object=EvaluateExampleReader()))
        evaluate_transform = af.transform(input_data_list=[evaluate_read_example],
                                          executor=PythonObjectExecutor(python_object=EvaluateTransformer()))
        # Register disk path used to save evaluate result
        evaluate_artifact_name = 'evaluate_artifact'
        evaluate_artifact = af.register_artifact(name=evaluate_artifact_name,
                                                 batch_uri=get_file_dir(__file__) + '/evaluate_model')
        # Evaluate model
        evaluate_channel = af.evaluate(input_data_list=[evaluate_transform],
                                       model_info=train_model,
                                       executor=PythonObjectExecutor(python_object=ModelEvaluator(evaluate_artifact_name)))
        # Validation of model
        # Read validation dataset and validate model before it is used to predict

        validate_example = af.register_example(name='validate_example',
                                               support_type=ExampleSupportType.EXAMPLE_BATCH,
                                               batch_uri=EXAMPLE_URI.format('evaluate'),
                                               data_format='npz')
        validate_read_example = af.read_example(example_info=validate_example,
                                                executor=PythonObjectExecutor(python_object=ValidateExampleReader()))
        validate_transform = af.transform(input_data_list=[validate_read_example],
                                          executor=PythonObjectExecutor(python_object=ValidateTransformer()))
        validate_artifact_name = 'validate_artifact'
        validate_artifact = af.register_artifact(name=validate_artifact_name,
                                                 batch_uri=get_file_dir(__file__) + '/validate_model')
        validate_channel = af.model_validate(input_data_list=[validate_transform],
                                             model_info=train_model,
                                             executor=PythonObjectExecutor(
                                                 python_object=ModelValidator(validate_artifact_name)))

        # Push model to serving
        # Register metadata of pushed model
        push_model_artifact_name = 'push_model_artifact'
        push_model_artifact = af.register_artifact(name=push_model_artifact_name,
                                                   batch_uri=get_file_dir(__file__) + '/pushed_model')
        push_model_channel = af.push_model(model_info=train_model,
                                           executor=PythonObjectExecutor(
                                               python_object=ModelPusher(push_model_artifact_name)))

        # Prediction(Inference)
        predict_example = af.register_example(name='predict_example',
                                              support_type=ExampleSupportType.EXAMPLE_BATCH,
                                              batch_uri=EXAMPLE_URI.format('predict'),
                                              data_format='npz')
        predict_read_example = af.read_example(example_info=predict_example,
                                               executor=PythonObjectExecutor(python_object=PredictExampleReader()))
        predict_transform = af.transform(input_data_list=[predict_read_example],
                                         executor=PythonObjectExecutor(python_object=PredictTransformer()))
        predict_channel = af.predict(input_data_list=[predict_transform],
                                     model_info=train_model,
                                     executor=PythonObjectExecutor(python_object=ModelPredictor()))

        # Save prediction result
        write_example = af.register_example(name='write_example',
                                            support_type=ExampleSupportType.EXAMPLE_BATCH,
                                            batch_uri=get_file_dir(__file__) + '/predict_model',
                                            data_format='fs')
        af.write_example(input_data=predict_channel,
                         example_info=write_example,
                         executor=PythonObjectExecutor(python_object=ExampleWriter()))

    # Define relation graph: train -> evaluate -> validate -> push -> predict
    af.stop_before_control_dependency(evaluate_channel, train_channel)
    af.stop_before_control_dependency(validate_channel, evaluate_channel)
    af.stop_before_control_dependency(push_model_channel, validate_channel)
    af.stop_before_control_dependency(predict_channel, push_model_channel)

    # Run workflow
    transform_dag = 'batch_train_batch_predict'
    af.deploy_to_airflow(project_root_path, dag_id=transform_dag)
    context = af.run(project_path=project_root_path,
                     dag_id=transform_dag,
                     scheduler_type=SchedulerType.AIRFLOW)


if __name__ == '__main__':
    project_path = example_util.init_project_path(".")
    run_project(project_path)
