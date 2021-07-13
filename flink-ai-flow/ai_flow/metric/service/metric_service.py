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
from ai_flow.endpoint.server.util import catch_exception
from ai_flow.metric.utils import proto_to_metric_meta, _warp_metric_meta_response, _warp_list_metric_metas_response, \
    proto_to_metric_summary, _warp_metric_summary_response, _warp_list_metric_summaries_response
from ai_flow.protobuf.message_pb2 import Response, ReturnCode
from ai_flow.protobuf.metric_service_pb2_grpc import MetricServiceServicer
from ai_flow.store.sqlalchemy_store import SqlAlchemyStore


class MetricService(MetricServiceServicer):

    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.store = SqlAlchemyStore(self.db_uri)

    @catch_exception
    def registerMetricMeta(self, request, context):
        metric_meta_proto = request.metric_meta
        metric_meta = proto_to_metric_meta(metric_meta_proto)
        res_metric_meta = self.store.register_metric_meta(metric_meta.metric_name,
                                                          metric_meta.metric_type,
                                                          metric_meta.project_name,
                                                          metric_meta.metric_desc,
                                                          metric_meta.dataset_name,
                                                          metric_meta.model_name,
                                                          metric_meta.job_name,
                                                          metric_meta.start_time,
                                                          metric_meta.end_time,
                                                          metric_meta.uri,
                                                          metric_meta.tags,
                                                          metric_meta.properties)
        return _warp_metric_meta_response(res_metric_meta)

    @catch_exception
    def updateMetricMeta(self, request, context):
        metric_meta_proto = request.metric_meta
        metric_meta = proto_to_metric_meta(metric_meta_proto)
        res_metric_meta = self.store.update_metric_meta(metric_meta.metric_name,
                                                        metric_meta.metric_desc,
                                                        metric_meta.project_name,
                                                        metric_meta.dataset_name,
                                                        metric_meta.model_name,
                                                        metric_meta.job_name,
                                                        metric_meta.start_time,
                                                        metric_meta.end_time,
                                                        metric_meta.uri,
                                                        metric_meta.tags,
                                                        metric_meta.properties)
        return _warp_metric_meta_response(res_metric_meta)

    @catch_exception
    def deleteMetricMeta(self, request, context):
        metric_name = request.metric_name
        try:
            self.store.delete_metric_meta(metric_name)
            return Response(return_code=str(ReturnCode.SUCCESS), return_msg='', data='')
        except Exception as e:
            return Response(return_code=str(ReturnCode.INTERNAL_ERROR), return_msg=str(e), data='')

    @catch_exception
    def getMetricMeta(self, request, context):
        metric_name = request.metric_name
        res_metric_meta = self.store.get_metric_meta(metric_name)
        return _warp_metric_meta_response(res_metric_meta)

    @catch_exception
    def listDatasetMetricMetas(self, request, context):
        dataset_name = request.dataset_name
        project_name = request.project_name.value if request.HasField('project_name') else None
        metric_metas = self.store.list_dataset_metric_metas(dataset_name=dataset_name, project_name=project_name)
        return _warp_list_metric_metas_response(metric_metas)

    @catch_exception
    def listModelMetricMetas(self, request, context):
        model_name = request.model_name
        project_name = request.project_name.value if request.HasField('project_name') else None
        metric_metas = self.store.list_model_metric_metas(model_name=model_name, project_name=project_name)
        return _warp_list_metric_metas_response(metric_metas)

    @catch_exception
    def registerMetricSummary(self, request, context):
        metric_summary_proto = request.metric_summary
        metric_summary = proto_to_metric_summary(metric_summary_proto)
        res_metric_summary = self.store.register_metric_summary(metric_summary.metric_name,
                                                                metric_summary.metric_key,
                                                                metric_summary.metric_value,
                                                                metric_summary.metric_timestamp,
                                                                metric_summary.model_version,
                                                                metric_summary.job_execution_id)
        return _warp_metric_summary_response(res_metric_summary)

    @catch_exception
    def updateMetricSummary(self, request, context):
        metric_summary_proto = request.metric_summary
        metric_summary = proto_to_metric_summary(metric_summary_proto)
        res_metric_summary = self.store.update_metric_summary(metric_summary.uuid,
                                                              metric_summary.metric_name,
                                                              metric_summary.metric_key,
                                                              metric_summary.metric_value,
                                                              metric_summary.metric_timestamp,
                                                              metric_summary.model_version,
                                                              metric_summary.job_execution_id)
        return _warp_metric_summary_response(res_metric_summary)

    @catch_exception
    def deleteMetricSummary(self, request, context):
        uuid = request.uuid
        try:
            self.store.delete_metric_summary(uuid)
            return Response(return_code=str(ReturnCode.SUCCESS), return_msg='', data='')
        except Exception as e:
            return Response(return_code=str(ReturnCode.INTERNAL_ERROR), return_msg=str(e), data='')

    @catch_exception
    def getMetricSummary(self, request, context):
        uuid = request.uuid
        metric_summary = self.store.get_metric_summary(uuid)
        return _warp_metric_summary_response(metric_summary)

    @catch_exception
    def listMetricSummaries(self, request, context):
        metric_name = request.metric_name.value if request.HasField('metric_name') else None
        metric_key = request.metric_key.value if request.HasField('metric_key') else None
        model_version = request.model_version.value if request.HasField('model_version') else None
        start_time = request.start_time.value if request.HasField('start_time') else None
        end_time = request.end_time.value if request.HasField('end_time') else None
        metric_summaries = self.store.list_metric_summaries(metric_name, metric_key, model_version, start_time,
                                                            end_time)
        return _warp_list_metric_summaries_response(metric_summaries)
