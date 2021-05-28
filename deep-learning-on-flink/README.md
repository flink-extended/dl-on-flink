[![Build Status](https://travis-ci.org/alibaba/flink-ai-extended.svg?branch=master)](https://travis-ci.org/alibaba/flink-ai-extended)

# deep-learning-on-flink

Deep Learning on Flink aims to integrate Flink and deep learning frameworks (e.g. TensorFlow, PyTorch, etc). 
It runs the deep learning tasks inside a Flink operator, so that Flink can help establish a distributed environment, 
manage the resource, read/write the records and handle the failures.

Currently, Deep Learning on Flink supports TensorFlow and PyTorch.

**contents**

- [TensorFlow support](#tensorflow-support)
  * [Support Version](#support-version)
  * [Quick Start](#quick-start)
    + [Setup](#setup)
    + [Build From Source](#build-from-source)
    + [Build Source in virtual environment](#build-source-in-virtual-environment)
    + [Example](#example)
  * [Distributed Running](#distributed-running)
    + [Deployment](#deployment)
    + [Running Distributed Programs](#running-distributed-programs)
  * [Distributed Running Example](#distributed-running-example)
    + [Setup & Build](#setup---build)
    + [Start Service](#start-service)
    + [Prepare data & code](#prepare-data---code)
    + [Submit train job](#submit-train-job)
    + [Visit Flink Cluster](#visit-flink-cluster)
    + [Stop all docker containers](#stop-all-docker-containers)
    + [Summary](#summary)
  * [Optional Tools](#optional-tools)
    + [Build framework and tensorflow python package Independently](#build-framework-and-tensorflow-python-package-independently)
    + [Build custom virtual environment package](#build-custom-virtual-environment-package)
- [Structure](#structure)
- [For More Information](#for-more-information)
- [License](#license)

# TensorFlow support
TensorFlow is a deep learning system developed by Google and open source, which is widely used in the field of deep learning. There are many inconveniences in distributed use and resource management of native TensorFlow, but it can not integrate with the existing widely used large data processing framework.

Flink is a data processing framework. It is widely used in data extraction, feature preprocessing and data cleaning.

This project combines TensorFlow with Flink and provides users with more convenient and useful tools.
**Currently, Flink job code can be written in both java with Flink Java API and in python with PyFlink. The algorithm code is written in python.**

## Support Version
TensorFlow: 1.15.0 & 2.3.1

Flink: 1.11.x
 
## Quick Start

### Setup

**Requirements**
1. python: 3.7
1. cmake >= 3.6
1. java 1.8
1. maven >=3.3.0

**Install python3**

macOS
```shell
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
export PATH="/usr/local/bin:/usr/local/sbin:$PATH"
brew install python@3.7
```
Ubuntu
```shell
sudo apt install python-dev
```

**Install pip**

```shell 
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

Ubuntu you can install with command:
```shell
sudo apt install python-pip
```

**Install pip dependencies**
Install the pip package dependencies (if using a virtual environment, omit the --user argument):
```shell
pip install -U --user pip six numpy wheel mock grpcio grpcio-tools
```
**Install cmake**

cmake version must >= 3.6

[cmake download page](https://cmake.org/download/) 

**Install java 8**

[java download page](http://www.oracle.com/technetwork/java/javase/downloads/index.html)

**Install maven**

maven version >=3.3.0

[download maven page](http://maven.apache.org/download.cgi)

```shell
tar -xvf apache-maven-3.6.1-bin.tar.gz
mv -rf apache-maven-3.6.1 /usr/local/
```
configuration environment variables
```shell
MAVEN_HOME=/usr/local/apache-maven-3.6.1
export MAVEN_HOME
export PATH=${PATH}:${MAVEN_HOME}/bin
```

### Build From Source
**Compiling source code depends on tensorflow. Compiling flink-ml-tensorflow module will automatically install tensorflow 1.15.0**

```shell 
mvn -DskipTests=true clean install
```
**If you run all tests, this step may take a long time, about 20 minutes, and wait patiently.**
**You can also skip the test run command: mvn -DskipTests=true clean install**

**Optional Commands**
```shell
# run all tests
mvn clean install

# skip unit tests
mvn -DskipUTs=true clean install

# skip integration tests
mvn -DskipITs=true clean install
```
If the above command is executed successfully, congratulations on your successful 
deployment of flink-ai-extended. Now you can write algorithm programs.

### Build Source in virtual environment

* change project [pom.xml](pom.xml) item pip.install.option from --user to -U
* create virtual environment:

```shell 
virtualenv tfenv
```
* enter the virtual environment

```shell 
source tfenv/bin/activate
```
* install pip dependencies

```shell 
pip install -U pip six numpy wheel mock grpcio grpcio-tools
```
* build source

```shell 
mvn clean install
```
* exit from virtual environment
```shell 
deactivate
```
                  
### Example

1. tensorflow add example
    **<p>python code:</p>**

```python
import tensorflow as tf
import time
import sys
from flink_ml_tensorflow.tensorflow_context import TFContext

def build_graph():
    global a
    i = 1
    a = tf.placeholder(tf.float32, shape=None, name="a")
    b = tf.reduce_mean(a, name="b")
    r_list = []
    v = tf.Variable(dtype=tf.float32, initial_value=tf.constant(1.0), name="v_" + str(i))
    c = tf.add(b, v, name="c_" + str(i))
    add = tf.assign(v, c, name="assign_" + str(i))
    sum = tf.summary.scalar(name="sum_" + str(i), tensor=c)
    r_list.append(add)
    global_step = tf.contrib.framework.get_or_create_global_step()
    global_step_inc = tf.assign_add(global_step, 1)
    r_list.append(global_step_inc)
    return r_list
    
def map_func(context):
    tf_context = TFContext(context)
    job_name = tf_context.get_role_name()
    index = tf_context.get_index()
    cluster_json = tf_context.get_tf_cluster()
    
    cluster = tf.train.ClusterSpec(cluster=cluster_json)
    server = tf.train.Server(cluster, job_name=job_name, task_index=index)
    sess_config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False,
                                 device_filters=["/job:ps", "/job:worker/task:%d" % index])
    t = time.time()
    if 'ps' == job_name:
        from time import sleep
        while True:
            sleep(1)
    else:
        with tf.device(tf.train.replica_device_setter(worker_device='/job:worker/task:' + str(index), cluster=cluster)):
            train_ops = build_graph()
            hooks = [tf.train.StopAtStepHook(last_step=2)]
            with tf.train.MonitoredTrainingSession(master=server.target, config=sess_config,
                                                    checkpoint_dir="./target/tmp/s1/" + str(t),
                                                    hooks=hooks) as mon_sess:
                while not mon_sess.should_stop():
                    print (mon_sess.run(train_ops, feed_dict={a: [1.0, 2.0, 3.0]}))
                    sys.stdout.flush()

``` 
   **<p>java code:</p>**
   add maven dependencies
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.alibaba</groupId>
    <artifactId>flink-ai-extended-examples</artifactId>
    <version>0.3.0</version>
    <packaging>jar</packaging>
    <dependencies>
        <dependency>
            <groupId>com.alibaba.flink.ml</groupId>
            <artifactId>flink-ml-tensorflow</artifactId>
            <version>0.3.0</version>
        </dependency>
        <dependency>
            <groupId>org.apache.curator</groupId>
            <artifactId>curator-framework</artifactId>
            <version>2.7.1</version>
        </dependency>
        <dependency>
            <groupId>org.apache.curator</groupId>
            <artifactId>curator-test</artifactId>
            <version>2.7.1</version>
            <exclusions>
                <exclusion>
                    <groupId>com.google.guava</groupId>
                    <artifactId>guava</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
            <version>20.0</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.1</version>
                <configuration>
                    <source>1.8</source>
                    <target>1.8</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```
*You can refer to the following POM*

[example pom.xml](flink-ml-examples/pom.xml)

```java
class Add{
    public static void main(String args[]) throws Exception{ 
    	// local zookeeper server.
        TestingServer server = new TestingServer(2181, true);
        String script = "./add.py";
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        // if zookeeper has other address
        Map<String, String> prop = new HashMap<>();
        prop.put(MLConstants.CONFIG_STORAGE_TYPE, MLConstants.STORAGE_ZOOKEEPER);
        prop.put(MLConstants.CONFIG_ZOOKEEPER_CONNECT_STR, "localhost:2181");
        TFConfig config = new TFConfig(2, 1, prop, script, "map_func", null);
        TFUtils.train(streamEnv, null, config);
        JobExecutionResult result = streamEnv.execute();
        server.stop();
    } 
}
```

## Distributed Running
### Deployment
**Distributed running environment:**

* **Start zookeeper service** 
https://zookeeper.apache.org/
* **Prepare python virtual environment:**
virtual environment workflow is shown in the following figure:
![venv](doc/image/usage/venv.jpg)

1. Build python virtual environment package. 
2. Put virtual environment package to a share file system such as HDFS.
3. Configure the virtual environment package address in build Flink machine learning job configuration
(TensorFlow:TFConfig, PyTorch:PyTorchConfig).
4. When running Flink job, each node downloads the virtual environment package and extracts it locally

    [[build docker script]](docker/build_cluster/build_flink_image.sh) 

    [[build virtual environment script]](docker/build_cluster/build_venv_package.sh)

* **Prepare Flink Cluster** 
1. [Flink standalone mode](https://ci.apache.org/projects/flink/flink-docs-release-1.8/ops/deployment/cluster_setup.html)
2. [Flink yarn mode](https://ci.apache.org/projects/flink/flink-docs-release-1.8/ops/deployment/yarn_setup.html)

### Running Distributed Programs

* **Developing Algorithmic Program** 

    [TensorFlow](flink-ml-examples/src/test/python/mnist_dist.py)

    [PyTorch](flink-ml-examples/src/test/python/all_reduce_test.py)

* **Developing Flink Job Program**

    [TensorFlow Train](flink-ml-examples/src/main/java/com/alibaba/flink/ml/examples/tensorflow/mnist/MnistDist.java) 
    
    [PyTorch Run](flink-ml-examples/src/main/java/com/alibaba/flink/ml/examples/pytorch/PyTorchRunDist.java)
    
* **Submit Flink job**

    [Submit flink job](https://ci.apache.org/projects/flink/flink-docs-release-1.8/ops/cli.html)

## Distributed Running Example

### Setup & Build
* **install docker**

[docker install](https://docs.docker.com/install/)

* **install flink-ai-extended**
```shell 
mvn -DskipTests=true clean install
```

* **Change work dir**
```shell 
cd docker/build_cluster/
```

**<font color=Red>Pay attention: projectRoot is flink-ai-extended project root path.</font>**



* **Build Docker Image**
[[build docker script]](docker/build_cluster/build_flink_image.sh)
```shell
sh  build_flink_image.sh
``` 
You can find flink image to use command:
```shell
docker images 
```

* **Build Virtual Environment**
[[build virtual environment script]](docker/build_cluster/build_venv_package.sh)
```shell 
sh build_venv_package.sh
```
You can find tfenv.zip in temp/test/ directory.

### Start Service
1. start zookeeper
2. start hdfs
3. start flink cluster

* **Start zookeeper**

[[start zookeeper script]](docker/build_cluster/start_zookeeper.sh)
```shell
sh start_zookeeper.sh
``` 
* **Start HDFS**

[[start hdfs script]](docker/build_cluster/start_hdfs.sh)
```shell 
sh start_hdfs.sh
```
* **Start flink cluster**

[[start flink cluster script]](docker/build_cluster/start_flink.sh)
```shell 
sh start_flink.sh
```

**<u>Also can start all service</u>**

[[start service script]](docker/build_cluster/start_cluster.sh)
```shell 
sh start_cluster.sh
```

### Prepare data & code

* **Copy virtual environment package to hdfs**

```shell 
docker exec flink-jm /opt/hadoop-2.8.0/bin/hadoop fs -put -f /opt/work_home/temp/test/tfenv.zip /user/root/tfenv.zip
```

* **Download mnist data**
```shell 
sh download_mnist_data.sh
```

* **Put train data to docker container**
```shell
docker cp ${projectRoot}/flink-ml-examples/target/data/ flink-jm:/tmp/mnist_input 
```

* **Package user python code**
```shell 
cd ${projectRoot}/flink-ml-examples/target/
mkdir code && cp ${projectRoot}/flink-ml-examples/src/test/python/* code/
zip -r ${projectRoot}/flink-ml-examples/target/code.zip code
```

* **Put code package to hdfs**
```shell 
docker exec flink-jm /opt/hadoop-2.8.0/bin/hadoop fs -put -f /opt/work_home/flink-ml-examples/target/code.zip hdfs://minidfs:9000/user/root/
```

### Submit train job
```shell 
docker exec flink-jm flink run  -c com.alibaba.flink.ml.examples.tensorflow.mnist.MnistDist /opt/work_home/flink-ml-examples/target/flink-ml-examples-0.3.0.jar --zk-conn-str minizk --mode StreamEnv --setup /opt/work_home/flink-ml-examples/src/test/python/mnist_data_setup.py --train mnist_dist.py --envpath hdfs://minidfs:9000/user/root/tfenv.zip --mnist-files /tmp/mnist_input --with-restart false --code-path hdfs://minidfs:9000/user/root/code.zip 
```
### Visit Flink Cluster
[Flink Cluster Address](http://localhost:8081)

### Stop all docker containers
[[stop all script]](docker/build_cluster/stop_cluster.sh)
```shell 
sh stop_cluster.sh
```
### Summary
*In the example above, zookeeper, flink, and HDFS can be deployed on different machines.*

*You can also use existing zookeeper, hdfs, flink cluster.*
     
## Optional Tools

### Build framework and tensorflow python package Independently
[build script](tools/build_wheel.sh)

run build_wheel.sh script, you will find python package in dist dir.
you can install the package with commend:
```shell 
pip install --user $package_path
```
### Build custom virtual environment package
running distributed programs you need a virtual environment package to upload to hdfs.

[build virtual environment script](tools/create_venv_package.sh)

you can change the script to add some extended python package.

# Structure

![structure](image/struct.jpg)
1. AM registers its address to zookeeper.
2. Worker and Ps get AM address from zookeeper.
3. Worker and Ps register their address to AM.
4. AM collect all Worker and Ps address.
5. Worker and Ps get cluster information.
6. Worker and Ps start algorithm python process.

# For More Information

[Design document](doc/design.md)

# License
[Apache License 2.0](LICENSE)
