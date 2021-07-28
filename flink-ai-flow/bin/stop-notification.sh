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

if [ ! -e ${AIFLOW_PID_DIR}/notification_service.pid ]; then
  echo "No notification service running"
fi

set +e
echo "Killing notification service"
for ((i=1;i<=3;i++))
do
  kill $(cat ${AIFLOW_PID_DIR}/notification_service.pid) >/dev/null 2>&1 && sleep 1
done

rm ${AIFLOW_PID_DIR}/notification_service.pid
echo "notification service killed"
