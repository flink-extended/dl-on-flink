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

MYSQL_CONN=$1
if [ ! ${MYSQL_CONN} ]; then
  echo "Error: you need to provide a mysql database to start the airflow."
  exit 1
fi

BIN=`dirname "${BASH_SOURCE-$0}"`
BIN=`cd "$BIN"; pwd`
. ${BIN}/init-aiflow-env.sh
${BIN}/init-airflow-env.sh ${MYSQL_CONN}

wait_for_airflow_web_server() {
  for i in {0..60}; do
    if grep -q 'Listening at:' ${AIFLOW_LOG_DIR}/$1 || curl -s localhost:8080 > /dev/null ; then
      return 0
    fi
    sleep 1
  done
  echo "Timeout waiting for airflow web server to run. Please check the log at ${AIFLOW_LOG_DIR}/$1"
  return 1
}

# Stop the running scheduler and web server if already running
if [ -e ${AIFLOW_PID_DIR}/scheduler.pid ] || [ -e ${AIFLOW_PID_DIR}/web.pid ]; then
  echo "Airflow is running, stopping first"
  ${BIN}/stop-airflow.sh
fi

echo "Starting Airflow Scheduler"
SCHEDULER_LOG_FILE_NAME=scheduler-$(date "+%Y%m%d-%H%M%S").log
airflow event_scheduler --subdir=${AIRFLOW_DEPLOY_PATH} > ${AIFLOW_LOG_DIR}/${SCHEDULER_LOG_FILE_NAME} 2>&1 &
echo $! > ${AIFLOW_PID_DIR}/scheduler.pid
echo "Airflow Scheduler started"

echo "Starting Airflow Web Server"
WEB_SERVER_LOG_FILE_NAME=web-$(date "+%Y%m%d-%H%M%S").log
airflow webserver -p 8080 > ${AIFLOW_LOG_DIR}/${WEB_SERVER_LOG_FILE_NAME} 2>&1 &
echo $! > ${AIFLOW_PID_DIR}/web.pid
wait_for_airflow_web_server ${WEB_SERVER_LOG_FILE_NAME}
echo "Airflow Web Server started"

echo "Scheduler log: ${AIFLOW_LOG_DIR}/${SCHEDULER_LOG_FILE_NAME}"
echo "Scheduler pid: $(cat ${AIFLOW_PID_DIR}/scheduler.pid)"
echo "Web Server log: ${AIFLOW_LOG_DIR}/${WEB_SERVER_LOG_FILE_NAME}"
echo "Web Server pid: $(cat ${AIFLOW_PID_DIR}/web.pid)"
echo "Airflow deploy path: ${AIRFLOW_DEPLOY_PATH}"

