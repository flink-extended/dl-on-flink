# API Document

## Operation API
**read_example** 
```python
def read_example(example_info: Union[ExampleMeta, Text, int],
                 executor: Optional[PythonObjectExecutor] = None,
                 exec_args: Optional[ExecuteArgs] = None) -> Channel:
    """
    Read example from the example operator. It can read example from external system.

    :param example_info: Information about the example which will be read. Its type can be ExampleMeta
                         of py:class:`ai_flow.meta.example_meta.ExampleMeta` or Text or int. The example_info
                         means name in the metadata service when its type is Text and it means id when its type is int.
                         The ai flow will get the example from metadata service by name or id.
    :param executor: The python user defined function in read example operator. User can write their own logic here.
    :param exec_args: The properties of read example, there are batch properties, stream properties and
                      common properties respectively.
    :return: Channel: data output channel.
    """
```
usage:
```python
import ai_flow as af
input_example = af.read_example(example_info=input_example_meta)

input_example = af.read_example(example_info=input_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadBatchExample()))

```

**write_example**

```python
def write_example(input_data: Channel,
                  example_info: Union[ExampleMeta, Text, int],
                  executor: Optional[PythonObjectExecutor] = None,
                  exec_args: ExecuteArgs = None
                  ) -> NoneChannel:
    """
    Write example to example operator. It can write example to external system.

    :param input_data: Channel from the specific operator which generates data.
    :param example_info: Information about the example which will be read. Its type can be ExampleMeta
                         of py:class:`ai_flow.meta.example_meta.ExampleMeta` or Text or int. The example_info
                         means name in he metadata service when its type is Text and it means id when its type is int.
                         The ai flow will get the example from metadata service by name or id.
    :param executor: The python user defined function in write example operator. User can write their own logic here.
    :param exec_args: The properties of read example, there are batch properties, stream properties and
                      common properties respectively.
    :return: NoneChannel: No data output
    """
```
usage:
```python
import ai_flow as af
af.write_example(input_data=input_example, example_info=output_example_meta)

af.write_example(input_data=input_example, example_info=output_example_meta,
                             executor=PythonObjectExecutor(python_object=WriteStreamExample()))

```

**transform**

```python
def transform(input_data_list: List[Channel],
              executor: BaseExecutor,
              exec_args: ExecuteArgs = None,
              output_num=1,
              name: Text = None) -> Union[Channel, Tuple[Channel]]:
    """
    Transformer operator. Transform the example so that the original example can be used for trainer or other operators
    after feature engineering, data cleaning or some other data transformation.

    :param input_data_list: List of input data. It contains multiple channels from the operators which generate data.
    :param executor: The user defined function in transform operator. User can write their own logic here.
    :param exec_args: The properties of read example, there are batch properties, stream properties and
                      common properties respectively.
    :param output_num: The output number of the operator. The default value is 1.
    :param name: Name of the transform operator.
    :return: Channel or Tuple[Channel]. It returns Channel When the output_num is 1 and returns Tuple[Channel] when
             the output_num is bigger than 1, and the len(Tuple(Channel)) is output_num.
    """
```
usage:
```python
import ai_flow as af
training_example = af.transform(input_data_list=[training_raw_example],
                                        executor=PythonObjectExecutor(python_object=TransformTrainData()),
                                        output_num=2,
                                        name='training_transformer')

```

**train**

```python
def train(input_data_list: List[Channel],
          executor: BaseExecutor,
          model_info: Union[ModelMeta, Text, int],
          base_model_info: Union[ModelMeta, Text, int] = None,
          exec_args: ExecuteArgs = None,
          output_num=0,
          name: Text = None) -> Union[NoneChannel, Channel, Tuple[Channel]]:
    """
    Trainer operator. Train model with the inputs or continually re-training the base model.

    :param input_data_list: List of Channel. It contains multiple channels from the operators which generate data.
    :param executor: The user defined function in train operator. User can write their own logic here.
    :param model_info: Information about the output model which is under training. Its type can be ModelMeta
                              of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The output_model_info
                              means name in he metadata service when its type is Text and it means id when its type is
                              int. The ai flow will get the model meta from metadata service by name or id.
    :param base_model_info: Information about the base model which will be trained. Its type can be ModelMeta
                            of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The base_model_info
                            means name in he metadata service when its type is Text and it means id when its type is
                            int. The ai flow will get the model meta from metadata service by name or id.
    :param exec_args: The properties of read example, there are batch properties, stream properties and
                      common properties respectively.
    :param output_num: The output number of the operator. The default value is 0.
    :param name: Name of the train operator.
    :return: NoneChannel, Channel, Tuple[Channel]: output data if train operation has output data else no output data.
```
usage:
```python
import ai_flow as af
train_channel = af.train(input_data_list=[training_example[0], training_example[1]],
                                    executor=PythonObjectExecutor(python_object=TrainModel()),
                                    model_info=model_meta, name='trainer')

```

**predict**

```python
def predict(input_data_list: List[Channel],
            model_info: Union[ModelMeta, Text, int],
            executor: BaseExecutor,
            model_version_info: Optional[Union[ModelVersionMeta, Text]] = None,
            exec_args: ExecuteArgs = None,
            output_num=1,
            name: Text = None) -> Union[NoneChannel, Channel, Tuple[Channel]]:
    """
    Predictor Operator. Do prediction job with the specific model version.

    :param input_data_list: List of Channel. It contains the example data used in prediction.
    :param model_info: Information about the model which is in prediction. Its type can be ModelMeta
                       of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The model_info
                       means name in he metadata service when its type is Text and it means id when its type is
                       int. The ai flow will get the model meta from metadata service by name or id.
    :param executor: The user defined function in predict operator. User can write their own logic here.
    :param model_version_info: Information about the model version which is in prediction. Its type can be
                               ModelVersionMeta of py:class:`ai_flow.meta.model_meta.ModelVersionMeta`
                               or Text. The model_version_info means version in he metadata service
                               when its type is Text. The ai flow will get the model meta from metadata
                               service by version.
    :param exec_args: The properties of read example, there are batch properties, stream properties and
                      common properties respectively.
    :param output_num: The output number of the operator. The default value is 1.
    :param name: Name of the predict operator.
    :return: Channel or Tuple[Channel]: predict output.
    """
```
usage:
```python
import ai_flow as af
predict_channel = af.predict(input_data_list=[predict_example], model_info=model_meta,
                             executor=PythonObjectExecutor(python_object=ModelPredict()),
                             name='predictor')

```

**evaluate**

```python
def evaluate(input_data_list: List[Channel],
             model_info: Union[ModelMeta, Text, int],
             executor: BaseExecutor,
             exec_args: ExecuteArgs = None,
             output_num=0,
             name: Text = None) -> Union[NoneChannel, Channel, Tuple[Channel]]:
    """
    Evaluate Operator. Do evaluate job with the specific model version.

    :param input_data_list: List of Channel. It contains the example data used in prediction.
    :param model_info: Information about the model which is in prediction. Its type can be ModelMeta
                       of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The model_info
                       means name in he metadata service when its type is Text and it means id when its type is
                       int. The ai flow will get the model meta from metadata service by name or id.
    :param executor: The user defined function in evaluate operator. User can write their own logic here.
    :param exec_args: The properties of read example, there are batch properties, stream properties and
                      common properties respectively.
    :param output_num: The output number of the operator. The default value is 0.
    :param name: Name of the predict operator.
    :return: NoneChannel.
    """
```
usage:
```python
import ai_flow as af
evaluate_channel = af.evaluate(input_data_list=[evaluate_example], model_info=model_meta,
                               executor=PythonObjectExecutor(python_object=ModelEvaluate()),
                               name='evaluate')

```


**example_validate**

```python
def example_validate(input_data: Channel,
                     executor: BaseExecutor,
                     exec_args: ExecuteArgs = None,
                     name: Text = None
                     ) -> NoneChannel:
    """
    Example Validator Operator. Identifies anomalies in training and serving data in this operator.

    :param input_data: Channel. It contains the example data used in evaluation.
    :param executor: The user defined function in example validate operator. User can write their own logic here.
    :param exec_args: The properties of read example, there are batch properties, stream properties and
                      common properties respectively.
    :param name: Name of the example validate operator.
    :return: NoneChannel.
    """
```
usage:
```python
import ai_flow as af
example_validate_channel = af.example_validate(input_data=test_example_1, output_result=example_evaluate_output,
                                                    executor=PythonObjectExecutor(python_object=TestExampleValidate()))

```

**model_validate**

```python
def model_validate(input_data_list: List[Channel],
                   model_info: Union[ModelMeta, Text, int],
                   executor: BaseExecutor,
                   model_version_info: Optional[Union[ModelVersionMeta, Text]] = None,
                   base_model_version_info: Optional[Union[ModelVersionMeta, Text]] = None,
                   exec_args: ExecuteArgs = None,
                   output_num=0,
                   name: Text = None) -> Union[NoneChannel, Channel, Tuple[Channel]]:
    """
    Model Validator Operator. Compare the performance of two different versions of the same model and choose the better
    model version to make it ready to be in the stage of deployment.

    :param input_data_list: List of Channel. It contains the example data used in model validation.
    :param model_info: Information about the model which is in model validation. Its type can be ModelMeta
                       of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The model_info
                       means name in he metadata service when its type is Text and it means id when its type is
                       int. The ai flow will get the model meta from metadata service by name or id.
    :param executor: The user defined function in model validate operator. User can write their own logic here.
    :param model_version_info: Information about the model version which is in model validation. Its type can be
                               ModelVersionMeta of py:class:`ai_flow.meta.model_meta.ModelVersionMeta`
                               or Text. The model_version_info means version in he metadata service
                               when its type is Text. The ai flow will get the model meta from metadata
                               service by version.
    :param base_model_version_info: Information about the model version which is in model validation. Its type can be
                                    ModelVersionMeta of py:class:`ai_flow.meta.model_meta.ModelVersionMeta`
                                    or Text. The model_version_info means version in he metadata service
                                    when its type is Text. The ai flow will get the model meta from metadata
                                    service by version.
    :param exec_args: The properties of read example, there are batch properties, stream properties and
                      common properties respectively.
    :param output_num: The output number of the operator. The default value is 0.
    :param name: Name of the model validate operator.
    :return: NoneChannel.
    """
```
usage:
```python
import ai_flow as af
validate_channel = af.model_validate(input_data_list=[validate_example], model_info=model_meta,
                                                 executor=PythonObjectExecutor(python_object=ModelValidate()),
                                                 model_version_info=None, base_model_version_info=None,
                                                 name='model_validator')

```

**push_model**

```python
def push_model(model_info: Union[ModelMeta, Text, int],
               executor: BaseExecutor,
               model_version_info: Optional[Union[ModelVersionMeta, Text]] = None,
               exec_args: ExecuteArgs = None,
               name: Text = None) -> NoneChannel:
    """
    Pusher operator. The pusher operator is used to push a validated model which is better than previous one to
    a deployment target.

    :param model_info: Information about the model which is in pusher. Its type can be ModelMeta
                       of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The model_info
                       means name in he metadata service when its type is Text and it means id when its type is
                       int. The ai flow will get the model meta from metadata service by name or id.
    :param executor: The user defined function in pusher operator. User can write their own logic here.
    :param model_version_info: Information about the model version which is in push. Its type can be
                               ModelVersionMeta of py:class:`ai_flow.meta.model_meta.ModelVersionMeta`
                               or Text. The model_version_info means version in he metadata service
                               when its type is Text. The ai flow will get the model meta from metadata
                               service by version.
    :param exec_args: The properties of read example, there are batch properties, stream properties and
                      common properties respectively.
    :param name: Name of the push operator.
    :return: NoneChannel.
    """
```
usage:
```python
import ai_flow as af
push_channel = af.push_model(model_info=model_meta,
                                         executor=PythonObjectExecutor(python_object=PushModel()))

```

**user_define_operation**

```python
def user_define_operation(
        executor: BaseExecutor,
        input_data_list: Union[None, Channel, List[Channel]] = None,
        exec_args: ExecuteArgs = None,
        output_num=1,
        name: Text = None) -> Union[NoneChannel, Channel, Tuple[Channel]]:
    """
    User defined operator.

    :param executor: The user defined function in operator. User can write their own logic here.
    :param input_data_list: List of input data. It contains multiple channels from the operators which generate data.
    :param exec_args: The properties of read example, there are batch properties, stream properties and
                      common properties respectively.
    :param output_num: The output number of the operator. The default value is 1.
    :param name: Name of this operator.
    :return: NoneChannel or Channel or Tuple[Channel].
    """
```
usage:
```python
import ai_flow as af
run = af.user_define_operation(executor=CmdExecutor(cmd_line="echo 'push model'"))
```

## Dependence API

**external_trigger**

```python
def external_trigger(name: Text = None) -> NoneChannel:
    """
    External trigger channel. Essentially it is an infinite sleeping job and is used as the trigger dependency
    in control dependencies. It can not be set in job config and only support stream mode.

    :param name: Name of the trigger.
    :return: NoneChannel: Identify external event triggers
    """
```
usage:
```python
import ai_flow as af
trigger = af.external_trigger(name='trigger')
```

**start_before_control_dependency**

```python
def start_before_control_dependency(src: Channel,
                                    dependency: Channel,
                                    ) -> None:
    """
    Add start-before control dependency. It means src channel will start when and only the dependency channel start.

    :param src: The src channel depended on the dependency channel.
    :param dependency: The channel which is the dependency.
    :return: None.
    """
```
usage:
```python
import ai_flow as af
af.start_before_control_dependency(predict_channel, validate_channel)
```

**stop_before_control_dependency**

```python
def stop_before_control_dependency(src: Channel,
                                   dependency: Channel,
                                   ) -> None:
    """
    Add stop-before control dependency. It means src channel will start when and only the dependency channel stop.

    :param src: The src channel depended on the dependency channel.
    :param dependency: The channel which is the dependency.
    :return: None.
    """
```
usage:
```python
import ai_flow as af
af.stop_before_control_dependency(predict_channel, train_channel)
```

**model_version_control_dependency**

```python
def model_version_control_dependency(src: Channel,
                                     model_name: Text,
                                     dependency: Channel,
                                     ) -> None:
    """
    Add model version control dependency. It means src channel will start when and only a new model version of the
    specific model is updated in notification service.

    :param src: The src channel depended on the new model version which is updated in notification service.
    :param model_name: Name of the model, refers to a specific model.
    :param dependency: The channel which is the dependency.
    :return: None.
    """
```
usage:
```python
import ai_flow as af
af.model_version_control_dependency(src=evaluate_channel, dependency=evaluate_trigger, model_name=train_model.name)
```

**example_control_dependency**

```python
def example_control_dependency(src: Channel,
                               example_name: Text,
                               dependency: Channel,
                               ) -> None:
    """
    Add example control dependency. It means src channel will start when and only the an new example of the specific
    example is updated in notification service.

    :param src: The src channel depended on the example which is updated in notification service.
    :param example_name: Name of the example, refers to a specific example.
    :param dependency: The channel which is the dependency.
    :return: None.
    """
```
usage:
```python
import ai_flow as af
af.example_control_dependency(src=example_channel, dependency=trigger, example_name=example_meta.name)
```

**user_define_control_dependency**

```python
def user_define_control_dependency(src: Channel,
                                   dependency: Channel,
                                   signal_key: Text,
                                   signal_value: Text,
                                   signal_name: Text = None,
                                   condition: SignalCondition = SignalCondition.NECESSARY,
                                   action: SignalAction = SignalAction.START,
                                   life: SignalLife = SignalLife.ONCE,
                                   value_condition: SignalValueCondition = SignalValueCondition.EQUAL
                                   ) -> None:
    """
    Add user defined control dependency.

    :param src: The src channel depended the signal which is updated in notification service.
    :param dependency: The channel which is the dependency.
    :param signal_key: The key of the signal.
    :param signal_value: The value of the signal.
    :param signal_name: The Name of the signal.
    :param condition: The signal condition. Sufficient or Necessary.
    :param action: The action act on the src channel. Start or Restart.
    :param life: The life of the signal. Once or Repeated.
    :param value_condition: The signal value condition. Equal or Update. Equal means the src channel will start or
                            restart only when in the condition that the notification service updates a value which
                            equals to the signal value under the specific signal key, while update means src channel
                            will start or restart when in the the condition that the notification service has a update
                            operation on the signal key which signal value belongs to.
    :return:None.
    """
```
usage:
```python
import ai_flow as af
af.user_define_control_dependency(src=cmd_executor, dependency=trigger, signal_key='key',
                                  signal_value='value', signal_name='name', condition=SignalCondition.NECESSARY
                                  , action=SignalAction.RESTART, life=SignalLife.ONCE,
                                  value_condition=SignalValueCondition.UPDATE)
```

## Configuration API

### project configuration
**project configuration api**

```python
def set_project_config_file(config_file: Text):
    """
    Set project config based on project.yaml in client.

    :param config_file: Path to project.yaml
    :return: None
    """
    
def project_config() -> Optional[ProjectConfig]:
    """
    :return: project configuration
    """
```
**project config project.yaml**
```yaml
project_name: local_batch_example
server_ip: localhost
server_port: 50052
ai_flow_home: /opt/ai_flow
blob_server.type: oss
blob_server.endpoint:
blob_server.bucket:
blob_server.access_key_id:
blob_server.access_key_secret:
```

### ai flow job configuration

```python
import ai_flow as af
with af.global_config_file(config_path=workflow_config_file):
    with af.config(config='python_train_job'):
```
**configuration file workflow_config.yaml**
```yaml
python_train_job:
  platform: kubernetes
  engine: python
  job_name: k8s_batch_train_example
  properties:
    clean_job_resource: "True"
    ai_flow_worker_image: xxxx
```

### job configurations

**local cmd**
```yaml
config_name:
  engine: cmd_line
  platform: local
```

**local python**
```yaml
config_name:
  engine: python
  platform: local
```

**local cmd**
```yaml
config_name:
  engine: cmd_line
  platform: local
```

**local flink**
```yaml
config_name:
  engine: flink
  platform: local
  local_mode: (python or java)
```

**kubernetes cmd**
```yaml
config_name:
  engine: cmd_line
  platform: kubernetes
  ai_flow_worker_image: ${}
```

**kubernetes python**
```yaml
config_name:
  engine: python
  platform: kubernetes
  ai_flow_worker_image: ${}
```

**kubernetes flink**
```yaml
config_name:
  engine: flink
  platform: kubernetes
  flink_home: /opt/flink
  ai_flow_worker_image: ${}
  parallelism: ${},
  resources:
    jobmanager:
      memory: ${}
      cpu: ${}
    taskmanager:
      memory: ${}
      cpu: ${}

  flink_conf:
    fs.overwrite-files: ${}
    fs.oss.endpoint: ${}
    fs.oss.accessKeyId: ${}
    fs.oss.accessKeySecret: ${}
```
## Meta API

**example api**
```python
def get_example_by_id(self, example_id) -> Optional[ExampleMeta]:
    """
    get an specific example in metadata store by example id.

    :param example_id: the example id
    :return: A single :py:class:`ai_flow.meta.example_meta.ExampleMeta` object if the example exists,
             Otherwise, returns None if the example does not exist.
    """
    

def get_example_by_name(self, example_name) -> Optional[ExampleMeta]:
    """
    get an specific example in metadata store by example name.

    :param example_name: the example name
    :return: A single :py:class:`ai_flow.meta.example_meta.ExampleMeta` object if the example exists,,
             Otherwise, returns None if the example does not exist.
    """
    

def register_example(self, name: Text, support_type: ExampleSupportType, data_type: Text = None,
                     data_format: Text = None, description: Text = None, batch_uri: Text = None,
                     stream_uri: Text = None, create_time: int = None, update_time: int = None,
                     properties: Properties = None, name_list: List[Text] = None,
                     type_list: List[DataType] = None) -> ExampleMeta:
    """
    register an example in metadata store.

    :param name: the name of the example
    :param support_type: the example's support_type
    :param data_type: the data type of the example
    :param data_format: the data format of the example
    :param description: the description of the example
    :param batch_uri: the batch uri of the example
    :param stream_uri: the stream uri of the example
    :param create_time: the time when the example is created
    :param update_time: the time when the example is updated
    :param properties: the properties of the example
    :param name_list: the name list of example's schema
    :param type_list: the type list corresponded to the name list of example's schema
    :return: A single :py:class:`ai_flow.meta.example_meta.ExampleMeta` object.
    """

def register_example_with_catalog(self, name: Text, support_type: ExampleSupportType,
                                  catalog_name: Text, catalog_type: Text,
                                  catalog_connection_uri: Text, catalog_version: Text,
                                  catalog_table: Text, catalog_database: Text = None) -> ExampleMeta:
    """
    register example with catalog in metadata store.

    :param name: the name of the example
    :param support_type: the example's support_type
    :param catalog_name: the name of the example catalog
    :param catalog_type: the type of the example catalog
    :param catalog_connection_uri: the connection uri of the example catalog
    :param catalog_version: the version of the example catalog
    :param catalog_table: the table of the example catalog
    :param catalog_database: the database of the example catalog
    :return: A single :py:class:`ai_flow.meta.example_meta.ExampleMeta` object.
    """
    

def register_examples(self, examples: List[ExampleMeta]) -> List[ExampleMeta]:
    """
    register multiple examples in metadata store.

    :param examples: A list of examples
    :return: List of :py:class:`ai_flow.meta.example_meta.ExampleMeta` objects.
    """


def update_example(self, example_name: Text, support_type: ExampleSupportType = None,
                   data_type: Text = None, data_format: Text = None,
                   description: Text = None, batch_uri: Text = None,
                   stream_uri: Text = None, update_time: int = None,
                   properties: Properties = None, name_list: List[Text] = None,
                   type_list: List[DataType] = None, catalog_name: Text = None,
                   catalog_type: Text = None, catalog_database: Text = None,
                   catalog_connection_uri: Text = None, catalog_version: Text = None,
                   catalog_table: Text = None) -> Optional[ExampleMeta]:
    """
    update example in metadata store.

    :param example_name: the name of the example
    :param support_type: the example's support_type
    :param data_type: the data type of the example
    :param data_format: the data format of the example
    :param description: the description of the example
    :param batch_uri: the batch uri of the example
    :param stream_uri: the stream uri of the example
    :param update_time: the time when the example is updated
    :param properties: the properties of the example
    :param name_list: the name list of example's schema
    :param type_list: the type list corresponded to the name list of example's schema
    :param catalog_name: the name of the example catalog
    :param catalog_type: the type of the example catalog
    :param catalog_database: :param catalog_database: the database of the example catalog
    :param catalog_connection_uri: the connection uri of the example catalog
    :param catalog_version: the version of the example catalog
    :param catalog_table: the table of the example catalog
    :return: A single :py:class:`ai_flow.meta.example_meta.ExampleMeta` object if update successfully.
    """
    

def list_example(self, page_size, offset) -> Optional[List[ExampleMeta]]:
    """
    List registered examples in metadata store.

    :param page_size: the limitation of the listed examples.
    :param offset: the offset of listed examples.
    :return: List of :py:class:`ai_flow.meta.example_meta.ExampleMeta` objects,
             return None if no examples to be listed.
    """


def delete_example_by_name(self, example_name) -> Status:
    """
    Delete the registered example by example name .

    :param example_name: the example name
    :return: Status.OK if the example is successfully deleted, Status.ERROR if the example does not exist otherwise.
    """

def delete_example_by_id(self, example_id):
    """
    Delete the registered example by example id .

    :param example_id: the example id
    :return: Status.OK if the example is successfully deleted, Status.ERROR if the example does not exist otherwise.
    """
```

**model api**

```python

def get_model_by_id(self, model_id) -> Optional[ModelMeta]:
    """
    get an specific model in metadata store by model id.

    :param model_id: Id of registered model
    :return: A single :py:class:`ai_flow.meta.model_meta.ModelMeta` object if the model relation exists,
    Otherwise, returns None if the model relation does not exist.
    """

def get_model_by_name(self, model_name) -> Optional[ModelMeta]:
    """
    get an specific model in metadata store by model name.

    :param model_name: Name of registered model
    :return: A single :py:class:`ai_flow.meta.model_meta.ModelMeta` object if the model relation exists,
    Otherwise, returns None if the model relation does not exist.
    """


def register_model(self, model_name, project_id, model_type, model_desc=None) -> ModelMeta:
    """
    register a model in metadata store

    :param model_name: Name of registered model
    :param project_id: Project id which registered model corresponded to.
    :param model_type: Type of registered model
    :param model_desc: Description of registered model
    :return: A single :py:class:`ai_flow.meta.model_meta.ModelMeta` object.
    """


def delete_model_by_id(self, model_id):
    """
    delete registered model by model id.

    :param model_id: Id of registered model
    :return: Status.OK if registered model is successfully deleted,
             Status.ERROR if registered model does not exist otherwise.
    """

def delete_model_by_name(self, model_name):
    """
    delete registered model by model name.

    :param model_name: Name of registered model
    :return: Status.OK if registered model is successfully deleted,
             Status.ERROR if registered model does not exist otherwise.
    """


def get_model_version_relation_by_version(self, version, model_id) -> Optional[ModelVersionRelationMeta]:
    """
    get an specific model version relation in metadata store by the model version name.

    :param version: the model version name
    :param model_id: the model id corresponded to the model version
    :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelVersionRelationMeta` object
             if the model version exists, Otherwise, returns None if the model version does not exist.
    """


def register_model_version_relation(self, version, model_id,
                                    workflow_execution_id=None) -> ModelVersionRelationMeta:
    """
    register a model version relation in metadata store.

    :param version: the specific model version
    :param model_id: the model id corresponded to the model version
    :param workflow_execution_id: the workflow execution id corresponded to the model version
    :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelVersionRelationMeta` object.
    """


def list_model_version_relation(self, model_id, page_size, offset):
    """
    List registered model version relations in metadata store.

    :param model_id: the model id corresponded to the model version
    :param page_size: the limitation of the listed model version relations.
    :param offset: the offset of listed model version relations.
    :return: List of :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` objects,
             return None if no model version relations to be listed.
    """


def delete_model_version_relation_by_version(self, version, model_id):
    """
    Delete the registered model version by model version name .

    :param version: the model version name
    :param model_id: the model id corresponded to the model version
    :return: Status.OK if the model version is successfully deleted,
             Status.ERROR if the model version does not exist otherwise.
    """


def get_model_version_by_version(self, version, model_id) -> Optional[ModelVersionMeta]:
    """
    get an specific model version in metadata store by model version name.

    :param version: User-defined version of registered model
    :param model_id: the model id corresponded to the model version
    :return: A single :py:class:`ai_flow.meta.model_meta.ModelVersionMeta` object if the model version exists,
    Otherwise, returns None if the model version does not exist.
    """


def register_model_version(self, model, model_path, workflow_execution_id=None, model_metric=None,
                           model_flavor=None, version_desc=None,
                           current_stage=ModelVersionStage.GENERATED) -> ModelVersionMeta:
    """
    register a model version in metadata store.

    :param model:  model id or model meta of registered model corresponded to model version
    :param model_path: Source path where the AIFlow model is stored.
    :param workflow_execution_id: id of workflow execution corresponded to model version
    :param model_metric: Metric address from AIFlow metric server of registered model.
    :param model_flavor: (Optional) Flavor feature of AIFlow registered model option.
    :param version_desc: (Optional) Description of registered model version.
    :param current_stage: (Optional) Stage of registered model version
    :return: A single :py:class:`ai_flow.meta.model_meta.ModelVersionMeta` object.
    """


def delete_model_version_by_version(self, version, model_id):
    """
    Delete registered model version by model version name .

    :param version: the model version name
    :param model_id: the model id corresponded to the model version
    :return: Status.OK if the model version is successfully deleted,
             Status.ERROR if the model version does not exist otherwise.
    """

def get_deployed_model_version(self, model_name):
    """
    Get Serving Model version
    :param model_name: the model name
    :return: model version meta.
    """
```

**project api**
```python
def get_project_by_id(self, project_id) -> Optional[ProjectMeta]:
    """
    get an specific project in metadata store by project id

    :param project_id: the project id
    :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object if the project exists,
             Otherwise, returns None if the project does not exist.
    """

def get_project_by_name(self, project_name) -> Optional[ProjectMeta]:
    """
    get an specific project in metadata store by project name
    :param project_name: the project name
    :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object if the project exists,
             Otherwise, returns None if the project does not exist.
    """

def register_project(self, name, uri: Text = None, properties: Properties = None,
                     user: Text = None, password: Text = None, project_type: Text = None) -> ProjectMeta:
    """
    register a project in metadata store.

    :param name: the name of the project
    :param uri: the uri of the project
    :param properties: the properties of the project
    :param user: the user of the project
    :param password: the password of the project
    :param project_type: the project type of the project
    :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object.
    """

def update_project(self, project_name: Text, uri: Text = None, properties: Properties = None,
                   user: Text = None, password: Text = None, project_type: Text = None) -> Optional[ProjectMeta]:
    """
    update project in metadata store.

    :param project_name: the name of the project
    :param uri: the uri of the project
    :param properties: the properties of the project
    :param user: the user of the project
    :param password: the password of the project
    :param project_type: the project type of the project
    :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object if update successfully.
    """

def list_project(self, page_size, offset) -> Optional[List[ProjectMeta]]:
    """
    List registered projects in metadata store.

    :param page_size: the limitation of the listed projects.
    :param offset: the offset of listed projects.
    :return: List of :py:class:`ai_flow.meta.project_meta.ProjectMeta` objects,
             return None if no projects to be listed.
    """

def delete_project_by_id(self, project_id) -> Status:
    """
    Delete the registered project by project id .

    :param project_id: the project id
    :return: Status.OK if the project is successfully deleted, Status.ERROR if the project does not exist otherwise.
    """

def delete_project_by_name(self, project_name) -> Status:
    """
    Delete the registered project by project name .

    :param project_name: the project name
    :return: Status.OK if the project is successfully deleted, Status.ERROR if the project does not exist otherwise.
    """
```

**artifact api**
```python
def get_artifact_by_id(self, artifact_id) -> Optional[ArtifactMeta]:
    """
    get an specific artifact in metadata store by artifact id.

    :param artifact_id: the artifact id
    :return: A single :py:class:`ai_flow.meta.artifact_meta.ArtifactMeta` object
             if the artifact exists, Otherwise, returns None if the artifact does not exist.
    """

def get_artifact_by_name(self, artifact_name) -> Optional[ArtifactMeta]:
    """
    get an specific artifact in metadata store by artifact name.

    :param artifact_name: the artifact name
    :return: A single :py:class:`ai_flow.meta.artifact_meta.ArtifactMeta` object
             if the artifact exists, Otherwise, returns None if the artifact does not exist.
    """

def register_artifact(self, name: Text, data_format: Text = None, description: Text = None,
                      batch_uri: Text = None, stream_uri: Text = None,
                      create_time: int = None, update_time: int = None,
                      properties: Properties = None) -> ArtifactMeta:
    """
    register an artifact in metadata store.

    :param name: the name of the artifact
    :param data_format: the data_format of the artifact
    :param description: the description of the artifact
    :param batch_uri: the batch uri of the artifact
    :param stream_uri: the stream uri of the artifact
    :param create_time: the time when the artifact is created
    :param update_time: the time when the artifact is updated
    :param properties: the properties of the artifact
    :return: A single :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` object.
    """

def update_artifact(self, artifact_name: Text, data_format: Text = None, description: Text = None,
                    batch_uri: Text = None, stream_uri: Text = None,
                    update_time: int = None, properties: Properties = None) -> Optional[ArtifactMeta]:
    """
    update artifact in metadata store.

    :param artifact_name: the name of the artifact
    :param data_format: the data_format of the artifact
    :param description: the description of the artifact
    :param batch_uri: the batch uri of the artifact
    :param stream_uri: the stream uri of the artifact
    :param update_time: the time when the artifact is updated
    :param properties: the properties of the artifact
    :return: A single :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` object if update successfully.
    """


def list_artifact(self, page_size, offset) -> Optional[List[ArtifactMeta]]:
    """
    List registered artifacts in metadata store.

    :param page_size: the limitation of the listed artifacts.
    :param offset: the offset of listed artifacts.
    :return: List of :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` objects,
             return None if no artifacts to be listed.
    """

def delete_artifact_by_id(self, artifact_id) -> Status:
    """
    Delete the registered artifact by artifact id .

    :param artifact_id: the artifact id
    :return: Status.OK if the artifact is successfully deleted,
             Status.ERROR if the artifact does not exist otherwise.
    """

def delete_artifact_by_name(self, artifact_name) -> Status:
    """
    Delete the registered artifact by artifact name .

    :param artifact_name: the artifact name
    :return: Status.OK if the artifact is successfully deleted,
             Status.ERROR if the artifact does not exist otherwise.
    """
```
## Project API
**run**
```python
def run(project_path: Text = None) -> Optional[int]:
    """
    Run project under the current project path.

    :param project_path: The path of the project path.
    :return: Workflow id.
    """
```

**wait_workflow_execution_finished**
```python
def wait_workflow_execution_finished(workflow_execution_id: int) -> Optional[int]:
    """
    Wait for the results which generates from the specific workflow execution.

    :param workflow_execution_id: The workflow execution id.
    :return: Schedule result of the workflow.
    """
    return _default_project.wait_for_result(workflow_id=workflow_execution_id)

```

**stop_execution_by_id**
```python
def stop_execution_by_id(workflow_execution_id: int) -> Tuple[int, int, Text]:
    """
    Stop the workflow execution by id.

    :param workflow_execution_id: The workflow execution id.
    :return: Return_code, Workflow_id, Message of the workflow execution.
    """
    return _default_project.stop_workflow_execution(workflow_execution_id=workflow_execution_id)
```

## Example

```python
import ai_flow as af
from ai_flow import ExampleSupportType, PythonObjectExecutor, ModelType
from ai_flow.util import path_util

from remote_example_executor import *

oss_config = {}
oss_config['blob_server.type'] = 'oss'
oss_config['blob_server.access_key_id'] = ''
oss_config['blob_server.access_key_secret'] = ''
oss_config['blob_server.endpoint'] = ''
oss_config['blob_server.bucket'] = ''
example_manager = OSSModelManager(oss_config)


def get_and_upload_project_data():
    """Get training job dataset locally"""
    train_data_file = path_util.get_file_dir(__file__) + '/../resources/mnist_train.npz'

    """Upload training dataset to OSS"""
    remote_train_data_file = example_manager.save_model(local_path=train_data_file)

    """Get evaluating job dataset"""
    evaluate_data_file = path_util.get_file_dir(__file__) + '/../resources/mnist_evaluate.npz'

    """Upload evaluate dataset to OSS"""
    remote_evaluate_data_file = example_manager.save_model(local_path=evaluate_data_file)

    """Get prediction job dataset"""
    prediction_data_file = path_util.get_file_dir(__file__) + '/../resources/mnist_predict.npz'

    """Upload predict dataset to OSS"""
    remote_predict_data_file = example_manager.save_model(local_path=prediction_data_file)

    return remote_train_data_file, remote_evaluate_data_file, remote_predict_data_file


def preparation_job(remote_train_data_file, remote_evaluate_data_file, remote_predict_data_file):
    """Metadata registration"""

    """Register training job example meta in metadata store"""
    training_example_meta = af.register_example(name='remote_mnist_train_data',
                                                support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                data_format='npz',
                                                batch_uri=remote_train_data_file)

    """Register model meta in metadata store"""
    model_meta = af.register_model(model_name='mnist_model', model_type=ModelType.SAVED_MODEL)

    """Register evaluating job example meta in metadata store"""
    evaluate_example_meta = af.register_example(name='remote_mnist_evaluate_data',
                                                support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                data_format='npz',
                                                batch_uri=remote_evaluate_data_file)

    """Register validating job example meta in metadata store"""
    validate_example_meta = af.register_example(name='remote_mnist_validate_data',
                                                support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                data_format='npz',
                                                batch_uri=remote_evaluate_data_file)

    """Register prediction job example meta in metadata store"""
    predict_example_meta = af.register_example(name='remote_mnist_prediction_data',
                                               support_type=ExampleSupportType.EXAMPLE_BATCH,
                                               data_format='npz',
                                               batch_uri=remote_predict_data_file)
    prediction_result = 'prediction_result'
    result = af.register_example(name='prediction_result',
                                 support_type=ExampleSupportType.EXAMPLE_BATCH,
                                 batch_uri=prediction_result)

    return training_example_meta, model_meta, evaluate_example_meta, validate_example_meta, predict_example_meta, result


def run_remote_mnist_keras_job():
    """main func"""

    """Get project data"""
    remote_train_data_file, remote_evaluate_data_file, remote_predict_data_file = get_and_upload_project_data()

    """Register meta in metadata store"""
    training_example_meta, model_meta, evaluate_example_meta, validate_example_meta, predict_example_meta, result = \
        preparation_job(remote_train_data_file, remote_evaluate_data_file, remote_predict_data_file)

    """Specify the configuration file to which runs this workflow"""
    workflow_config_file = get_file_dir(__file__) + '/../resources/workflow_config.yaml'

    """Set config for train job"""
    with af.global_config_file(config_path=workflow_config_file):
        with af.config(config='python_train_job'):
            """Read training dataset with af.read_example()"""
            train_raw_example = af.read_example(example_info=training_example_meta,
                                                executor=PythonObjectExecutor(python_object=LoadMnistTrainData()))

            """Training data preprocessing with af.transform()"""
            train_example = af.transform(input_data_list=[train_raw_example],
                                         executor=PythonObjectExecutor(python_object=TransformTrainData()),
                                         output_num=2,
                                         name='transformer')

            """Train model with af.train()"""
            train_channel = af.train(input_data_list=[train_example[0], train_example[1]],
                                     executor=PythonObjectExecutor(python_object=TrainModel()),
                                     model_info=model_meta,
                                     name='trainer')

        """Set config for evaluate job"""
        with af.config(config='python_evaluate_job'):
            """Read evaluating dataset with af.read()"""
            evaluate_raw_example = af.read_example(example_info=evaluate_example_meta,
                                                   executor=PythonObjectExecutor(python_object=LoadMnistEvaluateData()))

            """Evaluating data preprocessing with af.transform()"""
            evaluate_example = af.transform(input_data_list=[evaluate_raw_example],
                                            executor=PythonObjectExecutor(python_object=TransformEvaluateData()))
            """Evaluate model with af.evaluate()"""
            evaluate_channel = af.evaluate(input_data_list=[evaluate_example], model_info=model_meta,
                                           executor=PythonObjectExecutor(python_object=ModelEvaluate()),
                                           name='evaluator')

        """Set config for validating job"""
        with af.config(config='python_validate_job'):
            """Read validating dataset with af.read()"""
            validate_example = af.read_example(example_info=validate_example_meta,
                                               executor=PythonObjectExecutor(python_object=LoadMnistValidateData()))

            """Validate model with af.model_validate()"""
            validate_channel = af.model_validate(input_data_list=[validate_example], model_info=model_meta,
                                                 executor=PythonObjectExecutor(python_object=ModelValidate()),
                                                 name='validator')
        ## TODO: DESCREIBE the job
        """Set config for push job"""
        with af.config(config='python_push_job'):
            """Push model with af.push_model()"""
            push_channel = af.push_model(model_info=model_meta,
                                         executor=PythonObjectExecutor(python_object=PushModel()))

        """Set config for predict job"""
        with af.config(config='python_predict_job'):
            """Read prediction dataset with af.read()"""
            predict_example = af.read_example(example_info=predict_example_meta,
                                              executor=PythonObjectExecutor(python_object=LoadMnistPredictData()))

            """Predict with model with af.predict()"""
            predict_channel = af.predict(input_data_list=[predict_example], model_info=model_meta,
                                         executor=PythonObjectExecutor(python_object=ModelPredict()),
                                         name='predictor')

            """Write prediction result to file with af.write_example()"""
            af.write_example(input_data=predict_channel, example_info=result,
                             executor=PythonObjectExecutor(python_object=WriteExample()))

    """Set job control dependency"""

    """Evaluate job will start after train job finishes"""
    af.stop_before_control_dependency(evaluate_channel, train_channel)

    """Validate job will start after evaluate job finishes"""
    af.stop_before_control_dependency(validate_channel, evaluate_channel)

    """Push job will start after validate job finishes"""
    af.stop_before_control_dependency(push_channel, validate_channel)

    """Predict job will start after push job finishes"""
    af.stop_before_control_dependency(predict_channel, push_channel)

    """Run project with af.run_project()"""
    """project path is remote/"""
    workflow_id = af.run(path_util.get_file_dir(__file__) + '/../')

    """Wait for the workflow to finish with af.wait_workflow_execution_finished()"""
    res = af.wait_workflow_execution_finished(workflow_id)
    print("result {}".format(res))


if __name__ == '__main__':
    """Set project properties based on project.yaml"""
    af.set_project_config_file(get_file_dir(__file__) + '/../project.yaml')

    """Run workflow"""
    run_remote_mnist_keras_job()
```