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
set -e

virtualenv -p python3 /opt/work_home/temp/test/tfenv
cd /opt/work_home/temp/test
. tfenv/bin/activate
array=()
while read line|| [[ -n ${line} ]]
do
    array+=("$line")
done<../../user.properties

len=${#array[*]}
PACKAGES=""
begin=5
end=11
for i in $(seq ${begin} 1 ${end})
do
    PACKAGES="$PACKAGES ${array[i]}"
done
TENSORFLOW=${array[12]}
TORCH=${array[13]}
pip install ${PACKAGES}
pip install ${TENSORFLOW}
#pip install grpcio six numpy wheel mock keras_applications keras_preprocessing
#pip install -i https://pypi.doubanio.com/simple tensorflow==1.11.0
#pip install -i https://pypi.doubanio.com/simple torch torchvision
# pip install torch==1.1.0
# download torch slow so use aliyun address
# pip install http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/dl-on-flink/package/torch-1.0.1.post2-cp27-cp27mu-manylinux1_x86_64.whl
#pip install http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/dl-on-flink/package/torch-1.1.0-cp27-cp27mu-manylinux1_x86_64.whl
pip install torch==1.1.0
pip install ${TORCH}
#pip install torchvision==0.3.0
cd /opt/work_home/dl-on-flink-framework/python
pip install .
cd /opt/work_home/dl-on-flink-tensorflow/python
pip install .
cd /opt/work_home/temp/test
deactivate
touch /opt/work_home/temp/test/tfenv/lib/python3.5/site-packages/google/__init__.py

cd /opt/work_home/temp/test/
zip -ryq tfenv.zip tfenv
rm -rf tfenv
