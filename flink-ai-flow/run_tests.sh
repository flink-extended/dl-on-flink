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

CURRENT_DIR=`pwd`
trap "cd ${CURRENT_DIR}" EXIT
SOURCE_ROOT=$(cd "$(dirname "$0")";pwd)
echo ${SOURCE_ROOT}
export PYTHONPATH=${SOURCE_ROOT}
cd ${SOURCE_ROOT}
function run_tests() {
    code_path=$1
    test_files=$(find ${code_path} | grep -v __pycache__ | grep -v temp | grep test_ | grep "\.py$")

    for i in ${test_files}
    do
        echo "RUN TEST: ${i}"
        FILE_NAME=`basename ${i}`
        DIR_NAME=`dirname ${i}`
        cd ${DIR_NAME} && python3 -m unittest ${FILE_NAME}
        cd ${SOURCE_ROOT}
        sleep 2
    done

}

function run_test_class() {
    dir_name=$1
    class_name=$2
    echo "RUN TEST: ${2}"
    cd ${dir_name} && python3 -m unittest ${class_name}
    cd ${SOURCE_ROOT}
}
# python3 -m unittest discover -v ai_flow.test.api

mvn verify

run_tests 'ai_flow/test/common/'
run_tests 'ai_flow/test/graph'
run_tests 'ai_flow/test/workflow'
run_tests 'ai_flow/test/project'
run_tests 'ai_flow/test/context'
run_tests 'ai_flow/test/ai_graph'
run_tests 'ai_flow/test/translator'
run_tests 'ai_flow/test/runtime'
run_tests 'ai_flow/test/plugin_interface'
run_tests 'ai_flow/test/scheduler'
run_tests 'ai_flow/test/api'

run_tests 'ai_flow/test/store/'
run_tests 'ai_flow/test/model_center/'
run_tests 'ai_flow/test/endpoint/server/'
run_test_class 'ai_flow/test/endpoint/' 'test_client.TestAIFlowClientSqlite'
run_test_class 'ai_flow/test/endpoint/' 'test_mysql_client.TestAIFlowClientMySQL'
run_test_class 'ai_flow/test/endpoint/' 'test_high_availability.TestHighAvailableAIFlowServer'

run_tests 'ai_flow_plugins/tests/blob_manager_plugins'
