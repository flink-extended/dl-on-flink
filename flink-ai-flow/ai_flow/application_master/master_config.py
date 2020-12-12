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
from ai_flow.common.configuration import AIFlowConfiguration
from enum import Enum
from typing import Text


class DBType(str, Enum):
    SQLITE = "sql_lite"
    MYSQL = "mysql"

    @staticmethod
    def value_of(db_type):
        if db_type in ('SQL_LITE', 'sql_lite'):
            return DBType.SQLITE
        elif db_type in ('MYSQL', 'mysql'):
            return DBType.MYSQL
        else:
            raise NotImplementedError


class MasterConfig(AIFlowConfiguration):
    def get_sql_lite_db_file(self):
        db_uri = self.get_db_uri()
        return db_uri[10:]

    def get_master_port(self):
        return self["master_port"]

    def get_db_uri(self):
        return self["db_uri"]

    def get_db_type(self) -> DBType:
        return DBType.value_of(self["db_type"])

    def set_master_port(self, value):
        self["master_port"] = value

    def set_db_uri(self, db_type: DBType, uri: Text):
        self["db_type"] = db_type.value
        self["db_uri"] = uri

    def start_default_notification(self)->bool:
        if "start_default_notification" in self and self['start_default_notification'] is False:
            return False
        else:
            return True

    def set_notification_uri(self, notification_uri):
        self['notification_uri'] = notification_uri

    def get_notification_uri(self):
        return self.get('notification_uri')

