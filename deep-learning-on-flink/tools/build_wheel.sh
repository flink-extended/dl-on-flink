#!/bin/bash
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
PY="${PY:=python}"
echo use python $(which $PY)

basePath=$(cd `dirname $0`; pwd)
echo pathPath: ${basePath}

set -e
distPath=${basePath}/dist
if [[ ! -d ${distPath} ]]; then
  mkdir ${distPath}
fi

echo '############## building flink_ml_framework ##############'
frameworkPath=${basePath}/../flink-ml-framework/python/
cd ${frameworkPath}
${PY} setup.py bdist_wheel
cp ${frameworkPath}/dist/* ${distPath}/
rm -rf ${frameworkPath}/build/ ${frameworkPath}/dist/ ${frameworkPath}/flink_ml_framework.egg-info

echo '############## building flink_ml_tensorflow ##############'
tensorflowPath=${basePath}/../flink-ml-tensorflow/python/
cd ${tensorflowPath}
${PY} -m pip install -r build-requirements.txt
${PY} setup.py bdist_wheel
cp ${tensorflowPath}/dist/* ${distPath}/
rm -rf ${tensorflowPath}/build/ ${tensorflowPath}/dist/ ${tensorflowPath}/flink_ml_tensorflow.egg-info

echo '############## building flink_ml_tensorflow-2.x ##############'
tensorflowPath2=${basePath}/../flink-ml-tensorflow-2.x/python/
cd ${tensorflowPath2}
${PY} -m pip install -r build-requirements.txt
${PY} setup.py bdist_wheel
cp ${tensorflowPath2}/dist/* ${distPath}/
rm -rf ${tensorflowPath2}/build/ ${tensorflowPath2}/dist/ ${tensorflowPath2}/flink_ml_tensorflow.egg-info