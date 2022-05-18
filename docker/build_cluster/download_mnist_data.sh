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
projectPath=${basePath}/../../

set -e

dataDir=${projectPath}/dl-on-flink-examples/target/data
mkdir -p  ${dataDir}
wget https://raw.githubusercontent.com/wuchaochen/testdata/master/mnist/t10k-images-idx3-ubyte.gz -O ${dataDir}/t10k-images-idx3-ubyte.gz
wget https://raw.githubusercontent.com/wuchaochen/testdata/master/mnist/t10k-labels-idx1-ubyte.gz -O ${dataDir}/t10k-labels-idx1-ubyte.gz
wget https://raw.githubusercontent.com/wuchaochen/testdata/master/mnist/train-images-idx3-ubyte.gz -O ${dataDir}/train-images-idx3-ubyte.gz
wget https://raw.githubusercontent.com/wuchaochen/testdata/master/mnist/train-labels-idx1-ubyte.gz -O ${dataDir}/train-labels-idx1-ubyte.gz