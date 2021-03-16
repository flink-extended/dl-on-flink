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
from notification_service import service
from notification_service.event_storage import DbEventStorage
from notification_service.mongo_event_storage import MongoEventStorage
from ai_flow.store.mongo_store import MongoStore
from ai_flow.store.db.db_util import extract_db_engine_from_uri, parse_mongo_uri
from ai_flow.application_master.master_config import DBType


class NotificationService(service.NotificationService):

    def __init__(self, backend_store_uri):
        db_engine = extract_db_engine_from_uri(backend_store_uri)
        if DBType.value_of(db_engine) == DBType.MONGODB:
            username, password, host, port, db = parse_mongo_uri(backend_store_uri)
            super().__init__(storage=MongoEventStorage(host=host,
                                                       port=int(port),
                                                       username=username,
                                                       password=password,
                                                       db=db))
        else:
            super().__init__(storage=DbEventStorage(backend_store_uri))
