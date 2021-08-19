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

usage="Usage: init-airflow-with-celery-executor.sh [airflow-mysql-conn] [celery-broker_url] [celery-result_backend]"

if [ $# -ne 3 ]; then
  echo $usage
  exit 1
fi

MYSQL_CONN=$1
BROKER_URL=$2
RESULT_BACKEND=$3

BIN=`dirname "${BASH_SOURCE-$0}"`
BIN=`cd "$BIN"; pwd`
. ${BIN}/init-aiflow-env.sh

if [[ ! -f "${AIRFLOW_HOME}/airflow.cfg" ]] ; then
  ${BIN}/init-airflow-env.sh ${MYSQL_CONN}
fi

CURRENT_DIR=$(pwd)
cd ${AIRFLOW_HOME}
mv airflow.cfg airflow.cfg.tmpl
awk "{gsub(\"executor = LocalExecutor\", \"executor = CeleryExecutor\"); \
    gsub(\"broker_url = redis://redis:6379/0\", \"broker_url = ${BROKER_URL}\"); \
    gsub(\"result_backend = db\+postgresql://postgres:airflow@postgres/airflow\", \"result_backend = ${RESULT_BACKEND}\"); \
    print \$0}" airflow.cfg.tmpl > airflow.cfg
rm airflow.cfg.tmpl >/dev/null 2>&1 || true
cd ${CURRENT_DIR}