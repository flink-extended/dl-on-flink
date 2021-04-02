# Running Examples

We provide users with some python examples to illustrate the usage of AI Flow and more examples will be added soon.
Before you try the example, please make sure you have installed AI-Flow(locally or in Docker) following the instructions in [QuickStart](https://github.com/alibaba/flink-ai-extended/blob/master/flink-ai-flow/QUICKSTART.md)

### Python Examples

#### [1. Simple Transform Scheduled by AirFlow](python_examples/python_codes/simple_transform_airflow)
This example will read a csv file and calculate the square of each data point and then write to a new file to save results. 
The example codes under `python_examples/python_codes/simple_transform_airflow` dir follows the procedure **read file -> transform -> write file** to achieve the goal.
Besides, it is scheduled by AirFlow.


To run this example:
1. Make sure the AI Flow server, Airflow server and notification server is started on the target machine.

If you are in your local machine, please start them following guidance in [QuickStart](https://github.com/alibaba/flink-ai-extended/blob/master/flink-ai-flow/QUICKSTART.md).

If you are in Docker environment, these services should have been started.

2. Configure and Run script

Configure AirFlow Deploy path in `python_examples/project.yaml`. Then run commands:
```shell
 cd python_examples
 export PYTHONPATH=.
 python python_codes/simple_transform_airflow/simple_transform_airflow.py
```

When the program finishes, you should be able to view transform result in `sink_data.csv` file under `python_examples/python_codes/simple_transform_airflow` dir.

If you do not get the expected output, check logs in [Web UI](127.0.0.1:8080) or in log dir under the AirFlow Deploy dir.


### Simple Examples
See [QuickStart](https://github.com/alibaba/flink-ai-extended/blob/master/flink-ai-flow/QUICKSTART.md).
