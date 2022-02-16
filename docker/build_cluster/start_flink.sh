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
basePath=$(cd `dirname $0`; pwd)
projectPath=${basePath}/../../

# start jm
echo "flink job master starting..."
docker run -d --ulimit core=10000000000 -h flink-jm --name flink-jm --link minizk --link minidfs -v ${projectPath}:/opt/work_home/ -p 8081:8081 dl-on-flink/flink jobmanager
echo "flink job master started!"

# start tm
for i in 0 1 2
do
    echo "starting tm-${i} ..."
    docker run -d --ulimit core=10000000000 -h flink-tm-${i} --name flink-tm-${i} -e TASK_MANAGER_NUMBER_OF_TASK_SLOTS=2 -e JOB_MANAGER_RPC_ADDRESS=flink-jm --link minizk --link minidfs --link flink-jm dl-on-flink/flink taskmanager
    echo "tm-${i} started!"
done
