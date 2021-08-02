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

if [ -e ${AIFLOW_PID_DIR}/aiflow_server.pid ]; then
  echo "AiFlow server is running, stopping first"
  ${BIN}/stop-aiflow.sh
fi

echo "Starting AIFlow Server"
LOG_FILE_NAME=aiflow-server-$(date "+%Y%m%d-%H%M%S").log
start_aiflow.py > ${AIFLOW_LOG_DIR}/${LOG_FILE_NAME} 2>&1 &
echo $! > ${AIFLOW_PID_DIR}/aiflow_server.pid

echo "AIFlow Server started"
echo "AIFlow Server log: ${AIFLOW_LOG_DIR}/${LOG_FILE_NAME}"
echo "AIFlow Server pid: $(cat ${AIFLOW_PID_DIR}/aiflow_server.pid)"
