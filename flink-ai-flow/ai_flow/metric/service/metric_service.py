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
from ai_flow.meta.metric_meta import MetricType
from ai_flow.metric.utils import proto_to_metric_meta, _warp_metric_meta_response, _warp_list_metric_meta_response, \
    proto_to_metric_summary, _warp_metric_summary_response, _warp_list_metric_summary_response
from ai_flow.protobuf.message_pb2 import MetricTypeProto
from ai_flow.protobuf.message_pb2 import Response, ReturnCode
from ai_flow.protobuf.metric_service_pb2_grpc import MetricServiceServicer
from ai_flow.endpoint.server.util import catch_exception
from ai_flow.store.sqlalchemy_store import SqlAlchemyStore
from ai_flow.store.mongo_store import MongoStore
from ai_flow.store.db.db_util import extract_db_engine_from_uri, parse_mongo_uri
from ai_flow.application_master.master_config import DBType


class MetricService(MetricServiceServicer):

    def __init__(self, db_uri):
        self.db_uri = db_uri
        db_engine = extract_db_engine_from_uri(self.db_uri)
        if DBType.value_of(db_engine) == DBType.MONGODB:
            username, password, host, port, db = parse_mongo_uri(self.db_uri)
            self.store = MongoStore(host=host,
                                    port=int(port),
                                    username=username,
                                    password=password,
                                    db=db)
        else:
            self.store = SqlAlchemyStore(self.db_uri)

    @catch_exception
    def registerMetricMeta(self, request, context):
        metric_meta_proto = request.metric_meta

        metric_meta = proto_to_metric_meta(metric_meta_proto)

        res_metric_meta = self.store.register_metric_meta(metric_meta.name,
                                                          metric_meta.dataset_id,
                                                          metric_meta.model_name,
                                                          metric_meta.model_version,
                                                          metric_meta.job_id,
                                                          metric_meta.start_time,
                                                          metric_meta.end_time,
                                                          metric_meta.metric_type,
                                                          metric_meta.uri,
                                                          metric_meta.tags,
                                                          metric_meta.metric_description,
                                                          metric_meta.properties)

        return _warp_metric_meta_response(res_metric_meta)

    def registerMetricSummary(self, request, context):
        metric_summary_proto = request.metric_summary

        metric_summary = proto_to_metric_summary(metric_summary_proto)

        res_metric_summary = self.store.register_metric_summary(metric_id=metric_summary.metric_id,
                                                                metric_key=metric_summary.metric_key,
                                                                metric_value=metric_summary.metric_value)
        return _warp_metric_summary_response(res_metric_summary)

    def updateMetricMeta(self, request, context):
        metric_meta_proto = request.metric_meta
        if metric_meta_proto.metric_type == MetricTypeProto.DATASET:
            metric_type = MetricType.DATASET
        else:
            metric_type = MetricType.MODEL
        res_metric_meta = self.store.update_metric_meta(metric_meta_proto.uuid,
                                                        metric_meta_proto.name.value
                                                        if metric_meta_proto.HasField('name') else None,
                                                        metric_meta_proto.dataset_id.value
                                                        if metric_meta_proto.HasField('dataset_id') else None,
                                                        metric_meta_proto.model_name.value
                                                        if metric_meta_proto.HasField('model_name') else None,
                                                        metric_meta_proto.model_version.value
                                                        if metric_meta_proto.HasField('model_version') else None,
                                                        metric_meta_proto.job_id.value
                                                        if metric_meta_proto.HasField('job_id') else None,
                                                        metric_meta_proto.start_time.value
                                                        if metric_meta_proto.HasField('start_time') else None,
                                                        metric_meta_proto.end_time.value
                                                        if metric_meta_proto.HasField('end_time') else None,
                                                        metric_type,
                                                        metric_meta_proto.uri.value
                                                        if metric_meta_proto.HasField('uri') else None,
                                                        metric_meta_proto.tags.value
                                                        if metric_meta_proto.HasField('tags') else None,
                                                        metric_meta_proto.metric_description.value
                                                        if metric_meta_proto.HasField('metric_description') else None,
                                                        metric_meta_proto.properties
                                                        if {} == metric_meta_proto.properties else None)

        return _warp_metric_meta_response(res_metric_meta)

    def updateMetricSummary(self, request, context):
        metric_summary_proto = request.metric_summary
        res_metric_summary = self.store.update_metric_summary(
            uuid=metric_summary_proto.uuid,
            metric_id=metric_summary_proto.metric_id.value
            if metric_summary_proto.HasField('metric_id') else None,
            metric_key=metric_summary_proto.metric_key.value
            if metric_summary_proto.HasField('metric_key') else None,
            metric_value=metric_summary_proto.metric_value.value
            if metric_summary_proto.HasField('metric_value') else None
        )
        return _warp_metric_summary_response(res_metric_summary)

    def getMetricMeta(self, request, context):
        metric_name = request.metric_name
        res_metric_meta = self.store.get_metric_meta(metric_name)
        return _warp_metric_meta_response(res_metric_meta)

    def getDatasetMetricMeta(self, request, context):
        dataset_id = request.dataset_id
        metric_meta = self.store.get_dataset_metric_meta(dataset_id=dataset_id)
        return _warp_list_metric_meta_response(metric_meta)

    def getModelMetricMeta(self, request, context):
        model_name = request.model_name
        model_version = request.model_version
        metric_meta = self.store.get_model_metric_meta(model_name=model_name, model_version=model_version)
        return _warp_list_metric_meta_response(metric_meta)

    def getMetricSummary(self, request, context):
        metric_id = request.metric_id
        metric_summary = self.store.get_metric_summary(metric_id=metric_id)
        return _warp_list_metric_summary_response(metric_summary)

    def deleteMetricMeta(self, request, context):
        uuid = request.uuid
        try:
            self.store.delete_metric_meta(uuid)
            return Response(return_code=str(ReturnCode.SUCCESS), return_msg='', data='')
        except Exception as e:
            return Response(return_code=str(ReturnCode.INTERNAL_ERROR), return_msg=str(e), data='')

    def deleteMetricSummary(self, request, context):
        uuid = request.uuid
        try:
            self.store.delete_metric_summary(uuid)
            return Response(return_code=str(ReturnCode.SUCCESS), return_msg='', data='')
        except Exception as e:
            return Response(return_code=str(ReturnCode.INTERNAL_ERROR), return_msg=str(e), data='')
