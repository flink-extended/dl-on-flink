# Deep Learning on Flink

Deep Learning on Flink aims to integrate Flink and deep learning frameworks
(e.g. TensorFlow, PyTorch, etc) to enable distributed deep learning training and
inference on a Flink cluster.

It runs the deep learning tasks inside a Flink operator so that Flink can help
establish a distributed environment, manage the resource, read/write the data
with the rich connectors in Flink and handle the failures.

Currently, Deep Learning on Flink supports TensorFlow and PyTorch.

## Support Framework Version
- TensorFlow: 1.15.x & 2.3.x
- Pytorch: 1.x
- Flink: 1.14.x
 
## Getting Started

To get your hand dirty, you can follow [quick start](doc/quick_start.md) 
to submit an example job to a local standalone Flink cluster.

## Build From Source

**Requirements**
- python: 3.7
- cmake >= 3.6
- java 1.8
- maven >=3.3.0

Deep Learning on Flink requires Java and Python works together. Thus, we need 
to build for both Java and Python.

### Build Java

```shell 
mvn -DskipTests clean install
```

After finish, you can find the target distribution in the `flink-ml-dist/target`
folder.

### Build Python

#### Install from Source
You can run the following commands to install the Python packages from source

```sh
# Install flink-ml-framework first
pip install flink-ml-framework/python

# Note that you should only install one of the following as they require
# different versions of Tensorflow 
# For tensorflow 1.15.x
pip install flink-ml-tensorflow/python
# For tensorflow 2.3.x
pip install flink-ml-tensorflow-2.x/python
```

#### Build wheels
We provide a script to build wheels for Python packages, you can run the
following command.

```sh
bash tools/build_wheel.sh
```

After finish, you can find the wheels at `tools/dist`. Then you can install the
python package with the wheels.

```sh
pip install tools/dist/<wheel>
```

# For More Information

[Design document](doc/design.md)

# License
[Apache License 2.0](LICENSE)
