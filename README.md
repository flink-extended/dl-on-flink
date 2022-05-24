# Deep Learning on Flink

Deep Learning on Flink aims to integrate Flink and deep learning frameworks
(e.g. TensorFlow, PyTorch, etc.) to enable distributed deep learning training and
inference on a Flink cluster.

It runs the deep learning tasks inside a Flink operator so that Flink can help
establish a distributed environment, manage the resource, read/write the data
with the rich connectors in Flink and handle the failures.

Currently, Deep Learning on Flink supports TensorFlow.

## Supported Operating System
Deep Learning on Flink is tested and supported on the following 64-bit systems:

- Ubuntu 18.04
- macOS 10.15

## Support Framework Version
- TensorFlow: 1.15.x & 2.4.x
- PyTorch: 1.11.x
- Flink: 1.14.x
 
## Getting Started

You can follow the following quick starts to submit an example job with 
different deep learning frameworks to a local standalone Flink cluster.

- [Quick Start Tensorflow 1.15](doc/quick-start/quick_start_tensorflow_1.15.md)
- [Quick Start Tensorflow 2.4](doc/quick-start/quick_start_tensorflow_2.4.md)
- [Quick Start PyTorch](doc/quick-start/quick_start_pytorch.md)

## Build From Source

**Requirements**
- python: 3.7
- cmake >= 3.6
- java 1.8
- maven >=3.3.0

Deep Learning on Flink requires Java and Python works together. Thus, we need 
to build for both Java and Python.

### Initializing Submodules before Building Deep Learning on Flink from Source

Please use the following command to initialize submodules before building 
from source.

```bash
git submodule update --init --recursive
```

### Build Java

```shell 
mvn -DskipTests clean install
```

After finish, you can find the target distribution in the `dl-on-flink-dist/target`
folder.

### Build Python

#### Install from Source
You can run the following commands to install the Python packages from source

```sh
# Install dl-on-flink-framework first
pip install dl-on-flink-framework/python

# Note that you should only install one of the following as they require
# different versions of Tensorflow 
# For tensorflow 1.15.x
pip install dl-on-flink-tensorflow/python
# For tensorflow 2.4.x
pip install dl-on-flink-tensorflow-2.x/python
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
