# DL on Flink with Tensorflow

Deep learning on Flink can work with Tensorflow. You can train a Tensorflow
model with a Flink table and inference with the trained model on a Flink table.

## Quick Start Examples

Here are some end-to-end examples to distributed train a model and inference
with the trained model if you want to quickly try it out.

- [Quick Start Tensorflow 1.15](quick-start/quick_start_tensorflow_1.15.md)
- [Quick Start Tensorflow 1.15 Estimator](quick-start/quick_start_tensorflow_estimator_1.15.md)
- [Quick Start Tensorflow 2.4](quick-start/quick_start_tensorflow_2.4.md)
- [Quick Start Tensorflow 2.4 Estimator](quick-start/quick_start_tensorflow_estimator_2.4.md)

## API

DL on Flink provides API in both Java and Python. Java API is for the users that
are more comfortable writing their Flink job for data processing in Java. And
the Python API is for users that are more comfortable with PyFlink.

### Python

The core module of the Python API
is [tf_utils.](../dl-on-flink-tensorflow-2.x/python/dl_on_flink_tensorflow/tf_utils.py)
It provides methods to run training and inference job in Flink. All the methods
in `tf_utils` take
a [TFClusterConfig,](../dl-on-flink-tensorflow-2.x/python/dl_on_flink_tensorflow/tf_cluster_config.py)
which contains information about the number of the workers and ps, the
entrypoint of the worker and ps, and properties for the framework, etc. The
entrypoint is a python function that consumes the data from Flink and train the
model. It is where you build you model and run the training loop.

Here is an example using the Python API.

```python
if __name__ == '__main__':
    env = ...
    t_env = ...
    statement_set = ...

    source_table = ...
    config = TFClusterConfig.new_builder()
        .set_property('input_types', '..')
        .set_node_entry(train_entry)
        .set_worker_count(2)
        .build()

    tf_utils.train(statement_set, config, source_table, epoch=4)
    statement_set.execute().wait()
```

**Note:** We need to specify the "input_types" of the input table. It is a comma
seperated string of data types (e.g., "FLOAT_32,FLOAT32"). The data types should
match the data types of the input table. You can check
the [data type mapping.](#data-type)

The `setPythonEntry` should point to the following python function
`train_entry`.

```python
def train_entry(context):
    tf_context = TFContext(context)
    cluster = tf_context.get_tf_cluster_config()
    os.environ['TF_CONFIG'] = json.dumps({
        'cluster': cluster,
        'task': {'type': tf_context.get_node_type(),
                 'index': tf_context.get_index()}
    })

    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    with strategy.scope():
        model = ...

    def parse_csv(value):
        x, y = tf.io.decode_csv(value, record_defaults=[[0.], [0.]])
        return x, y

    dataset = tf_context.get_tfdataset_from_flink().map(parse_csv).batch(32)

    model.fit(dataset, epochs=10)
```

The entry function configures the environment variable for distributed training,
reads the sample data from Flink and trains a Tensorflow model. If your training
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
        import tensorflow as tf
        self._model = tf.keras.models.load_model(self._model_path)

    def eval(self, x):
        result = self._model.predict([x])
        return result.flatten()[0]


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
found [here.](../examples/linear/tensorflow)

### Estimator API

In addition to the `tf_utils` API, python also provides an Estimator API that is
compatible with the FlinkML API so that you don't need to write the training
script.

Here is an example of training a model with the Estimator API. As you can see,
the Estimator takes the model, loss function, optimizer, etc. so that you don't
need to write the python script to train the model. The model will be saved at
the given model path, after the job is finished.

We train a Keras model with the TFEstimator first.

```python
if __name__ == '__main__':
    env = ...
    t_env = ...
    statement_set = ...

    source_table = ...

    model = tf.keras.Model(...)
    loss = tf.keras.losses.MeanSquaredError()
    adam = tf.keras.optimizers.Adam()

    estimator = TFEstimator(statement_set, model, loss, adam, worker_num=2,
                            feature_cols="x",
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

    model = TFModel.load(env, model_path)
    res_table = model.transform(source_table)[0]
    res_table.execute().print()
```

An end-to-end example of the Estimator API can be
found [here.](../examples/linear/tensorflow-estimator)

### Java

The core class of the Java API
is [TFUtils.](../dl-on-flink-tensorflow-common/src/main/java/org/flinkextended/flink/ml/tensorflow/client/TFUtils.java)
it provides methods to run training and inference Tensorflow job in Flink. All
the methods in TFUtils takes
a [TFClusterConfig,](../dl-on-flink-tensorflow-common/src/main/java/org/flinkextended/flink/ml/tensorflow/client/TFClusterConfig.java)
which contains information about the number of the workers and ps, the
entrypoint of the worker and ps and properties for the framework, etc. The
entrypoint is a python function that consumes the data from Flink and train the
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

        final TFClusterConfig config = TFClusterConfig.newBuilder()
                .setPsCount(1)
                .setWorkerCount(2)
                .setPythonEntry("...", "...")
                .setProperty("input_types", "...")
                .build();

        TFUtils.train(statementSet, sourceTable, config);
        statementSet.execute();
    }
}
```

**Note:** We need to specify the "input_types" in the `TFClusterConfig`. It is a
comma seperated string of data types (e.g., "FLOAT_32,FLOAT32"). The data types
should match the data types of the input table. You can check
the [data type mapping.](#data-type)

The `setPythonEntry` should specify to the path and the function
name `train_entry` of the following python script.

```python
def train_entry(context):
    tf_context = TFContext(context)
    cluster = tf_context.get_tf_cluster_config()
    os.environ['TF_CONFIG'] = json.dumps({
        'cluster': cluster,
        'task': {'type': tf_context.get_node_type(),
                 'index': tf_context.get_index()}
    })

    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    with strategy.scope():
        model = ...

    def parse_csv(value):
        x, y = tf.io.decode_csv(value, record_defaults=[[0.], [0.]])
        return x, y

    dataset = tf_context.get_tfdataset_from_flink().map(parse_csv).batch(32)

    model.fit(dataset, epochs=10)
```

The training script above, configure the environment variable for distributed
training, read the sample data from Flink and train a Tensorflow model. If your
training script depends on some third party dependencies, you can check out
the [Dependency Management.](./dependency-management.md#java-api)

After model training, you can use the trained model to perform inference on a
Flink table. You can use the PyFlink udf to do inference same as the example
in [Python API](#Python) or use the `TFUtils#inference` method.

```java
class Main {
    public static void main(String[] args) {
        StreamExecutionEnvironment env =...
        StreamTableEnvironment tEnv =...
        StatementSet statementSet =...

        Table sourceTable =...

        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setWorldSize(2)
                        .setProperty("input_types", "...")
                        .setProperty("output_types", "...")
                        .setNodeEntry("...", "...")
                        .build();

        Schema outputSchema = ...

        Table output = TFUtils.inference(statementSet, sourceTable, config, outputSchema);
        statementSet.addInsert(TableDescriptor.forConnector("print").build(), output);
        statementSet.execute().await();
    }
}
```

**Note:** We need to specify the "input_types" and "output_types" in
the `TFClusterConfig`. They are comma seperated strings of data types
(e.g., "FLOAT_32,FLOAT32"). The "input_types" should match the data types of the
input table and the "output_types" should match the data types of the output
table. You can check the [data type mapping.](#data-type)

The `setPythonEntry` should specify the path and the function
name `inference_entry` of the following python script.

```python
def inference_entry(context):
    tf_context = TFContext(context)
    model_save_path = ...
    model = tf.keras.models.load_model(model_save_path)

    dataset = tf_context.get_tfdataset_from_flink().map(
        lambda value: tf.io.decode_csv(value, record_defaults=[[0.]]).batch(1)

    writer = tf_context.get_row_writer_to_flink()
    for x_tensor, in dataset:
        y = model.predict(x_tensor)[0][0]
    x_val = x_tensor.numpy()[0]
    writer.write(Row(x=x_val, y=y))
```

The end-to-end examples of Java API can be
found [here with Tensorflow 1.15](../dl-on-flink-examples/dl-on-flink-examples-tensorflow)
and [here with Tensorflow 2.](../dl-on-flink-examples/dl-on-flink-examples-tensorflow-2.x)

## Data Type

DL on Flink defines a set of data types that is used to bridge between the Flink
data type and Tensorflow data type. Here is the table of the mapping. Other data
types are unsupported currently.

| DL on Flink | Flink   | Tensorflow |
|-------------|---------|------------|
| FLOAT_32    | FLOAT   | float32    |
| FLOAT_64    | DOUBLE  | float64    |
| INT_32      | INTEGER | int32      |
| INT_64      | BIGINT  | int64      |
| STRING      | STRING  | string     | 