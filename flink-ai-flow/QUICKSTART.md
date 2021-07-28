# Quickstart
The Quickstart will show you how to install AI Flow and help you get started with an example in AI Flow.

- [Prerequisites](#prerequisites)
- [Install AI Flow](#install-ai-flow)
- [Start AI Flow](#start-ai-flow)
  * [Start Servers](#start-servers)
  * [Prepare AI Flow Project](#prepare-ai-flow-project)
  * [Run Example and Check the Execution Result](#run-example-and-check-the-execution-result)
  * [Stop Servers](#stop-servers)
- [Work with Docker](#work-with-docker)
- [Troubleshooting](#troubleshooting)

## Prerequisites
1. python3.7
2. pip
3. MySQL
4. yarn(1.22.10 or newer)

We strongly recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/index.html) or other similar tools to provide a isolated Python environment, 
in case of dependencies conflict error.
Please refer to MySQL  [document](https://dev.mysql.com/doc/refman/8.0/en/upgrading-from-previous-series.html) to install mysql server and client.

You need a started MySQL server, and a database to store AI Flow meta data.
```text
# If your MySQL server version is 8.0+, please remind to create database with specific character set 
# in case of primary key length error when creating Apache Airflow tables, like this:
CREATE DATABASE airflow CHARACTER SET UTF8mb3 COLLATE utf8_general_ci;
```

## Install AI Flow
Currently the AI Flow bundles a modified Airflow so you do not need to install the Apache Airflow manually.
We added an event-based scheduler named event_scheduler to Apache Airflow which is more powerful and has a Web UI to monitor the execution.

If you are installing AI Flow from source, you can install AI Flow by running the following command:

```shell
cd flink-ai-extended
bash flink-ai-flow/install_aiflow.sh
```
To make it easier to start server, some shell scripts like start-all-aiflow-services.sh will be installed with upon commands.
You could run with `which start-all-aiflow-services.sh` to check if the scripts are installed successfully. 
If not, you can reinstall with `sudo` command. Any other problems during the installation, please refer to the [Troubleshooting](#troubleshooting) section to see if it can help.
If you meet any problems during the installation, please refer to the [Troubleshooting](#troubleshooting) section to see if it can help.

## Start AI Flow

### Start Servers
Run following command to start Notification service, AI Flow Server and Airflow Server:

```shell
start-all-aiflow-services.sh
```

If you execute this command for the first time, you will get the following output:

```text
The ${AIRFLOW_HOME}/airflow.cfg is not exists. You need to provide a mysql database to initialize the airflow, e.g.:
start-all-aiflow-services.sh mysql://root:root@127.0.0.1/airflow
```

Please prepare the MySQL database refer to [Prerequisites](#prerequisites-1) and rerun the `start-all-aiflow-services.sh` with the MySQL parameter.
After that you will get the output like:

```text
Scheduler log: ${AIRFLOW_HOME}/scheduler.log
Scheduler pid: 69945
Web Server log: ${AIRFLOW_HOME}/web.log
Web Server pid: 69946
Master Server log:  ${AIRFLOW_HOME}/master_server.log
Master Server pid: 69947
Airflow deploy path: ${AIRFLOW_HOME}/airflow_deploy
Visit http://127.0.0.1:8080/ to access the airflow web server.
```
If you see the login page when visit http://127.0.0.1:8080/, you can login with the defaut user name(admin) and password(admin).

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

### Run Example and Check the Execution Result

To run the workflow, just execute:

```shell
# This path should be determined by yourself
export AIRFLOW_HOME=~/airflow
AIRFLOW_DEPLOY_PATH="${AIRFLOW_HOME}/airflow_deploy"

# This path is the absolute path of the flink-ai-flow project in your machine
SOURCE_CODE_DIR=/tmp/flink-ai-extended/flink-ai-flow

# A simple example is prepared in $SOURCE_CODE_DIR/examples/quickstart_example.
# Before running the example we need to append some dynamic config.
cp -r $SOURCE_CODE_DIR/examples $AIRFLOW_HOME/
echo "airflow_deploy_path: ${AIRFLOW_DEPLOY_PATH}" >> $AIRFLOW_HOME/examples/quickstart_example/project.yaml
python $AIRFLOW_HOME/examples/quickstart_example/python_codes/airflow_dag_example.py
```

You can find the scheduled workflow on the [Airflow Web Server](http://127.0.0.1:8080/).

The outputs of each job can be found under `${AIRFLOW_HOME}/logs/airflow_dag_example/job_1/`, `${AIRFLOW_HOME}/logs/airflow_dag_example/job_2/` and `${AIRFLOW_HOME}/logs/airflow_dag_example/job_3/`.

### Stop Servers

Run following command to stop notification server, Airflow Server and AI Flow Server:

```shell
stop-all-aiflow-services.sh
```
## Work with Docker
The Dockerfile is also provided, which helps users start a Flink AI Flow server. You can build an image like this:
```shell
docker build --rm -t flink-ai-extended/flink-ai-flow:v1 .
```

Before starting the container with the image, you need to make sure your MySQL server on your host machine has a valid database.
You can create the database using the following command in your MySQL CLI:
```SQL
CREATE DATABASE airflow CHARACTER SET UTF8mb3 COLLATE utf8_general_ci;
```

Then, to run the image, you need to pass your MySQL connection string as parameter, e.g.
```shell
 docker run -it -p 8080:8080 flink-ai-extended/flink-ai-flow:v1 mysql://user:password@127.0.0.1/airflow
```
Note, `127.0.0.1` should be replaced with `host.docker.internal` or any valid IP address which can be utilized by docker to access host machine's MySQL service.

To submit a workflow, you can run following commands.
```shell
python ${FLINK_AI_FLOW_SOURCES}/examples/quickstart_example/python_codes/airflow_dag_example.py
```
You can find the scheduled workflow on the [Airflow Web Server](http://127.0.0.1:8080/).
Once the workflow is done, you can check its correctness by viewing the output logs under `${AIRFLOW_HOME}/logs/airflow_dag_example` directory or via [Web UI](http://127.0.0.1:8080/). 


## Troubleshooting
### 1. Fail on mysqlclient installation
According to mysqlclient's [document](https://github.com/PyMySQL/mysqlclient#install), extra steps are needed for installing mysqlclient with pip. Please check the document and take corresponding actions.

### 2. Can't connect to MySQL server in docker
Detail message: `(2002, "Can't connect to MySQL server on '127.0.0.1' (115)")`

If your MySQL server is started at your local machine, your need to replace `mysql://user:password@127.0.0.1/airflow` with `mysql://user:password@host.docker.internal/airflow`.

### 3. caching_sha2_password could not be loaded

Due to MySQL's [document](https://dev.mysql.com/doc/refman/8.0/en/upgrading-from-previous-series.html), caching_sha2_password is the the default authentication plugin since MySQL 8.0. If you meet this problem 
when launching docker, you can fix it by changing it back to naive version. To do that, in your MySQL server on host machine, type following command:

```SQL
ALTER USER 'username' IDENTIFIED WITH mysql_native_password BY 'password';
```
Then restart MySQL service and the docker image.



