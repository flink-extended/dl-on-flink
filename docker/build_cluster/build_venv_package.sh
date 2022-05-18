#!/usr/bin/env bash
#
# Copyright 2022 Deep Learning on Flink Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
basePath=$(cd `dirname $0`; pwd)
set -e
dockerContainerName=venv-build
projectPath=${basePath}/../../
docker run -d --ulimit core=10000000000 -h ${dockerContainerName} --name ${dockerContainerName} -v ${projectPath}:/opt/work_home/ dl-on-flink/flink jobmanager
docker exec ${dockerContainerName} bash /opt/work_home/docker/flink/create_venv.sh
docker rm -f ${dockerContainerName}


