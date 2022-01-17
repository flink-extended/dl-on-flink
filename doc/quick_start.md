<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->

# Quick Start

This tutorial provides a quick introduction to using Deep Learning on Flink. 
This guide will show you how to download the latest stable version of Deep
Learning on Flink, install. You will run a simple Flink job locally to train
a linear model.

## Environment Requirement

- Java: 8
- Python: 3.7 
- Flink: 1.14
- TensorFlow: 1.15.x or 2.3.x

## Download & Install

### Download Flink
[Download the latest binary release](https://flink.apache.org/downloads.html) 
of Flink 1.14, then extract the archive:

```sh
tar -xzf flink-*.tgz
```

Please refer to [guide](https://nightlies.apache.org/flink/flink-docs-release-1.14//docs/try-flink/local_installation/) 
for more detailed step of downloading or installing Flink.

### Download Deep Learning on Flink
You can download the binary release of Deep Learning on Flink from
[release](https://github.com/flink-extended/dl-on-flink/releases), then extract
the archive:

```sh
tar -xzf flink-ml-*.tgz
```

Navigate to the extracted directory, you should see the following directory 
layout:

| Directory | Meaning |
|---|---|
|`lib/` | Directory containing the Deep Learning on Flink JARs compiled |
|`examples/` | Directory containing examples. |

### Install Python dependencies
In order to run Deep Learning on Flink job, we need install the python
dependency.

Python dependency should be installed with pip. We strongly recommend using
[virtualenv](https://virtualenv.pypa.io/en/latest/index.html) or other similar
tools for an isolated Python environment.

Use the following command to install `flink-ml-framwork`
```bash
pip install flink-ml-framework
```

Install `flink-ml-tensorflow` if you use Tensorflow 1.15.x
```bash
pip install flink-ml-tensorflow
```

Install `flink-ml-tensorflow-2.x` if you use Tensorflow 2.3.x
```bash
pip install flink-ml-tensorflow-2.x
```

## Starting Local Standalone Cluster

In this example, we use two workers to train the model. Thus, there has to be
at least 2 slots available in the Flink cluster. To do that, you can simply
config the `taskmanager.numberOfTaskSlots` at `config/flink-config.yaml` to 2.
You can use the following command to do that.

```sh
# We assume to be in the root directory of the Flink extracted distribution

sed -i '' 's/taskmanager.numberOfTaskSlots: 1/taskmanager.numberOfTaskSlots: 2/' ./conf/flink-conf.yaml
```

Usually, starting a local Flink cluster by running the following command is 
enough for this quick start guide.

**Note: If you are using virtualenv, you should start your local Flink cluster
with virtualenv activated.**

```sh
# We assume to be in the root directory of the Flink extracted distribution

./bin/start-cluster.sh
```

You should be able to navigate to the web UI at 
`http://<job manager ip address>:8081` to view the Flink dashboard and see that 
the cluster is up and running.

## Submit a Flink Job

The examples are included in the binary release.  You can download the binary 
release from [release](https://github.com/flink-extended/dl-on-flink/releases).

You can run the following command to submit the job.

**Note: If you are using virtualenv, you should submit the job
with virtualenv activated.**

```sh
export DL_ON_FLINK_DIR=<root dir of Deep Learning on Flink extracted distribution>

# We assume to be in the root directory of the Flink extracted distribution.

# For tensorflow 1.15.x
./bin/flink run \
  -py ${DL_ON_FLINK_DIR}/examples/tensorflow-on-flink/linear/flink_job.py \
  --jarfile ${DL_ON_FLINK_DIR}/lib/flink-ml-tensorflow-0.4-SNAPSHOT-jar-with-dependencies.jar
  
# For tensorflow 2.3.x
./bin/flink run \
  -py ${DL_ON_FLINK_DIR}/examples/tensorflow-on-flink/linear/flink_job.py \
  --jarfile ${DL_ON_FLINK_DIR}/lib/flink-ml-tensorflow-2.x-0.4-SNAPSHOT-jar-with-dependencies.jar
```

After the job is submitted successfully, you should see the job at running state
in the Flink web ui.

If the job is finished, you will see the model saved at `/tmp/linear`.