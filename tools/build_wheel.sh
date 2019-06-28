#!/bin/bash
basePath=$(cd `dirname $0`; pwd)
set -e
distPath=${basePath}/dist
if [[ ! -d ${distPath} ]]; then
  mkdir ${distPath}
fi

frameworkPath=${basePath}/../flink-ml-framework/python/
cd ${frameworkPath}
python setup.py bdist_wheel
cp ${frameworkPath}/dist/* ${distPath}/
rm -rf ${frameworkPath}/build/ ${frameworkPath}/dist/ ${frameworkPath}/flink_ml_framework.egg-info

tensorflowPath=${basePath}/../flink-ml-tensorflow/python/
cd ${tensorflowPath}
python setup.py bdist_wheel
cp ${tensorflowPath}/dist/* ${distPath}/
rm -rf ${tensorflowPath}/build/ ${tensorflowPath}/dist/ ${tensorflowPath}/flink_ml_tensorflow.egg-info