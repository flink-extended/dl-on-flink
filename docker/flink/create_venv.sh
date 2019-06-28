#!/bin/bash

set -e

virtualenv /opt/work_home/temp/test/tfenv
cd /opt/work_home/temp/test
. tfenv/bin/activate
pip install grpcio six numpy wheel mock keras_applications keras_preprocessing
pip install -i https://pypi.doubanio.com/simple tensorflow==1.11.0
#pip install -i https://pypi.doubanio.com/simple torch torchvision
# pip install torch==1.1.0
# download torch slow so use aliyun address
# pip install http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/flink-ml/package/torch-1.0.1.post2-cp27-cp27mu-manylinux1_x86_64.whl
pip install http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/flink-ml/package/torch-1.1.0-cp27-cp27mu-manylinux1_x86_64.whl
pip install torchvision==0.3.0
cd /opt/work_home/flink-ml-framework/python
pip install .
cd /opt/work_home/flink-ml-tensorflow/python
pip install .
cd /opt/work_home/temp/test
deactivate
touch /opt/work_home/temp/test/tfenv/lib/python2.7/site-packages/google/__init__.py

cd /opt/work_home/temp/test/
zip -ryq tfenv.zip tfenv
rm -rf tfenv
