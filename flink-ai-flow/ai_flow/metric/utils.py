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
import ast
from typing import Text, Optional, Union, List
from ai_flow.protobuf.metric_service_pb2 import MetricMetaResponse, ListMetricMetaResponse, \
    MetricSummaryResponse, ListMetricSummaryResponse
from ai_flow.endpoint.server import int64Value, stringValue
from ai_flow.common.properties import Properties
from ai_flow.meta.metric_meta import MetricMeta, MetricType, MetricSummary
from ai_flow.protobuf.message_pb2 import MetricMetaProto, MetricSummaryProto, MetricTypeProto, ReturnCode, \
    SUCCESS, RESOURCE_DOES_NOT_EXIST
from ai_flow.store.db.db_model import SqlMetricMeta, SqlMetricSummary
from ai_flow.store.db.db_model import MongoMetricSummary, MongoMetricMeta


def table_to_metric_meta(metric_meta_result) -> MetricMeta:
    properties = metric_meta_result.properties
    if properties is not None:
        properties = ast.literal_eval(properties)
    return MetricMeta(uuid=metric_meta_result.uuid,
                      name=metric_meta_result.name,
                      dataset_id=metric_meta_result.dataset_id,
                      model_name=metric_meta_result.model_name,
                      model_version=metric_meta_result.model_version,
                      job_id=metric_meta_result.job_id,
                      start_time=metric_meta_result.start_time,
                      end_time=metric_meta_result.end_time,
                      metric_type=MetricType.value_of(metric_meta_result.metric_type),
                      uri=metric_meta_result.uri,
                      tags=metric_meta_result.tags,
                      metric_description=metric_meta_result.metric_description,
                      properties=properties)


def table_to_metric_summary(metric_summary_result) -> MetricSummary:
    return MetricSummary(uuid=metric_summary_result.uuid,
                         metric_id=metric_summary_result.metric_id,
                         metric_key=metric_summary_result.metric_key,
                         metric_value=metric_summary_result.metric_value)


def metric_meta_to_table(name: Text,
                         dataset_id: int,
                         model_name: Optional[Text],
                         model_version: Optional[Text],
                         job_id: int,
                         start_time: int,
                         end_time: int,
                         metric_type: MetricType,
                         uri: Text,
                         tags: Text,
                         metric_description: Text,
                         properties: Properties,
                         store_type: Text = 'SqlAlchemyStore'):
    if properties is not None:
        properties = str(properties)
    if store_type == 'MongoStore':
        _class = MongoMetricMeta
    else:
        _class = SqlMetricMeta
    return _class(name=name,
                  dataset_id=dataset_id,
                  model_name=model_name,
                  model_version=model_version,
                  job_id=job_id,
                  start_time=start_time,
                  end_time=end_time,
                  metric_type=metric_type.value,
                  uri=uri,
                  tags=tags,
                  metric_description=metric_description,
                  properties=properties)


def metric_summary_to_table(metric_id: int,
                            metric_key: Text,
                            metric_value: Text,
                            store_type: Text = 'SqlAlchemyStore'):
    if store_type == 'MongoStore':
        _class = MongoMetricSummary
    else:
        _class = SqlMetricSummary
    return _class(metric_id=metric_id,
                  metric_key=metric_key,
                  metric_value=metric_value)


def metric_meta_to_proto(metric_meta: MetricMeta) -> MetricMetaProto:
    if metric_meta.metric_type == MetricType.DATASET:
        metric_type = MetricTypeProto.DATASET
    else:
        metric_type = MetricTypeProto.MODEL

    return MetricMetaProto(uuid=metric_meta.uuid,
                           name=stringValue(metric_meta.name),
                           dataset_id=int64Value(metric_meta.dataset_id),
                           model_name=stringValue(metric_meta.model_name),
                           model_version=stringValue(metric_meta.model_version),
                           job_id=int64Value(metric_meta.job_id),
                           start_time=int64Value(metric_meta.start_time),
                           end_time=int64Value(metric_meta.end_time),
                           metric_type=metric_type,
                           uri=stringValue(metric_meta.uri),
                           tags=stringValue(metric_meta.tags),
                           metric_description=stringValue(metric_meta.metric_description),
                           properties=metric_meta.properties)


def metric_summary_to_proto(metric_summary: MetricSummary) -> MetricSummaryProto:
    return MetricSummaryProto(uuid=metric_summary.uuid,
                              metric_id=int64Value(metric_summary.metric_id),
                              metric_key=stringValue(metric_summary.metric_key),
                              metric_value=stringValue(metric_summary.metric_value))


def proto_to_metric_meta(metric_meta_proto: MetricMetaProto) -> MetricMeta:
    if MetricTypeProto.DATASET == metric_meta_proto.metric_type:
        metric_type = MetricType.DATASET
    else:
        metric_type = MetricType.MODEL

    return MetricMeta(uuid=metric_meta_proto.uuid,
                      name=metric_meta_proto.name.value,
                      dataset_id=metric_meta_proto.dataset_id.value,
                      model_name=metric_meta_proto.model_name.value,
                      model_version=metric_meta_proto.model_version.value,
                      job_id=metric_meta_proto.job_id.value,
                      start_time=metric_meta_proto.start_time.value,
                      end_time=metric_meta_proto.end_time.value,
                      metric_type=metric_type,
                      uri=metric_meta_proto.uri.value if metric_meta_proto.HasField('uri') else None,
                      tags=metric_meta_proto.tags.value if metric_meta_proto.HasField('tags') else None,
                      metric_description=metric_meta_proto.metric_description.value
                      if metric_meta_proto.HasField('metric_description') else None,
                      properties=metric_meta_proto.properties
                      )


def proto_to_metric_summary(metric_summary_proto: MetricSummaryProto) -> MetricSummary:
    return MetricSummary(uuid=metric_summary_proto.uuid,
                         metric_id=metric_summary_proto.metric_id.value,
                         metric_key=metric_summary_proto.metric_key.value
                         if metric_summary_proto.HasField('metric_key') else None,
                         metric_value=metric_summary_proto.metric_value.value
                         if metric_summary_proto.HasField('metric_value') else None
                         )


def _warp_metric_meta_response(metric_meta: Optional[MetricMeta]) -> MetricMetaResponse:
    if metric_meta is not None:
        return MetricMetaResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                  metric_meta=metric_meta_to_proto(metric_meta))
    else:
        return MetricMetaResponse(return_code=1,
                                  return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                                  metric_meta=None)


def _warp_list_metric_meta_response(metric_meta: Union[None, MetricMeta, List[MetricMeta]]) -> MetricMetaResponse:
    if metric_meta is not None:
        if isinstance(metric_meta, MetricMeta):
            return ListMetricMetaResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                          metric_meta=[metric_meta_to_proto(metric_meta)])
        else:
            res = []
            for meta in metric_meta:
                res.append(metric_meta_to_proto(meta))
            return ListMetricMetaResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                          metric_meta=res)
    else:
        return ListMetricMetaResponse(return_code=1,
                                      return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                                      metric_meta=None)


def _warp_metric_summary_response(metric_summary: Optional[MetricSummary]) -> MetricSummaryResponse:
    if metric_summary is not None:
        return MetricSummaryResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                     metric_summary=metric_summary_to_proto(metric_summary))
    else:
        return MetricSummaryResponse(return_code=1,
                                     return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                                     metric_summary=None)


def _warp_list_metric_summary_response(metric_summary: Optional[List[MetricSummary]]) -> ListMetricSummaryResponse:
    if metric_summary is not None:
        res = []
        for summary in metric_summary:
            res.append(metric_summary_to_proto(summary))
        return ListMetricSummaryResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                         metric_summary=res)
    else:
        return ListMetricSummaryResponse(return_code=1,
                                         return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                                         metric_summary=None)
