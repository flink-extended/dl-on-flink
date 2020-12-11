#Quickstart

The Quickstart will introduce you how to install AIflow and help you get started with an example in AIflow.

##Prerequisites
1. python3.7
2. pip

##Installing AI Flow

If you are installing AI Flow from source, you can install AIflow by running the following command:

```shell
# remove the build cache if exists
rm -rf ai_flow.egg-info
rm -rf build
rm -rf dist
python3 setup.py bdist_wheel
python3 -m pip install dist/*.whl
```

If you are installing AI Flow from the release package, just run:

```shell
python3 -m pip install ai_flow-xxx-none-any.whl
```

##Python AI Flow Example
Here is a simple AI Flow example, and a line-by-line explanation will follows right below:

```python
import tempfile
import textwrap

from typing import List

from airflow.logging_config import configure_logging

import ai_flow
from python_ai_flow import Executor


def create_sever_config(root_dir_path):
    content = textwrap.dedent(f"""\
        # Config of master server
        
        # endpoint of master
        master_ip: localhost
        master_port: 50051
        # uri of database backend in master
        db_uri: sqlite:///{root_dir_path}/aiflow.db
        # type of database backend in master
        db_type: sql_lite
        # the default notification service should be enabled 
        # when using the built-in scheduler, 
        start_default_notification: True
        # uri of the default notification service
        notification_uri: localhost:50052
    """)
    master_yaml_path = root_dir_path + "/master.yaml"
    with open(master_yaml_path, "w") as f:
        f.write(content)
    return master_yaml_path


def create_project_config(root_dir_path):
    content = textwrap.dedent("""\
        # Config of project in client

        # name of the project
        project_name: test_project
        # endpoint of master
        master_ip: localhost
        master_port: 50051
    """)
    project_yaml_path = root_dir_path + "/project.yaml"
    with open(project_yaml_path, "w") as f:
        f.write(content)
    return project_yaml_path


def create_workflow_config(root_dir_path):
    content = textwrap.dedent("""\
        # Config of the jobs
        
        # Config of each job
        job_1:
            # Use local platform
            platform: local
            # Operation type is python
            engine: python
            # Name of the job
            job_name: job_1
        job_2:
            platform: local
            engine: python
            job_name: job_2
    """)
    workflow_config_path = root_dir_path + "/workflow_config.yaml"
    with open(root_dir_path + "/workflow_config.yaml", "w") as f:
        f.write(content)
    return workflow_config_path


def start_master(master_yaml_path):
    # enable the logging
    configure_logging()
    # create and start the AI Flow master server
    master = ai_flow.AIFlowMaster(config_file=master_yaml_path)
    master.start(is_block=False)
    return master


class PrintHelloExecutor(Executor):
    """
    A simple executor which just print "hello world!".
    """

    def __init__(self, job_name):
        super().__init__()
        self.job_name = job_name

    def execute(self, function_context: ai_flow.FunctionContext, input_list: List) -> None:
        print("hello world! {}".format(self.job_name))


def build_workflow(workflow_config_path):
    with ai_flow.global_config_file(workflow_config_path):
        # a workflow contains one or more jobs
        with ai_flow.config('job_1'):
            # a job contains one or mode operations
            op_1 = ai_flow.user_define_operation(
                ai_flow.PythonObjectExecutor(PrintHelloExecutor('job_1')))

        with ai_flow.config('job_2'):
            op_2 = ai_flow.user_define_operation(
                ai_flow.PythonObjectExecutor(PrintHelloExecutor('job_2')))

        # start op_2 after op_1 finished
        ai_flow.stop_before_control_dependency(op_2, op_1)


def run_workflow(root_dir_path, project_yaml_path):
    # set the project config file
    ai_flow.set_project_config_file(project_yaml_path)
    # use the built-in scheduler ai_flow.SchedulerType.AIFLOW
    res = ai_flow.run(root_dir_path,
                      dag_id='hello_world_example',
                      scheduler_type=ai_flow.SchedulerType.AIFLOW)
    # wait until the workflow finished
    ai_flow.wait_workflow_execution_finished(res)


if __name__ == '__main__':
    # all files will be placed at a temporary directory
    root_dir = tempfile.mkdtemp()

    # create the master server config
    master_yaml = create_sever_config(root_dir)
    # create the project config
    project_yaml = create_project_config(root_dir)
    # create the workflow config
    workflow_config = create_workflow_config(root_dir)

    # start a master server. 
    # for simplify we start it in current process, 
    # normally it should be started as a standalone server.
    master_server = start_master(master_yaml)

    # build the workflow
    build_workflow(workflow_config)
    # run the workflow
    run_workflow(root_dir, project_yaml)

    # as we started the master server in current process, we need to stop it at the end.
    master_server.stop()
    # the outputs of the python jobs can be found at the "${root_dir}/logs" directory.
    print("The output could be found in: %s/logs/" % root_dir)

```

The output in the logs directory should be:

*1_job_1_{timestamp}_stdout.log*:

```text
hello world! job_1
```

*1_job_2_{timestamp}_stdout.log*:

```text
hello world! job_2
```

The source code of this example could be found in 
`examples/simple_examples/python_codes/hello_world_example.py`

## Work with Airflow

AI Flow can also work with Airflow event scheduler, which is more powerful and has a Web UI to monitor the execution.

### Prerequisites

1. mysql

To start an Airflow server, you need to install and start a mysql server in your machine. 
Currently the AI Flow bundles a modified Airflow so users do not need to install the Apache Airflow manually.

### Configure and Start Airflow Server

The Airflow could be configured by following script. Note that the values ​​of the variables should be determined according to your machine.

```shell
set -e
export AIRFLOW_HOME=~/airflow
mkdir ${AIRFLOW_HOME} >/dev/null 2>&1 || true
MYSQL_HOST="127.0.0.1"
MYSQL_USER="root"
MYSQL_PASSWORD="root"
MYSQL_AIRFLOW_DATABASE="airflow"

CURRENT_DIR=$(pwd)
cd ${AIRFLOW_HOME}

# if the database has been created this command could be skip
mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD} -e "create database if not exists ${MYSQL_AIRFLOW_DATABASE}"

# create the configuration file
airflow initdb >/dev/null 2>&1 || true
mv airflow.cfg airflow.cfg.tmpl
awk "{gsub(\"sql_alchemy_conn = mysql://user:password@host/airflow\", \"sql_alchemy_conn = mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}/${MYSQL_AIRFLOW_DATABASE}\"); \
 gsub(\"load_examples = True\", \"load_examples = False\"); \
 gsub(\"load_default_connections = True\", \"load_default_connections = False\"); \
 gsub(\"dag_dir_list_interval = 300\", \"dag_dir_list_interval = 3\"); \
 print \$0}" airflow.cfg.tmpl > airflow.cfg

# prepare the database
airflow resetdb -y

cd ${CURRENT_DIR}
```

To start the Airflow scheduler and the web server, just run:

```shell
# this path should be determined according to your machine
export AIRFLOW_HOME=~/airflow
AIRFLOW_DEPLOY_PATH="${AIRFLOW_HOME}/airflow_deploy"

# create the pending directory if not exists
mkdir ${AIRFLOW_DEPLOY_PATH} >/dev/null 2>&1 || true

# start airflow scheduler and web server
airflow event_scheduler --subdir=${AIRFLOW_DEPLOY_PATH} > ${AIRFLOW_HOME}/scheduler.log 2>&1 &
echo $! > ${AIRFLOW_HOME}/scheduler.pid
airflow webserver -p 8080 > ${AIRFLOW_HOME}/web.log 2>&1 &
echo $! > ${AIRFLOW_HOME}/web.pid
echo "Scheduler log: ${AIRFLOW_HOME}/scheduler.log"
echo "Scheduler pid: $(cat ${AIRFLOW_HOME}/scheduler.pid)"
echo "Web Server log: ${AIRFLOW_HOME}/web.log"
echo "Web Server pid: $(cat ${AIRFLOW_HOME}/web.pid)"
echo "Airflow deploy path: ${AIRFLOW_DEPLOY_PATH}"
echo "Visit http://127.0.0.1:8080/ to access the airflow web server."
```

### Start AI Flow Master Server

When working with Airflow, the configuration of the AI Flow master server is different from using the built-in scheduler. 
Run following script to start a standalone AI Flow master server:

```shell
# this path should be determined according to your machine
export AIRFLOW_HOME=~/airflow
cat>${AIRFLOW_HOME}/start_master.py<<EOF
import os
import tempfile
import textwrap
import ai_flow
from airflow.logging_config import configure_logging


def create_sever_config(root_dir_path):
    content = textwrap.dedent(f"""\
        # Config of master server

        # endpoint of master
        master_ip: localhost
        master_port: 50051
        # uri of database backend in master
        db_uri: sqlite:///{root_dir_path}/aiflow.db
        # type of database backend in master
        db_type: sql_lite
        # the default notification service is no need to started
        # when using the airflow scheduler 
        start_default_notification: False
        # uri of the notification service
        notification_uri: localhost:50052
    """)
    master_yaml_path = root_dir_path + "/master.yaml"
    with open(master_yaml_path, "w") as f:
        f.write(content)
    return master_yaml_path


def start_master(master_yaml_path):
    configure_logging()
    master = ai_flow.AIFlowMaster(config_file=master_yaml_path)
    master.start(is_block=True)
    return master


if __name__ == '__main__':
    root_dir = os.path.dirname(__file__)
    master_yaml = create_sever_config(root_dir)
    start_master(master_yaml)

EOF
python3 ${AIRFLOW_HOME}/start_master.py > ${AIRFLOW_HOME}/master_server.log 2>&1 &
echo $! > ${AIRFLOW_HOME}/master_server.pid
echo "Master Server pid: $(cat ${AIRFLOW_HOME}/master_server.pid)"
```

### Prepare AI Flow Project

In order to properly adapt to the Airflow, the AI Flow project should have such a directory structure:

```text
SimpleProject
├─ project.yaml
├─ jar_dependencies
├─ resources
└─ python_codes
   ├─ __init__.py
   ├─ my_ai_flow.py
   └─ requirements.txt
```

For python jobs we only need to prepare the `python_codes` directory, the `resources` directory and the `project.yaml`.

Run following script to prepare a simple AI Flow project:

```shell
# this path should be determined according to your machine
export AIRFLOW_HOME=~/airflow

CURRENT_DIR=$(pwd)
# the AIRFLOW_DEPLOY_PATH needs to be the same as when starting the airflow server
AIRFLOW_DEPLOY_PATH="${AIRFLOW_HOME}/airflow_deploy"

# create the dir if not exists
mkdir SimpleProject >/dev/null 2>&1 || true
cd SimpleProject

# prepare the project.yaml
cat>project.yaml<<EOF
project_name: simple_project
master_ip: localhost
master_port: 50051
# for airflow scheduler this option should be enabled.
notification_uri: localhost:50052
airflow_deploy_path: ${AIRFLOW_DEPLOY_PATH}
EOF

# prepare the workflow_config.yaml
# create the dir if not exists
mkdir resources >/dev/null 2>&1 || true
cd resources
cat>workflow_config.yaml<<EOF
job_1:
  platform: local
  engine: python
  job_name: job_1

job_2:
  platform: local
  engine: python
  job_name: job_2

job_3:
  platform: local
  engine: python
  job_name: job_3
EOF
cd ../

# prepare the workflow python code
# create the dir if not exists
mkdir python_codes >/dev/null 2>&1 || true
cd python_codes
cat>airflow_dag_example.py<<EOF
import os
from typing import List

import ai_flow as af
from ai_flow import FunctionContext
from ai_flow.common.scheduler_type import SchedulerType
from python_ai_flow import Executor


class PrintHelloExecutor(Executor):
    def __init__(self, job_name):
        super().__init__()
        self.job_name = job_name

    def execute(self, function_context: FunctionContext, input_list: List) -> None:
        print("hello world! {}".format(self.job_name))


project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_workflow():
    with af.global_config_file(project_path + '/resources/workflow_config.yaml'):
        with af.config('job_1'):
            op_1 = af.user_define_operation(af.PythonObjectExecutor(PrintHelloExecutor('job_1')))

        with af.config('job_2'):
            op_2 = af.user_define_operation(af.PythonObjectExecutor(PrintHelloExecutor('job_2')))

        with af.config('job_3'):
            op_3 = af.user_define_operation(af.PythonObjectExecutor(PrintHelloExecutor('job_2')))

    af.stop_before_control_dependency(op_3, op_1)
    af.stop_before_control_dependency(op_3, op_2)


def run_workflow():
    build_workflow()
    af.set_project_config_file(project_path + '/project.yaml')
    # the airflow scheduler do not support waiting until the execution finished
    # so we just submit the workflow and exit
    af.run(project_path, dag_id='airflow_dag_example', scheduler_type=SchedulerType.AIRFLOW)


if __name__ == '__main__':
    run_workflow()

EOF
cd $CURRENT_DIR
```

### Run the Workflow and Check the Execution Result

To run the workflow, just execute:

```shell
# this path should be determined according to your machine
export AIRFLOW_HOME=~/airflow

python3 SimpleProject/python_codes/airflow_dag_example.py
```

You can find the scheduled workflow on the [Airflow Web Server](http://127.0.0.1:8080/).

The outputs of each job can be found under `${AIRFLOW_HOME}/logs/airflow_dag_example/job_1/`, `${AIRFLOW_HOME}/logs/airflow_dag_example/job_2/` and `${AIRFLOW_HOME}/logs/airflow_dag_example/job_3/`.

### Stop the Airflow Server and the AI Flow Master Server

The Airflow Server and the AI Flow Master don't have stop command so we could only shut down the service by killing related processes:

```shell
# this path should be determined according to your machine
export AIRFLOW_HOME=~/airflow
# the AIRFLOW_DEPLOY_PATH needs to be the same as when starting the airflow server
AIRFLOW_DEPLOY_PATH="${AIRFLOW_HOME}/airflow_deploy"

set +e
for((i=1;i<=3;i++));do kill $(cat ${AIRFLOW_HOME}/scheduler.pid) >/dev/null 2>&1 && sleep 1;done
for((i=1;i<=3;i++));do kill $(cat ${AIRFLOW_HOME}/web.pid) >/dev/null 2>&1 && sleep 1;done
for((i=1;i<=3;i++));do kill $(cat ${AIRFLOW_HOME}/master_server.pid) >/dev/null 2>&1 && sleep 1;done
rm -rf ${AIRFLOW_DEPLOY_PATH}
```
