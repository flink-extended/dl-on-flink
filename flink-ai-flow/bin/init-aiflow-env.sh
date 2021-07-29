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

export AIFLOW_HOME=${AIRFLOW_HOME:-~/aiflow}
export AIFLOW_PID_DIR=${AIFLOW_PID_DIR:-/tmp}
export AIFLOW_LOG_DIR="${AIFLOW_HOME}/logs"
export AIRFLOW_DEPLOY_PATH="${AIFLOW_HOME}/airflow_deploy"

export AIRFLOW_HOME=${AIRFLOW_HOME:-~/airflow}

# create directory if not exist
[ -d ${AIFLOW_HOME} ] || mkdir ${AIFLOW_HOME}
[ -d ${AIFLOW_LOG_DIR} ] || mkdir ${AIFLOW_LOG_DIR}
[ -d ${AIRFLOW_HOME} ] || mkdir ${AIRFLOW_HOME}
[ -d ${AIRFLOW_DEPLOY_PATH} ] || mkdir ${AIRFLOW_DEPLOY_PATH}

# maybe config airflow.cfg if AIRFLOW_DB_CONN is given
if [ $# -eq 1 ]; then
  AIRFLOW_DB_CONN=$1
  if [[ ! -f "${AIRFLOW_HOME}/airflow.cfg" ]] ; then
    echo "${AIRFLOW_HOME}/airflow.cfg does not exist creating one."
    CURRENT_DIR=$(pwd)
    cd ${AIRFLOW_HOME}

    # create the configuration file
    airflow config list >/dev/null 2>&1 || true
    mv airflow.cfg airflow.cfg.tmpl
    awk "{gsub(\"sql_alchemy_conn = sqlite:///${AIRFLOW_HOME}/airflow.db\", \"sql_alchemy_conn = ${AIRFLOW_DB_CONN}\"); \
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

    # init database
    airflow db init

    cd ${CURRENT_DIR}
  else
    echo "${AIRFLOW_HOME}/airflow.cfg already exist. Using the existing airflow.cfg"
  fi

  # create a default Admin user for airflow
  echo "Try to create admin airflow user"
  airflow users create \
      --username admin \
      --password admin \
      --firstname admin \
      --lastname admin \
      --role Admin \
      --email admin@example.org
fi