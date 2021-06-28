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
from typing import List, Text

from ai_flow.meta.dataset_meta import DatasetMeta
from ai_flow.endpoint.server.exception import AIFlowException
from ai_flow.store.db.db_model import SqlDataset, SqlProject, SqlModelRelation, \
    SqlModelVersionRelation, SqlArtifact
from ai_flow.store.db.db_model import (MongoProject, MongoDataset,
                                       MongoArtifact,
                                       MongoModelRelation, MongoModelVersionRelation)


class MetaToTable:

    @staticmethod
    def dataset_meta_to_table(name, data_format, description, uri,
                              create_time, update_time, properties, name_list, type_list, catalog_name,
                              catalog_type, catalog_database, catalog_connection_uri, catalog_table,
                              store_type='SqlAlchemyStore'):
        if properties is not None:
            properties = str(properties)
        if name_list is not None:
            name_list = str(name_list)
        if type_list is not None:
            data_type_list = []
            for c in type_list:
                data_type_list.append(c.value)
            data_type_list = str(data_type_list)
        else:
            data_type_list = None
        if store_type == 'MongoStore':
            _class = MongoDataset
        else:
            _class = SqlDataset
        return _class(name=name, format=data_format,
                      description=description, uri=uri, create_time=create_time,
                      update_time=update_time, properties=properties, name_list=name_list, type_list=data_type_list,
                      catalog_name=catalog_name, catalog_type=catalog_type, catalog_database=catalog_database,
                      catalog_connection_uri=catalog_connection_uri, catalog_table=catalog_table)

    @staticmethod
    def dataset_meta_list_to_table(dataset_meta_list: List[DatasetMeta], store_type='SqlAlchemyStore'):
        list_dataset_table = []
        for dataset_meta in dataset_meta_list:
            if dataset_meta.schema is not None:
                name_list = dataset_meta.schema.name_list
                type_list = dataset_meta.schema.type_list
                if name_list is not None and type_list is not None:
                    if len(name_list) != len(type_list):
                        raise AIFlowException("the length of name list and type list should be the same")
                if name_list is not None and type_list is None:
                    raise AIFlowException("the length of name list and type list should be the same")
                if name_list is None and type_list is not None:
                    raise AIFlowException("the length of name list and type list should be the same")
            else:
                name_list = None
                type_list = None
            list_dataset_table.append(MetaToTable.dataset_meta_to_table(name=dataset_meta.name,
                                                                        data_format=dataset_meta.data_format,
                                                                        description=dataset_meta.description,
                                                                        uri=dataset_meta.uri,
                                                                        create_time=dataset_meta.create_time,
                                                                        update_time=dataset_meta.update_time,
                                                                        properties=dataset_meta.properties,
                                                                        name_list=name_list,
                                                                        type_list=type_list,
                                                                        catalog_name=dataset_meta.catalog_name,
                                                                        catalog_type=dataset_meta.catalog_type,
                                                                        catalog_database=dataset_meta.catalog_database,
                                                                        catalog_connection_uri=dataset_meta.catalog_connection_uri,
                                                                        catalog_table=dataset_meta.catalog_table,
                                                                        store_type=store_type))
        return list_dataset_table

    @staticmethod
    def project_meta_to_table(name,
                              uri,
                              properties,
                              store_type='SqlAlchemyStore'
                              ):
        if properties is not None:
            properties = str(properties)
        if store_type == 'MongoStore':
            _class = MongoProject
        else:
            _class = SqlProject
        return _class(name=name, properties=properties, uri=uri)

    @staticmethod
    def artifact_meta_to_table(name, artifact_type, description, uri,
                               create_time, update_time, properties, store_type='SqlAlchemyStore'):
        if properties is not None:
            properties = str(properties)
        if store_type == 'MongoStore':
            _class = MongoArtifact
        else:
            _class = SqlArtifact
        return _class(name=name, artifact_type=artifact_type, description=description, uri=uri,
                      create_time=create_time, update_time=update_time, properties=properties)

    @staticmethod
    def model_relation_meta_to_table(name, project_id, store_type='SqlAlchemyStore'):
        if store_type == 'MongoStore':
            _class = MongoModelRelation
        else:
            _class = SqlModelRelation
        return _class(name=name, project_id=project_id)

    @staticmethod
    def model_version_relation_to_table(version, model_id, project_snapshot_id, store_type='SqlAlchemyStore'):
        if store_type == 'MongoStore':
            _class = MongoModelVersionRelation
        else:
            _class = SqlModelVersionRelation
        return _class(version=version, model_id=model_id,
                      project_snapshot_id=project_snapshot_id)

