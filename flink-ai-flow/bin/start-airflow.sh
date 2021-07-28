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

BIN=`dirname "${BASH_SOURCE-$0}"`
BIN=`cd "$BIN"; pwd`
. ${BIN}/aiflow-config.sh

MYSQL_CONN=$1
if [ ! ${MYSQL_CONN} ]; then
  echo "Error: you need to provide a mysql database to start the airflow."
  exit 1
fi

if [[ ! -f "${AIRFLOW_HOME}/airflow.cfg" ]] ; then
  echo "${AIRFLOW_HOME}/airflow.cfg does not exist creating one."

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
      gsub(\"# scheduler =\", \"scheduler = EventBasedSchedulerJob\"); \
      gsub(\"execute_tasks_new_python_interpreter = False\", \"execute_tasks_new_python_interpreter = True\"); \
      gsub(\"min_serialized_dag_update_interval = 30\", \"min_serialized_dag_update_interval = 0\"); \
      print \$0}" airflow.cfg.tmpl > airflow.cfg
  rm airflow.cfg.tmpl >/dev/null 2>&1 || true

  cd ${CURRENT_DIR}
fi

# create a default Admin user for airflow
echo "Try to create admin user"
airflow users create \
    --username admin \
    --password admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email admin@example.org

AIFLOW_LOG_DIR="${AIFLOW_HOME}/logs"
[ -d ${AIFLOW_LOG_DIR} ] || mkdir ${AIFLOW_LOG_DIR}

AIRFLOW_DEPLOY_PATH="${AIFLOW_HOME}/airflow_deploy"

echo "Starting Airflow Scheduler"
SCHEDULER_LOG_FILE_NAME=scheduler-$(date "+%Y%m%d-%H%M%S").log
airflow event_scheduler --subdir=${AIRFLOW_DEPLOY_PATH} > ${AIFLOW_LOG_DIR}/${SCHEDULER_LOG_FILE_NAME} 2>&1 &
echo $! > ${AIFLOW_PID_DIR}/scheduler.pid
echo "Airflow Scheduler started"

echo "Starting Airflow Web Server"
WEB_SERVER_LOG_FILE_NAME=web-$(date "+%Y%m%d-%H%M%S").log
airflow webserver -p 8080 > ${AIFLOW_LOG_DIR}/${WEB_SERVER_LOG_FILE_NAME} 2>&1 &
echo $! > ${AIFLOW_PID_DIR}/web.pid
echo "Airflow Web Server started"

echo "Scheduler log: ${AIFLOW_LOG_DIR}/${SCHEDULER_LOG_FILE_NAME}"
echo "Scheduler pid: $(cat ${AIFLOW_PID_DIR}/scheduler.pid)"
echo "Web Server log: ${AIFLOW_LOG_DIR}/${WEB_SERVER_LOG_FILE_NAME}"
echo "Web Server pid: $(cat ${AIFLOW_PID_DIR}/web.pid)"
echo "Airflow deploy path: ${AIRFLOW_DEPLOY_PATH}"

