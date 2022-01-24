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
docker exec flink-jm flink run  -c org.flinkextended.flink.ml.examples.tensorflow.mnist.MnistDist /opt/work_home/flink-ml-examples/target/flink-ml-examples-0.3.0.jar --zk-conn-str minizk --mode StreamEnv --setup /opt/work_home/flink-ml-examples/src/test/python/mnist_data_setup.py --train mnist_dist.py --envpath hdfs://minidfs:9000/user/root/tfenv.zip --mnist-files /tmp/mnist_input --with-restart false --code-path hdfs://minidfs:9000/user/root/code.zip 
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

### Build custom virtual environment package
running distributed programs you need a virtual environment package to upload to hdfs.

[build virtual environment script](tools/create_venv_package.sh)

you can change the script to add some extended python package.