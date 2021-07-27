

# Tutorial

This tutorial will show you how to write a workflow using AI Flow and walk you through some fundamental AI Flow concepts, objects, and their usage.



## Target

In the tutorial, we will write a simplified machine learning workflow to train a KNN model using iris training dataset and verify the effectiveness of the model in prediction job. 

Furthermore, in this workflow, the training job will be a periodical batch job using scikit learn library. Once the batch training job finishes, we will start a validation job to validate the correctness and generalization ability of the generated model. Finally, when a model is validated, we will start a flink  job to utilize the model to do prediction(inference) and save predication results to a local file.


## Configuration of Flink AI Flow Server
To work with Flink AI Flow, we should add some configurations for Flink AI Flow Server.
The config file, named as `master.yaml`, should locate in `$AIRFLOW_HOME` or `~/airflow` directory.

Remember to update fields according to your own environment.

### master.yaml
```yaml
 # Config of master server
# endpoint of AI Flow Server
server_ip: localhost
server_port: 50051
# uri of database backend of AIFlow server
db_uri: {db_uri} # sqlite:////path/to/airflow/aiflow.db or mysql://username:password@127.0.0.1/airflow
# type of database backend in master
db_type: {db_type} # sql_lite or mysql
# whether to start the scheduler service
start_scheduler_service: True
# uri of notification service
notification_uri: localhost:50052
# scheduler config
scheduler:
  scheduler_class_name: ai_flow_plugins.scheduler_plugins.airflow.airflow_scheduler.AirFlowScheduler
  scheduler_config:
    airflow_deploy_path: /absolute/path/to/airflow/airflow_deploy
    notification_service_uri: localhost:50052
```

## Prepare Project Directory
Before writing the workflow, we should prepare a project directory as follows:

```
tutorial_project/
        |- workflows/
           |- tutorial_workflow/
              |- tutorial_workflow.py 
              |- tutorial_workflow.yaml 
        |- dependencies/
            |-python 
            |-jar
        |- resources/
        └─ project.yaml
```

`tutorial_project` is the root directory of the project and `workflows` is used to save codes and config files of workflows in this project. In this tutorial, we will create a `tutorial_workflow` directory for our workflow. In the `tutorial_workflow.py`, we will add our actual codes for defining the workflow and `tutorial_workflow.yaml` includes some configs of our workflow.

The `dependecies` directory is used to save python/java/go dependencies that will be used by our workflow.

The `resources` directory is for saving all other files(e.g., datasets) that will be used by the project.

The `project.yaml` is for configuring the whole project. 

Now let's go over above config files one by one.

### project.yaml
Here is an example of the project.yaml for tutorial project.
```yaml
project_name: tutorial_project
server_ip: localhost
server_port: 50051
blob:
  blob_manager_class: ai_flow_plugins.blob_manager_plugins.local_blob_manager.LocalBlobManager
```
In `project_name`, we define the project name, which will be the default namespace of workflows in this project as well. 

> Namespace in Flink AI Flow is used for isolation. Each workflow can only send events to its own namespace while it can listen on multiple namespaces. The reason for enabling listening on multiple namespaces is that the workflow could be triggered by external events from notification service.

For `server_ip` and `server_port`,  they tell where the `AIFlowServer` is running on.

Then, we configure the `blob` property which tells Flink AI Flow where to execute workflows in this project(i.e., local or remote env).

Here we choose to use `LocalBlobManager` and as a result, the project will run locally. 

We currently also provide `OssBlobManager` which allows users to submit and run their workflow remotely.

### tutorial_workflow.yaml 
Next, we will introduce how to write the workflow configuration yaml file.
```yaml
train:
  job_type: python
  periodic_config:
    interval: '0,0,0,60' # The train job will be executed every 60s

validate:
  job_type: python

predict:
  job_type: flink
  properties:
    run_mode: cluster
    flink_run_args: #The flink run command args(-pym, -pyexec etc.). It's type is List.
      - -pyexec
      - /path/to/bin/python # path to your python3.7 executable path
```
In the workflow yaml, we define the properties of each job. 

For `train` job, its job type is `python`, which means the user defined logic in this job will be executed using `python`. Besides, we set the `periodic_config` to be `interval: '0,0,0,60'` which means the job will be executed every 60s.

For `validate` job, we only config its job type to be `python`.

For `predict` job, we set its job type to be `flink`, which means this job is a flink job. In addition, to use flink, we need to set some flink-specific properties including `run_mode` (cluster or local) and `flink_run_args`. For the `flink_run_args`, we follow the list format of `yaml` to add the args such as the `-pyexec`.

## Writing the Workflow Code

Now, let's start coding to implement workflow described in Target section

### Importing Modules
In Flink AI Flow, a workflow is just a Python script. Let’s create `tutorial_workflow.py` and start by importing the libraries we will need.


```python
import os

# Entry of accessing Flink AI Flow API
import ai_flow as af

# Enum class for marking different stages of our workflow
from ai_flow.model_center.entity.model_version_stage import ModelVersionEventType

# Util functions provided by ai_flow
from ai_flow.util.path_util import get_file_dir

# User-defined processors; we will introduce them in tutorial_processors.py
from tutorial_processors import DatasetReader, ModelTrainer, ValidateDatasetReader, ModelValidator, Source, Sink, \
    Predictor

# Declare the location of dataset
DATASET_URI = os.path.abspath(os.path.join(__file__, "../../../")) + '/resources/iris_{}.csv'

```

###  Defining a Training Job
In our design, the workflow in Flink AI Flow is a DAG(Directed Acyclic Graph) or to be more specific, it is a [AIGraph](). Each node in the graph is an [AINode](), which contains a processor. Users should write their custom logic in the processor. 

In the AIGraph, nodes are connected by 2 types of edges. The first one is named as `DataEdge` which means the destination node depends on the output of the source node. The other is `ControlEdge` which means the destination node depends on the control conditions from source node. We will dive deeper into this kind of edges later.

For now, let's concentrate on the set of AINodes connected by only data edges. Such a set of nodes and data edges between them constitutes a sub-graph. This sub-graph, together with the predefined job config in workflow config yaml, is mapped to a Job by Flink AI Flow framework.

So, to summarize, each Flink AI Flow job is made up of a job config, some AINodes and the data edges between those nodes. 

These concepts seem to be a little difficult, but do not worry. Let's look at some code snippets, and you will find it pretty easy to define a job with provided API of Flink AI Flow.

In the following codes, we define a training job of our workflow:
```python
    artifact_prefix = af.current_project_config().get_project_name() + "."
    # Training of model
    with af.job_config('train'):
        # Register metadata of training data(dataset), `uri` refers to the file path
        train_dataset = af.register_dataset(name=artifact_prefix + 'train_dataset',
                                            uri=DATASET_URI.format('train'))
        # Read data from the registered dataset with user-defined read_dataset_processor
        train_read_dataset = af.read_dataset(dataset_info=train_dataset,
                                             read_dataset_processor=DatasetReader())

        # Register model metadata
        train_model = af.register_model(model_name=artifact_prefix + 'KNN',
                                        model_desc='KNN model')
        # Train the model with user-defined training_processor
        train_channel = af.train(input=[train_read_dataset],
                                 training_processor=ModelTrainer(),
                                 model_info=train_model)
```

In the above codes, methods like `register_dataset` and `register_model` are just used to save same metadata(e.g., the name of the model or the uri of the dataset) into the database. The return value of these methods are some metadata objects(e.g. `DatasetMeta` or `ModelMeta`), which can be used to query database or serve as parameters of other methods.

On the other hand, `read_dataset()` and `train()` are of another type. We call them `Operators` as they have some specific semantics and will create corresponding `AINodes`. Then, how do we define the data dependency of those newly created nodes? We just put the output of `read_dataset` method into the `input` arg of `train()` method. Such codes imply input of the training node created by`train()` is the output of the node created by `read_dataset()` .  The return values of methods like `train()` are `Channel` or list of `Channel`s.

In Flink AI Flow, `Channel` represents the output of AINodes. More vividly, `Channel` is one end of the `DataEdge`. The following picture shows the relation among `AINodes`, `DataEdges` and `Channels`:

![](images/tutorial/channels.png)

In the example, AINode N0 has 3 outputs(i.e., 3 channels whose source node is N0). We can make N1 accepts the c0 and c1 channels and N2 accepts c1 and c2 channels. Accordingly, there are 4 DataEdges in all. With such design, we can manipulate the data dependencies more flexibly and reuse the data easier.



Currently, the only puzzle left is how do we implement the processors including `DatasetReader()` and `ModelTrainer()`. We will introduce them later in [Implementing custom processor Processors](#implementing-custom-processors) section. Next, let's pay attention to defining the Validation and Prediction jobs.

###  Defining the Validation Job and the Prediction Job

Here we define the left 2 jobs of our workflow. They are pretty similar to what we have done in defining the training job.

```python
		# Validation of model
    with af.job_config('validate'):
        # Read validation dataset
        validate_dataset = af.register_dataset(name=artifact_prefix + 'validate_dataset',
                                               uri=DATASET_URI.format('test'))
        # Validate model before it is used to predict
        validate_read_dataset = af.read_dataset(dataset_info=validate_dataset,
                                                read_dataset_processor=ValidateDatasetReader())
        validate_artifact_name = artifact_prefix + 'validate_artifact'
        validate_artifact = af.register_artifact(name=validate_artifact_name,
                                                 uri=get_file_dir(__file__) + '/validate_result')
        validate_channel = af.model_validate(input=[validate_read_dataset],
                                             model_info=train_model,
                                             model_validation_processor=ModelValidator(validate_artifact_name))

    # Prediction(Inference) using flink
    with af.job_config('predict'):
        # Read test data and do prediction
        predict_dataset = af.register_dataset(name=artifact_prefix + 'predict_dataset',
                                              uri=DATASET_URI.format('test'))
        predict_read_dataset = af.read_dataset(dataset_info=predict_dataset,
                                               read_dataset_processor=Source())
        predict_channel = af.predict(input=[predict_read_dataset],
                                     model_info=train_model,
                                     prediction_processor=Predictor())
        # Save prediction result
        write_dataset = af.register_dataset(name=artifact_prefix + 'write_dataset',
                                            uri=get_file_dir(__file__) + '/predict_result.csv')
        af.write_dataset(input=predict_channel,
                         dataset_info=write_dataset,
                         write_dataset_processor=Sink())

```

In above codes, we use 3 new predefined operators by Flink AI Flow: `model_validate()` , `predict()`, `write_dataset()`. 

In addition, in Flink AI Flow, if they don't find the operators needed, users can also define their own operators with the `user_define_operation()` API.

### Defining the Relation between Jobs
We now have defined 3 jobs. Each job is a sub-graph and have some nodes connected by `DataEdge`s. Then we will need to define the relation between jobs to make sure our workflow is scheduled and run correctly. As we have mentioned in [Target](#Target) section, the training job will run periodically and once the training finishes, the validation job should be started to validate the latest generated model. If there is a model passes the validation and get deployed, we should (re)start the downstream prediction job using flink to get better inference.



After reviewing above description, we find that some upstream jobs control the downstream jobs. For instance, the training job controls the (re)start of validation job. We keep using AIGraph abstraction to depicts these control relations. But at this time, each AINode in this new AIGraph is a job(a subgraph in fact!). Edges to connect these job nodes are named as `ControlEdge`. We also call such control relation as *control dependencies*.

In Flink AI Flow, we implement control dependencies via *Events*. That is, the upstream job can send specific events to downstream jobs and downstream jobs will take actions due to the events and rules defined by users.

```python
		# Define relation graph connected by control edge: train -> validate -> predict
    af.action_on_model_version_event(job_name='validate',
                                     model_version_event_type=ModelVersionEventType.MODEL_GENERATED,
                                     model_name=train_model.name)
    af.action_on_model_version_event(job_name='predict',
                                     model_version_event_type=ModelVersionEventType.MODEL_VALIDATED,
                                     model_name=train_model.name)
```

In above codes, the first `ControlEdge` we defined is that the `validate` job (Note, this job name is defined in the yaml file of workflow configs) will be restarted(the default action) when there is a `MODEL_GENERATED` event of training model received by the scheduler. The second  `ControlEdge` we defined is that the `predict` job will be restarted when there is a `MODEL_VALIDATED` event of training model received by the scheduler. 

Besides, the well-defined out-of-box API for managing machine learning jobs, Flink AI Flow exposes the extremely expressive API `action_on_events()` to allow users write their own event-based control dependencies.

## Managing the Workflow

We have finished the definition of the workflow. Now we need to submit and run it.

```python
def run_workflow():
    # Init project
    af.init_ai_flow_context()

    artifact_prefix = af.current_project_config().get_project_name() + "."
    # Training of model
    with af.job_config('train'):
        ...
    # Validation of model
    with af.job_config('validate'):
        ...
    # Prediction(Inference) using flink
    with af.job_config('predict'):
        ...

    # Define relation graph connected by control edge: train -> validate -> predict
    af.action_on_model_version_event(job_name='validate',
                                     model_version_event_type=ModelVersionEventType.MODEL_GENERATED,
                                     model_name=train_model.name)
    af.action_on_model_version_event(job_name='predict',
                                     model_version_event_type=ModelVersionEventType.MODEL_VALIDATED,
                                     model_name=train_model.name)
    # Submit and run workflow
    af.workflow_operation.submit_workflow(af.current_workflow_config().workflow_name)
    af.workflow_operation.start_new_workflow_execution(af.current_workflow_config().workflow_name)

if __name__ == '__main__':
    run_workflow()
```

Above codes show the basic use of workflow administration API. You may notice that our naming convention of workflow management API seems inconsistent: `submit_workflow()` and `start_new_workflow_execution()`. 

In fact, in our design, `Workflow` defines the execution logic of a set of jobs together with control edges among them. But after definition, the workflow will not be run. Instead, the workflow will be scheduled and triggered by the scheduler(e.g., Airflow scheduler) after calling `start_new_workflow_execution()`. The execution entity of workflow is named as `WorkflowExecution`, which is created by the scheduler. One advantage of this design is that reproducing a workflow can be much easier as we can locate the past workflow execution with all environments conveniently.



## Implementing custom processors

As we have mentioned, users need to write their own logic in processors for each job. Currently, Flink AI Flow supports `bash`, `python` and `flink` processors.

The following codes are the `DatasetReader` processor whose type is `python`:

```python
EXAMPLE_COLUMNS = ['sl', 'sw', 'pl', 'pw', 'type']

class DatasetReader(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        """
        Read dataset using pandas
        """
        # Gets the registered dataset meta info
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        # Read the file using pandas
        train_data = pd.read_csv(dataset_meta.uri, header=0, names=EXAMPLE_COLUMNS)
        # Prepare dataset
        y_train = train_data.pop(EXAMPLE_COLUMNS[4])
        return [[train_data.values, y_train.values]]
```

As you can see, it is just a python program using pandas library without any mystery.

Next, we show  a code example of flink processors:

```python 
class Predictor(flink.FlinkPythonProcessor):
    def __init__(self):
        super().__init__()
        self.model_name = None

    def setup(self, execution_context: flink.ExecutionContext):
        self.model_name = execution_context.config['model_info'].name

    def process(self, execution_context: flink.ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        """
        Use pyflink udf to do prediction
        """
        model_meta = af.get_deployed_model_version(self.model_name)
        model_path = model_meta.model_path
        clf = load(model_path)

        class Predict(ScalarFunction):
            def eval(self, sl, sw, pl, pw):
                records = [[sl, sw, pl, pw]]
                df = pd.DataFrame.from_records(records, columns=['sl', 'sw', 'pl', 'pw'])
                return clf.predict(df)[0]

        execution_context.table_env.register_function('mypred',
                                                      udf(f=Predict(),
                                                          input_types=[DataTypes.FLOAT(), DataTypes.FLOAT(),
                                                                       DataTypes.FLOAT(), DataTypes.FLOAT()],
                                                          result_type=DataTypes.FLOAT()))
        return [input_list[0].select("mypred(sl,sw,pl,pw)")]
```

It is written in Pyflink for convenience but Flink Java Processor is also supported. And to run flink job without bugs, please make sure the properties for running a flink job is set properly in `tutorial_workflow.yaml` according to your local environment. 



Note, if you use some special dependencies and choose to submit the workflow to a remote environment for execution, you should put your dependencies in the `tutorial_workflow/dependencies` folder and refer them properly. That's because Flink AI Flow will upload the whole project directory to remote for execution and users need to make sure in the remote env, the python processors can run correctly.

## Run the whole workflow
Now we have finished the introduction of how to write a workflow. For the whole codes, please go to check `flink-ai-extended/flink-ai-flow/examples/tutorial_project` directory. After configuring the yaml file according to your own environment, it is time to run the workflow. 

Before running, please make sure you have installed Flink AI Flow and started AIFlowServer, notification service and scheduler correctly according to the QuickStart document.

Then, type following commands in your terminal:
```bash
cd flink-ai-extended/flink-ai-flow/examples/tutorial_project
python workflows/tutorial_workflow/tutorial_workflow.py
```

Once the bash command returns(it should take no longer than 1 minute), go to check the airflow WebUI to see if the workflow is submitted successfully. If it is success, wait a minute(because we set the training job to be executed every 1 minute in the yaml file) then you can see the graph like this:

![](images/tutorial/success_workflow.png)

You can view the prediction output under in the file `examples/tutorial_project/workflows/tutorial_workflow/predict_result.csv` as well.

If you find any job fails, you can go to check logs under directory like `examples/tutorial_project/temp/tutorial_workflow/$jobname/202107xxxxx/logs`. The log files will give you the error information in detail. Also, checking the log in the airflow WebUI is also a good choice.

## Conclusion
Congratulations! You have been equipped with necessary knowledge to write your own workflow. For further reading, you can check our design doc, [API doc](https://flink-ai-flow.readthedocs.io/en/latest/index.html) and [examples](https://github.com/alibaba/flink-ai-extended/tree/master/flink-ai-flow/examples). 



