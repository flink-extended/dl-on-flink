# DL on Flink with PyTorch

Deep learning on Flink can work with PyTorch. You can train a PyTorch model with
a Flink table and inference with the trained model on a Flink table.

## Quick Start Examples

Here are some end-to-end examples to distributed train a model and inference
with the trained model if you want to quickly try it out.

- [Quick Start PyTorch](quick-start/quick_start_pytorch.md)
- [Quick Start PyTorch Estimator](quick-start/quick_start_pytorch_estimator.md)

## API

DL on Flink provides API in both Java and Python. Java API is for the users that
are more comfortable writing their Flink job for data processing in Java. And
Python API is for users that are more comfortable with PyFlink.

### Python

The core module of the Python API
is [pytorch_utils.](../dl-on-flink-pytorch/python/dl_on_flink_pytorch/pytorch_utils.py)
It provides methods to run training and inference job in Flink. All the methods
in `pytorch_utils` take
a [PyTorchClusterConfig,](../dl-on-flink-pytorch/python/dl_on_flink_pytorch/pytorch_cluster_config.py)
which contains information about the world size of the PyTorch cluster, the
entrypoint of the node and properties for the framework, etc. The entrypoint of
the node is a python function that consumes the data from Flink and train the
model. It is where you build you model and run the training loop.

Here is an example using the Python API.

```python
if __name__ == '__main__':
    env = ...
    t_env = ...
    statement_set = ...

    source_table = ...
    config = PyTorchClusterConfig.new_builder()
        .set_property('input_types', '..')
        .set_node_entry(train_entry)
        .set_world_size(2)
        .build()

    pytorch_utils.train(statement_set, config, source_table, epoch=4)
    statement_set.execute().wait()
```

**Note:** we need to specify the "input_types" of the input table. It is a comma
seperated string of data types (e.g., "FLOAT_32,FLOAT32"). The data types should
match the data types of the input table. You can check
the [data type mapping.](#data-type)

The `setPythonEntry` should point to the following python function
`train_entry`.

```python
class LinearModel(nn.Module):
    ...


def train_entry(context):
    pytorch_context = PyTorchContext(context)
    os.environ['MASTER_ADDR'] = pytorch_context.get_master_ip()
    os.environ['MASTER_PORT'] = str(pytorch_context.get_master_port())
    dist.init_process_group(backend='gloo',
                            world_size=pytorch_context.get_world_size(),
                            rank=pytorch_context.get_rank())
    data_loader = DataLoader(pytorch_context.get_dataset_from_flink(),
                             batch_size=128)

    model = DDP(LinearModel())
    loss_fn = ...
    optimizer = ...

    for batch, (x, y) in enumerate(data_loader):
        optimizer.zero_grad()
        pred = model(x)
        loss = loss_fn(pred, y)
        loss.backward()
        optimizer.step()

    ...
```

The entry function configures the environment variable for distributed training,
reads the sample data from Flink and trains a PyTorch model. If your training
script depends on some third party dependencies, you can check out
the [Dependency Management.](./dependency-management.md#python-api)

After model training, you can use the trained model to perform inference on a
Flink table. We recommend doing the inference in the PyFlink udf.

```python
class Predict(ScalarFunction):

    def __init__(self, _model_path):
        super().__init__()
        self._model = None
        self._model_path = _model_path

    def open(self, function_context: FunctionContext):
        self._model = torch.load(self._model_path)

    def eval(self, x):
        result = self._model(...)
        return result.item()


if __name__ == '__main__':
    env = ...
    t_env = ...

    source_table = ...
    predict = udf(f=Predict(model_path), result_type=...)

    result_table = source_table.add_columns(
        predict(source_table.x).alias("predict"))
    result_table.execute().print()
```

The end-to-end example of the Python API can be
found [here.](../examples/linear/pytorch)

### Estimator API

In addition to the `pytorch_utils` API, we also provide an Estimator API in
Python that is compatible with the FlinkML API so that you don't need to write
the training script.

Here is an example of training a model with the Estimator API. As you can see,
the Estimator takes the model, loss function, optimizer, etc. so that you don't
need to write the python script to train the model. The model will be saved at
the given model path, after the job is finished.

We train a PyTorch model with the PyTorchEstimator first.

```python
if __name__ == '__main__':
    env = ...
    t_env = ...
    statement_set = ...

    source_table = ...

    model = ...
    loss = nn.MSELoss()


    def optimizer_creator(_model: nn.Module):
        return torch.optim.SGD(_model.parameters(), lr=0.1)


    estimator = PyTorchEstimator(statement_set, model, loss, optimizer_creator,
                                 worker_num=2, feature_cols="x",
                                 label_col="y", max_epochs=1,
                                 batch_size=128)

    model = estimator.fit(source_table)

    model_path = ...
    model.save(model_path)

    statement_set.execute().wait()
```

Then we can use the trained model for inference.

```python
if __name__ == '__main__':
    env = ...
    t_env = ...
    statement_set = ...

    source_table = ...

    model = PyTorchModel.load(env, model_path)
    res_table = model.transform(source_table)[0]
    res_table.execute().print()
```

An end-to-end example of the Estimator API can be
found [here.](../examples/linear/pytorch-estimator)

### Java

The core class of the Java API
is [PyTorchUtils.](../dl-on-flink-pytorch/src/main/java/org/flinkextended/flink/ml/pytorch/PyTorchUtils.java)
It provides methods to run training and inference job in Flink. All the methods
in `PyTorchUtils` takes
a [PyTorchClusterConfig,](../dl-on-flink-pytorch/src/main/java/org/flinkextended/flink/ml/pytorch/PyTorchClusterConfig.java)
which contains information about the world size of the PyTorch cluster, the
entrypoint of the node and properties for the framework, etc. The entrypoint of
the node is a python script that consumes the data from Flink and train the
model. It is where you build you model and run the training loop.

Here is an example that write the Flink job in Java and the entrypoint in
python.

```java
class Main {
    public static void main(String[] args) {
        StreamExecutionEnvironment env =...
        StreamTableEnvironment tEnv =...
        StatementSet statementSet =...

        Table sourceTable =...

        final PyTorchClusterConfig config =
                PyTorchClusterConfig.newBuilder()
                        .setWorldSize(2)
                        .setNodeEntry("...", "...")
                        .setProperty("input_types", "...")
                        .build();

        PyTorchUtils.train(statementSet, sourceTable, config);
        statementSet.execute();
    }
}
```

**Note:** We need to specify the "input_types" in the `PyTorchClusterConfig`. It
is a comma seperated string of data types (e.g., "FLOAT_32,FLOAT32"). The data
types should match the data types of the input table. You can check
the [data type mapping.](#data-type)

The `setPythonEntry` should specify the path and the function name `train_entry`
of the following python script.

```python
class LinearModel(nn.Module):
    ...


def train_entry(context):
    pytorch_context = PyTorchContext(context)
    os.environ['MASTER_ADDR'] = pytorch_context.get_master_ip()
    os.environ['MASTER_PORT'] = str(pytorch_context.get_master_port())
    dist.init_process_group(backend='gloo',
                            world_size=pytorch_context.get_world_size(),
                            rank=pytorch_context.get_rank())
    data_loader = DataLoader(pytorch_context.get_dataset_from_flink(),
                             batch_size=128)

    model = DDP(LinearModel())
    loss_fn = ...
    optimizer = ...

    for batch, (x, y) in enumerate(data_loader):
        optimizer.zero_grad()
        pred = model(x)
        loss = loss_fn(pred, y)
        loss.backward()
        optimizer.step()

    ...
```

The training script above, configure the environment variable for distributed
training, read the sample data from Flink and train a PyTorch model. If your
training script depends on some third party dependencies, you can check out
the [Dependency Management.](./dependency-management.md#java-api)

After model training, you can use the trained model to perform inference on a
Flink table. You can use the PyFlink udf to do inference same as the example
in [Python API](#Python) or use the `PyTorchUtils#inference` method.

Here is an example using the `PyTorchUtils#inference` method.

```java
class Main {
    public static void main(String[] args) {
        StreamExecutionEnvironment env =...
        StreamTableEnvironment tEnv =...
        StatementSet statementSet =...

        Table sourceTable =...

        final PyTorchClusterConfig config =
                PyTorchClusterConfig.newBuilder()
                        .setWorldSize(2)
                        .setProperty("input_types", "...")
                        .setProperty("output_types", "...")
                        .setNodeEntry("...", "...")
                        .build();

        Schema outputSchema = ...

        Table output = PyTorchUtils.inference(statementSet, sourceTable, config, outputSchema);
        statementSet.addInsert(TableDescriptor.forConnector("print").build(), output);
        statementSet.execute().await();
    }
}
```

**Note:** We need to specify the "input_types" and "output_types" in
the `PyTorchClusterConfig`. They are comma seperated strings of data types
(e.g., "FLOAT_32,FLOAT32"). The "input_types" should match the data types of the
input table and the "output_types" should match the data types of the output
table. You can check the [data type mapping.](#data-type)

The `setPythonEntry` should specify the path and the function
name `inference_entry` of the following python script.

```python
def inference_entry(context: Context):
    pytorch_context = PyTorchContext(context)
    model_path = ...
    model = torch.load(model_path)
    model.eval()

    data_loader = DataLoader(pytorch_context.get_dataset_from_flink())
    writer = pytorch_context.get_data_writer_to_flink()
    for (x,) in data_loader:
        y = model(x)
        writer.write(Row(x=x.item(), y=y.item()))
```

The end-to-end examples of Java API can be
found [here.](../dl-on-flink-examples/dl-on-flink-examples-pytorch)

## Data Type

DL on Flink defines a set of data types that is used to bridge between the Flink
data type and PyTorch data type. Here is the table of the mapping. Other data
types are unsupported currently.

| DL on Flink | Flink   | PyTorch |
|-------------|---------|---------|
| FLOAT_32    | FLOAT   | float32 |
| FLOAT_64    | DOUBLE  | float64 |
| INT_32      | INTEGER | int32   |
| INT_64      | BIGINT  | int64   |


