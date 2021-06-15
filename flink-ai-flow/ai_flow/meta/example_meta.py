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
from enum import Enum
from typing import Text, List

from ai_flow.common.properties import Properties
from ai_flow.util.json_utils import Jsonable


class ExampleSupportType(str, Enum):
    EXAMPLE_STREAM = 'EXAMPLE_STREAM'
    EXAMPLE_BATCH = 'EXAMPLE_BATCH'
    EXAMPLE_BOTH = 'EXAMPLE_BOTH'


class DataType(str, Enum):
    INT32 = 'INT32'
    INT64 = 'INT64'
    FLOAT32 = 'FLOAT32'
    FLOAT64 = 'FLOAT64'
    STRING = 'STRING'
    INT32ARRAY = 'INT32ARRAY'
    INT64ARRAY = 'INT64ARRAY'
    FLOAT32ARRAY = 'FLOAT32ARRAY'
    FLOAT64ARRAY = 'FLOAT64ARRAY'
    STRINGARRAY = 'STRINGARRAY'
    BYTES = 'BYTES'
    BYTESARRAY = 'BYTESARRAY'


class Schema(Jsonable):
    def __init__(self,
                 name_list: List[Text] = None,
                 type_list: List[DataType] = None):
        self.name_list = name_list
        self.type_list = type_list

    def __str__(self):
        return '<\n' \
               'Schema\n' \
               'name_list:{},\n' \
               'type_list:{},\n' \
               '>'.format(self.name_list, self.type_list)


class ExampleMeta(Jsonable):
    """define example meta """

    def __init__(self,
                 name: Text,
                 support_type: ExampleSupportType,
                 data_type: Text = None,
                 data_format: Text = None,
                 description: Text = None,
                 batch_uri: Text = None,
                 stream_uri: Text = None,
                 create_time: int = None,
                 update_time: int = None,
                 properties: Properties = None,
                 schema: Schema = None,
                 catalog_name: Text = None,
                 catalog_type: Text = None,
                 catalog_database: Text = None,
                 catalog_connection_uri: Text = None,
                 catalog_version: Text = None,
                 catalog_table: Text = None,
                 uuid: int = None) -> None:
        """ create example meta
        Args:
            name: example name
            support_type: BATCH, STREAM or BOTH execution mode
            data_type: numpy, pandas, etc.
            data_format: csv, json, etc.
            description: example description
            batch_uri: batch data persistent storage
            stream_uri: stream data persistent storage
            create_time: create example datetime
            update_time: update example datetime
            properties: properties for the example
        """
        self.name = name
        self.support_type = support_type
        self.data_type = data_type
        self.data_format = data_format
        self.description = description
        self.batch_uri = batch_uri
        self.stream_uri = stream_uri
        self.create_time = create_time
        self.update_time = update_time
        self.properties = properties
        self.schema = schema
        self.catalog_name = catalog_name
        self.catalog_type = catalog_type
        self.catalog_database = catalog_database
        self.catalog_connection_uri = catalog_connection_uri
        self.catalog_version = catalog_version
        self.catalog_table = catalog_table
        self.uuid = uuid

    def __str__(self):
        return '<\n' \
               'ExampleMeta\n' \
               'uuid:{},\n' \
               'name:{},\n' \
               'support_type:{},\n' \
               'data_format:{}, \n' \
               'description:{},\n' \
               'batch_uri:{},\n' \
               'stream_uri:{},\n' \
               'create_time:{},\n' \
               'update_time:{},\n' \
               'properties:{},\nschema:{},\n' \
               'catalog_type:{},\ncatalog_connection_uri:{}' \
               '\n>'.format(
            self.uuid, self.name, self.support_type, self.data_format,
            self.description, self.batch_uri, self.stream_uri,
            self.create_time, self.update_time, self.properties, self.schema,
            self.catalog_name, self.catalog_type, self.catalog_database,
            self.catalog_connection_uri, self.catalog_version, self.catalog_table)


# example api
def create_example(name: Text,
                   support_type: ExampleSupportType,
                   data_type: Text = None,
                   data_format: Text = None,
                   description: Text = None,
                   batch_uri: Text = None,
                   stream_uri: Text = None,
                   create_time: int = None,
                   update_time: int = None,
                   properties: Properties = None,
                   name_list: List[Text] = None,
                   type_list: List[DataType] = None,
                   catalog_name: Text = None,
                   catalog_type: Text = None,
                   catalog_database: Text = None,
                   catalog_connection_uri: Text = None,
                   catalog_version: Text = None,
                   catalog_table: Text = None,
                   ) -> ExampleMeta:
    schema = Schema(name_list=name_list, type_list=type_list)
    return ExampleMeta(name=name, support_type=support_type, data_type=data_type,
                       data_format=data_format, description=description,
                       batch_uri=batch_uri, stream_uri=stream_uri, schema=schema,
                       create_time=create_time, update_time=update_time, properties=properties,
                       catalog_name=catalog_name, catalog_type=catalog_type, catalog_database=catalog_database,
                       catalog_connection_uri=catalog_connection_uri, catalog_version=catalog_version,
                       catalog_table=catalog_table
                       )
