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

from ai_flow.api.context_extractor import ContextExtractor
from notification_service.base_notification import UNDEFINED_EVENT_TYPE, ANY_CONDITION
from ai_flow.client.ai_flow_client import get_ai_flow_client
from ai_flow.ai_graph.ai_node import AINode, ReadDatasetNode, WriteDatasetNode
from ai_flow.graph.channel import Channel
from ai_flow.workflow.control_edge import ControlEdge, \
    JobAction, EventLife, ValueCondition, DEFAULT_NAMESPACE, AIFlowInternalEventType, \
    EventCondition, SchedulingRule, MeetAnyEventCondition
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
    Reads the dataset through the user-defined processor based on the metadata of dataset. The processor reads dataset
    from external system and generates the :class:`~ai_flow.ai_graph.ai_node.ReadDatasetNode` with
    :class:`~ai_flow.meta.dataset_meta.DatasetMeta`.

    :param dataset_info: Information about the dataset read by the processor. The type of dataset information could be
                                      :class:`~ai_flow.meta.dataset_meta.DatasetMeta` or Text(i.e. the name of dataset)
                                      or int(i.e. the id of dataset). If the type is Text or int, this method will get
                                      the metadata of dataset by the name or id of dataset by default.
    :param read_dataset_processor: The user-defined processor composed of the logic that reads dataset.
    :param name: Name of the reading dataset operator represent for the
                            :class:`~ai_flow.ai_graph.ai_node.ReadDatasetNode`.
    :return: The :class:`~ai_flow.graph.channel.Channel`.
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
    Writes the dataset through the user-defined processor based on the metadata of dataset. The processor writes dataset
    to external system and generates the :class:`~ai_flow.ai_graph.ai_node.WriteDatasetNode` with
    :class:`~ai_flow.meta.dataset_meta.DatasetMeta`.

    :param input: The input :class:`~ai_flow.graph.channel.Channel` from the operator that generates the data used to
                            write dataset.
    :param dataset_info: Information about the dataset writen by the processor. The type of dataset information could be
                                      :class:`~ai_flow.meta.dataset_meta.DatasetMeta` or Text(i.e. the name of dataset)
                                      or int(i.e. the id of dataset). If the type is Text or int, this method will get
                                      the metadata of dataset by the name or id of dataset by default.
    :param write_dataset_processor: The user-defined processor composed of the logic that writes dataset.
    :param name: Name of the writing dataset operator represent for the
                            :class:`~ai_flow.ai_graph.ai_node.WriteDatasetNode`.
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
    Transforms dataset through the user-defined processor based on the input :class:`~ai_flow.graph.channel.Channel`.
    The processor generates the transforming :class:`~ai_flow.ai_graph.ai_node.AINode`.

    :param input: List of the input :class:`~ai_flow.graph.channel.Channel` that contains the multiple channels from the
                           operators which generate the data used to transform.
    :param transform_processor: The user-defined processor composed of the transformation logic.
    :param output_num: The output :class:`~ai_flow.graph.channel.Channel` number of the transforming operator.
                                      The default value is 1.
    :param name: Name of the transforming operator represent for the :class:`~ai_flow.ai_graph.ai_node.AINode`.
    :return: Returns the :class:`~ai_flow.graph.channel.Channel` when the `output_num` is 1 and returns
                 Tuple[:class:`~ai_flow.graph.channel.Channel`] when the `output_num` is bigger than 1.
    """
    return user_define_operation(input=input,
                                 name=name,
                                 processor=transform_processor,
                                 output_num=output_num,
                                 operation_type='transform')


def train(input: Union[Channel, List[Channel]],
          model_info: Union[ModelMeta, Text, int],
          training_processor,
          base_model_info: Union[ModelMeta, Text, int] = None,
          output_num=0,
          name: Text = None) -> Union[Channel, Tuple[Channel]]:
    """
    Trains model through the user-defined processor with the information of models based on the input
    :class:`~ai_flow.graph.channel.Channel`. The processor generates the model training
    :class:`~ai_flow.ai_graph.ai_node.AINode`.

    :param input: List of the input :class:`~ai_flow.graph.channel.Channel` that contains the multiple channels from the
                           operators which generate the data used to train model.
    :param model_info: Information about the model trained by the processor. The type of model could be
                                     :class:`~ai_flow.meta.model_meta.ModelMeta` or Text(i.e. the name of model) or int(
                                     i.e. the id of model). If the type is Text or int, this method will get the
                                     metadata of model by the name or id of model by default.
    :param training_processor: The user-defined processor composed of the logic that trains model.
    :param base_model_info: Information about the base model for training by the processor. The type of model could be
                                              :class:`~ai_flow.meta.model_meta.ModelMeta` or Text or int. The
                                              `base_model_info` means the name of model when the type is Text and it
                                              means the id of model when the type is int, which gets the metadata of
                                              model by the id or name of model.
    :param output_num: The output :class:`~ai_flow.graph.channel.Channel` number of the model training operator.
                                      The default value is 0.
    :param name: Name of the model training operator represent for the :class:`~ai_flow.ai_graph.ai_node.AINode`.
    :return: Returns the :class:`~ai_flow.graph.channel.Channel` when the `output_num` is 1 and returns
                 Tuple[:class:`~ai_flow.graph.channel.Channel`] when the `output_num` is bigger than 1.
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
    Predicts through the user-defined processor with the information of model and model version based on the input
    :class:`~ai_flow.graph.channel.Channel`. The processor generates the model prediction
    :class:`~ai_flow.ai_graph.ai_node.AINode`.

    :param input: List of the input :class:`~ai_flow.graph.channel.Channel` that contains the multiple channels from the
                           operators which generate the data used to predict model.
    :param model_info: Information about the model predicted by the processor. The type of model could be
                                     :class:`~ai_flow.meta.model_meta.ModelMeta` or Text(i.e. the name of model) or int(
                                     i.e. the id of model). If the type is Text or int, this method will get the
                                     metadata of model by the name or id of model by default.
    :param prediction_processor: The user-defined processor composed of the logic that predicts model.
    :param model_version_info: Information about the model version predicted by the processor. The type of model version
                                                  could be :class:`~ai_flow.meta.model_meta.ModelVersionMeta` or Text(
                                                  i.e. the `version` field of
                                                  :class:`~ai_flow.meta.model_meta.ModelVersionMeta`). If the type is
                                                  Text, this method will get the metadata of model version by the
                                                  version of model version by default.
    :param output_num: The output :class:`~ai_flow.graph.channel.Channel` number of the model prediction operator.
                                      The default value is 1.
    :param name: Name of the model prediction operator represent for the :class:`~ai_flow.ai_graph.ai_node.AINode`.
    :return: Returns the :class:`~ai_flow.graph.channel.Channel` when the `output_num` is 1 and returns
                 Tuple[:class:`~ai_flow.graph.channel.Channel`] when the `output_num` is bigger than 1.
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
    Evaluates model through the user-defined processor with the information of model based on the input
    :class:`~ai_flow.graph.channel.Channel`. The processor generates the model evaluating
    :class:`~ai_flow.ai_graph.ai_node.AINode`.

    :param input: List of the input :class:`~ai_flow.graph.channel.Channel` that contains the multiple channels from the
                           operators which generate the data used to evaluate model.
    :param model_info: Information about the model evaluated by the processor. The type of model could be
                                     :class:`~ai_flow.meta.model_meta.ModelMeta` or Text(i.e. the name of model) or int(
                                     i.e. the id of model). If the type is Text or int, this method will get the
                                     metadata of model by the name or id of model by default.
    :param evaluation_processor: The user-defined processor composed of the logic that evaluates model.
    :param output_num: The output :class:`~ai_flow.graph.channel.Channel` number of the model evaluating operator.
                                      The default value is 0.
    :param name: Name of the model evaluating operator represent for the :class:`~ai_flow.ai_graph.ai_node.AINode`.
    :return: Returns the :class:`~ai_flow.graph.channel.Channel` when the `output_num` is 1 and returns
                 Tuple[:class:`~ai_flow.graph.channel.Channel`] when the `output_num` is bigger than 1.
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
    Validates dataset through the user-defined processor based on the input :class:`~ai_flow.graph.channel.Channel`.
    The processor generates the dataset validating :class:`~ai_flow.ai_graph.ai_node.AINode`.

    :param input: List of the input :class:`~ai_flow.graph.channel.Channel` that contains the multiple channels from
                           the operators which generate the data used to validate dataset.
    :param dataset_validation_processor: The user-defined processor composed of the logic that validates dataset.
    :param name: Name of the dataset validating operator represent for the :class:`~ai_flow.ai_graph.ai_node.AINode`.
    :return: Returns the :class:`~ai_flow.graph.channel.Channel` when the `output_num` is 1 and returns
                 Tuple[:class:`~ai_flow.graph.channel.Channel`] when the `output_num` is bigger than 1.
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
    Validates model through the user-defined processor with the information of model and model versions based on the input
    :class:`~ai_flow.graph.channel.Channel`. The processor generates the model validating
    :class:`~ai_flow.ai_graph.ai_node.AINode`.

    :param input: List of the input :class:`~ai_flow.graph.channel.Channel` that contains the multiple channels from the
                           operators which generate the data used to validate model.
    :param model_info: Information about the model validated by the processor. The type of model could be
                                     :class:`~ai_flow.meta.model_meta.ModelMeta` or Text(i.e. the name of model) or int(
                                     i.e. the id of model). If the type is Text or int, this method will get the
                                     metadata of model by the name or id of model by default.
    :param model_validation_processor: The user-defined processor composed of the logic that validates model.
    :param model_version_info: Information about the model version validated by the processor. The type of model version
                                                  could be :class:`~ai_flow.meta.model_meta.ModelVersionMeta` or Text(
                                                  i.e. the `version` field of
                                                  :class:`~ai_flow.meta.model_meta.ModelVersionMeta`). If the type is
                                                  Text, this method will get the metadata of model version by the
                                                  version of model version by default.
    :param base_model_version_info: Information about the base model version for validating by the processor. The type
                                                            of model version could be
                                                            :class:`~ai_flow.meta.model_meta.ModelVersionMeta` or Text(
                                                            i.e. the `version` field of 
                                                            :class:`~ai_flow.meta.model_meta.ModelVersionMeta`). If the
                                                            type is Text, this method will get the metadata of model
                                                            version by the version of model version by default.
    :param output_num: The output :class:`~ai_flow.graph.channel.Channel` number of the model validating operator.
                                      The default value is 0.
    :param name: Name of the model validating operator represent for the :class:`~ai_flow.ai_graph.ai_node.AINode`.
    :return: Returns the :class:`~ai_flow.graph.channel.Channel` when the `output_num` is 1 and returns
                 Tuple[:class:`~ai_flow.graph.channel.Channel`] when the `output_num` is bigger than 1.
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
    Pushes model through the user-defined processor with the information of model version based on the input
    :class:`~ai_flow.graph.channel.Channel`. The processor generates the model pushing
    :class:`~ai_flow.ai_graph.ai_node.AINode`.

    :param model_info: Information about the model pushed by the processor. The type of model could be
                                     :class:`~ai_flow.meta.model_meta.ModelMeta` or Text(i.e. the name of model) or int(
                                     i.e. the id of model). If the type is Text or int, this method will get the
                                     metadata of model by the name or id of model by default.
    :param pushing_model_processor: The user-defined processor composed of the logic that pushes model.
    :param model_version_info: Information about the model version pushed by the processor. The type of model version
                                                  could be :class:`~ai_flow.meta.model_meta.ModelVersionMeta` or Text(
                                                  i.e. the `version` field of
                                                  :class:`~ai_flow.meta.model_meta.ModelVersionMeta`). If the type is
                                                  Text, this method will get the metadata of model version by the
                                                  version of model version by default.
    :param name: Name of the model pushing operator represent for the :class:`~ai_flow.ai_graph.ai_node.AINode`.
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


def user_define_operation(input: Union[None, Channel, List[Channel]] = None,
                          processor=None,
                          output_num=1,
                          name: Text = None,
                          operation_type: Text = 'user_define_operation',
                          **kwargs) -> Union[None, Channel, Tuple[Channel]]:
    """
    Operation through the user-defined processor based on the input :class:`~ai_flow.graph.channel.Channel`. The
    processor generates the :class:`~ai_flow.ai_graph.ai_node.AINode`.

    :param input: List of the input :class:`~ai_flow.graph.channel.Channel` that contains the multiple channels from the
                           operators which generate the data.
    :param processor: The user-defined processor composed of the processing logic.
    :param output_num: The output :class:`~ai_flow.graph.channel.Channel` number. The default value is 1.
    :param name: Name of the operator represent for the :class:`~ai_flow.ai_graph.ai_node.AINode`.
    :param operation_type: The type of the operation.
    :param kwargs: The arguments of the operation used.
    :return: Returns None when no output and returns the :class:`~ai_flow.graph.channel.Channel` when the `output_num`
                 is 1 and returns Tuple[:class:`~ai_flow.graph.channel.Channel`] when the `output_num` is bigger than 1.
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
                    value_condition: ValueCondition = ValueCondition.EQUALS,
                    action: JobAction = JobAction.START):
    """
    When the specified event is met, the :class:`~ai_flow.workflow.control_edge.JobAction` is triggered on the job with
    the given job name. It is a convenient method to add a :class:`~ai_flow.workflow.control_edge.MeetAnyEventCondition`
    with one event to a job.

    :param job_name: The name of the job triggered.
    :param event_key: The key of the event met.
    :param event_value: The value of the event met.
    :param event_type: The type of the event met.
    :param sender: The sender of event which uses the name of the job. If sender is None, the sender is dependency.
    :param namespace: The namespace of the event which uses the name of the project.
    :param value_condition: The event :class:`~ai_flow.workflow.control_edge.ValueCondition`, whose value is EQUALS or UPDATE.
                                            EQUALS means the source channel will start or restart only in the condition
                                            that the notification service updates a value which equals to the event
                                            value under the specified event key, while UPDATE means the source channel
                                            will start or restart when in the the condition that the notification
                                            service has a update operation on the event key which event value belongs.
    :param action: The :class:`~ai_flow.workflow.control_edge.JobAction` acts on the source channel whose value includes
                             START, RESTART, STOP and NONE.
    """
    event_condition = MeetAnyEventCondition()
    event_condition.add_event(event_key, event_value, event_type, namespace, sender, EventLife.ONCE, value_condition)
    action_on_events(job_name, event_condition, action)


def action_on_events(job_name: Text, event_condition: EventCondition, action: JobAction):
    """
    Defines a rule which is the combination of a :class:`~ai_flow.workflow.control_edge.EventCondition` and
    :class:`~ai_flow.workflow.control_edge.JobAction`, on the job with the given name. When the
    :class:`~ai_flow.workflow.control_edge.EventCondition` of the rule met, the corresponding
    :class:`~ai_flow.workflow.control_edge.JobAction` will be triggered on the job. User could call the method
    multiple times on the same job to add multiples rules, the rules will be checked according to the order of the
    the method call.

    :param job_name: The name of the job to add the rule.
    :param event_condition: The :class:`~ai_flow.workflow.control_edge.EventCondition` of the rule.
    :param action: The :class:`~ai_flow.workflow.control_edge.JobAction` to take when the
                             :class:`~ai_flow.workflow.control_edge.EventCondition` is met.
    """
    rule = SchedulingRule(event_condition, action)
    control_edge = ControlEdge(destination=job_name, scheduling_rule=rule)
    current_graph().add_edge(job_name, control_edge)


def action_on_model_version_event(job_name: Text,
                                  model_name: Text,
                                  model_version_event_type: Text,
                                  namespace: Text = DEFAULT_NAMESPACE,
                                  action: JobAction = JobAction.RESTART):
    """
    Adds the model version control dependency. It means the job will take given action when the type of model version
    event is updated to the specified  type.

    :param job_name: The name of the job triggered.
    :param model_name: The name of the model refer to a specified model.
    :param model_version_event_type: The type of the model version event, whose value is of the
                                                             :class:`~ai_flow.model_center.entity.model_version_stage.ModelVersionEventType`.
    :param namespace: The namespace of the event which uses the name of the project.
    :param action: The :class:`~ai_flow.workflow.control_edge.JobAction` acts on the source channel whose value includes
                             START, RESTART, STOP and NONE.
    """
    action_on_event(job_name=job_name,
                    event_key=model_name,
                    event_value="*",
                    event_type=model_version_event_type,
                    action=action,
                    value_condition=ValueCondition.UPDATED,
                    namespace=namespace,
                    sender=ANY_CONDITION)


def action_on_dataset_event(job_name: Text,
                            dataset_name: Text,
                            namespace: Text = DEFAULT_NAMESPACE,
                            action: JobAction = JobAction.START):
    """
    Adds the dataset control dependency. It means the job will take given action when only a new dataset of the
    specified dataset is updated in notification service.

    :param job_name: The name of the job triggered.
    :param dataset_name: The name of the dataset refer to a specified dataset.
    :param namespace: The namespace of the event which uses the name of the project.
    :param action: The :class:`~ai_flow.workflow.control_edge.JobAction` acts on the source channel whose value includes
                             START, RESTART, STOP and NONE.
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
                         action: JobAction = JobAction.START):
    """
    Triggers the job with the given name when the status of the upstream job changes.

    :param job_name: The name of the job triggered.
    :param upstream_job_name: The name of the upstream job.
    :param upstream_job_status: The status of the upstream job.
    :param action: The :class:`~ai_flow.workflow.control_edge.JobAction` acts on the source channel whose value includes
                             START, RESTART, STOP and NONE.
    """
    event_key = '.'.join([current_workflow_config().workflow_name, upstream_job_name])
    action_on_event(job_name=job_name,
                    event_key=event_key,
                    event_type=AIFlowInternalEventType.JOB_STATUS_CHANGED,
                    sender=upstream_job_name,
                    event_value=upstream_job_status,
                    action=action,
                    namespace=current_project_config().get_project_name())


def set_context_extractor(context_extractor: ContextExtractor):
    """
    Set the :class:`ContextExtractor` for the current workflow.

    :param context_extractor: the :class:`ContextExtractor` for the current workflow.
    """
    current_graph().set_context_extractor(context_extractor)
