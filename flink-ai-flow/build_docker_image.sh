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
    1. Build full ai flow docker image:
    build_docker_image.sh name(Name and optionally a tag in the 'name:tag' format)
    2. Build mini ai flow docker image:
    build_docker_image.sh name(Name and optionally a tag in the 'name:tag' format) mini
    "
}

if [ $# == 1 ] ; then
  docker build -t "$1" .
elif [[ $# == 2 && $2 == 'mini' ]]; then
  docker build -t "$1" . --build-arg ai_flow_package_type=mini
else
  printUsage
  exit 1
fi