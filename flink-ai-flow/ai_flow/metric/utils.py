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
from ai_flow.common.properties import Properties
from ai_flow.endpoint.server import stringValue, int64Value
from ai_flow.meta.metric_meta import MetricMeta, MetricType, MetricSummary
from ai_flow.protobuf.message_pb2 import MetricMetaProto, MetricSummaryProto, MetricTypeProto, ReturnCode, \
    RESOURCE_DOES_NOT_EXIST, SUCCESS
from ai_flow.protobuf.metric_service_pb2 import MetricMetaResponse, MetricSummaryResponse, ListMetricSummariesResponse, \
    ListMetricMetasResponse
from ai_flow.store.db.db_model import SqlMetricMeta, SqlMetricSummary, MongoMetricMeta, MongoMetricSummary


def table_to_metric_meta(metric_meta_result) -> MetricMeta:
    properties = metric_meta_result.properties
    if properties is not None:
        properties = ast.literal_eval(properties)
    return MetricMeta(metric_name=metric_meta_result.metric_name,
                      metric_type=MetricType.value_of(metric_meta_result.metric_type),
                      metric_desc=metric_meta_result.metric_desc,
                      project_name=metric_meta_result.project_name,
                      dataset_name=metric_meta_result.dataset_name,
                      model_name=metric_meta_result.model_name,
                      job_name=metric_meta_result.job_name,
                      start_time=metric_meta_result.start_time,
                      end_time=metric_meta_result.end_time,
                      uri=metric_meta_result.uri,
                      tags=metric_meta_result.tags,
                      properties=properties)


def table_to_metric_summary(metric_summary_result) -> MetricSummary:
    return MetricSummary(uuid=metric_summary_result.uuid,
                         metric_name=metric_summary_result.metric_name,
                         metric_key=metric_summary_result.metric_key,
                         metric_value=metric_summary_result.metric_value,
                         metric_timestamp=metric_summary_result.metric_timestamp,
                         model_version=metric_summary_result.model_version,
                         job_execution_id=metric_summary_result.job_execution_id)


def metric_meta_to_table(metric_name: Text,
                         metric_type: MetricType,
                         metric_desc: Optional[Text],
                         project_name: Text,
                         dataset_name: Optional[Text],
                         model_name: Optional[Text],
                         job_name: Optional[Text],
                         start_time: int,
                         end_time: int,
                         uri: Optional[Text],
                         tags: Optional[Text],
                         properties: Properties,
                         store_type: Text = 'SqlAlchemyStore'):
    if properties is not None:
        properties = str(properties)
    if store_type == 'MongoStore':
        _class = MongoMetricMeta
    else:
        _class = SqlMetricMeta
    return _class(metric_name=metric_name,
                  metric_type=metric_type.value,
                  metric_desc=metric_desc,
                  project_name=project_name,
                  dataset_name=dataset_name,
                  model_name=model_name,
                  job_name=job_name,
                  start_time=start_time,
                  end_time=end_time,
                  uri=uri,
                  tags=tags,
                  properties=properties)


def metric_summary_to_table(metric_name: Text,
                            metric_key: Text,
                            metric_value: Text,
                            metric_timestamp: int,
                            model_version: Optional[Text],
                            job_execution_id: Optional[Text],
                            store_type: Text = 'SqlAlchemyStore'):
    if store_type == 'MongoStore':
        _class = MongoMetricSummary
    else:
        _class = SqlMetricSummary
    return _class(metric_name=metric_name,
                  metric_key=metric_key,
                  metric_value=metric_value,
                  metric_timestamp=metric_timestamp,
                  model_version=model_version,
                  job_execution_id=job_execution_id)


def metric_meta_to_proto(metric_meta: MetricMeta) -> MetricMetaProto:
    if metric_meta.metric_type == MetricType.DATASET:
        metric_type = MetricTypeProto.DATASET
    else:
        metric_type = MetricTypeProto.MODEL
    return MetricMetaProto(metric_name=stringValue(metric_meta.metric_name),
                           metric_type=metric_type,
                           metric_desc=stringValue(metric_meta.metric_desc),
                           project_name=stringValue(metric_meta.project_name),
                           dataset_name=stringValue(metric_meta.dataset_name),
                           model_name=stringValue(metric_meta.model_name),
                           job_name=stringValue(metric_meta.job_name),
                           start_time=int64Value(metric_meta.start_time),
                           end_time=int64Value(metric_meta.end_time),
                           uri=stringValue(metric_meta.uri),
                           tags=stringValue(metric_meta.tags),
                           properties=metric_meta.properties)


def metric_summary_to_proto(metric_summary: MetricSummary) -> MetricSummaryProto:
    return MetricSummaryProto(uuid=metric_summary.uuid,
                              metric_name=stringValue(metric_summary.metric_name),
                              metric_key=stringValue(metric_summary.metric_key),
                              metric_value=stringValue(metric_summary.metric_value),
                              metric_timestamp=int64Value(metric_summary.metric_timestamp),
                              model_version=stringValue(metric_summary.model_version),
                              job_execution_id=stringValue(metric_summary.job_execution_id))


def proto_to_metric_meta(metric_meta_proto: MetricMetaProto) -> MetricMeta:
    if MetricTypeProto.DATASET == metric_meta_proto.metric_type:
        metric_type = MetricType.DATASET
    else:
        metric_type = MetricType.MODEL
    return MetricMeta(
        metric_name=metric_meta_proto.metric_name.value if metric_meta_proto.HasField('metric_name') else None,
        metric_type=metric_type,
        metric_desc=metric_meta_proto.metric_desc.value
        if metric_meta_proto.HasField('metric_desc') else None,
        project_name=metric_meta_proto.project_name.value,
        dataset_name=metric_meta_proto.dataset_name.value if metric_meta_proto.HasField(
            'dataset_name') else None,
        model_name=metric_meta_proto.model_name.value if metric_meta_proto.HasField(
            'model_name') else None,
        job_name=metric_meta_proto.job_name.value if metric_meta_proto.HasField('job_name') else None,
        start_time=metric_meta_proto.start_time.value if metric_meta_proto.HasField(
            'start_time') else None,
        end_time=metric_meta_proto.end_time.value if metric_meta_proto.HasField(
            'end_time') else None,
        uri=metric_meta_proto.uri.value if metric_meta_proto.HasField('uri') else None,
        tags=metric_meta_proto.tags.value if metric_meta_proto.HasField('tags') else None,
        properties=None if metric_meta_proto.properties == {} else metric_meta_proto.properties,
    )


def proto_to_metric_summary(metric_summary_proto: MetricSummaryProto) -> MetricSummary:
    return MetricSummary(uuid=metric_summary_proto.uuid,
                         metric_name=metric_summary_proto.metric_name.value if metric_summary_proto.HasField(
                             'metric_name') else None,
                         metric_key=metric_summary_proto.metric_key.value if metric_summary_proto.HasField(
                             'metric_key') else None,
                         metric_value=metric_summary_proto.metric_value.value if metric_summary_proto.HasField(
                             'metric_value') else None,
                         metric_timestamp=metric_summary_proto.metric_timestamp.value if metric_summary_proto.HasField(
                             'metric_timestamp') else None,
                         model_version=metric_summary_proto.model_version.value if metric_summary_proto.HasField(
                             'model_version') else None,
                         job_execution_id=metric_summary_proto.job_execution_id.value if metric_summary_proto.HasField(
                             'job_execution_id') else None
                         )


def _warp_metric_meta_response(metric_meta: Optional[MetricMeta]) -> MetricMetaResponse:
    if metric_meta is not None:
        return MetricMetaResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                  metric_meta=metric_meta_to_proto(metric_meta))
    else:
        return MetricMetaResponse(return_code=1,
                                  return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                                  metric_meta=None)


def _warp_list_metric_metas_response(metric_metas: Union[None, MetricMeta, List[MetricMeta]]) -> MetricMetaResponse:
    if metric_metas is not None:
        if isinstance(metric_metas, MetricMeta):
            return ListMetricMetasResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                           metric_metas=[metric_meta_to_proto(metric_metas)])
        else:
            res = []
            for metric_meta in metric_metas:
                res.append(metric_meta_to_proto(metric_meta))
            return ListMetricMetasResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                           metric_metas=res)
    else:
        return ListMetricMetasResponse(return_code=1,
                                       return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                                       metric_metas=None)


def _warp_metric_summary_response(metric_summary: Optional[MetricSummary]) -> MetricSummaryResponse:
    if metric_summary is not None:
        return MetricSummaryResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                     metric_summary=metric_summary_to_proto(metric_summary))
    else:
        return MetricSummaryResponse(return_code=1,
                                     return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                                     metric_summary=None)


def _warp_list_metric_summaries_response(
        metric_summaries: Union[None, MetricSummary, List[MetricSummary]]) -> ListMetricSummariesResponse:
    if metric_summaries is not None:
        if isinstance(metric_summaries, MetricSummary):
            return ListMetricSummariesResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                               metric_summaries=[metric_summary_to_proto(metric_summaries)])
        else:
            res = []
            for metric_summary in metric_summaries:
                res.append(metric_summary_to_proto(metric_summary))
            return ListMetricSummariesResponse(return_code=0, return_msg=ReturnCode.Name(SUCCESS).lower(),
                                               metric_summaries=res)
    else:
        return ListMetricSummariesResponse(return_code=1,
                                           return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                                           metric_summaries=None)
