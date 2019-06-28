#!/bin/bash
basePath=$(cd `dirname $0`; pwd)
set -e
if [[ 1 -ne $# ]]; then
    echo "usage: create_venv_package.sh sourcePath"
    exit 1
fi
sourcePath=$1
echo "source path:${sourcePath}"

virtualenv ${basePath}/tfenv
cd ${basePath}
. tfenv/bin/activate
pip install grpcio six numpy wheel mock keras_applications keras_preprocessing
pip install tensorflow==1.11.0
cd ${sourcePath}/flink-ml-framework/python
pip install .
cd ${sourcePath}/flink-ml-tensorflow/python
pip install .
cd ${basePath}
deactivate
touch ${basePath}/tfenv/lib/python2.7/site-packages/google/__init__.py

cd ${basePath}
zip -ryq tfenv.zip tfenv
rm -rf tfenv
