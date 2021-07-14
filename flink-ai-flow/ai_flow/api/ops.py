#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
from typing import Union, Text, Tuple, Optional, List

from notification_service.base_notification import UNDEFINED_EVENT_TYPE, ANY_CONDITION
from ai_flow.client.ai_flow_client import get_ai_flow_client
from ai_flow.ai_graph.ai_node import AINode, ReadDatasetNode, WriteDatasetNode
from ai_flow.graph.channel import Channel
from ai_flow.workflow.control_edge import ControlEdge, \
    TaskAction, EventLife, ValueCondition, ConditionType, DEFAULT_NAMESPACE, AIFlowInternalEventType, ConditionConfig
from ai_flow.ai_graph.ai_graph import current_graph, add_ai_node_to_graph
from ai_flow.meta.dataset_meta import DatasetMeta
from ai_flow.meta.model_meta import ModelMeta, ModelVersionMeta
from ai_flow.context.project_context import current_project_config
from ai_flow.context.workflow_config_loader import current_workflow_config
from ai_flow.workflow.status import Status


def read_dataset(dataset_info: Union[DatasetMeta, Text, int],
                 read_dataset_processor=None,
                 name: Text = None) -> Channel:
    """
    Read dataset from the dataset operator. It can read dataset from external system.

    :param dataset_info: Information about the dataset which will be read. Its type can be DatasetMeta
                         of py:class:`ai_flow.meta.dataset_meta.DatasetMeta` or Text or int. The dataset_info
                         means name in the metadata service when its type is Text and it means id when its type is int.
                         The ai flow will get the dataset from metadata service by name or id.
    :param read_dataset_processor: The python user defined function in read dataset operator. User can write their own logic here.
    :param name: Name of the read_dataset operator.
    :return: Channel: data output channel.
    """
    if isinstance(dataset_info, DatasetMeta):
        dataset_meta = dataset_info
    elif isinstance(dataset_info, Text):
        dataset_meta = get_ai_flow_client().get_dataset_by_name(dataset_info)
    else:
        dataset_meta = get_ai_flow_client().get_dataset_by_id(dataset_info)

    node = ReadDatasetNode(name=name,
                           processor=read_dataset_processor,
                           properties=None,
                           node_type='read_dataset',
                           dataset=dataset_meta)
    add_ai_node_to_graph(node, inputs=None)
    outputs = node.outputs()
    output: Channel = outputs[0]
    return output


def write_dataset(input: Channel,
                  dataset_info: Union[DatasetMeta, Text, int],
                  write_dataset_processor=None,
                  name: Text = None
                  ) -> None:
    """
    Write dataset to dataset operator. It can write dataset to external system.

    :param input: Channel from the specific operator which generates data.
    :param dataset_info: Information about the dataset which will be read. Its type can be DataSetMeta
                         of py:class:`ai_flow.meta.dataset_meta.DatasetMeta` or Text or int. The dataset_info
                         means name in the metadata service when its type is Text and it means id when its type is int.
                         The ai flow will get the dataset from metadata service by name or id.
    :param write_dataset_processor: The python user defined function in write dataset operator. User can write their own logic here.
    :param name: Name of the read_dataset operator.
    :return: None.
    """
    if isinstance(dataset_info, DatasetMeta):
        dataset_meta = dataset_info
    elif isinstance(dataset_info, Text):
        dataset_meta = get_ai_flow_client().get_dataset_by_name(dataset_info)
    else:
        dataset_meta = get_ai_flow_client().get_dataset_by_id(dataset_info)

    node = WriteDatasetNode(name=name,
                            processor=write_dataset_processor,
                            properties=None,
                            node_type='write_dataset',
                            dataset=dataset_meta)
    add_ai_node_to_graph(node, inputs=input)
    return None


def transform(input: Union[Channel, List[Channel]],
              transform_processor,
              output_num=1,
              name: Text = None) -> Union[Channel, Tuple[Channel]]:
    """
    Transformer operator. Transform the dataset so that the original dataset can be used for trainer or other operators
    after feature engineering, data cleaning or some other data transformation.

    :param input: List of input data. It contains multiple channels from the operators which generate data.
    :param transform_processor: The user defined function in transform operator. User can write their own logic here.
    :param output_num: The output number of the operator. The default value is 1.
    :param name: Name of the transform operator.
    :return: Channel or Tuple[Channel]. It returns Channel When the output_num is 1 and returns Tuple[Channel] when
             the output_num is bigger than 1, and the len(Tuple(Channel)) is output_num.
    """
    return user_define_operation(input=input,
                                 name=name,
                                 processor=transform_processor,
                                 output_num=output_num,
                                 operation_type='transform')


def train(input: Union[Channel, List[Channel]],
          training_processor,
          model_info: Union[ModelMeta, Text, int],
          base_model_info: Union[ModelMeta, Text, int] = None,
          output_num=0,
          name: Text = None) -> Union[Channel, Tuple[Channel]]:
    """
    Trainer operator. Train model with the inputs or continually re-training the base model.

    :param input: List of Channel. It contains multiple channels from the operators which generate data.
    :param training_processor: The user defined function in train operator. User can write their own logic here.
    :param model_info: Information about the output model which is under training. Its type can be ModelMeta
                              of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The output_model_info
                              means name in the metadata service when its type is Text and it means id when its type is
                              int. The ai flow will get the model meta from metadata service by name or id.
    :param base_model_info: Information about the base model which will be trained. Its type can be ModelMeta
                            of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The base_model_info
                            means name in the metadata service when its type is Text and it means id when its type is
                            int. The ai flow will get the model meta from metadata service by name or id.
    :param output_num: The output number of the operator. The default value is 0.
    :param name: Name of the train operator.
    :return: Channel, Tuple[Channel].
    """
    if isinstance(model_info, ModelMeta):
        output_model_meta = model_info
    elif isinstance(model_info, Text):
        output_model_meta = get_ai_flow_client().get_model_by_name(model_info)
    else:
        output_model_meta = get_ai_flow_client().get_model_by_id(model_info)

    if base_model_info is not None:
        if isinstance(base_model_info, ModelMeta):
            base_model_meta = base_model_info
        elif isinstance(base_model_info, Text):
            base_model_meta = get_ai_flow_client().get_model_by_name(base_model_info)
        else:
            base_model_meta = get_ai_flow_client().get_model_by_id(base_model_info)
    else:
        base_model_meta = None

    return user_define_operation(input=input,
                                 name=name,
                                 processor=training_processor,
                                 model_info=output_model_meta,
                                 base_model_info=base_model_meta,
                                 output_num=output_num,
                                 operation_type='train')


def predict(input: Union[Channel, List[Channel]],
            model_info: Union[ModelMeta, Text, int],
            prediction_processor,
            model_version_info: Optional[Union[ModelVersionMeta, Text]] = None,
            output_num=1,
            name: Text = None) -> Union[Channel, Tuple[Channel]]:
    """
    Predictor Operator. Do prediction job with the specific model version.

    :param input: List of Channel. It contains the dataset data used in prediction.
    :param model_info: Information about the model which is in prediction. Its type can be ModelMeta
                       of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The model_info
                       means name in the metadata service when its type is Text and it means id when its type is
                       int. The ai flow will get the model meta from metadata service by name or id.
    :param prediction_processor: The user defined function in predict operator. User can write their own logic here.
    :param model_version_info: Information about the model version which is in prediction. Its type can be
                               ModelVersionMeta of py:class:`ai_flow.meta.model_meta.ModelVersionMeta`
                               or Text. The model_version_info means version in the metadata service
                               when its type is Text. The ai flow will get the model meta from metadata
                               service by version.
    :param output_num: The output number of the operator. The default value is 1.
    :param name: Name of the predict operator.
    :return: Channel or Tuple[Channel].
    """
    if isinstance(model_info, ModelMeta):
        model_meta = model_info
    elif isinstance(model_info, Text):
        model_meta = get_ai_flow_client().get_model_by_name(model_info)
    else:
        model_meta = get_ai_flow_client().get_model_by_id(model_info)

    if isinstance(model_version_info, ModelVersionMeta):
        model_version_meta = model_version_info
    elif isinstance(model_version_info, Text):
        model_version_meta = get_ai_flow_client() \
            .get_model_version_by_version(model_version_info,
                                          get_ai_flow_client().get_model_by_name(model_meta.name).uuid)
    else:
        model_version_meta = None

    return user_define_operation(input=input,
                                 name=name,
                                 model_info=model_meta,
                                 processor=prediction_processor,
                                 model_version_info=model_version_meta,
                                 output_num=output_num,
                                 operation_type='predict')


def evaluate(input: Union[Channel, List[Channel]],
             model_info: Union[ModelMeta, Text, int],
             evaluation_processor,
             output_num=0,
             name: Text = None) -> Union[Channel, Tuple[Channel]]:
    """
    Evaluate Operator. Do evaluate job with the specific model version.

    :param input: List of Channel. It contains the dataset data used in prediction.
    :param model_info: Information about the model which is in prediction. Its type can be ModelMeta
                       of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The model_info
                       means name in the metadata service when its type is Text and it means id when its type is
                       int. The ai flow will get the model meta from metadata service by name or id.
    :param evaluation_processor: The user defined function in evaluate operator. User can write their own logic here.
    :param output_num: The output number of the operator. The default value is 0.
    :param name: Name of the predict operator.
    :return: NoneChannel.
    """
    if isinstance(model_info, ModelMeta):
        model_meta = model_info
    elif isinstance(model_info, Text):
        model_meta = get_ai_flow_client().get_model_by_name(model_info)
    else:
        model_meta = get_ai_flow_client().get_model_by_id(model_info)

    return user_define_operation(input=input,
                                 name=name,
                                 model_info=model_meta,
                                 processor=evaluation_processor,
                                 output_num=output_num,
                                 operation_type='evaluate')


def dataset_validate(input: Channel,
                     dataset_validation_processor,
                     name: Text = None
                     ) -> None:
    """
    Dataset Validator Operator. Identifies anomalies in training and serving data in this operator.

    :param input: Channel. It contains the dataset data used in evaluation.
    :param dataset_validation_processor: The user defined function in dataset validate operator. User can write their own logic here.
    :param name: Name of the dataset validate operator.
    :return: NoneChannel.
    """
    return user_define_operation(input=input,
                                 processor=dataset_validation_processor,
                                 name=name,
                                 output_num=0,
                                 operation_type='dataset_validate'
                                 )


def model_validate(input: Union[Channel, List[Channel]],
                   model_info: Union[ModelMeta, Text, int],
                   model_validation_processor,
                   model_version_info: Optional[Union[ModelVersionMeta, Text]] = None,
                   base_model_version_info: Optional[Union[ModelVersionMeta, Text]] = None,
                   output_num=0,
                   name: Text = None) -> Union[Channel, Tuple[Channel]]:
    """
    Model Validator Operator. Compare the performance of two different versions of the same model and choose the better
    model version to make it ready to be in the stage of deployment.

    :param input: List of Channel. It contains the dataset data used in model validation.
    :param model_info: Information about the model which is in model validation. Its type can be ModelMeta
                       of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The model_info
                       means name in the metadata service when its type is Text and it means id when its type is
                       int. The ai flow will get the model meta from metadata service by name or id.
    :param model_validation_processor: The user defined function in model validate operator. User can write their own logic here.
    :param model_version_info: Information about the model version which is in model validation. Its type can be
                               ModelVersionMeta of py:class:`ai_flow.meta.model_meta.ModelVersionMeta`
                               or Text. The model_version_info means version in the metadata service
                               when its type is Text. The ai flow will get the model meta from metadata
                               service by version.
    :param base_model_version_info: Information about the model version which is in model validation. Its type can be
                                    ModelVersionMeta of py:class:`ai_flow.meta.model_meta.ModelVersionMeta`
                                    or Text. The model_version_info means version in the metadata service
                                    when its type is Text. The ai flow will get the model meta from metadata
                                    service by version.
    :param output_num: The output number of the operator. The default value is 0.
    :param name: Name of the model validate operator.
    :return: Channel.
    """
    if isinstance(model_info, ModelMeta):
        model_meta = model_info
    elif isinstance(model_info, Text):
        model_meta = get_ai_flow_client().get_model_by_name(model_info)
    else:
        model_meta = get_ai_flow_client().get_model_by_id(model_info)

    if isinstance(model_version_info, ModelVersionMeta):
        model_version_meta = model_version_info
    elif isinstance(model_version_info, Text):
        model_version_meta = get_ai_flow_client() \
            .get_model_version_by_version(model_version_info,
                                          get_ai_flow_client().get_model_by_name(model_meta.name).uuid)
    else:
        model_version_meta = None

    if isinstance(base_model_version_info, ModelVersionMeta):
        base_model_version_meta = model_version_info
    elif isinstance(base_model_version_info, Text):
        base_model_version_meta = get_ai_flow_client() \
            .get_model_version_by_version(model_version_info,
                                          get_ai_flow_client().get_model_by_name(model_meta.name).uuid)
    else:
        base_model_version_meta = None

    return user_define_operation(input=input,
                                 model_info=model_meta,
                                 processor=model_validation_processor,
                                 name=name,
                                 model_version_info=model_version_meta,
                                 base_model_version_info=base_model_version_meta,
                                 output_num=output_num,
                                 operation_type='model_validate'
                                 )


def push_model(model_info: Union[ModelMeta, Text, int],
               pushing_model_processor,
               model_version_info: Optional[Union[ModelVersionMeta, Text]] = None,
               name: Text = None) -> None:
    """
    Pusher operator. The pusher operator is used to push a validated model which is better than previous one to
    a deployment target.

    :param model_info: Information about the model which is in pusher. Its type can be ModelMeta
                       of py:class:`ai_flow.meta.model_meta.ModelMeta` or Text or int. The model_info
                       means name in the metadata service when its type is Text and it means id when its type is
                       int. The ai flow will get the model meta from metadata service by name or id.
    :param pushing_model_processor: The user defined function in pusher operator. User can write their own logic here.
    :param model_version_info: Information about the model version which is in push. Its type can be
                               ModelVersionMeta of py:class:`ai_flow.meta.model_meta.ModelVersionMeta`
                               or Text. The model_version_info means version in the metadata service
                               when its type is Text. The ai flow will get the model meta from metadata
                               service by version.
    :param name: Name of the push operator.
    :return: None.
    """
    if isinstance(model_info, ModelMeta) or model_info is None:
        model_meta = model_info
    elif isinstance(model_info, Text):
        model_meta = get_ai_flow_client().get_model_by_name(model_info)
    else:
        model_meta = get_ai_flow_client().get_model_by_id(model_info)

    if isinstance(model_version_info, ModelVersionMeta) or model_version_info is None:
        model_version_info = None
    elif isinstance(model_version_info, Text):
        model_version_info = get_ai_flow_client().get_model_version_by_version(version=model_version_info,
                                                                               model_id=model_meta.uuid)

    return user_define_operation(model_info=model_meta,
                                 processor=pushing_model_processor,
                                 model_version_info=model_version_info,
                                 name=name,
                                 operation_type='push_model')


def user_define_operation(
        processor=None,
        input: Union[None, Channel, List[Channel]] = None,
        output_num=1,
        name: Text = None,
        operation_type: Text = 'user_define_operation',
        **kwargs) -> Union[None, Channel, Tuple[Channel]]:
    """
    User defined operator.

    :param operation_type: The type of the operation.
    :param processor: The user defined function in operator. User can write their own logic here.
    :param input: It contains multiple channels from the operators which generate data.
    :param output_num: The output number of the operator. The default value is 1.
    :param name: Name of this operator.
    :param kwargs:
    :return: None or Channel or Tuple[Channel].
    """
    node = AINode(name=name,
                  processor=processor,
                  properties=None,
                  output_num=output_num,
                  node_type=operation_type,
                  **kwargs)
    add_ai_node_to_graph(node, inputs=input)
    outputs = node.outputs()
    if 0 == output_num:
        return None
    else:
        if 1 == len(outputs):
            output: Channel = outputs[0]
            return output
        else:
            output: List[Channel] = []
            for i in outputs:
                tmp: Channel = i
                output.append(tmp)
            return tuple(output)


def action_on_event(job_name: Text,
                    event_key: Text,
                    event_value: Text,
                    event_type: Text = UNDEFINED_EVENT_TYPE,
                    sender: Text = None,
                    namespace: Text = DEFAULT_NAMESPACE,
                    condition_type: ConditionType = ConditionType.NECESSARY,
                    action: TaskAction = TaskAction.START,
                    life: EventLife = EventLife.ONCE,
                    value_condition: ValueCondition = ValueCondition.EQUALS
                    ):
    """
       Add user defined control logic.
       :param job_name: The job name identify the job.
       :param namespace: The namespace of the event, which value uses the project name.
       :param event_key: The key of the event.
       :param event_value: The value of the event.
       :param event_type: The type of the event.
       :param sender: The event sender identity,which value uses the name of the job. If sender is None, the sender will be dependency.
       :param condition_type: The event condition type. Sufficient or Necessary.
       :param action: The action act on the src channel. Start or Restart.
       :param life: The life of the event. Once or Repeated.
       :param value_condition: The event value condition. Equal or Update. Equal means the src channel will start or
                               restart only when in the condition that the notification service updates a value which
                               equals to the event value under the specific event key, while update means src channel
                               will start or restart when in the the condition that the notification service has a update
                               operation on the event key which event value belongs.
       :return:None.
       """
    control_edge = ControlEdge(destination=job_name,
                               condition_config=ConditionConfig(
                                   event_key=event_key,
                                   event_value=event_value,
                                   event_type=event_type,
                                   condition_type=condition_type,
                                   action=action,
                                   life=life,
                                   value_condition=value_condition,
                                   namespace=namespace,
                                   sender=sender)
                               )
    current_graph().add_edge(job_name, control_edge)


def action_on_model_version_event(job_name: Text,
                                  model_name: Text,
                                  model_version_event_type: Text,
                                  namespace: Text = DEFAULT_NAMESPACE,
                                  action: TaskAction = TaskAction.RESTART,
                                  ) -> None:
    """
    Add model version control dependency. It means src channel will start when and only a new model version of the
    specific model is updated in notification service.

    :param action: ai_flow.workflow.control_edge.TaskAction
    :param namespace: the namespace of the event.
    :param model_version_event_type: one of ai_flow.model_center.entity.model_version_stage.ModelVersionEventType
    :param job_name: The job name
    :param model_name: Name of the model, refers to a specific model.
    :return: None.
    """
    action_on_event(job_name=job_name,
                    event_key=model_name,
                    event_value="*",
                    event_type=model_version_event_type,
                    action=action,
                    life=EventLife.ONCE,
                    value_condition=ValueCondition.UPDATED,
                    condition_type=ConditionType.SUFFICIENT,
                    namespace=namespace,
                    sender=ANY_CONDITION)


def action_on_dataset_event(job_name: Text,
                            dataset_name: Text,
                            action: TaskAction = TaskAction.START,
                            namespace: Text = DEFAULT_NAMESPACE
                            ) -> None:
    """
    Add dataset control dependency. It means src channel will start when and only the an new dataset of the specific
    dataset is updated in notification service.
    :param namespace: the namespace of the dataset
    :param job_name: The job name
    :param dataset_name: Name of the dataset, refers to a specific dataset.
    :param action: ai_flow.workflow.control_edge.TaskAction
    :return: None.
    """
    action_on_event(job_name=job_name,
                    event_key=dataset_name,
                    event_value="created",
                    event_type=AIFlowInternalEventType.DATASET_CHANGED,
                    action=action,
                    namespace=namespace,
                    sender=ANY_CONDITION
                    )


def action_on_job_status(job_name: Text,
                         upstream_job_name: Text,
                         upstream_job_status: Status = Status.FINISHED,
                         action: TaskAction = TaskAction.START):
    """
    Trigger job by upstream job status changed.
    :param job_name: The job name
    :param upstream_job_name: The upstream job name
    :param upstream_job_status: The upstream job status, type: ai_flow.workflow.status.Status
    :param action: The ai_flow.workflow.control_edge.TaskAction type.
    :return:
    """
    action_on_event(job_name=job_name,
                    event_key=current_workflow_config().workflow_name,
                    event_type=AIFlowInternalEventType.JOB_STATUS_CHANGED,
                    sender=upstream_job_name,
                    event_value=upstream_job_status,
                    action=action,
                    namespace=current_project_config().get_project_name(),
                    condition_type=ConditionType.SUFFICIENT
                    )
