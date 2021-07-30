import ai_flow as af
import os

from ai_flow_plugins.job_plugins.flink import FlinkJavaProcessor

preprocess_jar_filename = "wdl-preprocess-0.1-SNAPSHOT.jar"


def main():
    af.init_ai_flow_context()
    check_dependencies()

    with af.job_config('preprocess'):
        af.user_define_operation(processor=FlinkJavaProcessor(entry_class="org.aiflow.StreamPredictPreprocess",
                                                              main_jar_file=preprocess_jar_filename,
                                                              args=["localhost:9092", "input", "output"]))

    workflow_name = af.current_workflow_config().workflow_name
    stop_workflow_executions(workflow_name)
    af.workflow_operation.submit_workflow(workflow_name)
    af.workflow_operation.start_new_workflow_execution(workflow_name)


def check_dependencies():
    jar_path = os.path.join(af.current_project_context().get_dependencies_path(), "jar", preprocess_jar_filename)
    if not os.path.exists(jar_path):
        print("{} doesn't exist! \n"
              "Please put the jar in dependencies/jar".format(jar_path))
        exit(-1)


def stop_workflow_executions(workflow_name):
    workflow_executions = af.workflow_operation.list_workflow_executions(workflow_name)
    for workflow_execution in workflow_executions:
        af.workflow_operation.stop_workflow_execution(workflow_execution.workflow_execution_id)


if __name__ == '__main__':
    main()
