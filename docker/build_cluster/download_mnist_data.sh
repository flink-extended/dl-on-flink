#!/usr/bin/env bash
basePath=$(cd `dirname $0`; pwd)
projectPath=${basePath}/../../

set -e

dataDir=${projectPath}/flink-ml-examples/target/data
mkdir -p  ${dataDir}
wget http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/flink-ml/data/t10k-images-idx3-ubyte.gz -O ${dataDir}/t10k-images-idx3-ubyte.gz
wget http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/flink-ml/data/t10k-labels-idx1-ubyte.gz -O ${dataDir}/t10k-labels-idx1-ubyte.gz
wget http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/flink-ml/data/train-images-idx3-ubyte.gz -O ${dataDir}/train-images-idx3-ubyte.gz
wget http://etaose.oss-cn-hangzhou-zmf.aliyuncs.com/test/flink-ml/data/train-labels-idx1-ubyte.gz -O ${dataDir}/train-labels-idx1-ubyte.gz