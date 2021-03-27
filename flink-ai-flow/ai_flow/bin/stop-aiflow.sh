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
AIRFLOW_DEPLOY_PATH="${AIRFLOW_HOME}/airflow_deploy"

set +e
for((i=1;i<=3;i++));do kill $(cat ${AIRFLOW_HOME}/scheduler.pid) >/dev/null 2>&1 && sleep 1;done
for((i=1;i<=3;i++));do kill $(cat ${AIRFLOW_HOME}/web.pid) >/dev/null 2>&1 && sleep 1;done
for((i=1;i<=3;i++));do kill $(cat ${AIRFLOW_HOME}/master_server.pid) >/dev/null 2>&1 && sleep 1;done
for((i=1;i<=3;i++));do kill $(cat ${AIRFLOW_HOME}/notification_service.pid) >/dev/null 2>&1 && sleep 1;done
rm -rf ${AIRFLOW_DEPLOY_PATH}
