#!/usr/bin/env bash
##
## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##   http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.
##
set -e
export AIRFLOW_HOME=${AIRFLOW_HOME:-~/airflow}

if [[ ! -f "${AIRFLOW_HOME}/airflow.cfg" ]] ; then
    MYSQL_CONN=$1
    if [[ "${MYSQL_CONN}" = "" ]] ; then
        echo "The \${AIRFLOW_HOME}/airflow.cfg is not exists. You need to provide a mysql database to initialize the airflow, e.g.:"
        echo "start-aiflow.sh mysql://root:root@127.0.0.1/airflow"
        exit 1
    fi
    mkdir ${AIRFLOW_HOME} >/dev/null 2>&1 || true

    CURRENT_DIR=$(pwd)
    cd ${AIRFLOW_HOME}

    # create the configuration file
    airflow db init >/dev/null 2>&1 || true
    mv airflow.cfg airflow.cfg.tmpl
    awk "{gsub(\"sql_alchemy_conn = sqlite:///${AIRFLOW_HOME}/airflow.db\", \"sql_alchemy_conn = ${MYSQL_CONN}\"); \
        gsub(\"load_examples = True\", \"load_examples = False\"); \
        gsub(\"load_default_connections = True\", \"load_default_connections = False\"); \
        gsub(\"dag_dir_list_interval = 300\", \"dag_dir_list_interval = 3\"); \
        gsub(\"executor = SequentialExecutor\", \"executor = LocalExecutor\"); \
        gsub(\"dags_are_paused_at_creation = True\", \"dags_are_paused_at_creation = False\"); \
        gsub(\"# mp_start_method =\", \"mp_start_method = forkserver\"); \
        gsub(\"execute_tasks_new_python_interpreter = False\", \"execute_tasks_new_python_interpreter = True\"); \
        gsub(\"min_serialized_dag_update_interval = 30\", \"min_serialized_dag_update_interval = None\"); \
        print \$0}" airflow.cfg.tmpl > airflow.cfg

    # prepare the database
    airflow db reset -y

    cd ${CURRENT_DIR}
fi

AIRFLOW_DEPLOY_PATH="${AIRFLOW_HOME}/airflow_deploy"

# create the pending directory if not exists
mkdir ${AIRFLOW_DEPLOY_PATH} >/dev/null 2>&1 || true

# start notification service
start_notification_service.py > ${AIRFLOW_HOME}/notification_service.log 2>&1 &
echo $! > ${AIRFLOW_HOME}/notification_service.pid

# start airflow scheduler and web server
airflow event_scheduler --subdir=${AIRFLOW_DEPLOY_PATH} > ${AIRFLOW_HOME}/scheduler.log 2>&1 &
echo $! > ${AIRFLOW_HOME}/scheduler.pid
airflow webserver -p 8080 > ${AIRFLOW_HOME}/web.log 2>&1 &
echo $! > ${AIRFLOW_HOME}/web.pid
start_aiflow.py > ${AIRFLOW_HOME}/master_server.log 2>&1 &
echo $! > ${AIRFLOW_HOME}/master_server.pid
echo "Notification service log: ${AIRFLOW_HOME}/notification_service.log"
echo "Notification service pid: $(cat ${AIRFLOW_HOME}/notification_service.pid)"
echo "Scheduler log: ${AIRFLOW_HOME}/scheduler.log"
echo "Scheduler pid: $(cat ${AIRFLOW_HOME}/scheduler.pid)"
echo "Web Server log: ${AIRFLOW_HOME}/web.log"
echo "Web Server pid: $(cat ${AIRFLOW_HOME}/web.pid)"
echo "Master Server log: ${AIRFLOW_HOME}/master_server.log"
echo "Master Server pid: $(cat ${AIRFLOW_HOME}/master_server.pid)"
echo "Airflow deploy path: ${AIRFLOW_DEPLOY_PATH}"
echo "Visit http://127.0.0.1:8080/ to access the airflow web server."
