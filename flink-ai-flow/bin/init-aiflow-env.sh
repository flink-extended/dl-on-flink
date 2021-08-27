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

export AIFLOW_HOME=${AIFLOW_HOME:-~/aiflow}
export AIFLOW_PID_DIR=${AIFLOW_PID_DIR:-/tmp}
export AIFLOW_LOG_DIR="${AIFLOW_HOME}/logs"
export AIRFLOW_DEPLOY_PATH="${AIFLOW_HOME}/airflow_deploy"

DEFAULT_DB_CONN="sqlite:///${AIFLOW_HOME}/aiflow.db"
export AIFLOW_DB_CONN=${AIFLOW_DB_CONN:-${DEFAULT_DB_CONN}}
export AIFLOW_DB_TYPE=${AIFLOW_DB_TYPE:-SQL_LITE}

export AIRFLOW_HOME=${AIRFLOW_HOME:-~/airflow}

# create directory if not exist
[ -d ${AIFLOW_HOME} ] || mkdir ${AIFLOW_HOME}
[ -d ${AIFLOW_PID_DIR} ] || mkdir ${AIFLOW_PID_DIR}
[ -d ${AIFLOW_LOG_DIR} ] || mkdir ${AIFLOW_LOG_DIR}
[ -d ${AIRFLOW_HOME} ] || mkdir ${AIRFLOW_HOME}
[ -d ${AIRFLOW_DEPLOY_PATH} ] || mkdir ${AIRFLOW_DEPLOY_PATH}


DEFAULT_NOTIFICATION_SERVER_URI="localhost:50051"
function get_ip_addr() {
  SYSTEM=$(uname -s)
  if [[ ${SYSTEM} == "Darwin" ]]; then
    DEFAULT_NOTIFICATION_SERVER_URI="$(ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}'):50051"
  elif [[ ${SYSTEM} == "Linux" ]]; then
    DEFAULT_NOTIFICATION_SERVER_URI="$(hostname -I | xargs):50051"
  else
    echo "Please init AIFlow on Linux or macOS."
    exit 1
  fi
}
get_ip_addr
export NOTIFICATION_SERVER_URI=${NOTIFICATION_SERVER_URI:-${DEFAULT_NOTIFICATION_SERVER_URI}}
