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

from ai_flow.meta.example_meta import ExampleMeta
from ai_flow.endpoint.server.exception import AIFlowException
from ai_flow.store.db.db_model import SqlExample, SqlProject, SqlJob, SqlWorkflowExecution, SqlModelRelation, \
    SqlModelVersionRelation, SqlArtifact
from ai_flow.store.db.db_model import (MongoProject, MongoExample, MongoJob,
                                       MongoArtifact, MongoWorkflowExecution,
                                       MongoModelRelation, MongoModelVersionRelation)


class MetaToTable:

    @staticmethod
    def example_meta_to_table(name, support_type, data_type, data_format, description, batch_uri, stream_uri,
                              create_time, update_time, properties, name_list, type_list, catalog_name,
                              catalog_type, catalog_database, catalog_connection_uri, catalog_version, catalog_table,
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
            _class = MongoExample
        else:
            _class = SqlExample
        return _class(name=name, support_type=support_type, data_type=data_type, format=data_format,
                      description=description, batch_uri=batch_uri, stream_uri=stream_uri, create_time=create_time,
                      update_time=update_time, properties=properties, name_list=name_list, type_list=data_type_list,
                      catalog_name=catalog_name, catalog_type=catalog_type, catalog_database=catalog_database,
                      catalog_connection_uri=catalog_connection_uri, catalog_version=catalog_version,
                      catalog_table=catalog_table)

    @staticmethod
    def example_meta_list_to_table(example_meta_list: List[ExampleMeta], store_type='SqlAlchemyStore'):
        list_example_table = []
        for example_meta in example_meta_list:
            if example_meta.schema is not None:
                name_list = example_meta.schema.name_list
                type_list = example_meta.schema.type_list
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
            list_example_table.append(MetaToTable.example_meta_to_table(name=example_meta.name,
                                                                        support_type=example_meta.support_type,
                                                                        data_type=example_meta.data_type,
                                                                        data_format=example_meta.data_format,
                                                                        description=example_meta.description,
                                                                        batch_uri=example_meta.batch_uri,
                                                                        stream_uri=example_meta.stream_uri,
                                                                        create_time=example_meta.create_time,
                                                                        update_time=example_meta.update_time,
                                                                        properties=example_meta.properties,
                                                                        name_list=name_list,
                                                                        type_list=type_list,
                                                                        catalog_name=example_meta.catalog_name,
                                                                        catalog_type=example_meta.catalog_type,
                                                                        catalog_database=example_meta.catalog_database,
                                                                        catalog_connection_uri=example_meta.catalog_connection_uri,
                                                                        catalog_table=example_meta.catalog_table,
                                                                        catalog_version=example_meta.catalog_version,
                                                                        store_type=store_type))
        return list_example_table

    @staticmethod
    def project_meta_to_table(name,
                              uri,
                              properties,
                              user,
                              password,
                              project_type,
                              store_type='SqlAlchemyStore'
                              ):
        if properties is not None:
            properties = str(properties)
        if store_type == 'MongoStore':
            _class = MongoProject
        else:
            _class = SqlProject
        return _class(name=name, properties=properties, uri=uri, user=user, password=password,
                      project_type=project_type)

    @staticmethod
    def job_meta_to_table(name, job_id, properties, start_time, end_time, job_state, log_uri,
                          workflow_execution_id, signature, store_type='SqlAlchemyStore'):
        if properties is not None:
            properties = str(properties)
        if store_type == 'MongoStore':
            _class = MongoJob
        else:
            _class = SqlJob
        return _class(job_id=job_id, name=name, properties=properties, start_time=start_time, end_time=end_time,
                      job_state=job_state, log_uri=log_uri, workflow_execution_id=workflow_execution_id,
                      signature=signature)

    @staticmethod
    def artifact_meta_to_table(name, data_format, description, batch_uri, stream_uri,
                               create_time, update_time, properties, store_type='SqlAlchemyStore'):
        if properties is not None:
            properties = str(properties)
        if store_type == 'MongoStore':
            _class = MongoArtifact
        else:
            _class = SqlArtifact
        return _class(name=name, data_format=data_format, description=description, batch_uri=batch_uri,
                      stream_uri=stream_uri, create_time=create_time, update_time=update_time,
                      properties=properties)

    @staticmethod
    def workflow_execution_meta_to_table(name, properties, start_time, end_time,
                                         execution_state, log_uri, workflow_json, signature,
                                         project_id, store_type='SqlAlchemyStore'):
        if properties is not None:
            properties = str(properties)
        if store_type == 'MongoStore':
            _class = MongoWorkflowExecution
        else:
            _class = SqlWorkflowExecution
        return _class(name=name, properties=properties, start_time=start_time, end_time=end_time,
                      execution_state=execution_state, log_uri=log_uri,
                      workflow_json=workflow_json,
                      signature=signature, project_id=project_id)

    @staticmethod
    def model_relation_meta_to_table(name, project_id, store_type='SqlAlchemyStore'):
        if store_type == 'MongoStore':
            _class = MongoModelRelation
        else:
            _class = SqlModelRelation
        return _class(name=name, project_id=project_id)

    @staticmethod
    def model_version_relation_to_table(version, model_id, workflow_execution_id, store_type='SqlAlchemyStore'):
        if store_type == 'MongoStore':
            _class = MongoModelVersionRelation
        else:
            _class = SqlModelVersionRelation
        return _class(version=version, model_id=model_id,
                      workflow_execution_id=workflow_execution_id)

