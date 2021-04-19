from ai_flow.common.scheduler_type import SchedulerType
import os
import ai_flow as af
from ai_flow import CmdExecutor, ExampleSupportType, ExecuteArgs, Args, PythonObjectExecutor, List
from ai_flow.plugins.engine import CMDEngine
from ai_flow.plugins.local_platform import LocalPlatform
from python_ai_flow import Executor, FunctionContext
from python_ai_flow.python_engine import PythonEngine
from examples.example_utils import example_util


# Transform Executor class
class SimpleTransform(Executor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        # Calculate square of each data point the result(a pandas.dataframe)
        result = input_list[0]
        cols = result.columns
        for col in cols:
            result[col] = result[col].map(lambda x: x ** 2)
        return [result]


def run_project(project_root_path):

    af.set_project_config_file(example_util.get_project_config_file(project_root_path))
    # Config command line job, we set platform to local and engine to cmd_line here
    cmd_job_config = af.BaseJobConfig(platform=LocalPlatform.platform(), engine=CMDEngine().engine())
    with af.config(cmd_job_config):
        # Command line job executor
        cmd_job = af.user_define_operation(executor=CmdExecutor(cmd_line="echo Start AI flow"))

    # Config python job, we set platform to local and engine to python here
    python_job_config = af.BaseJobConfig(platform=LocalPlatform.platform(), engine=PythonEngine.engine())

    # Set execution mode of this python job to BATCH,
    # which indicates jobs with this config is running in the form of batch.
    python_job_config.exec_mode = af.ExecutionMode.BATCH

    with af.config(python_job_config):
        # Path of Source data(under '..../simple_transform_airflow' dir)
        source_path = os.path.dirname(os.path.abspath(__file__)) + '/source_data.csv'
        print(source_path)
        # Path of Sink data
        sink_path = os.path.dirname(os.path.abspath(__file__)) + '/sink_data.csv'
        print(sink_path)

        # To make the project replaceable, we register the example in metadata service
        read_example_meta = af.register_example(name='read_example', support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                data_format='csv', data_type='pandas', batch_uri=source_path)

        # Read training example using af.read_example()
        # example_info is the meta information of the example
        read_example_channel = af.read_example(example_info=read_example_meta, exec_args=ExecuteArgs(
            batch_properties=Args(header=None, names=["a", "b", "c"])))

        # Transform examples using af.transform()
        transform_channel = af.transform(input_data_list=[read_example_channel],
                                         executor=PythonObjectExecutor(python_object=SimpleTransform()))

        write_example_meta = af.register_example(name='write_example', support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                 data_format='csv', data_type='pandas', batch_uri=sink_path)

        # Write example to specific path
        write = af.write_example(input_data=transform_channel, example_info=write_example_meta,
                                 exec_args=ExecuteArgs(batch_properties=Args(sep='_', header=False, index=False)))

    # Add control dependency, which means read_example job will start right after command line job finishes.
    af.stop_before_control_dependency(read_example_channel, cmd_job)

    transform_dag = example_util.get_parent_dir_name(__file__)
    af.deploy_to_airflow(project_root_path, dag_id=transform_dag)
    context = af.run(project_path=project_root_path,
                     dag_id=transform_dag,
                     scheduler_type=SchedulerType.AIRFLOW)


if __name__ == '__main__':
    project_path = example_util.init_project_path(".")
    run_project(project_path)
