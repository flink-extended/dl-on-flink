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
import logging
import time

from ai_flow.store import MONGO_DB_ALIAS_META_SERVICE
from typing import Optional, Text, List, Union

import mongoengine

from ai_flow.common.status import Status
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.dataset_meta import DatasetMeta, Properties, DataType, Schema
from ai_flow.meta.metric_meta import MetricMeta, MetricType, MetricSummary
from ai_flow.meta.model_relation_meta import ModelRelationMeta, ModelVersionRelationMeta
from ai_flow.meta.project_meta import ProjectMeta
from ai_flow.metadata_store.utils.MetaToTable import MetaToTable
from ai_flow.metadata_store.utils.ResultToMeta import ResultToMeta
from ai_flow.metric.utils import table_to_metric_meta, table_to_metric_summary, metric_meta_to_table, \
    metric_summary_to_table
from ai_flow.model_center.entity.model_version_stage import STAGE_DELETED, get_canonical_stage, STAGE_GENERATED, \
    STAGE_DEPLOYED, STAGE_VALIDATED
from ai_flow.protobuf.message_pb2 import INVALID_PARAMETER_VALUE, RESOURCE_ALREADY_EXISTS
from ai_flow.endpoint.server.exception import AIFlowException
from ai_flow.endpoint.server.high_availability import Member
from ai_flow.store.abstract_store import AbstractStore
from ai_flow.store.db.db_model import (MongoProject, MongoDataset, MongoModelVersion,
                                       MongoArtifact, MongoRegisteredModel, MongoModelRelation,
                                       MongoMetricSummary, MongoMetricMeta,
                                       MongoModelVersionRelation, MongoMember, MongoProjectSnapshot)
from ai_flow.store.db.db_util import parse_mongo_uri

if not hasattr(time, 'time_ns'):
    time.time_ns = lambda: int(time.time() * 1e9)

_logger = logging.getLogger(__name__)

TRUE = True
UPDATE_FAIL = -1
deleted_character = '~~'


class MongoStore(AbstractStore):
    """
    MongoDB backend store for tracking metadata for AIFlow backend entities.
    """

    CREATE_RETRY_TIMES = 3

    def __init__(self, **kwargs):
        """
        Create database backend storage by specified database URI

        :param db_uri: The mongodb database URI string to connect to the database.
        """
        super(MongoStore, self).__init__()
        db_conf = {
            "host": kwargs.get("host"),
            "port": kwargs.get("port"),
            "username": kwargs.get("username"),
            "password": kwargs.get("password"),
            "db": kwargs.get("db"),
        }
        self.db_uri = "mongodb://{username}:{password}@{host}:{port}/{db}?authSource=admin".format(**db_conf)
        MongoStoreConnManager().connect(self.db_uri, kwargs.get("db"))

    def _save_all(self, objs):
        """
        Backend entities store into database
        """
        if type(objs) is list:
            for obj in objs:
                obj.save()
        else:
            objs.save()

    """dataset api"""

    def get_dataset_by_id(self, dataset_id) -> Optional[DatasetMeta]:
        """
        get a specific dataset in metadata store by dataset id.

        :param dataset_id: the dataset id
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object if the dataset exists,
                 Otherwise, returns None if the dataset does not exist.
        """
        dataset_result = MongoDataset.objects(uuid=dataset_id, is_deleted__ne=TRUE)
        if len(dataset_result) == 0:
            return None
        return ResultToMeta.result_to_dataset_meta(dataset_result[0])

    def get_dataset_by_name(self, dataset_name) -> Optional[DatasetMeta]:
        """
        get a specific dataset in metadata store by dataset name.

        :param dataset_name: the dataset name
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object if the dataset exists,,
                 Otherwise, returns None if the dataset does not exist.
        """
        dataset_result = MongoDataset.objects(name=dataset_name, is_deleted__ne=TRUE)
        if len(dataset_result) == 0:
            return None
        return ResultToMeta.result_to_dataset_meta(dataset_result[0])

    def _register_dataset(self, name: Text, data_format: Text = None,
                          description: Text = None, uri: Text = None,
                          properties: Properties = None,
                          name_list: List[Text] = None, type_list: List[DataType] = None,
                          catalog_name: Text = None, catalog_type: Text = None,
                          catalog_connection_uri: Text = None,
                          catalog_table: Text = None, catalog_database: Text = None) -> DatasetMeta:
        """
        register an dataset in metadata store.

        :param name: the name of the dataset
        :param data_format: the data format of the dataset
        :param description: the description of the dataset
        :param uri: the uri of the dataset
        :param properties: the properties of the dataset
        :param name_list: the name list of dataset's schema
        :param type_list: the type list corresponded to the name list of dataset's schema
        :param catalog_name: the catalog name that will register in environment
        :param catalog_type: the catalog type of the dataset
        :param catalog_connection_uri: the connection uri of the catalog
        :param catalog_table: the table where the dataset is stored in the catalog
               if dataset is stored in the external catalog
        :param catalog_database: the database where the dataset is stored in the catalog
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object.
        """
        update_time = create_time = int(time.time() * 1000)
        before_dataset = self.get_dataset_by_name(dataset_name=name)
        if before_dataset is not None:
            # if the user has registered exactly the same dataset before,
            # do nothing in metadata store and return the registered dataset.
            if _compare_dataset_fields(data_format, description, uri,
                                       properties, name_list, type_list,
                                       catalog_name, catalog_type, catalog_database,
                                       catalog_connection_uri, catalog_table, before_dataset):
                return before_dataset
            else:
                # if the dataset registered this time has the same name but different fields,
                # raise the AIFlowException.
                raise AIFlowException("You have registered the dataset with same name: \"{}\" "
                                      "but different fields".format(name))
        try:
            if name_list is not None and type_list is not None:
                if len(name_list) != len(type_list):
                    raise AIFlowException("the length of name list and type list should be the same")
            if name_list is not None and type_list is None:
                raise AIFlowException("the length of name list and type list should be the same")
            if name_list is None and type_list is not None:
                raise AIFlowException("the length of name list and type list should be the same")
            dataset = MetaToTable.dataset_meta_to_table(name=name, data_format=data_format,
                                                        description=description, uri=uri, create_time=create_time,
                                                        update_time=update_time, properties=properties,
                                                        name_list=name_list, type_list=type_list,
                                                        catalog_name=catalog_name, catalog_type=catalog_type,
                                                        catalog_database=catalog_database,
                                                        catalog_connection_uri=catalog_connection_uri,
                                                        catalog_table=catalog_table,
                                                        store_type=type(self).__name__)
            dataset.save()
            schema = Schema(name_list=name_list, type_list=type_list)
            return DatasetMeta(uuid=dataset.uuid, name=name, data_format=data_format,
                               description=description, uri=uri, create_time=create_time, update_time=update_time,
                               properties=properties, schema=schema, catalog_name=catalog_name,
                               catalog_type=catalog_type, catalog_database=catalog_database,
                               catalog_connection_uri=catalog_connection_uri, catalog_table=catalog_table)
        except mongoengine.OperationError as e:
            raise AIFlowException('Registered Dataset (name={}) already exists. '
                                  'Error: {}'.format(dataset.name, str(e)))

    def register_dataset(self, name: Text, data_format: Text = None,
                         description: Text = None, uri: Text = None, properties: Properties = None,
                         name_list: List[Text] = None, type_list: List[DataType] = None):
        """
        register an dataset in metadata store.

        :param name: the name of the dataset
        :param data_format: the data format of the dataset
        :param description: the description of the dataset
        :param uri: the uri of the dataset
        :param properties: the properties of the dataset
        :param name_list: the name list of dataset's schema
        :param type_list: the type list corresponded to the name list of dataset's schema
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object.
        """
        return self._register_dataset(name=name,
                                      data_format=data_format, description=description, uri=uri,
                                      properties=properties, name_list=name_list, type_list=type_list)

    def register_dataset_with_catalog(self, name: Text, catalog_name: Text,
                                      catalog_type: Text, catalog_connection_uri: Text,
                                      catalog_table: Text, catalog_database: Text = None):
        """
        register an dataset in metadata store with catalog.

        :param name: the name of the dataset
        :param catalog_name: the catalog name that will register in environment
        :param catalog_type: the catalog type of the dataset
        :param catalog_connection_uri: the connection uri of the catalog
        :param catalog_table: the table where the dataset is stored in the catalog
        :param catalog_database: the database where the dataset is stored in the catalog
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object.
        """
        return self._register_dataset(name=name, catalog_name=catalog_name,
                                      catalog_type=catalog_type,
                                      catalog_connection_uri=catalog_connection_uri,
                                      catalog_table=catalog_table,
                                      catalog_database=catalog_database)

    def register_datasets(self, dataset_meta_list: List[DatasetMeta]) -> List[DatasetMeta]:
        """
        register multiple datasets in metadata store.

        :param dataset_meta_list: A list of datasets
        :return: List of :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` objects.
        """
        try:
            datasets = MetaToTable.dataset_meta_list_to_table(dataset_meta_list, store_type=type(self).__name__)
            for ex in datasets:
                ex.save()
            for dataset_meta, dataset in zip(dataset_meta_list, datasets):
                dataset_meta.uuid = dataset.uuid
            return dataset_meta_list
        except mongoengine.OperationError as e:
            raise AIFlowException(str(e))

    def update_dataset(self, dataset_name: Text,
                       data_format: Text = None, description: Text = None,
                       uri: Text = None, properties: Properties = None,
                       name_list: List[Text] = None, type_list: List[DataType] = None, catalog_name: Text = None,
                       catalog_type: Text = None, catalog_database: Text = None,
                       catalog_connection_uri: Text = None,
                       catalog_table: Text = None) -> Optional[DatasetMeta]:

        try:
            dataset: MongoDataset = MongoDataset.objects(name=dataset_name).first()
            if dataset is None:
                return None
            if data_format is not None:
                dataset.format = data_format
            if description is not None:
                dataset.description = description
            if uri is not None:
                dataset.uri = uri
            if properties is not None:
                dataset.properties = str(properties)
            if name_list is not None:
                dataset.name_list = str(name_list)
            if type_list is not None:
                data_type_list = []
                for data_type in type_list:
                    data_type_list.append(data_type.value)
                data_type_list = str(data_type_list)
                dataset.type_list = data_type_list
            if catalog_name is not None:
                dataset.catalog_name = catalog_name
            if catalog_type is not None:
                dataset.catalog_type = catalog_type
            if catalog_database is not None:
                dataset.catalog_database = catalog_database
            if catalog_connection_uri is not None:
                dataset.connection_config = catalog_connection_uri
            if catalog_table is not None:
                dataset.catalog_table = catalog_table
            dataset.update_time = int(time.time() * 1000)
            dataset.save()
            return ResultToMeta.result_to_dataset_meta(dataset)
        except mongoengine.OperationError as e:
            raise AIFlowException(e)

    def list_datasets(self, page_size, offset) -> Optional[List[DatasetMeta]]:
        """
        List registered datasets in metadata store.

        :param page_size: the limitation of the listed datasets.
        :param offset: the offset of listed datasets.
        :return: List of :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` objects,
                 return None if no datasets to be listed.
        """
        dataset_result = MongoDataset.objects(is_deleted__ne=TRUE).skip(offset).limit(page_size)
        if len(dataset_result) == 0:
            return None
        dataset_list = []
        for dataset in dataset_result:
            dataset_list.append(ResultToMeta.result_to_dataset_meta(dataset))
        return dataset_list

    def delete_dataset_by_name(self, dataset_name) -> Status:
        """
        Delete the registered dataset by dataset name .

        :param dataset_name: the dataset name
        :return: Status.OK if the dataset is successfully deleted, Status.ERROR if the dataset does not exist otherwise.
        """
        try:
            dataset = MongoDataset.objects(name=dataset_name, is_deleted__ne=TRUE).first()
            if dataset is None:
                return Status.ERROR
            deleted_dataset_counts = MongoDataset.objects(
                name__startswith=deleted_character + dataset_name + deleted_character, is_deleted=TRUE).count()
            dataset.is_deleted = TRUE
            dataset.name = deleted_character + dataset.name + deleted_character + str(deleted_dataset_counts + 1)
            dataset.save()
            return Status.OK
        except mongoengine.OperationError as e:
            raise AIFlowException(str(e))

    def delete_dataset_by_id(self, dataset_id) -> Status:
        """
        Delete the registered dataset by dataset id .

        :param dataset_id: the dataset id
        :return: Status.OK if the dataset is successfully deleted, Status.ERROR if the dataset does not exist otherwise.
        """
        dataset = self.get_dataset_by_id(dataset_id=dataset_id)
        if dataset is None:
            return Status.ERROR
        return self.delete_dataset_by_name(dataset.name)

    """project api"""

    def get_project_by_id(self, project_id) -> Optional[ProjectMeta]:
        """
        get a specific project in metadata store by project id

        :param project_id: the project id
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object if the project exists,
                 Otherwise, returns None if the project does not exist.
        """
        project_result = MongoProject.objects(uuid=project_id, is_deleted__ne=TRUE)
        if len(project_result) == 0:
            return None
        return ResultToMeta.result_to_project_meta(project_result[0])

    def get_project_by_name(self, project_name) -> Optional[ProjectMeta]:
        """
        get a specific project in metadata store by project name
        :param project_name: the project name
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object if the project exists,
                 Otherwise, returns None if the project does not exist.
        """
        project_result = MongoProject.objects(name=project_name, is_deleted__ne=TRUE)
        if len(project_result) == 0:
            return None
        return ResultToMeta.result_to_project_meta(project_result[0])

    def register_project(self, name: Text, uri: Text, properties: Properties = None) -> ProjectMeta:
        """
        register a project in metadata store.

        :param name: the name of the project
        :param uri: the uri of the project
        :param properties: the properties of the project
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object.
        """
        before_project = self.get_project_by_name(project_name=name)
        if before_project is not None:
            # if the user has registered exactly the same project before,
            # do nothing in metadata store and return the registered project.
            if _compare_project_fields(uri, properties, before_project):
                return before_project
            else:
                # if the project registered this time has the same name but different fields,
                # raise the AIFlowException.
                raise AIFlowException("You have registered the project with same name: \"{}\" "
                                      "but different fields".format(name))

        try:
            project = MetaToTable.project_meta_to_table(name=name, uri=uri, properties=properties,
                                                        store_type=type(self).__name__)
            project.save()
            project_meta = ProjectMeta(uuid=project.uuid, name=name, uri=uri, properties=properties)
            return project_meta
        except mongoengine.OperationError as e:
            raise AIFlowException('Registered Project (name={}) already exists. '
                                  'Error: {}'.format(project.name, str(e)))

    def list_project(self, page_size, offset) -> Optional[List[ProjectMeta]]:
        """
        List registered projects in metadata store.

        :param page_size: the limitation of the listed projects.
        :param offset: the offset of listed projects.
        :return: List of :py:class:`ai_flow.meta.project_meta.ProjectMeta` objects,
                 return None if no projects to be listed.
        """

        project_result = MongoProject.objects(is_deleted__ne=TRUE).skip(offset).limit(page_size)
        if len(project_result) == 0:
            return None
        projects = []
        for project in project_result:
            projects.append(ResultToMeta.result_to_project_meta(project))
        return projects

    def update_project(self, project_name: Text, uri: Text = None, properties: Properties = None) -> Optional[ProjectMeta]:
        try:
            project: MongoProject = MongoProject.objects(name=project_name, is_deleted__ne=TRUE).first()
            if project is None:
                return None
            if uri is not None:
                project.uri = uri
            if properties is not None:
                project.properties = str(properties)
            project.save()
            return ResultToMeta.result_to_project_meta(project)
        except mongoengine.OperationError as e:
            raise AIFlowException(e)

    def delete_project_by_id(self, project_id) -> Status:
        """
        Delete the registered project by project id .

        :param project_id: the project id
        :return: Status.OK if the project is successfully deleted, Status.ERROR if the project does not exist otherwise.
        """
        project = self.get_project_by_id(project_id=project_id)
        if project is None:
            return Status.ERROR
        return self.delete_project_by_name(project_name=project.name)

    def delete_project_by_name(self, project_name) -> Status:
        """
        Delete the registered project by project name .

        :param project_name: the project name
        :return: Status.OK if the project is successfully deleted, Status.ERROR if the project does not exist otherwise.
        """
        try:
            project = MongoProject.objects(name=project_name, is_deleted__ne=TRUE).first()
            if project is None:
                return Status.ERROR
            deleted_project_counts = MongoProject.objects(
                name__startswith=deleted_character + project_name + deleted_character,
                is_deleted=TRUE).count()
            project.is_deleted = TRUE
            project.name = deleted_character + project.name + deleted_character + str(deleted_project_counts + 1)
            model_version_list = []
            for per_model in project.model_relation:
                deleted_model_relation_counts = MongoModelRelation.objects(
                    name__startswith=deleted_character + per_model.name + deleted_character,
                    is_deleted=TRUE).count()
                per_model.is_deleted = TRUE
                per_model.name = deleted_character + per_model.name + deleted_character + str(
                    deleted_model_relation_counts + 1)
                for model_version in per_model.model_version_relation:
                    deleted_model_version_relation_counts = MongoModelVersionRelation.objects(
                        version__startswith=deleted_character + model_version.version + deleted_character,
                        is_deleted=TRUE).count()
                    model_version.is_deleted = TRUE
                    model_version.version = deleted_character + model_version.version + deleted_character + str(
                        deleted_model_version_relation_counts + 1)
                    # update for unqine constraint
                    model_version.version_model_id_unique = f'{model_version.version}-{model_version.model_id}'
                    model_version.version_workflow_execution_id_unique = f'{model_version.version}-{model_version.workflow_execution_id}'
                model_version_list += per_model.model_version_relation
            self._save_all(
                [project] + project.model_relation + model_version_list)
            return Status.OK
        except mongoengine.OperationError as e:
            raise AIFlowException(str(e))

    """model api"""

    def get_model_relation_by_id(self, model_id) -> Optional[ModelRelationMeta]:
        """
        get a specific model relation in metadata store by model id.

        :param model_id: the model id
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` object if the model relation
                 exists, Otherwise, returns None if the model relation does not exist.
        """
        model_result = MongoModelRelation.objects(uuid=model_id, is_deleted__ne=TRUE)
        if len(model_result) == 0:
            return None
        return ResultToMeta.result_to_model_relation_meta(model_result[0])

    def get_model_relation_by_name(self, name) -> Optional[ModelRelationMeta]:
        """
        get a specific model relation in metadata store by model name.

        :param name: the model name
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` object if the model relation
                 exists, Otherwise, returns None if the model relation does not exist.
        """
        model_result = MongoModelRelation.objects(name=name, is_deleted__ne=TRUE)
        if len(model_result) == 0:
            return None
        return ResultToMeta.result_to_model_relation_meta(model_result[0])

    def register_model_relation(self, name: Text,
                                project_id: int = None) -> ModelRelationMeta:
        """
        register a model relation in metadata store

        :param name: the name of the model
        :param project_id: the project id which the model corresponded to.
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` object.
        """
        before_model_relation = self.get_model_relation_by_name(name=name)
        if before_model_relation is not None:
            # if the user has registered exactly the same model relation before,
            # do nothing in metadata store and return the registered model relation.
            if _compare_model_relation_fields(project_id, before_model_relation):
                return before_model_relation
            else:
                # if the dataset registered this time has the same name but different fields,
                # raise the AIFlowException.
                raise AIFlowException("You have registered the model relation with same name: \"{}\" "
                                      "but different project uuid".format(name))
        try:
            model = MetaToTable.model_relation_meta_to_table(name=name,
                                                             project_id=project_id,
                                                             store_type=type(self).__name__)
            model.save()
            # update reference field
            if project_id is not None:
                project = MongoProject.objects(uuid=project_id).first()
                if project.model_relation is None:
                    project.model_relation = [model]
                else:
                    project.model_relation.append(model)
                project.save()
            model_meta = ModelRelationMeta(uuid=model.uuid, name=name, project_id=project_id)
            return model_meta
        except mongoengine.OperationError as e:
            raise AIFlowException('Registered Model (name={}) already exists. '
                                  'Error: {}'.format(model.name, str(e)))

    def list_model_relation(self, page_size, offset) -> Optional[List[ModelRelationMeta]]:
        """
        List registered model relations in metadata store.

        :param page_size: the limitation of the listed model relations.
        :param offset: the offset of listed model relations.
        :return: List of :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` objects,
                 return None if no model relations to be listed.
        """
        model_result = MongoModelRelation.objects(is_deleted__ne=TRUE).skip(offset).limit(page_size)
        if len(model_result) == 0:
            return None
        models = []
        for model in model_result:
            models.append(ResultToMeta.result_to_model_relation_meta(model))
        return models

    def delete_model_relation_by_id(self, model_id) -> Status:
        """
        Delete the registered model by model id .

        :param model_id: the model id
        :return: Status.OK if the model is successfully deleted, Status.ERROR if the model does not exist otherwise.
        """
        model = self.get_model_relation_by_id(model_id=model_id)
        if model is None:
            return Status.ERROR
        return self.delete_model_relation_by_name(model_name=model.name)

    def delete_model_relation_by_name(self, model_name) -> Status:
        """
        Delete the registered model by model name .

        :param model_name: the model name
        :return: Status.OK if the model is successfully deleted, Status.ERROR if the model does not exist otherwise.
        """
        try:
            model = MongoModelRelation.objects(name=model_name, is_deleted__ne=TRUE).first()
            if model is None:
                return Status.ERROR
            deleted_model_counts = MongoModelRelation.objects(
                name__startswith=deleted_character + model.name + deleted_character,
                is_deleted=TRUE).count()
            model.is_deleted = TRUE
            model.name = deleted_character + model.name + deleted_character + str(deleted_model_counts + 1)
            for model_version in model.model_version_relation:
                deleted_model_version_counts = MongoModelVersionRelation.objects(
                    version__startswith=deleted_character + model_version.version + deleted_character,
                    is_deleted=TRUE).count()
                model_version.is_deleted = TRUE
                model_version.version = deleted_character + model_version.version + deleted_character + str(
                    deleted_model_version_counts + 1)
                # update for unqine constraint
                model_version.version_model_id_unique = f'{model_version.version}-{model_version.model_id}'
                model_version.version_workflow_execution_id_unique = f'{model_version.version}-{model_version.workflow_execution_id}'
            self._save_all([model] + model.model_version_relation)
            return Status.OK
        except mongoengine.OperationError as e:
            raise AIFlowException(str(e))

    '''model version api'''

    def get_model_version_relation_by_version(self, version_name, model_id) -> Optional[ModelVersionRelationMeta]:
        """
        get a specific model version relation in metadata store by the model version name.

        :param version_name: the model version name
        :param model_id: the model id corresponded to the model version
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelVersionRelationMeta` object
                 if the model version exists, Otherwise, returns None if the model version does not exist.
        """
        model_version_result = MongoModelVersionRelation.objects(version=version_name, model_id=model_id,
                                                                 is_deleted__ne=TRUE)
        if len(model_version_result) == 0:
            return None
        return ResultToMeta.result_to_model_version_relation_meta(model_version_result[0])

    def register_model_version_relation(self, version: Text,
                                        model_id: int,
                                        project_snapshot_id: int = None) -> ModelVersionRelationMeta:
        """
        register a model version relation in metadata store.

        :param version: the specific model version
        :param model_id: the model id corresponded to the model version
        :param project_snapshot_id: the project snapshot id corresponded to the model version
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelVersionRelationMeta` object.
        """
        try:
            model_version_relation = MetaToTable.model_version_relation_to_table(version=version,
                                                                                 model_id=model_id,
                                                                                 project_snapshot_id=project_snapshot_id,
                                                                                 store_type=type(self).__name__)
            model_version_relation.save()
            # update reference field
            if model_id is not None:
                model_relation = MongoModelRelation.objects(uuid=model_id).first()
                if model_relation.model_version_relation is None:
                    model_relation.model_version_relation = [model_version_relation]
                else:
                    model_relation.model_version_relation.append(model_version_relation)
                model_relation.save()

            if project_snapshot_id is not None:
                project_snapshot = MongoProjectSnapshot.objects(uuid=project_snapshot_id).first()
                if project_snapshot.model_version_relation is None:
                    project_snapshot.model_version_relation = [model_version_relation]
                else:
                    project_snapshot.model_version_relation.append(model_version_relation)
                project_snapshot.save()

            model_version_relation_meta = ModelVersionRelationMeta(version=version, model_id=model_id,
                                                                   project_snapshot_id=project_snapshot_id)
            return model_version_relation_meta
        except mongoengine.OperationError as e:
            raise AIFlowException('Registered ModelVersion (name={}) already exists. '
                                  'Error: {}'.format(model_version_relation.version, str(e)))

    def list_model_version_relation(self, model_id, page_size, offset) -> Optional[List[ModelVersionRelationMeta]]:
        """
        List registered model version relations in metadata store.

        :param model_id: the model id corresponded to the model version
        :param page_size: the limitation of the listed model version relations.
        :param offset: the offset of listed model version relations.
        :return: List of :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` objects,
                 return None if no model version relations to be listed.
        """
        model_version_result = MongoModelVersionRelation.objects(model_id=model_id, is_deleted__ne=TRUE).skip(
            offset).limit(page_size)
        if len(model_version_result) == 0:
            return None
        model_version_list = []
        for version in model_version_result:
            model_version_list.append(ResultToMeta.result_to_model_version_relation_meta(version))
        return model_version_list

    def delete_model_version_relation_by_version(self, version, model_id) -> Status:
        """
        Delete the registered model version by model version name .

        :param version: the model version name
        :param model_id: the model id corresponded to the model version
        :return: Status.OK if the model version is successfully deleted,
                 Status.ERROR if the model version does not exist otherwise.
        """
        try:
            model_version = MongoModelVersionRelation.objects(version=version, model_id=model_id,
                                                              is_deleted__ne=TRUE).first()
            if model_version is None:
                return Status.ERROR
            deleted_model_version_counts = MongoModelVersionRelation.objects(
                version__startswith=deleted_character + version + deleted_character,
                is_deleted=TRUE).count()
            model_version.is_deleted = TRUE
            model_version.version = deleted_character + model_version.version + deleted_character + str(
                deleted_model_version_counts + 1)
            # update for unqine constraint
            model_version.version_model_id_unique = f'{model_version.version}-{model_version.model_id}'
            model_version.version_workflow_execution_id_unique = f'{model_version.version}-{model_version.workflow_execution_id}'
            model_version.save()
            return Status.OK
        except mongoengine.OperationError as e:
            raise AIFlowException(str(e))

    """artifact api"""

    def get_artifact_by_id(self, artifact_id: int) -> Optional[ArtifactMeta]:
        """
        get a specific artifact in metadata store by artifact id.

        :param artifact_id: the artifact id
        :return: A single :py:class:`ai_flow.meta.artifact_meta.ArtifactMeta` object
                 if the artifact exists, Otherwise, returns None if the artifact does not exist.
        """
        artifact_result = MongoArtifact.objects(uuid=artifact_id, is_deleted__ne=TRUE)
        if len(artifact_result) == 0:
            return None
        artifact = ResultToMeta.result_to_artifact_meta(artifact_result[0])
        return artifact

    def get_artifact_by_name(self, artifact_name: Text) -> Optional[ArtifactMeta]:
        """
        get a specific artifact in metadata store by artifact name.

        :param artifact_name: the artifact name
        :return: A single :py:class:`ai_flow.meta.artifact_meta.ArtifactMeta` object
                 if the artifact exists, Otherwise, returns None if the artifact does not exist.
        """
        artifact_result = MongoArtifact.objects(name=artifact_name, is_deleted__ne=TRUE)
        if len(artifact_result) == 0:
            return None
        artifact = ResultToMeta.result_to_artifact_meta(artifact_result[0])
        return artifact

    def register_artifact(self, name: Text, artifact_type: Text = None, description: Text = None,
                          uri: Text = None,
                          properties: Properties = None) -> ArtifactMeta:
        """
        register an artifact in metadata store.

        :param name: the name of the artifact
        :param artifact_type: the type of the artifact
        :param description: the description of the artifact
        :param uri: the uri of the artifact
        :param properties: the properties of the artifact
        :return: A single :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` object.
        """
        before_artifact = self.get_artifact_by_name(artifact_name=name)
        if before_artifact is not None:
            # if the user has registered exactly the same artifact before,
            # do nothing in metadata store and return the registered artifact.
            if _compare_artifact_fields(artifact_type, description, uri,
                                        properties, before_artifact):
                return before_artifact
            else:
                # if the artifact registered this time has the same name but different fields,
                # raise the AIFlowException.
                raise AIFlowException("You have registered the artifact with same name: \"{}\""
                                      " but different fields".format(name))
        try:
            create_time = update_time = int(time.time() * 1000)
            artifact = MetaToTable.artifact_meta_to_table(name=name, artifact_type=artifact_type,
                                                          description=description, uri=uri,
                                                          create_time=create_time,
                                                          update_time=update_time, properties=properties,
                                                          store_type=type(self).__name__)
            artifact.save()
            artifact_meta = ArtifactMeta(uuid=artifact.uuid, name=name, artifact_type=artifact_type,
                                         description=description, uri=uri, create_time=create_time,
                                         update_time=update_time, properties=properties)
            return artifact_meta
        except mongoengine.OperationError as e:
            raise AIFlowException('Registered Artifact (name={}) already exists. '
                                  'Error: {}'.format(artifact.name, str(e)))

    def update_artifact(self, name: Text, artifact_type: Text = None,
                        description: Text = None, uri: Text = None,
                        properties: Properties = None) -> Optional[ArtifactMeta]:
        try:
            artifact: MongoArtifact = MongoArtifact.objects(name=name, is_deleted__ne=TRUE).first()
            if artifact is None:
                return None
            if artifact_type is not None:
                artifact.artifact_type = artifact_type
            if description is not None:
                artifact.description = description
            if uri is not None:
                artifact.uri = uri
            if properties is not None:
                artifact.properties = str(properties)
            artifact.update_time = int(time.time() * 1000)
            artifact.save()
            return ResultToMeta.result_to_artifact_meta(artifact)
        except mongoengine.OperationError as e:
            raise AIFlowException(str(e))

    def list_artifact(self, page_size, offset) -> Optional[List[ArtifactMeta]]:
        """
        List registered artifacts in metadata store.

        :param page_size: the limitation of the listed artifacts.
        :param offset: the offset of listed artifacts.
        :return: List of :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` objects,
                 return None if no artifacts to be listed.
        """
        artifact_result = MongoArtifact.objects(is_deleted__ne=TRUE).skip(offset).limit(page_size)
        if len(artifact_result) == 0:
            return None
        artifact_list = []
        for artifact in artifact_result:
            artifact_list.append(ResultToMeta.result_to_artifact_meta(artifact))
        return artifact_list

    def delete_artifact_by_id(self, artifact_id) -> Status:
        """
        Delete the registered artifact by artifact id .

        :param artifact_id: the artifact id
        :return: Status.OK if the artifact is successfully deleted,
                 Status.ERROR if the artifact does not exist otherwise.
        """
        artifact = self.get_artifact_by_id(artifact_id=artifact_id)
        if artifact is None:
            return Status.ERROR
        return self.delete_artifact_by_name(artifact.name)

    def delete_artifact_by_name(self, artifact_name) -> Status:
        """
        Delete the registered artifact by artifact name .

        :param artifact_name: the artifact name
        :return: Status.OK if the artifact is successfully deleted,
                 Status.ERROR if the artifact does not exist otherwise.
        """
        try:
            artifact = MongoArtifact.objects(name=artifact_name, is_deleted__ne=TRUE).first()
            if artifact is None:
                return Status.ERROR
            deleted_artifact_counts = MongoArtifact.objects(
                name__startswith=deleted_character + artifact_name + deleted_character,
                is_deleted=TRUE).count()
            artifact.is_deleted = TRUE
            artifact.name = deleted_character + artifact.name + deleted_character + str(deleted_artifact_counts + 1)
            artifact.save()
            return Status.OK
        except mongoengine.OperationError as e:
            raise AIFlowException(str(e))

    def get_deployed_model_version(self, model_name):
        return self.get_model_with_stage(model_name, STAGE_DEPLOYED)

    def get_latest_validated_model_version(self, model_name):
        return self.get_model_with_stage(model_name, STAGE_VALIDATED)

    def get_latest_generated_model_version(self, model_name):
        return self.get_model_with_stage(model_name, STAGE_GENERATED)

    def get_model_with_stage(self, model_name, stage):
        if model_name is None:
            raise AIFlowException('Registered model name cannot be empty.', INVALID_PARAMETER_VALUE)
        model_version = MongoModelVersion.objects(model_name=model_name, current_stage=stage)
        if len(model_version) == 0:
            return None
        else:
            return model_version[len(model_version) - 1].to_meta_entity()

    @classmethod
    def _get_registered_model(cls, model_name):
        """
        Query registered model in Model Center filter by model name

        :param model_name: Unique name for registered model within Model Center.
        """
        if model_name is None:
            raise AIFlowException('Registered model name cannot be empty.', INVALID_PARAMETER_VALUE)

        register_models = MongoRegisteredModel.objects(model_name=model_name)

        if len(register_models) == 0:
            return None
        else:
            _logger.info("Get registered model name: %s, versions: %s.", register_models[0].model_name,
                         register_models[0].model_version)
            return register_models[0]

    def create_registered_model(self, model_name, model_desc=None):
        """
        Create a new registered model in model repository.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.
        :param model_desc: (Optional) Description of registered model.

        :return: Object of :py:class:`ai_flow.model_center.entity.RegisteredModel` created in Model Center.
        """
        if model_name is None:
            raise AIFlowException('Registered model name cannot be empty.', INVALID_PARAMETER_VALUE)
        try:
            before_model = self._get_registered_model(model_name=model_name)
            if before_model is not None:
                if _compare_model_fields(model_desc, before_model):
                    registered_model = MongoRegisteredModel(model_name=model_name,
                                                            model_desc=model_desc)
                    return registered_model.to_meta_entity()
                else:
                    raise AIFlowException("You have registered the model with same name: \"{}\" "
                                          "but different fields".format(model_name), RESOURCE_ALREADY_EXISTS)
            registered_model = MongoRegisteredModel(model_name=model_name,
                                                    model_desc=model_desc)
            registered_model.save()
            return registered_model.to_meta_entity()
        except mongoengine.OperationError as e:
            raise AIFlowException('Registered Model (name={}) already exists. Error: {}'.format(model_name, str(e)),
                                  RESOURCE_ALREADY_EXISTS)

    def update_registered_model(self, registered_model, model_name=None, model_desc=None):
        """
        Update metadata for RegisteredModel entity. Either ``model_name`` or ``model_desc``
        should be non-None. Backend raises exception if registered model with given name does not exist.

        :param registered_model: :py:class:`ai_flow.model_center.entity.RegisteredModel` object.
        :param model_name: (Optional) New proposed name for the registered model.
        :param model_desc: (Optional) Description of registered model.

        :return: A single updated :py:class:`ai_flow.model_center.entity.RegisteredModel` object.
        """
        registered_model = self._get_registered_model(registered_model.model_name)
        if registered_model is None:
            return None
        else:
            try:
                if model_name is not None:
                    registered_model.model_name = model_name
                    # Update model name of registered model version
                    for model_version in registered_model.model_version:
                        model_version.model_name = model_name
                if model_desc is not None:
                    registered_model.model_desc = model_desc
                self._save_all([registered_model] + registered_model.model_version)
                return registered_model.to_meta_entity()
            except mongoengine.OperationError as e:
                raise AIFlowException(
                    'Registered model (name={}) already exists. Error: {}'.format(model_name, str(e)),
                    RESOURCE_ALREADY_EXISTS)

    def delete_registered_model(self, registered_model):
        """
        Delete registered model based on specific model name.
        Backend raises exception if registered model with given name does not exist.

        :param registered_model: :py:class:`ai_flow.model_center.entity.RegisteredModel` object.

        :return: None
        """
        try:
            registered_model = self._get_registered_model(registered_model.model_name)
            registered_model.delete()
            return Status.OK
        except mongoengine.OperationError as e:
            raise AIFlowException(str(e))

    def list_registered_models(self):
        """
        List of registered models backend in Model Center.

        :return: List of :py:class:`ai_flow.model_center.entity.RegisteredModel` objects.
        """
        return [registered_model.to_detail_entity() for registered_model in MongoRegisteredModel.objects()]

    def get_registered_model_detail(self, registered_model):
        """
        Get registered model detail filter by model name and model version for Model Center.

        :param registered_model: :py:class:`ai_flow.model_center.entity.RegisteredModel` object.

        :return: Object of :py:class:`ai_flow.model_center.entity.RegisteredModelDetail` backend in Model Center.
        """
        registered_model = self._get_registered_model(registered_model.model_name)
        return None if registered_model is None else registered_model.to_detail_entity()

    @classmethod
    def _get_model_version(cls, model_version):
        model_name = model_version.model_name
        model_version = model_version.model_version
        if model_name is None:
            raise AIFlowException('Registered model name cannot be empty.', INVALID_PARAMETER_VALUE)
        if model_version is None:
            raise AIFlowException('Registered model version cannot be empty.', INVALID_PARAMETER_VALUE)

        model_versions = MongoModelVersion.objects(model_name=model_name, model_version=model_version,
                                                   current_stage__ne=STAGE_DELETED)

        if len(model_versions) == 0:
            return None
        else:
            _logger.info("Get registered model version: %s of model name: %s.", model_versions[0],
                         model_versions[0].model_name)
            return model_versions[0]

    @classmethod
    def _list_model_versions(cls, registered_model):
        model_name = registered_model.model_name
        if model_name is None:
            raise AIFlowException('Registered model name cannot be empty.', INVALID_PARAMETER_VALUE)

        return MongoModelVersion.objects(model_name=model_name, current_stage__ne=STAGE_DELETED)

    @classmethod
    def _count_deleted_model_version(cls, model_version):
        model_name = model_version.model_name
        model_version = model_version.model_version
        if model_name is None:
            raise AIFlowException('Registered model name cannot be empty.', INVALID_PARAMETER_VALUE)
        if model_version is None:
            raise AIFlowException('Registered model version cannot be empty.', INVALID_PARAMETER_VALUE)

        return MongoModelVersion.objects(model_name=model_name,
                                         model_version__startswith=deleted_character + model_version + deleted_character,
                                         current_stage__ne=STAGE_DELETED).count()

    def create_model_version(self, model_name, model_path, model_type=None,
                             version_desc=None, current_stage=STAGE_GENERATED):
        """
        Create a new model version from given model source and model metric.

        :param model_name: Name for containing registered model.
        :param model_path: Source path where the AIFlow model is stored.
        :param model_type: (Optional) Type of AIFlow registered model option.
        :param version_desc: (Optional) Description of registered model version.
        :param current_stage: (Optional) Stage of registered model version

        :return: Object of :py:class:`ai_flow.model_center.entity.ModelVersion` created in Model Center.
        """

        def next_version(current_version):
            if current_version is None:
                return "1"
            else:
                return str(current_version + 1)

        for attempt in range(self.CREATE_RETRY_TIMES):
            try:
                registered_model = self._get_registered_model(model_name)
                if registered_model is None:
                    return None
                else:
                    model_versions = self._list_model_versions(registered_model)
                    if model_versions is None:
                        version_num = 0
                    else:
                        version_num = len(model_versions)
                    model_version = next_version(version_num)
                    doc_model_version = MongoModelVersion(model_name=model_name,
                                                          model_version=model_version,
                                                          model_path=model_path,
                                                          model_type=model_type,
                                                          version_desc=version_desc,
                                                          current_stage=get_canonical_stage(current_stage))
                    doc_model_version.save()
                    # update reference field
                    if model_name is not None:
                        registered_model = MongoRegisteredModel.objects(model_name=model_name).first()
                        if registered_model.model_version is None:
                            registered_model.model_version = [doc_model_version]
                        else:
                            registered_model.model_version.append(doc_model_version)
                        registered_model.save()
                    return doc_model_version.to_meta_entity()
            except mongoengine.OperationError as e:
                logging.info(model_version)
                more_retries = self.CREATE_RETRY_TIMES - attempt - 1
                _logger.info(
                    'Create model version (model_version=%s) error (model_name=%s). Retrying %s more time%s.',
                    model_version, model_name,
                    str(more_retries), 's' if more_retries > 1 else '')
        raise AIFlowException(
            'Create model version error (model_name={}). Giving up after {} attempts.'.format(model_name,
                                                                                              self.CREATE_RETRY_TIMES))

    def update_model_version(self, model_version, model_path=None, model_type=None,
                             version_desc=None, current_stage=None):
        """
        Update metadata associated with a model version in model repository.

        :param model_version: :py:class:`ai_flow.model_center.entity.ModelVersion` object.
        :param model_path: (Optional) New Source path where AIFlow model is stored.
        :param model_type: (Optional) Type of AIFlow registered model option.
        :param version_desc: (Optional) New Description of registered model version.
        :param current_stage: (Optional) New desired stage for this model version.

        :return: A single updated :py:class:`ai_flow.model_center.entity.ModelVersion` object.
        """
        serving_model_version = self.get_deployed_model_version(model_version.model_name)
        if serving_model_version is not None and current_stage == 'DEPLOYED':
            raise AIFlowException('There is already a serving model version="{}" of model="{}"'.
                                  format(serving_model_version.model_version, serving_model_version.model_name))
        model_version = self._get_model_version(model_version)
        if model_version is None:
            return None
        else:
            try:
                if model_path is not None:
                    model_version.model_path = model_path
                if model_type is not None:
                    model_version.model_type = model_type
                if version_desc is not None:
                    model_version.version_desc = version_desc
                if current_stage is not None:
                    model_version.current_stage = get_canonical_stage(current_stage)
                model_version.save()
                return model_version.to_meta_entity()
            except mongoengine.OperationError as e:
                raise AIFlowException(
                    'Update model version error (model_name={}, model_version={}).'.format(model_version.model_name,
                                                                                           model_version.model_version))

    def delete_model_version(self, model_version):
        """
        Delete model version in model repository.

        :param model_version: :py:class:`ai_flow.model_center.entity.ModelVersion` object.

        :return: None
        """
        doc_model_version = self._get_model_version(model_version)
        if doc_model_version is None:
            return None

        doc_model_version.model_path = "REDACTED-SOURCE-PATH"
        doc_model_version.model_type = "REDACTED-TYPE-FEATURE"
        doc_model_version.version_status = None
        doc_model_version.version_desc = None
        doc_model_version.current_stage = STAGE_DELETED
        doc_model_version.save()

    def get_model_version_detail(self, model_version):
        """
        :param model_version: :py:class:`ai_flow.model_center.entity.ModelVersion` object.

        :return: Object of :py:class:`ai_flow.model_center.entity.ModelVersionDetail` backend in Model Center.
        """
        doc_model_version = self._get_model_version(model_version)
        return None if doc_model_version is None else doc_model_version.to_meta_entity()

    def register_metric_meta(self,
                             name,
                             dataset_id,
                             model_name,
                             model_version,
                             job_id,
                             start_time,
                             end_time,
                             metric_type,
                             uri,
                             tags,
                             metric_description,
                             properties) -> MetricMeta:
        """
        register metric meta to store
        :param name: the metric name
        :param dataset_id: the dataset id of the metric or model metric associate with dataset id
        :param model_name: if then model metric, associate with model name
        :param model_version: if then model metric, associate with model version
        :param job_id: the job_id which create the metric
        :param start_time:
        :param end_time:
        :param metric_type: MetricType DATASET or MODEL
        :param uri: the metric uri
        :param tags: such as flink,tensorflow
        :param metric_description:
        :param properties:
        :return:
        """
        try:
            metric_meta_table = metric_meta_to_table(name,
                                                     dataset_id,
                                                     model_name,
                                                     model_version,
                                                     job_id,
                                                     start_time,
                                                     end_time,
                                                     metric_type,
                                                     uri,
                                                     tags,
                                                     metric_description,
                                                     properties,
                                                     type(self).__name__)
            metric_meta_table.save()
            return MetricMeta(uuid=metric_meta_table.uuid,
                              name=name,
                              dataset_id=dataset_id,
                              model_name=model_name,
                              model_version=model_version,
                              job_id=job_id,
                              start_time=start_time,
                              end_time=end_time,
                              metric_type=metric_type,
                              uri=uri,
                              tags=tags,
                              metric_description=metric_description,
                              properties=properties)
        except Exception as e:
            raise AIFlowException('Registered metric meta failed!'
                                  'Error: {}'.format(str(e)))

    def delete_metric_meta(self, uuid: int):
        try:
            metric_meta_table = MongoMetricMeta.objects(uuid=uuid).first()
            metric_meta_table.is_deleted = TRUE
            metric_meta_table.save()
        except Exception as e:
            raise AIFlowException('delete metric meta failed!'
                                  'Error: {}'.format(str(e)))

    def register_metric_summary(self,
                                metric_id,
                                metric_key,
                                metric_value) -> MetricSummary:
        """
        register metric summary
        :param metric_id: associate with metric meta uuid
        :param metric_key:
        :param metric_value:
        :return:
        """
        try:
            metric_summary_table = metric_summary_to_table(metric_id, metric_key, metric_value, type(self).__name__)
            metric_summary_table.save()
            return MetricSummary(uuid=metric_summary_table.uuid,
                                 metric_id=metric_id,
                                 metric_key=metric_key,
                                 metric_value=metric_value)
        except mongoengine.OperationError as e:
            raise AIFlowException('Registered metric summary failed!'
                                  'Error: {}'.format(str(e)))

    def delete_metric_summary(self, uuid: int):
        try:
            metric_summary_table = MongoMetricSummary.objects(uuid=uuid).first()
            metric_summary_table.is_deleted = TRUE
            metric_summary_table.save()
        except Exception as e:
            raise AIFlowException('delete metric summary failed!'
                                  'Error: {}'.format(str(e)))

    def update_metric_meta(self,
                           uuid,
                           name=None,
                           dataset_id=None,
                           model_name=None,
                           model_version=None,
                           job_id=None,
                           start_time=None,
                           end_time=None,
                           metric_type=None,
                           uri=None,
                           tags=None,
                           metric_description=None,
                           properties=None) -> MetricMeta:
        """
        register metric meta to store
        :param uuid: metric meta unique id
        :param name:
        :param dataset_id: the dataset id of the metric or model metric associate with dataset id
        :param model_name:
        :param model_version: if then model metric, associate with model version id
        :param job_id: the job_id which create the metric
        :param start_time:
        :param end_time:
        :param metric_type: MetricType DATASET or MODEL
        :param uri: the metric uri
        :param tags: such as flink,tensorflow
        :param metric_description:
        :param properties:
        :return:
        """
        try:
            metric_meta_table: MongoMetricMeta = MongoMetricMeta.objects(uuid=uuid, is_deleted__ne=TRUE).first()
            if name is not None:
                metric_meta_table.name = name
            if dataset_id is not None:
                metric_meta_table.dataset_id = dataset_id
            if model_name is not None:
                metric_meta_table.model_name = model_name
            if model_version is not None:
                metric_meta_table.model_version = model_version
            if job_id is not None:
                metric_meta_table.job_id = job_id
            if start_time is not None:
                metric_meta_table.start_time = start_time
            if end_time is not None:
                metric_meta_table.end_time = end_time
            if metric_type is not None:
                metric_meta_table.metric_type = metric_type.value
            if uri is not None:
                metric_meta_table.uri = uri
            if tags is not None:
                metric_meta_table.tags = tags
            if metric_description is not None:
                metric_meta_table.metric_description = metric_description
            if properties is not None and properties != {}:
                metric_meta_table.properties = str(properties)
            metric_meta_table.save()
            return table_to_metric_meta(metric_meta_table)
        except Exception as e:
            raise AIFlowException('Registered metric meta failed!'
                                  'Error: {}'.format(str(e)))

    def update_metric_summary(self,
                              uuid,
                              metric_id=None,
                              metric_key=None,
                              metric_value=None) -> MetricSummary:
        """
        register metric summary
        :param uuid: metric summary unique id
        :param metric_id: associate with metric meta uuid
        :param metric_key:
        :param metric_value:
        :return:
        """
        try:
            metric_summary_table = MongoMetricSummary.objects(uuid=uuid, is_deleted__ne=TRUE).first()
            if metric_id is not None:
                metric_summary_table.metric_id = metric_id
            if metric_key is not None:
                metric_summary_table.metric_key = metric_key
            if metric_value is not None:
                metric_summary_table.metric_value = metric_value
            metric_summary_table.save()
            return table_to_metric_summary(metric_summary_table)
        except Exception as e:
            raise AIFlowException('Registered metric summary failed!'
                                  'Error: {}'.format(str(e)))

    def get_metric_meta(self, name) -> Union[None, MetricMeta]:
        """
        get dataset metric
        :param name:
        :return:
        """
        try:
            metric_meta_table = MongoMetricMeta.objects(name=name, is_deleted__ne=TRUE).first()

            if metric_meta_table is None:
                return None
            else:
                _logger.info("Get dataset metric.")
                return table_to_metric_meta(metric_meta_table)

        except Exception as e:
            raise AIFlowException('Get metric meta  '
                                  'Error: {}'.format(str(e)))

    def get_dataset_metric_meta(self, dataset_id) -> Union[None, MetricMeta, List[MetricMeta]]:
        """
        get dataset metric
        :param dataset_id:
        :return:
        """
        try:
            metric_meta_tables = MongoMetricMeta.objects(dataset_id=dataset_id,
                                                         metric_type=MetricType.DATASET.value,
                                                         is_deleted__ne=TRUE)

            if len(metric_meta_tables) == 0:
                return None
            elif len(metric_meta_tables) == 1:
                _logger.info("Get dataset metric.")
                metric_meta_table = metric_meta_tables[0]
                return table_to_metric_meta(metric_meta_table)
            else:
                _logger.info("Get dataset metric.")
                res = []
                for metric_meta_table in metric_meta_tables:
                    res.append(table_to_metric_meta(metric_meta_table))
                return res
        except Exception as e:
            raise AIFlowException('Get metric meta  '
                                  'Error: {}'.format(str(e)))

    def get_model_metric_meta(self, model_name, model_version) -> Union[None, MetricMeta, List[MetricMeta]]:
        """
        get model metric
        :param model_name:
        :param model_version:
        :return:
        """
        try:
            metric_meta_tables = MongoMetricMeta.objects(model_name=model_name,
                                                         model_version=model_version,
                                                         metric_type=MetricType.MODEL.value,
                                                         is_deleted__ne=TRUE)

            if len(metric_meta_tables) == 0:
                return None
            elif len(metric_meta_tables) == 1:
                metric_meta_table = metric_meta_tables[0]
                return table_to_metric_meta(metric_meta_table)
            else:
                result = []
                for metric_meta_table in metric_meta_tables:
                    result.append(table_to_metric_meta(metric_meta_table))
                return result
        except Exception as e:
            raise AIFlowException('Get metric meta  '
                                  'Error: {}'.format(str(e)))

    def get_metric_summary(self, metric_id) -> Optional[List[MetricSummary]]:
        """
        get metric summary
        :param metric_id:
        :return:
        """
        try:
            metric_summary_tables = MongoMetricSummary.objects(metric_id=metric_id,
                                                               is_deleted__ne=TRUE)

            if len(metric_summary_tables) == 0:
                return None
            else:
                _logger.info("Get metric summary.")
                res = []
                for metric_summary_table in metric_summary_tables:
                    res.append(table_to_metric_summary(metric_summary_table))
                return res
        except Exception as e:
            raise AIFlowException('Get metric summary  '
                                  'Error: {}'.format(str(e)))

    """member api"""

    def list_living_members(self, ttl_ms) -> List[Member]:
        try:
            member_models = MongoMember.objects(update_time__gte=time.time_ns() / 1000000 - ttl_ms)
            return [Member(m.version, m.server_uri, int(m.update_time)) for m in member_models]
        except Exception as e:
            raise AIFlowException("List living AIFlow Member Error.") from e

    def update_member(self, server_uri, server_id):
        try:
            member = MongoMember.objects(server_uri=server_uri).first()
            if member is None:
                member = MongoMember()
                member.version = 1
                member.server_uri = server_uri
                member.update_time = time.time_ns() / 1000000
                member.uuid = server_id
                member.save()
            else:
                if member.uuid != server_id:
                    raise Exception("The server uri '%s' is already exists in the storage!" %
                                    server_uri)
                member.version += 1
                member.update_time = time.time_ns() / 1000000
                member.save()
        except Exception as e:
            raise AIFlowException("Update AIFlow Member Error.") from e

    def clear_dead_members(self, ttl_ms):
        try:
            members = MongoMember.objects(update_time__lt=time.time_ns() / 1000000 - ttl_ms)
            if len(members) == 0:
                return None
            else:
                for member in members:
                    member.delete()
        except Exception as e:
            raise AIFlowException("Clear dead AIFlow Member Error.") from e


def _compare_dataset_fields(data_format, description, uri,
                            properties, name_list, type_list, catalog_name,
                            catalog_type, catalog_database, catalog_connection_uri, catalog_table,
                            before_dataset) -> bool:
    return data_format == before_dataset.data_format and description == before_dataset.description \
           and uri == before_dataset.uri \
           and properties == before_dataset.properties and name_list == before_dataset.schema.name_list \
           and type_list == before_dataset.schema.type_list and catalog_name == before_dataset.catalog_name \
           and catalog_type == before_dataset.catalog_type and catalog_database == before_dataset.catalog_database \
           and catalog_connection_uri == before_dataset.catalog_connection_uri \
           and catalog_table == before_dataset.catalog_table


def _compare_artifact_fields(artifact_type, description, uri, properties, before_artifact):
    return artifact_type == before_artifact.artifact_type and description == before_artifact.description \
           and uri == before_artifact.uri and properties == before_artifact.properties


def _compare_model_fields(model_desc, before_model):
    return model_desc == before_model.model_desc


def _compare_model_relation_fields(project_id, before_model_relation):
    return project_id == before_model_relation.project_id


def _compare_project_fields(uri, properties, before_project):
    return uri == before_project.uri and properties == before_project.properties


class MongoStoreConnManager(object):
    _instance = None
    _conns = {}
    _connected_uris = set()
    _closed_uris = set()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def connect(self, db_uri, db_name, db_alias=MONGO_DB_ALIAS_META_SERVICE):
        if db_uri not in self._conns:
            self._conns[db_uri] = mongoengine.connect(db_name, host=db_uri, alias=db_alias)
            self._connected_uris.add(db_uri)

    def disconnect(self, db_uri, db_alias=MONGO_DB_ALIAS_META_SERVICE):
        if db_uri in self._conns:
            mongoengine.disconnect(alias=db_alias)
            self._connected_uris.remove(db_uri)
            self._closed_uris.add(db_uri)

    def disconnect_all(self):
        current_connected_uris = self._connected_uris.copy()
        for uri in current_connected_uris:
            self.disconnect(uri)

    def drop(self, db_uri_without_auth):
        db_uri = f'{db_uri_without_auth}?authSource=admin'
        if db_uri in self._conns:
            _, _, _, _, db = parse_mongo_uri(db_uri_without_auth)
            self._conns[db_uri].drop_database(db)

    def drop_all(self):
        current_connected_uris = self._connected_uris.copy()
        for db_uri in current_connected_uris:
            self.drop(db_uri)
