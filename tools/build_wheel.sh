#!/bin/bash
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
PY="${PY:=python}"
echo use python $(which $PY)

basePath=$(cd `dirname $0`; pwd)
echo basePath: ${basePath}

set -e
distPath=${basePath}/dist
if [[ ! -d ${distPath} ]]; then
  mkdir ${distPath}
fi

echo '############## building dl_on_flink_framework ##############'
frameworkPath=${basePath}/../dl-on-flink-framework/python/
cd ${frameworkPath} && [ -d ./build ] && echo "removing previous build dir" && rm -rf ./build
${PY} setup.py bdist_wheel
cp ${frameworkPath}/dist/* ${distPath}/
rm -rf ${frameworkPath}/build/ ${frameworkPath}/dist/ ${frameworkPath}/dl_on_flink_framework.egg-info

echo '############## building dl_on_flink_tensorflow ##############'
tensorflowPath=${basePath}/../dl-on-flink-tensorflow/python/
cd ${tensorflowPath} && [ -d ./build ] && echo "removing previous build dir" && rm -rf ./build
${PY} setup.py bdist_wheel
cp ${tensorflowPath}/dist/* ${distPath}/
rm -rf ${tensorflowPath}/build/ ${tensorflowPath}/dist/ ${tensorflowPath}/dl_on_flink_tensorflow.egg-info

echo '############## building dl_on_flink_tensorflow-2.x ##############'
tensorflowPath2=${basePath}/../dl-on-flink-tensorflow-2.x/python/
cd ${tensorflowPath2} && [ -d ./build ] && echo "removing previous build dir" && rm -rf ./build
${PY} setup.py bdist_wheel
cp ${tensorflowPath2}/dist/* ${distPath}/
rm -rf ${tensorflowPath2}/build/ ${tensorflowPath2}/dist/ ${tensorflowPath2}/dl_on_flink_tensorflow.egg-info