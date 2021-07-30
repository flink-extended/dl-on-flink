## Guidance on Running Wide and Deep Example

### Intro
This example, named 'wide and deep', aims at showing the mix use of [Flink-AI-Flow](https://github.com/alibaba/flink-ai-extended/blob/master/flink-ai-flow/QUICKSTART.md) and [TF-on-Flink](https://github.com/alibaba/flink-ai-extended/tree/master/deep-learning-on-flink). 
In this example, we will train a [DNNLinearCombinedClassifier](https://arxiv.org/abs/1606.07792) for a binary classification task.
In the codes, we will show how to train a model with TF-on-Flink, which can directly consume training samples from flink and how to define and execute the streaming training and streaming prediction tasks with AIFlow.

### Environment Requirements
1. Flink-AI-Flow([ref](https://github.com/alibaba/flink-ai-extended/blob/master/flink-ai-flow/QUICKSTART.md))
2. TF-on-Flink([ref](https://github.com/alibaba/flink-ai-extended/tree/master/deep-learning-on-flink))
3. Flink(1.11+)
4. Kafka(1.x or 2.x)
5. Hadoop
6. Zookeeper

After building TF-on-Flink and installing Flink-AI-Flow, we need to put `.jar` files under the `flink-1.11.3/lib` dir.
Find the  `flink-ml-tensorflow-0.4-SNAPSHOT-jar-with-dependencies.jar` in your TF-on-Flink project's target dir.
Then copy the jar and the https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka_2.11/1.11.3/flink-sql-connector-kafka_2.11-1.11.3.jar into `flink-1.11.3/lib` dir. 


### Usage
#### HDFS Initialization

- Edit `$HADOOP_HOME/etc/hadoop/core-site.xml` of hadoop:
    ```shell
    <property>
    <name>fs.default.name</name>
    <value>hdfs://127.0.0.1:9000</value>
    </property>
    ```
- Start hadoop
    ```shell
    hadoop namenode -format
    $HADOOP_HOME/sbin/start-all.sh
    ```
- Create directory in hdfs and upload codes
  
    The `code.zip` must be produced by zipping the `wide_and_deep/dependencies/python/code` directory.
    If users define their own logic in the python files under this dir, they should reproduce the zip file by running
    ```shell
    cd wide_and_deep/dependencies/python && zip -r code.zip code
    ```
    ```shell
    hdfs dfs -mkdir /demo
    hdfs dfs -put ./code.zip /demo
    ```

  
#### Kafka Initialization
In the project, we will use Kafka to generate a data stream and the dataset used is `census_data/adult.data`. 
To download the dataset, run `python wide_and_deep/dependencies/python/code/census_dataset.py` to save the dataset in `/tmp` dir.
   
Then, run `python wide_and_deep/dependencies/python/kafka_util/census_kafka_data.py` to create topics and generate kafka data stream.

#### Start up the whole environment
- Start flink:
```shell
start-cluster.sh
```
- Start AIFlow Server
```shell
start-all-aiflow-services.sh mysql://admin:admin@127.0.0.1/airflow
```
Note, the user should refer to QuickStart for starting AIFlow correctly.

#### Run the Wide and Deep project's workflow
Before running the demo, the user need to check the 2 project.yaml is configured properly:

```shell
1. flink-ai-flow/examples/wide_and_deep/project.yaml
2. flink-ai-flow/examples/wide_and_deep/dependencies/python/code/project.yaml
```
Make sure these 2 files use same config.

Only for the first time of running the project, we need to init the AIFlow:
```shell
python wide_and_deep/workflows/wdl/census_init.py 
```

Then, run the workflow:
```shell
export PYTHONPATH=wide_and_deep/dependencies/python
python wide_and_deep/workflows/wdl/wdl.py
```

#### Run the Wide and Deep project's workflow with Flink jar job
You can also run the workflow that use Flink jar to run the stream predict preprocessing. To do that you want to 
make the Flink job jar with the following command at wide_and_deep/java/preprocess:
```
mvn clean package
```

Put the `wide_and_deep/java/preprocess/target/wdl-preprocess-0.1-SNAPSHOT.jar` in `wide_and_deep/dependencies/jar`.

Run the workflow with argument:
```shell
export PYTHONPATH=wide_and_deep/dependencies/python
python wide_and_deep/workflows/wdl/wdl.py true
```

#### Check results
After launching the project, users can go to [AIFlow Web UI](127.0.0.1:8080) to check all jobs are scheduled correctly and 
   go to Flink Web UI to make sure the flink job run as expected.
   Or go to Kafka Cli to check continuous generated prediction output.
