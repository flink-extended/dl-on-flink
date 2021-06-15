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


class DatasetMeta(Jsonable):
    """define dataset meta """

    def __init__(self,
                 name: Text,
                 data_format: Text = None,
                 description: Text = None,
                 uri: Text = None,
                 create_time: int = None,
                 update_time: int = None,
                 properties: Properties = None,
                 schema: Schema = None,
                 catalog_name: Text = None,
                 catalog_type: Text = None,
                 catalog_database: Text = None,
                 catalog_connection_uri: Text = None,
                 catalog_table: Text = None,
                 uuid: int = None) -> None:
        """ create dataset meta
        Args:
            name: dataset name
            data_format: csv, json, etc.
            description: dataset description
            uri: data persistent storage
            create_time: create dataset datetime
            update_time: update dataset datetime
            properties: properties for the dataset
            schema: column list
        """
        self.name = name
        self.data_format = data_format
        self.description = description
        self.uri = uri
        self.create_time = create_time
        self.update_time = update_time
        self.properties = properties
        self.schema = schema
        self.catalog_name = catalog_name
        self.catalog_type = catalog_type
        self.catalog_database = catalog_database
        self.catalog_connection_uri = catalog_connection_uri
        self.catalog_table = catalog_table
        self.uuid = uuid

    def __str__(self):
        return '<\n' \
               'DatasetMeta\n' \
               'uuid:{},\n' \
               'name:{},\n' \
               'data_format:{}, \n' \
               'description:{},\n' \
               'uri:{},\n' \
               'create_time:{},\n' \
               'update_time:{},\n' \
               'properties:{},\n' \
               'schema:{},\n' \
               'catalog_name:{},\n'\
               'catalog_type:{},\n' \
               'catalog_database:{},\n' \
               'catalog_connection_uri:{},\n' \
               'catalog_table:{}' \
               '\n>'.format(
            self.uuid, self.name, self.data_format, self.description, self.uri,
            self.create_time, self.update_time, self.properties, self.schema,
            self.catalog_name, self.catalog_type, self.catalog_database,
            self.catalog_connection_uri, self.catalog_table)


# dataset api
def create_dataset(name: Text,
                   data_format: Text = None,
                   description: Text = None,
                   uri: Text = None,
                   create_time: int = None,
                   update_time: int = None,
                   properties: Properties = None,
                   name_list: List[Text] = None,
                   type_list: List[DataType] = None,
                   catalog_name: Text = None,
                   catalog_type: Text = None,
                   catalog_database: Text = None,
                   catalog_connection_uri: Text = None,
                   catalog_table: Text = None,
                   ) -> DatasetMeta:
    schema = Schema(name_list=name_list, type_list=type_list)
    return DatasetMeta(name=name, data_format=data_format, description=description,
                       uri=uri, schema=schema, create_time=create_time, update_time=update_time,
                       properties=properties, catalog_name=catalog_name, catalog_type=catalog_type,
                       catalog_database=catalog_database, catalog_connection_uri=catalog_connection_uri,
                       catalog_table=catalog_table
                       )
