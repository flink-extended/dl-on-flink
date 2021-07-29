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
. ${BIN}/init-aiflow-env.sh

if [ ! -e ${AIFLOW_PID_DIR}/scheduler.pid ]; then
  echo "No airflow scheduler running"
fi

if [ ! -e ${AIFLOW_PID_DIR}/web.pid ]; then
  echo "No airflow web server running"
fi

set +e
echo "Killing Airflow scheduler and web server"
for ((i=1;i<=3;i++))
do
  kill $(cat ${AIFLOW_PID_DIR}/scheduler.pid) >/dev/null 2>&1 && sleep 1
  kill $(cat ${AIFLOW_PID_DIR}/web.pid) >/dev/null 2>&1 && sleep 1
done

rm ${AIFLOW_PID_DIR}/scheduler.pid
rm ${AIFLOW_PID_DIR}/web.pid
echo "Airflow scheduler and web server killed"
