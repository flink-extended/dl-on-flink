# Guidance on Running Workflow on Events Example

The workflow_on_event project contains three workflows to demonstrate how the workflow_execution_on_events() API 
works. We will introduce the logic of each workflow and give you step-by-step instructions
to run the workflows locally.

## Introduction to our Workflow

The overall machine learning scenario first starts with some data. In our case, the data is produced hourly. Whenever
hourly data is produced, it should trigger an hourly data preprocess workflow to do the pre-processing for that specific
hour of data. When all the data for that day are ready, we should start the daily training workflow to train a new
model with the data of that day.

### Init Workflow

The init workflow is a dummy workflow to initialize the necessary dataset meta and model meta to run the other workflows
in the project. It should be run once before running other workflows. 

The init workflow specifies where the dataset and model will be stored.

### Hourly Data Workflow

The hourly data workflow is a long-running workflow that produces the training data hourly. The data training data we 
use is the MNIST dataset, its uri is specified in the `mnist_train` dataset meta. We will randomly select some samples 
from the dataset to be the dataset for that hour as if the training sample is generated every hour. The data will be 
produced at the uri of the `hourly_data` dataset meta.  

Whenever hourly data is produced, it sends an event with the following format:
```json
{
  "namespace": "workflow_on_event",
  "event_type": "DATA_EVENT",
  "key": "hourly_data",
  "value": "ready",
  "context": "2021-09-13T15"
}
``` 
The `context` is the hour of the produced data in iso format.

### Hourly Preprocess Workflow

The Hourly Preprocess Workflow runs whenever the following event arrives:
 ```json
{
  "namespace": "workflow_on_event",
  "event_type": "DATA_EVENT",
  "key": "hourly_data",
  "value": "ready",
  "sender": "*"
}
``` 
The context of the WorkflowExecution is the `context` field of the event. So the Hourly Preprocess Workflow
should be triggered when the Hourly Data Workflow produced an hourly dataset.

The Hourly Preprocess Workflow will transform the hourly data and copy it to the uri of the `daily_data` dataset meta.

At the end of the workflow, it checks if all the hourly datasets are ready for that day. If so, it sends an event with
the following format:
```json
{
  "namespace": "workflow_on_event",
  "event_type": "DATA_EVENT",
  "key": "daily_data",
  "value": "ready",
  "context": "2021-09-13"
}
``` 
The `context` is the day when all the hourly data is ready.

### Daily Workflow

The Daily Workflow is triggered by the following event:
 ```json
{
  "namespace": "workflow_on_event",
  "event_type": "DATA_EVENT",
  "key": "daily_data",
  "value": "ready",
  "sender": "*"
}
``` 
The context of the WorkflowExecution is the `context` field of the event. 

The Daily Workflow train a new model with the data from the day specified in the event context. It loads a base
model for training if there is a deployed/validated/generated model train today or yesterday. Therefore, a new model
is registered every day with the model name `daily_model_{date}`. You can train multiple model versions of the model if
you run the Daily Workflow for the same day multiple times.

After training, we have a validate job to validate the model with the validating dataset. It compares the score with the
current model version with the previous model version and mark the current model version as validated if the score of 
The current model version is higher.

## How to Run

In this section, we show step-by-step instructions to start the workflows in the project. We strongly suggest that you
have successfully followed the [Quick Start](https://github.com/alibaba/flink-ai-extended/wiki/Quick-Start) so that you 
are comfortable with starting an AIFlow server and running a workflow.

All the commands in this section should run at the `flink-ai-flow/examples/workflow_on_event` directory. 

### Initialization

We start by initializing the dataset metadata and model metadata. To do that, you can simply run

```bash
python workflows/init/init.py
```
 
If the command runs successfully, you should see the registered dataset and model on the AIFlow web UI or database. And
we are ready to submit the three workflows we introduced above. As we have shown above, the Hourly Preprocess Workflow
and the Daily Workflow are triggered by events. The Hourly Data Workflow should be triggered manually, and it sends
events to trigger the downstream workflow, Hourly Preprocess Workflow, which will then trigger the Daily Workflow.
Therefore, we want to submit and run the Hourly Data Workflow at the end.
 
### Submit Hourly Preprocess Workflow

You can submit the Hourly Preprocess Workflow with the following command:

```bash
python workflows/hourly_preprocess_workflow/hourly_preprocess_workflow.py
```

If you see a DAG with the name `workflow_on_event.hourly_preprocess_workflow` in Airflow UI, you have successfully 
submitted the workflow. There will be no Workflow Execution created. Therefore, you will not see any DagRun in the 
Airflow UI.

### Submit Daily Workflow

Similarly, You can submit the Daily Workflow with the following command:

```bash
python workflows/daily_workflow/daily_workflow.py
```

If you see a DAG with the name `workflow_on_event.daily_workflow` in Airflow UI, you have successfully submitted
the workflow. There will be no Workflow Execution created. Therefore, you will not see any DagRun in the Airflow UI.

### Submit and Run Hourly Data Workflow

Now we want to submit and run the Hourly Data Workflow to produce the hourly data. You can do that will the following
command:

```bash
python workflows/hourly_data_workflow/hourly_data_workflow.py
``` 

You should see the DAG `workflow_on_event.hourly_data_workflow` running at the Airflow UI, you have successfully submit 
and run the workflow.

The Hourly Data Workflow produces the hourly data every minute by default. You can change how often it produces the 
hourly data in `python workflows/hourly_data_workflow/hourly_data_workflow.py`.

### Check result

Now you have an hourly_data_workflow to produce the hourly data periodically. You can check the hourly produced data at
`/tmp/hourly_data`.

And you should see the `hourly_preprocess_workflow` start running whenever hourly data is produced. You can check 
the `/tmp/daily_data` for the dataset produced by the Hourly Preprocess Workflow.
   
The `daily workflow` will run whenever the daily dataset is ready. After the Daily Workflow runs successfully, you can 
check the model meta and model version meta at AIFlow web UI or Database.
