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
Find the `flink-ml-dist-0.3.0.jar`, `flink-ml-framework-0.3.0.jar`, `flink-ml-operator-0.3.0.jar`, `flink-ml-tensorflow-0.3.0.jar` in your TF-on-Flink project's target dir.
Then copy these 4 jars and the `jar_dependencies/flink-sql-connector-kafka_2.11-1.11.3.jar` and `jar_dependencies/kafka-clients-2.8.0.jar`into `flink-1.11.3/lib` dir. 


### Usage
#### HDFS Initialization

- Edit `/usr/local/Cellar/hadoop/3.3.0/libexec/etc/hadoop/core-site.xml` of hadoop:
    ```shell
    <property>
    <name>fs.default.name</name>
    <value>hdfs://127.0.0.1:9000</value>
    </property>
    ```
- Start hadoop
    ```shell
    hadoop namenode -format
    /usr/local/Cellar/hadoop/3.3.0/sbin/start-all.sh
    ```
- Create directory in hdfs and upload codes
    ```shell
    hdfs dfs -mkdir /demo
    hdfs dfs -put ./code.zip /demo
    ```
  Note, the `code.zip` must be produced by zipping the `wide_and_deep_example/python_codes/code` directory.
  If users define their own logic in the python files under this dir, they should reproduce the zip file by running
  ```shell
  rm -r ./temp && cd python_codes/ && zip -r ../code.zip ./code && cd ..
  ```
  
#### Kafka Initialization
In the project, we will use Kafka to generate a data stream and the dataset used is `census_data/adult.data`. 
   To download the dataset, run `python python_codes/code/census_dataset.py` to save the dataset in `/tmp` dir.
   
Then, run `python python_codes/kafka_util/census_kafka_data.py` to create topics and generate kafka data stream.

#### Start up the whole environment
- Start flink:
```shell
start-cluster.sh
```
- Start AIFlow
```shell
start-aiflow.sh mysql://admin:admin@127.0.0.1/airflow
```
Note, the user should refer to QuickStart for starting AIFlow correctly.

#### Run the Wide and Deep project's workflow
Before running the demo, the user need to check the 2 project.yaml is configured properly:

```shell
1. flink-ai-flow/examples/wide_and_deep_example/project.yaml
2. flink-ai-flow/examples/wide_and_deep_example/python_codes/code/project.yaml
```
Make sure these 2 files use same config(e.g. the `airflow_deploy_path`)

Only for the first time of running the project, we need to init the AIFlow:
```shell
python python_codes/census_init.py 
```

Then, run the workflow:
```shell
python python_codes/census_workflow.py
```

#### Check results
After launching the project, users can go to [AIFlow Web UI](127.0.0.1:8080) to check all jobs are scheduled correctly and 
   go to Flink Web UI to make sure the flink job run as expected.
   Or go to Kafka Cli to check continuous generated prediction output.
