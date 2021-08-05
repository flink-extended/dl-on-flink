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
ROOT_DIR=$(cd "$(dirname "$0")" || exit;pwd)
cd "${ROOT_DIR}" || exit

function printUsage() {
    echo "Usage:
    1. Build full ai flow sdist package:
    build_ai_flow_package.sh sdist
    2. Build full ai flow wheel package:
    build_ai_flow_package.sh wheel
    3. Build mini ai flow sdist package:
    build_ai_flow_package.sh sdist mini
    4. Build mini ai flow wheel package:
    build_ai_flow_package.sh wheel mini
    "
}

if [ $# == 1 ] ; then
  package_type=$1
elif [[ $# == 2 && $2 == 'mini' ]]; then
  export BUILD_MINI_AI_FLOW_PACKAGE='true'
  package_type=$1
else
  printUsage
  exit 1
fi

if [ "$package_type" == 'sdist' ]; then
  package_type='sdist'
elif [ "$package_type" == 'wheel' ]; then
  package_type='bdist_wheel'
else
  printUsage
  exit 1
fi

python3 setup.py "$package_type"
