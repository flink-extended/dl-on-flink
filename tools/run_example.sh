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

set -euo pipefail

USAGE="run_example.sh <DL_ON_FLINK_BIN> <DL_ON_FLINK_WHEEL_DIR>"

DL_ON_FLINK_BIN=${1:-}
DL_ON_FLINK_WHEEL_DIR=${2:-}

if [[ -z "${DL_ON_FLINK_BIN}" || -z "${DL_ON_FLINK_WHEEL_DIR}" ]]; then
  echo "${USAGE}"
  exit 0
fi

DL_ON_FLINK_BIN=$(realpath "${DL_ON_FLINK_BIN}")
DL_ON_FLINK_WHEEL_DIR=$(realpath "${DL_ON_FLINK_WHEEL_DIR}")

# Download Flink
FLINK_BIN=flink-1.14.4-bin-scala_2.11.tgz
[ -f ${FLINK_BIN} ] || curl -LO https://archive.apache.org/dist/flink/flink-1.14.4/flink-1.14.4-bin-scala_2.11.tgz
tar -xzf flink-1.14.4-bin-scala_2.11.tgz

# Un-tar DL on Flink
tar -xzf "${DL_ON_FLINK_BIN}" --directory "${PWD}"
DL_ON_FLINK_DIR_ARRAY=("${PWD}"/dl-on-flink-dist-*)
DL_ON_FLINK_DIR="${DL_ON_FLINK_DIR_ARRAY[0]}"

pip install --pre -f "${DL_ON_FLINK_WHEEL_DIR}" dl-on-flink-framework

# Start flink cluster
cd flink-1.14.4
sed -i.bak 's/taskmanager.numberOfTaskSlots: 1/taskmanager.numberOfTaskSlots: 2/' ./conf/flink-conf.yaml
rm ./conf/flink-conf.yaml.bak
./bin/start-cluster.sh

# Tensorflow 1.15 linear example
pip install --pre -f "${DL_ON_FLINK_WHEEL_DIR}" dl-on-flink-tensorflow

# Stream Train
MODEL_PATH="${PWD}"/./tf1/linear
./bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/tensorflow-on-flink/linear/flink_train.py \
  --jarfile "${DL_ON_FLINK_DIR}"/lib/dl-on-flink-tensorflow-*-jar-with-dependencies.jar \
  --model-path "${MODEL_PATH}"
[[ -d "${MODEL_PATH}" ]] || echo "Model doesn't exist at ${MODEL_PATH}" || exit 1

./bin/flink run -py "${DL_ON_FLINK_DIR}"/examples/tensorflow-on-flink/linear/flink_inference.py \
  --model-path "${MODEL_PATH}"

# Batch train iteratively
./bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/tensorflow-on-flink/linear/flink_train.py \
  --jarfile "${DL_ON_FLINK_DIR}"/lib/dl-on-flink-tensorflow-*-jar-with-dependencies.jar \
  --model-path "${MODEL_PATH}" \
  --epoch 100 \
  --sample-count 5120
[[ -d "${MODEL_PATH}" ]] || echo "Model doesn't exist at ${MODEL_PATH}" || exit 1

./bin/flink run -py "${DL_ON_FLINK_DIR}"/examples/tensorflow-on-flink/linear/flink_inference.py \
  --model-path "${MODEL_PATH}"

pip uninstall -y dl-on-flink-tensorflow

# Tensorflow 2.4 linear example
pip install --pre -f "${DL_ON_FLINK_WHEEL_DIR}" dl-on-flink-tensorflow-2.x

# Stream train
MODEL_PATH="${PWD}"/./tf2/linear
./bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/tensorflow-on-flink/linear/flink_train.py \
  --jarfile "${DL_ON_FLINK_DIR}"/lib/dl-on-flink-tensorflow-2.x-*-jar-with-dependencies.jar \
  --model-path "${MODEL_PATH}"
[[ -d "${MODEL_PATH}" ]] || echo "Model doesn't exist at ${MODEL_PATH}" || exit 1

./bin/flink run -py "${DL_ON_FLINK_DIR}"/examples/tensorflow-on-flink/linear/flink_inference.py \
  --model-path "${MODEL_PATH}"

# Batch train iteratively
./bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/tensorflow-on-flink/linear/flink_train.py \
  --jarfile "${DL_ON_FLINK_DIR}"/lib/dl-on-flink-tensorflow-2.x-*-jar-with-dependencies.jar \
  --model-path "${MODEL_PATH}" \
  --epoch 100 \
  --sample-count 5120
[[ -d "${MODEL_PATH}" ]] || echo "Model doesn't exist at ${MODEL_PATH}" || exit 1

./bin/flink run -py "${DL_ON_FLINK_DIR}"/examples/tensorflow-on-flink/linear/flink_inference.py \
  --model-path "${MODEL_PATH}"

pip uninstall -y dl-on-flink-tensorflow-2.x

# PyTorch linear example
pip install --pre -f "${DL_ON_FLINK_WHEEL_DIR}" dl-on-flink-pytorch

# Stream train
MODEL_PATH="${PWD}"/./pytorch/linear
./bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/pytorch-on-flink/linear/flink_train.py \
  --jarfile "${DL_ON_FLINK_DIR}"/lib/dl-on-flink-pytorch-*-jar-with-dependencies.jar \
  --model-path "${MODEL_PATH}"
[[ -d "${MODEL_PATH}" ]] || echo "Model doesn't exist at ${MODEL_PATH}" || exit 1

./bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/pytorch-on-flink/linear/flink_inference.py \
  -pyfs "${DL_ON_FLINK_DIR}"/examples/pytorch-on-flink/linear/linear.py \
  --model-path "${MODEL_PATH}"

# Batch train iteratively
~/Downloads/flink-1.14.2/bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/pytorch-on-flink/linear/flink_train.py \
  --jarfile "${DL_ON_FLINK_DIR}"/lib/dl-on-flink-pytorch-*-jar-with-dependencies.jar \
  --model-path "${MODEL_PATH}" \
  --epoch 100 \
  --sample-count 1280
[[ -d "${MODEL_PATH}" ]] || echo "Model doesn't exist at ${MODEL_PATH}" || exit 1

./bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/pytorch-on-flink/linear/flink_inference.py \
  -pyfs "${DL_ON_FLINK_DIR}"/examples/pytorch-on-flink/linear/linear.py \
  --model-path "${MODEL_PATH}"

pip uninstall -y dl-on-flink-pytorch

./bin/stop-cluster.sh