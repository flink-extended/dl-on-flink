import os

FLINK_HOME = "/Users/chenwuchao/soft/apache/flink-1.9.0/" #os.environ["FLINK_HOME"]
FLINK_BIN = FLINK_HOME + "/bin/flink"
JOB_MAIN_CLASS = "com.alibaba.flink.ml.workflow.runtime.TransformJob" #os.environ["JOB_MAIN_CLASS"]
JOB_MAIN_JAR = "/Users/chenwuchao/code/github/flink-ai-extended/flink-ml-workflow-shade/target/flink-ml-workflow-shade-0.1.0.jar" #os.environ["JOB_MAIN_JAR"]
