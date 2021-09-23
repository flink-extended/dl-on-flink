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
import asyncio
import functools
import inspect
import logging
import os
import sys
import tempfile
import threading
from concurrent import futures
from typing import Dict

import grpc
from grpc import _common, _server
from grpc._cython.cygrpc import StatusCode
from grpc._server import _serialize_response, _status, _abort, _Context, _unary_request, \
    _select_thread_pool_for_behavior, _unary_response_in_pool

from ai_flow.endpoint.server.high_availability import SimpleAIFlowServerHaManager, HighAvailableService
from ai_flow.endpoint.server.server_config import DBType
from ai_flow.metadata_store.service.service import MetadataService
from ai_flow.metric.service.metric_service import MetricService
from ai_flow.model_center.service.service import ModelCenterService
from ai_flow.protobuf.high_availability_pb2_grpc import add_HighAvailabilityManagerServicer_to_server
from ai_flow.scheduler_service.service.service import SchedulerService, SchedulerServiceConfig
from ai_flow.store.db.base_model import base
from ai_flow.store.db.db_util import extract_db_engine_from_uri, create_db_store
from ai_flow.store.mongo_store import MongoStoreConnManager
from ai_flow.store.sqlalchemy_store import SqlAlchemyStore
from notification_service.proto import notification_service_pb2_grpc
from notification_service.service import NotificationService

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../../..")))

from ai_flow.protobuf import model_center_service_pb2_grpc, \
    metadata_service_pb2_grpc, metric_service_pb2_grpc, scheduling_service_pb2_grpc

_PORT = '50051'
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class AIFlowServer(object):
    """
    Block/Async server of an AIFlow Rest Endpoint that provides Metadata/Model/Notification function service.
    """

    def __init__(self, store_uri=None, port=_PORT,
                 start_default_notification: bool = True,
                 notification_uri=None,
                 start_meta_service: bool = True,
                 start_model_center_service: bool = True,
                 start_metric_service: bool = True,
                 start_scheduler_service: bool = True,
                 scheduler_service_config: Dict = None,
                 enabled_ha: bool = False,
                 ha_manager=None,
                 ha_server_uri=None,
                 ha_storage=None,
                 ttl_ms: int = 10000):
        self.store_uri = store_uri
        self.db_type = DBType.value_of(extract_db_engine_from_uri(store_uri))
        self.executor = Executor(futures.ThreadPoolExecutor(max_workers=10))
        self.server = grpc.server(self.executor)
        self.start_default_notification = start_default_notification
        self.enabled_ha = enabled_ha
        self.start_scheduler_service = start_scheduler_service
        server_uri = 'localhost:{}'.format(port)
        notification_uri = server_uri if start_default_notification and notification_uri is None else notification_uri
        if start_default_notification:
            logging.info("start default notification service.")
            notification_service_pb2_grpc.add_NotificationServiceServicer_to_server(
                NotificationService.from_storage_uri(store_uri),
                self.server)
        if start_model_center_service:
            logging.info("start model center service.")

            model_center_service_pb2_grpc.add_ModelCenterServiceServicer_to_server(
                ModelCenterService(store_uri=store_uri,
                                   notification_uri=notification_uri),
                self.server)
        if start_meta_service:
            logging.info("start meta service.")
            metadata_service_pb2_grpc.add_MetadataServiceServicer_to_server(
                MetadataService(db_uri=store_uri, server_uri=server_uri), self.server)
        if start_metric_service:
            logging.info("start metric service.")
            metric_service_pb2_grpc.add_MetricServiceServicer_to_server(MetricService(db_uri=store_uri), self.server)

        if start_scheduler_service:
            self._add_scheduler_service(scheduler_service_config, store_uri, notification_uri)

        if enabled_ha:
            self._add_ha_service(ha_manager, ha_server_uri, ha_storage, store_uri, ttl_ms)

        self.server.add_insecure_port('[::]:' + str(port))

        self._stop = threading.Event()

    def _add_scheduler_service(self, scheduler_service_config, db_uri, notification_uri):
        logging.info("start scheduler service.")
        real_config = SchedulerServiceConfig(scheduler_service_config)
        self.scheduler_service = SchedulerService(real_config, db_uri, notification_uri)
        scheduling_service_pb2_grpc.add_SchedulingServiceServicer_to_server(self.scheduler_service,
                                                                            self.server)

    def _add_ha_service(self, ha_manager, ha_server_uri, ha_storage, store_uri, ttl_ms):
        if ha_manager is None:
            ha_manager = SimpleAIFlowServerHaManager()
        if ha_server_uri is None:
            raise ValueError("ha_server_uri is required with ha enabled!")
        if ha_storage is None:
            ha_storage = create_db_store(store_uri)
        self.ha_service = HighAvailableService(ha_manager, ha_server_uri, ha_storage, ttl_ms)
        add_HighAvailabilityManagerServicer_to_server(self.ha_service, self.server)

    def run(self, is_block=False):
        if self.enabled_ha:
            self.ha_service.start()
        self.server.start()
        if self.start_scheduler_service:
            self.scheduler_service.start()
        logging.info('AIFlow server started.')
        if is_block:
            try:
                while not self._stop.is_set():
                    self._stop.wait(_ONE_DAY_IN_SECONDS)
            except KeyboardInterrupt:
                logging.info("received KeyboardInterrupt")
                self.stop()
        else:
            pass

    def stop(self, clear_sql_lite_db_file=False):
        logging.info("stopping AIFlow server")
        if self.start_scheduler_service:
            self.scheduler_service.stop()
        self.server.stop(0)
        if self.enabled_ha:
            self.ha_service.stop()
        self.executor.shutdown()

        if self.db_type == DBType.SQLITE and clear_sql_lite_db_file:
            store = SqlAlchemyStore(self.store_uri)
            base.metadata.drop_all(store.db_engine)
            os.remove(self.store_uri[10:])
        elif self.db_type == DBType.MONGODB:
            MongoStoreConnManager().disconnect_all()

        self._stop.set()
        logging.info('AIFlow server stopped.')

    def _clear_db(self):
        if self.db_type == DBType.SQLITE:
            store = SqlAlchemyStore(self.store_uri)
            base.metadata.drop_all(store.db_engine)
            base.metadata.create_all(store.db_engine)
        elif self.db_type == DBType.MONGODB:
            MongoStoreConnManager().drop_all()


def _loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    if not loop.is_running() or loop.is_closed():
        loop.run_forever()
    pending = asyncio.all_tasks(loop=loop)
    if pending:
        loop.run_until_complete(asyncio.gather(*pending))


class Executor(futures.Executor):
    def __init__(self, thread_pool, loop=None):
        super().__init__()
        self._shutdown = False
        self._thread_pool = thread_pool
        self._loop = loop or asyncio.get_event_loop()
        if not self._loop.is_running() or self._loop.is_closed():
            self._thread = threading.Thread(target=_loop, args=(self._loop,), daemon=True)
            self._thread.start()

    def submit(self, fn, *args, **kwargs):
        if self._shutdown:
            raise RuntimeError('Cannot schedule new futures after shutdown.')
        if not self._loop.is_running():
            raise RuntimeError('Loop must be started before any function could be submitted.')
        if inspect.iscoroutinefunction(fn):
            coroutine = fn(*args, **kwargs)
            return asyncio.run_coroutine_threadsafe(coroutine, self._loop)
        else:
            func = functools.partial(fn, *args, **kwargs)
            return self._loop.run_in_executor(self._thread_pool, func)

    def shutdown(self, wait=True):
        self._shutdown = True
        if wait:
            self._thread_pool.shutdown()


async def _call_behavior_async(rpc_event, state, behavior, argument, request_deserializer):
    context = _Context(rpc_event, state, request_deserializer)
    try:
        return await behavior(argument, context), True
    except Exception as e:
        with state.condition_type:
            if e not in state.rpc_errors:
                logging.exception(e)
                _abort(state, rpc_event.operation_call, StatusCode.unknown, _common.encode(e))
        return None, False


async def _unary_response_in_pool_async(rpc_event, state, behavior, argument_thunk, request_deserializer,
                                        response_serializer):
    argument = argument_thunk()
    if argument is not None:
        response, proceed = await _call_behavior_async(rpc_event, state, behavior, argument, request_deserializer)
        if proceed:
            serialized_response = _serialize_response(rpc_event, state, response, response_serializer)
            if serialized_response is not None:
                _status(rpc_event, state, serialized_response)


def _handle_unary_unary(rpc_event, state, method_handler, default_thread_pool):
    unary_request = _unary_request(rpc_event, state, method_handler.request_deserializer)
    thread_pool = _select_thread_pool_for_behavior(method_handler.unary_unary, default_thread_pool)
    if asyncio.iscoroutinefunction(method_handler.unary_unary):
        return thread_pool.submit(_unary_response_in_pool_async, rpc_event, state, method_handler.unary_unary,
                                  unary_request, method_handler.request_deserializer,
                                  method_handler.response_serializer)
    else:
        return thread_pool.submit(_unary_response_in_pool, rpc_event, state, method_handler.unary_unary, unary_request,
                                  method_handler.request_deserializer, method_handler.response_serializer)


_server._handle_unary_unary = _handle_unary_unary

if __name__ == '__main__':
    fd, temp_db_file = tempfile.mkstemp()
    os.close(fd)
    store_uri = '%s%s' % ('sqlite:///', temp_db_file)
    server = AIFlowServer(store_uri=store_uri)
    server.run(is_block=True)
