#!/bin/bash

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
# pip install http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/flink-ml/package/torch-1.0.1.post2-cp27-cp27mu-manylinux1_x86_64.whl
#pip install http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/flink-ml/package/torch-1.1.0-cp27-cp27mu-manylinux1_x86_64.whl
pip install torch==1.1.0
pip install ${TORCH}
#pip install torchvision==0.3.0
cd /opt/work_home/flink-ml-framework/python
pip install .
cd /opt/work_home/flink-ml-tensorflow/python
pip install .
cd /opt/work_home/temp/test
deactivate
touch /opt/work_home/temp/test/tfenv/lib/python3.5/site-packages/google/__init__.py

cd /opt/work_home/temp/test/
zip -ryq tfenv.zip tfenv
rm -rf tfenv
