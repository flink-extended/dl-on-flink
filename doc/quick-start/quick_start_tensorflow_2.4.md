<!--
  Copyright 2022 Deep Learning on Flink Authors
  
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
  
      http://www.apache.org/licenses/LICENSE-2.0
  
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
  -->

# Quick Start

This tutorial provides a quick introduction to using Deep Learning on Flink. 
This guide will show you how to download and install the latest stable version 
of Deep Learning on Flink. You will run a simple Flink job locally to train
a linear model.

## Environment Requirement

- Java: 8
- Python: 3.7 
- Flink: 1.14
- TensorFlow: 2.4

We strongly recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/index.html)
or other similar tools for an isolated Python environment.

```bash
pip install virtualenv
virtualenv venv --python=python3.7
source venv/bin/activate
```

## Download & Install

### Download Flink
Download a stable release of Flink 1.14, then extract the archive:

```sh
curl -LO https://archive.apache.org/dist/flink/flink-1.14.4/flink-1.14.4-bin-scala_2.11.tgz
tar -xzf flink-1.14.4-bin-scala_2.11.tgz
```

Please refer to [guide](https://nightlies.apache.org/flink/flink-docs-release-1.14//docs/try-flink/local_installation/) 
for more detailed step of downloading or installing Flink.

### Download Deep Learning on Flink
You can download the stable released binary release of Deep Learning on Flink,
then extract the archive:

```sh
curl -LO https://github.com/flink-extended/dl-on-flink/releases/download/0.5.0/dl-on-flink-dist-0.5.0-bin.tgz
tar -xzf dl-on-flink-dist-0.5.0-bin.tgz
export DL_ON_FLINK_DIR="${PWD}"/./dl-on-flink-dist-0.5.0
```

Navigate to the extracted directory, you should see the following directory 
layout:

| Directory | Meaning |
|---|---|
|`lib/` | Directory containing the Deep Learning on Flink JARs compiled |
|`examples/` | Directory containing examples. |

### Install Python dependencies
In order to run Deep Learning on Flink job, we need install the python
dependency with pip.

Install the latest stable release of `dl-on-flink-framwork`
```bash
python3 -m pip install --upgrade dl-on-flink-framework~=0.5
```

Install the latest stable release of `dl-on-flink-tensorflow-2.x`
```bash
python3 -m pip install --upgrade dl-on-flink-tensorflow-2.x~=0.5
```

## Starting Local Standalone Cluster

In this example, we use two workers to train the model. Thus, there has to be
at least 2 slots available in the Flink cluster. To do that, you should
config the `taskmanager.numberOfTaskSlots` at `config/flink-config.yaml` to 2
with the following command.

```sh
cd flink-1.14.4
sed -i.bak 's/taskmanager.numberOfTaskSlots: 1/taskmanager.numberOfTaskSlots: 2/' ./conf/flink-conf.yaml
```

Usually, starting a local Flink cluster by running the following command is 
enough for this quick start guide.

```sh
./bin/start-cluster.sh
```

You should be able to navigate to the web UI at 
`http://localhost:8081` to view the Flink dashboard and see that 
the cluster is up and running.

## Model Train

The examples are included in the binary release. You can run the following
command to submit the Deep Learning on Flink job to train the linear model.

```sh
export MODEL_PATH="${PWD}"/./linear

# Stream Training
./bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/linear/tensorflow/flink_train.py \
  --jarfile "${DL_ON_FLINK_DIR}"/lib/dl-on-flink-tensorflow-2.x-0.5.0-jar-with-dependencies.jar \
  --model-path "${MODEL_PATH}"

# Batch Training with 5120 samples for 100 epochs
./bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/linear/tensorflow/flink_train.py \
  --jarfile "${DL_ON_FLINK_DIR}"/lib/dl-on-flink-tensorflow-2.x-0.5.0-jar-with-dependencies.jar \
  --model-path "${MODEL_PATH}" \
  --epoch 100 \
  --sample-count 5120
```

After the job is submitted successfully, you should see the job at running state
in the Flink web ui.

If the job is finished, you will see the model saved at `$MODEL_PATH`.

## Inference

Now you can submit another Flink job to use the trained linear model to do
inference.

```sh

./bin/flink run \
  -py "${DL_ON_FLINK_DIR}"/examples/linear/tensorflow/flink_inference.py \
  --model-path "${MODEL_PATH}"

```