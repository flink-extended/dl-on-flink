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
from typing import Optional, Text, List, Union
import sqlalchemy.exc
import sqlalchemy.orm
from sqlalchemy import and_, cast, Integer

from ai_flow.common.status import Status
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.dataset_meta import DatasetMeta, Properties, DataType, Schema
from ai_flow.meta.metric_meta import MetricMeta, MetricType, MetricSummary
from ai_flow.meta.model_relation_meta import ModelRelationMeta, ModelVersionRelationMeta
from ai_flow.meta.project_meta import ProjectMeta
from ai_flow.meta.workflow_meta import WorkflowMeta
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
from ai_flow.store.db.base_model import base
from ai_flow.store.db.db_model import SqlDataset, SqlModelRelation, SqlModelVersionRelation, SqlProject, \
    SqlWorkflow, SqlEvent, SqlArtifact, SqlMember, SqlProjectSnapshot
from ai_flow.store.db.db_model import SqlMetricMeta, SqlMetricSummary
from ai_flow.store.db.db_model import SqlRegisteredModel, SqlModelVersion
from ai_flow.store.db.db_util import extract_db_engine_from_uri, create_sqlalchemy_engine, _get_managed_session_maker

if not hasattr(time, 'time_ns'):
    time.time_ns = lambda: int(time.time() * 1e9)

_logger = logging.getLogger(__name__)

sqlalchemy.orm.configure_mappers()

TRUE = 'True'
UPDATE_FAIL = -1
deleted_character = '~~'


class SqlAlchemyStore(AbstractStore):
    """
    SQLAlchemy compliant backend store for tracking metadata for AIFlow backend entities.
    AIFlow supports database dialects including ``sqlite``, ``mysql``, ``postgresql`` and ``mssql``.
    As specified in SQLAlchemy docs <https://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls>`_ ,
    database URI is expected in the following format:
    ``<dialect>+<driver>://<username>:<password>@<host>:<port>/<database>``.
    If you don't specify any database driver, SQLAlchemy uses a dialect's default driver.
    """

    CREATE_RETRY_TIMES = 3

    def __init__(self, db_uri):
        """
        Create database backend storage by specified database URI

        :param db_uri: The SQLAlchemy database URI string to connect to the database.
                       See the `SQLAlchemy docs <https://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls>`_
                       for format specifications. AIFlow supports database dialects including ``sqlite``, ``mysql``,
                       ``postgresql`` and ``mssql``.
        """
        super(SqlAlchemyStore, self).__init__()
        self.db_uri = db_uri
        self.db_type = extract_db_engine_from_uri(db_uri)
        self.db_engine = create_sqlalchemy_engine(db_uri)
        base.metadata.create_all(self.db_engine)
        # Verify that database sql model tables exist.
        SqlAlchemyStore._verify_registry_tables_exist(self.db_engine)
        base.metadata.bind = self.db_engine
        SessionMaker = sqlalchemy.orm.sessionmaker(bind=self.db_engine)
        self.ManagedSessionMaker = _get_managed_session_maker(SessionMaker)

    @staticmethod
    def _verify_registry_tables_exist(db_engine):
        """
        Verify database sql model tables exist.

        :param db_engine: SQLAlchemy database engine to connect to the database.
        """
        # Verify that sql model tables have been created.
        inspected_tables = set(sqlalchemy.inspect(db_engine).get_table_names())
        expected_tables = [
            SqlDataset.__tablename__,
            SqlModelRelation.__tablename__,
            SqlModelVersionRelation.__tablename__,
            SqlProject.__tablename__,
            SqlProjectSnapshot.__tablename__,
            SqlWorkflow.__tablename__,
            SqlArtifact.__tablename__,
            SqlRegisteredModel.__tablename__,
            SqlModelVersion.__tablename__,
            SqlEvent.__tablename__,
            SqlMember.__tablename__
        ]
        if any([table not in inspected_tables for table in expected_tables]):
            raise AIFlowException("Database migration in unexpected state.")

    def _save_to_db(self, session, objs):
        """
        Backend entities store into database
        """
        if type(objs) is list:
            session.add_all(objs)
        else:
            session.add(objs)

    """dataset api"""

    def get_dataset_by_id(self, dataset_id) -> Optional[DatasetMeta]:
        """
        get a specific dataset in metadata store by dataset id.

        :param dataset_id: the dataset id
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object if the dataset exists,
                 Otherwise, returns None if the dataset does not exist.
        """
        with self.ManagedSessionMaker() as session:
            dataset_result = session.query(SqlDataset).filter(SqlDataset.uuid == dataset_id,
                                                              SqlDataset.is_deleted != TRUE).all()
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
        with self.ManagedSessionMaker() as session:
            dataset_result = session.query(SqlDataset).filter(
                and_(SqlDataset.name == dataset_name, SqlDataset.is_deleted != TRUE)).all()
            if len(dataset_result) == 0:
                return None
            return ResultToMeta.result_to_dataset_meta(dataset_result[0])

    def _register_dataset(self, name: Text, data_format: Text = None,
                          description: Text = None, uri: Text = None, properties: Properties = None,
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
        with self.ManagedSessionMaker() as session:
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
                                                            catalog_table=catalog_table)
                session.add(dataset)
                session.flush()
                schema = Schema(name_list=name_list, type_list=type_list)
                return DatasetMeta(uuid=dataset.uuid, name=name, data_format=data_format,
                                   description=description, uri=uri, create_time=create_time, update_time=update_time,
                                   properties=properties, schema=schema, catalog_name=catalog_name,
                                   catalog_type=catalog_type, catalog_database=catalog_database,
                                   catalog_connection_uri=catalog_connection_uri, catalog_table=catalog_table)
            except sqlalchemy.exc.IntegrityError as e:
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
        return self._register_dataset(name=name, data_format=data_format, description=description,
                                      uri=uri, properties=properties, name_list=name_list, type_list=type_list)

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
                                      catalog_type=catalog_type, catalog_connection_uri=catalog_connection_uri,
                                      catalog_table=catalog_table, catalog_database=catalog_database)

    def register_datasets(self, dataset_meta_list: List[DatasetMeta]) -> List[DatasetMeta]:
        """
        register multiple datasets in metadata store.

        :param dataset_meta_list: A list of datasets
        :return: List of :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` objects.
        """
        with self.ManagedSessionMaker() as session:
            try:
                datasets = MetaToTable.dataset_meta_list_to_table(dataset_meta_list)
                session.add_all(datasets)
                session.flush()
                for dataset_meta, dataset in zip(dataset_meta_list, datasets):
                    dataset_meta.uuid = dataset.uuid
                return dataset_meta_list
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException(str(e))

    def update_dataset(self, dataset_name: Text,  data_format: Text = None,
                       description: Text = None, uri: Text = None,
                       properties: Properties = None,
                       name_list: List[Text] = None, type_list: List[DataType] = None, catalog_name: Text = None,
                       catalog_type: Text = None, catalog_database: Text = None,
                       catalog_connection_uri: Text = None,
                       catalog_table: Text = None) -> Optional[DatasetMeta]:
        with self.ManagedSessionMaker() as session:
            try:
                dataset: SqlDataset = session.query(SqlDataset).filter(SqlDataset.name == dataset_name).first()
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
                session.flush()
                return ResultToMeta.result_to_dataset_meta(dataset)
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException(e)

    def list_datasets(self, page_size, offset) -> Optional[List[DatasetMeta]]:
        """
        List registered datasets in metadata store.

        :param page_size: the limitation of the listed datasets.
        :param offset: the offset of listed datasets.
        :return: List of :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` objects,
                 return None if no datasets to be listed.
        """
        with self.ManagedSessionMaker() as session:
            dataset_result = session.query(SqlDataset).filter(SqlDataset.is_deleted != TRUE).limit(
                page_size).offset(
                offset).all()
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
        with self.ManagedSessionMaker() as session:
            try:
                dataset = session.query(SqlDataset).filter(
                    and_(SqlDataset.name == dataset_name, SqlDataset.is_deleted != TRUE)).first()
                if dataset is None:
                    return Status.ERROR
                deleted_dataset_counts = session.query(SqlDataset).filter(
                    and_(SqlDataset.name.like(deleted_character + dataset_name + deleted_character + '%')),
                    SqlDataset.is_deleted == TRUE).count()
                dataset.is_deleted = TRUE
                dataset.name = deleted_character + dataset.name + deleted_character + str(deleted_dataset_counts + 1)
                session.flush()
                return Status.OK
            except sqlalchemy.exc.IntegrityError as e:
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
        with self.ManagedSessionMaker() as session:
            project_result = session.query(SqlProject).filter(
                and_(SqlProject.uuid == project_id, SqlProject.is_deleted != TRUE)).all()
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
        with self.ManagedSessionMaker() as session:
            project_result = session.query(SqlProject).filter(
                and_(SqlProject.name == project_name, SqlProject.is_deleted != TRUE)).all()
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
        with self.ManagedSessionMaker() as session:
            try:
                project = MetaToTable.project_meta_to_table(name=name, uri=uri, properties=properties)
                session.add(project)
                session.flush()
                project_meta = ProjectMeta(uuid=project.uuid, name=name, uri=uri, properties=properties)
                return project_meta
            except sqlalchemy.exc.IntegrityError as e:
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
        with self.ManagedSessionMaker() as session:
            project_result = session.query(SqlProject).filter(SqlProject.is_deleted != TRUE).limit(
                page_size).offset(
                offset).all()
            if len(project_result) == 0:
                return None
            projects = []
            for project in project_result:
                projects.append(ResultToMeta.result_to_project_meta(project))
            return projects

    def update_project(self, project_name: Text, uri: Text = None, properties: Properties = None) -> Optional[ProjectMeta]:
        with self.ManagedSessionMaker() as session:
            try:
                project: SqlProject = session.query(SqlProject).filter(
                    and_(SqlProject.name == project_name, SqlProject.is_deleted != TRUE)).first()
                if project is None:
                    return None
                if uri is not None:
                    project.uri = uri
                if properties is not None:
                    project.properties = str(properties)
                session.flush()
                return ResultToMeta.result_to_project_meta(project)
            except sqlalchemy.exc.IntegrityError as e:
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
        with self.ManagedSessionMaker() as session:
            try:
                project = session.query(SqlProject).filter(
                    and_(SqlProject.name == project_name, SqlProject.is_deleted != TRUE)).first()
                if project is None:
                    return Status.ERROR
                deleted_project_counts = session.query(SqlProject).filter(
                    and_(SqlProject.name.like(deleted_character + project_name + deleted_character + '%')
                         , SqlProject.is_deleted == TRUE)).count()
                project.is_deleted = TRUE
                project.name = deleted_character + project.name + deleted_character + str(deleted_project_counts + 1)
                model_version_list = []
                for per_model in project.model_relation:
                    deleted_model_relation_counts = session.query(SqlModelRelation).filter(
                        and_(SqlModelRelation.name.like(deleted_character + per_model.name + deleted_character + '%'),
                             SqlModelRelation.is_deleted == TRUE)).count()
                    per_model.is_deleted = TRUE
                    per_model.name = deleted_character + per_model.name + deleted_character + str(
                        deleted_model_relation_counts + 1)
                    for model_version in per_model.model_version_relation:
                        deleted_model_version_relation_counts = session.query(SqlModelVersionRelation).filter(
                            and_(SqlModelVersionRelation.version.like(
                                deleted_character + model_version.version + deleted_character + '%'),
                                SqlModelVersionRelation.is_deleted == TRUE)).count()
                        model_version.is_deleted = TRUE
                        model_version.version = deleted_character + model_version.version + deleted_character + str(
                            deleted_model_version_relation_counts + 1)
                    model_version_list += per_model.model_version_relation
                session.add_all(
                    [project] + project.model_relation + model_version_list)
                session.flush()
                return Status.OK
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException(str(e))

    """model api"""

    def get_model_relation_by_id(self, model_id) -> Optional[ModelRelationMeta]:
        """
        get a specific model relation in metadata store by model id.

        :param model_id: the model id
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` object if the model relation
                 exists, Otherwise, returns None if the model relation does not exist.
        """
        with self.ManagedSessionMaker() as session:
            model_result = session.query(SqlModelRelation).filter(
                and_(SqlModelRelation.uuid == model_id, SqlModelRelation.is_deleted != TRUE)).all()
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
        with self.ManagedSessionMaker() as session:
            model_result = session.query(SqlModelRelation).filter(
                and_(SqlModelRelation.name == name, SqlModelRelation.is_deleted != TRUE)).all()
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
        with self.ManagedSessionMaker() as session:
            try:
                model = MetaToTable.model_relation_meta_to_table(name=name, project_id=project_id)
                session.add(model)
                session.flush()
                model_meta = ModelRelationMeta(uuid=model.uuid, name=name, project_id=project_id)
                return model_meta
            except sqlalchemy.exc.IntegrityError as e:
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
        with self.ManagedSessionMaker() as session:
            model_result = session.query(SqlModelRelation).filter(SqlModelRelation.is_deleted != TRUE).limit(
                page_size).offset(
                offset).all()
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
        with self.ManagedSessionMaker() as session:
            try:
                model = session.query(SqlModelRelation).filter(
                    and_(SqlModelRelation.name == model_name, SqlModelRelation.is_deleted != TRUE)).first()
                if model is None:
                    return Status.ERROR
                deleted_model_counts = session.query(SqlModelRelation).filter(
                    and_(SqlModelRelation.name.like(deleted_character + model.name + deleted_character + '%'),
                         SqlModelRelation.is_deleted == TRUE)).count()
                model.is_deleted = TRUE
                model.name = deleted_character + model.name + deleted_character + str(deleted_model_counts + 1)
                for model_version in model.model_version_relation:
                    deleted_model_version_counts = session.query(SqlModelVersionRelation).filter(
                        and_(
                            SqlModelVersionRelation.version.like(
                                deleted_character + model_version.version + deleted_character + '%')),
                        SqlModelVersionRelation.is_deleted == TRUE).count()
                    model_version.is_deleted = TRUE
                    model_version.version = deleted_character + model_version.version + deleted_character + str(
                        deleted_model_version_counts + 1)
                session.add_all([model] + model.model_version_relation)
                session.flush()
                return Status.OK
            except sqlalchemy.exc.IntegrityError as e:
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
        with self.ManagedSessionMaker() as session:
            model_version_result = session.query(SqlModelVersionRelation).filter(
                and_(SqlModelVersionRelation.version == version_name, SqlModelVersionRelation.is_deleted != TRUE,
                     SqlModelVersionRelation.model_id == model_id)).all()
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
        with self.ManagedSessionMaker() as session:
            try:
                model_version = MetaToTable.model_version_relation_to_table(version=version,
                                                                            model_id=model_id,
                                                                            project_snapshot_id=project_snapshot_id)
                session.add(model_version)
                session.flush()
                model_version_meta = ModelVersionRelationMeta(version=version, model_id=model_id,
                                                              project_snapshot_id=project_snapshot_id)
                return model_version_meta
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException('Registered ModelVersion (name={}) already exists. '
                                      'Error: {}'.format(model_version.version, str(e)))

    def list_model_version_relation(self, model_id, page_size, offset) -> Optional[List[ModelVersionRelationMeta]]:
        """
        List registered model version relations in metadata store.

        :param model_id: the model id corresponded to the model version
        :param page_size: the limitation of the listed model version relations.
        :param offset: the offset of listed model version relations.
        :return: List of :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` objects,
                 return None if no model version relations to be listed.
        """
        with self.ManagedSessionMaker() as session:
            model_version_result = session.query(SqlModelVersionRelation).filter(
                and_(SqlModelVersionRelation.model_id == model_id, SqlModelVersionRelation.is_deleted != TRUE)).limit(
                page_size).offset(offset).all()
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
        with self.ManagedSessionMaker() as session:
            try:
                model_version = session.query(SqlModelVersionRelation).filter(
                    and_(SqlModelVersionRelation.version == version, SqlModelVersionRelation.model_id == model_id,
                         SqlModelVersionRelation.is_deleted != TRUE)).first()
                if model_version is None:
                    return Status.ERROR
                deleted_model_version_counts = session.query(SqlModelVersionRelation).filter(
                    and_(SqlModelVersionRelation.version.like(deleted_character + version + deleted_character + '%')),
                    SqlModelVersionRelation.is_deleted == TRUE).count()
                model_version.is_deleted = TRUE
                model_version.version = deleted_character + model_version.version + deleted_character + str(
                    deleted_model_version_counts + 1)
                session.flush()
                return Status.OK
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException(str(e))

    '''workflow api'''

    def register_workflow(self, name, project_id, properties=None) -> WorkflowMeta:
        """
        Register a workflow in metadata store.

        :param name: the workflow name
        :param project_id: the id of project which contains the workflow
        :param properties: the workflow properties
        """
        update_time = create_time = int(time.time() * 1000)
        with self.ManagedSessionMaker() as session:
            try:
                workflow = MetaToTable.workflow_to_table(name=name,
                                                         project_id=project_id,
                                                         properties=properties,
                                                         create_time=create_time,
                                                         update_time=update_time)
                session.add(workflow)
                session.flush()
                return WorkflowMeta(uuid=workflow.uuid, name=name,
                                    project_id=project_id, properties=properties,
                                    create_time=create_time, update_time=update_time)
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException('Error: {}'.format(workflow.name, workflow.project_id, str(e)))

    def get_workflow_by_name(self, project_name, workflow_name) -> Optional[WorkflowMeta]:
        """
        Get a workflow by specific project name and workflow name

        :param project_name: the name of project which contains the workflow
        :param workflow_name: the workflow name
        """
        with self.ManagedSessionMaker() as session:
            project = self.get_project_by_name(project_name)
            if not project:
                raise AIFlowException("The project name you specific doesn't exists, project: \"{}\""
                                      .format(project_name))
            workflow = session.query(SqlWorkflow).filter(SqlWorkflow.project_id == project.uuid,
                                                         SqlWorkflow.name == workflow_name,
                                                         SqlWorkflow.is_deleted.is_(False)).scalar()
            return None if workflow is None else ResultToMeta.result_to_workflow_meta(workflow)

    def get_workflow_by_id(self, workflow_id) -> Optional[WorkflowMeta]:
        """
        Get a workflow by specific uuid

        :param workflow_id: the uuid of workflow
        """
        with self.ManagedSessionMaker() as session:
            workflow = session.query(SqlWorkflow).filter(SqlWorkflow.uuid == workflow_id,
                                                         SqlWorkflow.is_deleted.is_(False)).scalar()
            return None if workflow is None else ResultToMeta.result_to_workflow_meta(workflow)

    def list_workflows(self, project_name, page_size, offset) -> Optional[List[WorkflowMeta]]:
        """
        List all workflows of the specific project

        :param project_name: the name of project which contains the workflow
        :param page_size     limitation of listed workflows.
        :param offset        offset of listed workflows.
        """

        with self.ManagedSessionMaker() as session:
            project = self.get_project_by_name(project_name)
            if not project:
                raise AIFlowException("The project name you specific doesn't exists, project: \"{}\""
                                      .format(project_name))
            workflow_result = session.query(SqlWorkflow).filter(SqlWorkflow.project_id == project.uuid,
                                                                SqlWorkflow.is_deleted.is_(False)).limit(
                page_size).offset(offset).all()
            if len(workflow_result) == 0:
                return None
            workflow_list = []
            for workflow in workflow_result:
                workflow_list.append(ResultToMeta.result_to_workflow_meta(workflow))
            return workflow_list

    def delete_workflow_by_name(self, project_name, workflow_name) -> Status:
        """
        Delete the workflow by specific project and workflow name

        :param project_name: the name of project which contains the workflow
        :param workflow_name: the workflow name
        """
        workflow = self.get_workflow_by_name(project_name=project_name,
                                             workflow_name=workflow_name)
        if workflow is None:
            return Status.ERROR
        else:
            return self.delete_workflow_by_id(workflow.uuid)

    def delete_workflow_by_id(self, workflow_id) -> Status:
        """
        Delete the workflow by specific id

        :param workflow_id: the uuid of workflow
        """
        with self.ManagedSessionMaker() as session:
            try:
                workflow = session.query(SqlWorkflow).filter(SqlWorkflow.uuid == workflow_id,
                                                             SqlWorkflow.is_deleted.is_(False)).scalar()
                if workflow is None:
                    return Status.ERROR
                deleted_workflow_counts = session.query(SqlWorkflow).filter(
                    SqlWorkflow.project_id == workflow.project_id,
                    SqlWorkflow.name.like(deleted_character + workflow.name + deleted_character + '%'),
                    SqlWorkflow.is_deleted.is_(True)).count()
                workflow.is_deleted = True
                workflow.name = deleted_character + workflow.name + deleted_character + str(deleted_workflow_counts + 1)
                session.flush()
                return Status.OK
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException(str(e))

    def update_workflow(self, workflow_name, project_name, properties=None) -> Optional[WorkflowMeta]:
        """
        Update the workflow

        :param workflow_name: the workflow name
        :param project_name: the name of project which contains the workflow
        :param properties: (Optional) the properties need to be updated
        """
        with self.ManagedSessionMaker() as session:
            try:
                project = self.get_project_by_name(project_name)
                if not project:
                    raise AIFlowException("The project name you specific doesn't exists, project: \"{}\""
                                          .format(project_name))
                workflow = session.query(SqlWorkflow).filter(SqlWorkflow.name == workflow_name,
                                                             SqlWorkflow.project_id == project.uuid).scalar()
                if workflow is None:
                    return None
                if properties is not None:
                    workflow.properties = str(properties)

                workflow.update_time = int(time.time() * 1000)
                session.flush()
                return ResultToMeta.result_to_workflow_meta(workflow)
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException(e)

    """artifact api"""

    def get_artifact_by_id(self, artifact_id: int) -> Optional[ArtifactMeta]:
        """
        get a specific artifact in metadata store by artifact id.

        :param artifact_id: the artifact id
        :return: A single :py:class:`ai_flow.meta.artifact_meta.ArtifactMeta` object
                 if the artifact exists, Otherwise, returns None if the artifact does not exist.
        """
        with self.ManagedSessionMaker() as session:
            artifact_result = session.query(SqlArtifact).filter(
                and_(SqlArtifact.uuid == artifact_id, SqlArtifact.is_deleted != TRUE)).all()
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
        with self.ManagedSessionMaker() as session:
            artifact_result = session.query(SqlArtifact).filter(
                and_(SqlArtifact.name == artifact_name, SqlArtifact.is_deleted != TRUE)).all()
            if len(artifact_result) == 0:
                return None
            artifact = ResultToMeta.result_to_artifact_meta(artifact_result[0])
            return artifact

    def register_artifact(self, name: Text, artifact_type: Text = None,
                          description: Text = None, uri: Text = None,
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
        with self.ManagedSessionMaker() as session:
            try:
                create_time = update_time = int(time.time() * 1000)
                artifact = MetaToTable.artifact_meta_to_table(name=name, artifact_type=artifact_type,
                                                              description=description, uri=uri,
                                                              create_time=create_time,
                                                              update_time=update_time, properties=properties)
                session.add(artifact)
                session.flush()
                artifact_meta = ArtifactMeta(uuid=artifact.uuid, name=name, artifact_type=artifact_type,
                                             description=description, uri=uri,
                                             create_time=create_time,
                                             update_time=update_time, properties=properties)
                return artifact_meta
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException('Registered Artifact (name={}) already exists. '
                                      'Error: {}'.format(artifact.name, str(e)))

    def update_artifact(self, name: Text, artifact_type: Text = None,
                        description: Text = None, uri: Text = None,
                        properties: Properties = None) -> Optional[ArtifactMeta]:
        with self.ManagedSessionMaker() as session:
            try:
                artifact: SqlArtifact = session.query(SqlArtifact).filter(
                    and_(SqlArtifact.name == name, SqlArtifact.is_deleted != TRUE)).first()
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
                session.flush()
                return ResultToMeta.result_to_artifact_meta(artifact)
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException(str(e))

    def list_artifact(self, page_size, offset) -> Optional[List[ArtifactMeta]]:
        """
        List registered artifacts in metadata store.

        :param page_size: the limitation of the listed artifacts.
        :param offset: the offset of listed artifacts.
        :return: List of :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` objects,
                 return None if no artifacts to be listed.
        """
        with self.ManagedSessionMaker() as session:
            artifact_result = session.query(SqlArtifact).filter(SqlArtifact.is_deleted != TRUE).limit(page_size).offset(
                offset).all()
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
        with self.ManagedSessionMaker() as session:
            try:
                artifact = session.query(SqlArtifact).filter(
                    and_(SqlArtifact.name == artifact_name, SqlArtifact.is_deleted != TRUE)).first()
                if artifact is None:
                    return Status.ERROR
                deleted_artifact_counts = session.query(SqlArtifact).filter(
                    and_(SqlArtifact.name.like(deleted_character + artifact_name + deleted_character + '%')),
                    SqlArtifact.is_deleted == TRUE).count()
                artifact.is_deleted = TRUE
                artifact.name = deleted_character + artifact.name + deleted_character + str(deleted_artifact_counts + 1)
                session.flush()
                return Status.OK
            except sqlalchemy.exc.IntegrityError as e:
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
        with self.ManagedSessionMaker() as session:
            model_version = session.query(SqlModelVersion).filter(
                and_(SqlModelVersion.model_name == model_name, SqlModelVersion.current_stage == stage)) \
                .order_by(cast(SqlModelVersion.model_version, Integer).desc()).first()
            if model_version is None:
                return None
            else:
                return model_version.to_meta_entity()

    @classmethod
    def _get_registered_model(cls, session, model_name):
        """
        Query registered model in Model Center filter by model name

        :param model_name: Unique name for registered model within Model Center.
        """
        if model_name is None:
            raise AIFlowException('Registered model name cannot be empty.', INVALID_PARAMETER_VALUE)

        register_models = session.query(SqlRegisteredModel).filter(SqlRegisteredModel.model_name == model_name).all()

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
        with self.ManagedSessionMaker() as session:
            try:
                before_model = self._get_registered_model(session, model_name=model_name)
                if before_model is not None:
                    if _compare_model_fields(model_desc, before_model):
                        sql_registered_model = SqlRegisteredModel(model_name=model_name,
                                                                  model_desc=model_desc)
                        return sql_registered_model.to_meta_entity()
                    else:
                        raise AIFlowException("You have registered the model with same name: \"{}\" "
                                              "but different fields".format(model_name), RESOURCE_ALREADY_EXISTS)
                sql_registered_model = SqlRegisteredModel(model_name=model_name,
                                                          model_desc=model_desc)
                self._save_to_db(session, sql_registered_model)
                session.flush()
                return sql_registered_model.to_meta_entity()
            except sqlalchemy.exc.IntegrityError as e:
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
        with self.ManagedSessionMaker() as session:
            sql_registered_model = self._get_registered_model(session, registered_model.model_name)
            if sql_registered_model is None:
                return None
            else:
                try:
                    if model_name is not None:
                        sql_registered_model.model_name = model_name
                        # Update model name of registered model version
                        for sql_model_version in sql_registered_model.model_version:
                            sql_model_version.model_name = model_name
                    if model_desc is not None:
                        sql_registered_model.model_desc = model_desc
                    self._save_to_db(session, [sql_registered_model] + sql_registered_model.model_version)
                    session.flush()
                    return sql_registered_model.to_meta_entity()
                except sqlalchemy.exc.IntegrityError as e:
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
        with self.ManagedSessionMaker() as session:
            sql_registered_model = self._get_registered_model(session, registered_model.model_name)
            if sql_registered_model is not None:
                session.delete(sql_registered_model)

    def list_registered_models(self):
        """
        List of registered models backend in Model Center.

        :return: List of :py:class:`ai_flow.model_center.entity.RegisteredModel` objects.
        """
        with self.ManagedSessionMaker() as session:
            return [sql_registered_model.to_detail_entity()
                    for sql_registered_model in session.query(SqlRegisteredModel).all()]

    def get_registered_model_detail(self, registered_model):
        """
        Get registered model detail filter by model name and model version for Model Center.

        :param registered_model: :py:class:`ai_flow.model_center.entity.RegisteredModel` object.

        :return: Object of :py:class:`ai_flow.model_center.entity.RegisteredModelDetail` backend in Model Center.
        """
        with self.ManagedSessionMaker() as session:
            sql_registered_model = self._get_registered_model(session, registered_model.model_name)
            return None if sql_registered_model is None else sql_registered_model.to_detail_entity()

    @classmethod
    def _get_sql_model_version(cls, session, model_version):
        model_name = model_version.model_name
        model_version = model_version.model_version
        if model_name is None:
            raise AIFlowException('Registered model name cannot be empty.', INVALID_PARAMETER_VALUE)
        if model_version is None:
            raise AIFlowException('Registered model version cannot be empty.', INVALID_PARAMETER_VALUE)
        conditions = [
            SqlModelVersion.model_name == model_name,
            SqlModelVersion.model_version == model_version,
            SqlModelVersion.current_stage != STAGE_DELETED
        ]
        model_versions = session.query(SqlModelVersion).filter(*conditions).all()

        if len(model_versions) == 0:
            return None
        else:
            _logger.info("Get registered model version: %s of model name: %s.", model_versions[0],
                         model_versions[0].model_name)
            return model_versions[0]

    @classmethod
    def _list_sql_model_versions(cls, session, registered_model):
        model_name = registered_model.model_name
        if model_name is None:
            raise AIFlowException('Registered model name cannot be empty.', INVALID_PARAMETER_VALUE)
        conditions = [
            SqlModelVersion.model_name == model_name,
            SqlModelVersion.current_stage != STAGE_DELETED
        ]
        return session.query(SqlModelVersion).filter(*conditions).all()

    @classmethod
    def _delete_model_version_count(cls, session, model_version):
        model_name = model_version.model_name
        model_version = model_version.model_version
        if model_name is None:
            raise AIFlowException('Registered model name cannot be empty.', INVALID_PARAMETER_VALUE)
        if model_version is None:
            raise AIFlowException('Registered model version cannot be empty.', INVALID_PARAMETER_VALUE)
        conditions = [
            SqlModelVersion.model_name == model_name,
            SqlModelVersion.model_version.like(_gen_like_entity_name(model_version)),
            SqlModelVersion.current_stage != STAGE_DELETED
        ]
        return session.query(SqlModelVersion).filter(*conditions).count()

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

        with self.ManagedSessionMaker() as session:
            for attempt in range(self.CREATE_RETRY_TIMES):
                try:
                    sql_registered_model = self._get_registered_model(session, model_name)
                    if sql_registered_model is None:
                        return None
                    else:
                        model_versions = self._list_sql_model_versions(session, sql_registered_model)
                        if model_versions is None:
                            version_num = 0
                        else:
                            version_num = len(model_versions)
                        model_version = next_version(version_num)
                        sql_model_version = SqlModelVersion(model_name=model_name,
                                                            model_version=model_version,
                                                            model_path=model_path,
                                                            model_type=model_type,
                                                            version_desc=version_desc,
                                                            current_stage=get_canonical_stage(current_stage))
                        self._save_to_db(session, [sql_registered_model, sql_model_version])
                        session.flush()
                        return sql_model_version.to_meta_entity()
                except sqlalchemy.exc.IntegrityError:
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
        with self.ManagedSessionMaker() as session:
            serving_model_version = self.get_deployed_model_version(model_version.model_name)
            if serving_model_version is not None and current_stage == 'DEPLOYED':
                raise AIFlowException('There is already a serving model version="{}" of model="{}"'.
                                      format(serving_model_version.model_version, serving_model_version.model_name))
            sql_model_version = self._get_sql_model_version(session, model_version)
            if sql_model_version is None:
                return None
            else:
                try:
                    if model_path is not None:
                        sql_model_version.model_path = model_path
                    if model_type is not None:
                        sql_model_version.model_type = model_type
                    if version_desc is not None:
                        sql_model_version.version_desc = version_desc
                    if current_stage is not None:
                        sql_model_version.current_stage = get_canonical_stage(current_stage)
                    self._save_to_db(session, sql_model_version)
                    session.flush()
                    return sql_model_version.to_meta_entity()
                except sqlalchemy.exc.IntegrityError as e:
                    raise AIFlowException(
                        'Update model version error (model_name={}, model_version={}).'.format(model_version.model_name,
                                                                                               model_version.model_version))

    def delete_model_version(self, model_version):
        """
        Delete model version in model repository.

        :param model_version: :py:class:`ai_flow.model_center.entity.ModelVersion` object.

        :return: None
        """
        with self.ManagedSessionMaker() as session:
            sql_model_version = self._get_sql_model_version(session, model_version)
            if sql_model_version is None:
                return None
            else:
                sql_model_version = self._get_sql_model_version(session, model_version)
                sql_model_version.model_path = "REDACTED-SOURCE-PATH"
                sql_model_version.model_type = "REDACTED-TYPE-FEATURE"
                sql_model_version.version_status = None
                sql_model_version.version_desc = None
                sql_model_version.current_stage = STAGE_DELETED
                self._save_to_db(session, sql_model_version)

    def get_model_version_detail(self, model_version):
        """
        :param model_version: :py:class:`ai_flow.model_center.entity.ModelVersion` object.

        :return: Object of :py:class:`ai_flow.model_center.entity.ModelVersionDetail` backend in Model Center.
        """
        with self.ManagedSessionMaker() as session:
            sql_model_version = self._get_sql_model_version(session, model_version)
            return None if sql_model_version is None else sql_model_version.to_meta_entity()

    """metric api"""

    def register_metric_meta(self, metric_name, metric_type, project_name, metric_desc=None, dataset_name=None,
                             model_name=None, job_name=None, start_time=None, end_time=None, uri=None, tags=None,
                             properties=None) -> MetricMeta:
        with self.ManagedSessionMaker() as session:
            try:
                metric_meta_table = metric_meta_to_table(metric_name, metric_type, metric_desc, project_name,
                                                         dataset_name, model_name, job_name, start_time, end_time, uri,
                                                         tags, properties)
                session.add(metric_meta_table)
                session.flush()
                return MetricMeta(metric_name=metric_name,
                                  metric_type=metric_type,
                                  metric_desc=metric_desc,
                                  project_name=project_name,
                                  dataset_name=dataset_name,
                                  model_name=model_name,
                                  job_name=job_name,
                                  start_time=start_time,
                                  end_time=end_time,
                                  uri=uri,
                                  tags=tags,
                                  properties=properties)
            except Exception as e:
                raise AIFlowException('Register metric meta failed! Error: {}.'.format(str(e)))

    def update_metric_meta(self, metric_name, metric_desc=None, project_name=None, dataset_name=None,
                           model_name=None, job_name=None, start_time=None, end_time=None, uri=None, tags=None,
                           properties=None) -> MetricMeta:
        with self.ManagedSessionMaker() as session:
            try:
                metric_meta_table: SqlMetricMeta = session.query(SqlMetricMeta).filter(
                    and_(SqlMetricMeta.metric_name == metric_name, SqlMetricMeta.is_deleted != TRUE)
                ).first()
                if metric_desc is not None:
                    metric_meta_table.metric_desc = metric_desc
                if project_name is not None:
                    metric_meta_table.project_name = project_name
                if dataset_name is not None:
                    metric_meta_table.dataset_name = dataset_name
                if model_name is not None:
                    metric_meta_table.model_name = model_name
                if job_name is not None:
                    metric_meta_table.job_name = job_name
                if start_time is not None:
                    metric_meta_table.start_time = start_time
                if end_time is not None:
                    metric_meta_table.end_time = end_time
                if uri is not None:
                    metric_meta_table.uri = uri
                if tags is not None:
                    metric_meta_table.tags = tags
                if properties is not None and properties != {}:
                    metric_meta_table.properties = str(properties)
                session.add(metric_meta_table)
                session.flush()
                return table_to_metric_meta(metric_meta_table)
            except Exception as e:
                raise AIFlowException('Update metric meta failed! Error: {}.'.format(str(e)))

    def delete_metric_meta(self, metric_name):
        with self.ManagedSessionMaker() as session:
            try:
                metric_meta = session.query(SqlMetricMeta).filter(
                    and_(SqlMetricMeta.metric_name == metric_name, SqlMetricMeta.is_deleted != TRUE)).first()
                if metric_meta is None:
                    return Status.ERROR
                deleted_metric_meta_counts = session.query(SqlMetricMeta).filter(
                    and_(SqlMetricMeta.metric_name.like(
                        deleted_character + metric_meta.metric_name + deleted_character + '%')),
                    SqlDataset.is_deleted == TRUE).count()
                metric_meta.is_deleted = TRUE
                metric_meta.metric_name = deleted_character + metric_meta.metric_name + deleted_character + str(
                    deleted_metric_meta_counts + 1)
                for metric_summary in metric_meta.metric_summary:
                    deleted_metric_summary_counts = session.query(SqlMetricSummary).filter(
                        and_(SqlMetricSummary.metric_name.like(
                            deleted_character + metric_summary.metric_name + deleted_character + '%'),
                            SqlMetricSummary.is_deleted == TRUE)).count()
                    metric_summary.is_deleted = TRUE
                    metric_summary.metric_name = deleted_character + metric_summary.metric_name + deleted_character + str(
                        deleted_metric_summary_counts + 1)
                session.add_all([metric_meta] + metric_meta.metric_summary)
                session.flush()
                return Status.OK
            except Exception as e:
                raise AIFlowException('Delete metric meta failed! Error: {}.'.format(str(e)))

    def get_metric_meta(self, metric_name) -> Union[None, MetricMeta]:
        with self.ManagedSessionMaker() as session:
            try:
                conditions = [
                    SqlMetricMeta.metric_name == metric_name,
                    SqlMetricMeta.is_deleted != TRUE
                ]
                metric_meta_table = session.query(SqlMetricMeta).filter(*conditions).first()
                if metric_meta_table is None:
                    return None
                else:
                    return table_to_metric_meta(metric_meta_table)
            except Exception as e:
                raise AIFlowException('Get metric meta failed! Error: {}.'.format(str(e)))

    def list_dataset_metric_metas(self, dataset_name, project_name=None) -> Union[None, MetricMeta, List[MetricMeta]]:
        with self.ManagedSessionMaker() as session:
            try:
                conditions = [
                    SqlMetricMeta.dataset_name == dataset_name,
                    SqlMetricMeta.metric_type == MetricType.DATASET.value,
                    SqlMetricMeta.is_deleted != TRUE
                ]
                if project_name is not None:
                    conditions.append(SqlMetricMeta.project_name == project_name)
                metric_meta_tables = session.query(SqlMetricMeta).filter(*conditions).all()
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
                raise AIFlowException('Get dataset metric metas failed! Error: {}.'.format(str(e)))

    def list_model_metric_metas(self, model_name, project_name=None) -> Union[
            None, MetricMeta, List[MetricMeta]]:
        with self.ManagedSessionMaker() as session:
            try:
                conditions = [
                    SqlMetricMeta.model_name == model_name,
                    SqlMetricMeta.metric_type == MetricType.MODEL.value,
                    SqlMetricMeta.is_deleted != TRUE
                ]
                if project_name is not None:
                    conditions.append(SqlMetricMeta.project_name == project_name)
                metric_meta_tables = session.query(SqlMetricMeta).filter(*conditions).all()
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
                raise AIFlowException('Get model metric metas failed! Error: {}.'.format(str(e)))

    def register_metric_summary(self, metric_name, metric_key, metric_value, metric_timestamp, model_version=None,
                                job_execution_id=None) -> MetricSummary:
        with self.ManagedSessionMaker() as session:
            try:
                metric_summary_table = metric_summary_to_table(metric_name, metric_key, metric_value, metric_timestamp,
                                                               model_version, job_execution_id)
                session.add(metric_summary_table)
                session.flush()
                return MetricSummary(uuid=metric_summary_table.uuid,
                                     metric_name=metric_name,
                                     metric_key=metric_key,
                                     metric_value=metric_value,
                                     metric_timestamp=metric_timestamp,
                                     model_version=model_version,
                                     job_execution_id=job_execution_id)
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException('Register metric summary failed! Error: {}.'.format(str(e)))

    def update_metric_summary(self, uuid, metric_name=None, metric_key=None, metric_value=None, metric_timestamp=None,
                              model_version=None, job_execution_id=None) -> MetricSummary:
        with self.ManagedSessionMaker() as session:
            try:
                metric_summary_table = session.query(SqlMetricSummary).filter(
                    and_(SqlMetricSummary.uuid == uuid, SqlMetricSummary.is_deleted != TRUE)
                ).first()
                if metric_name is not None:
                    metric_summary_table.metric_name = metric_name
                if metric_key is not None:
                    metric_summary_table.metric_key = metric_key
                if metric_value is not None:
                    metric_summary_table.metric_value = metric_value
                if metric_timestamp is not None:
                    metric_summary_table.metric_timestamp = metric_timestamp
                if model_version is not None:
                    metric_summary_table.model_version = model_version
                if job_execution_id is not None:
                    metric_summary_table.job_execution_id = job_execution_id
                session.add(metric_summary_table)
                session.flush()
                return table_to_metric_summary(metric_summary_table)
            except sqlalchemy.exc.IntegrityError as e:
                raise AIFlowException('Update metric summary failed! Error: {}.'.format(str(e)))

    def delete_metric_summary(self, uuid: int):
        with self.ManagedSessionMaker() as session:
            try:
                conditions = [
                    SqlMetricSummary.uuid == uuid
                ]
                metric_summary_table = session.query(SqlMetricSummary).filter(*conditions).first()
                metric_summary_table.is_deleted = TRUE
                session.add(metric_summary_table)
                session.flush()
            except Exception as e:
                raise AIFlowException('Delete metric summary failed! Error: {}.'.format(str(e)))

    def get_metric_summary(self, uuid) -> Union[None, MetricSummary]:
        with self.ManagedSessionMaker() as session:
            try:
                conditions = [
                    SqlMetricSummary.uuid == uuid,
                    SqlMetricSummary.is_deleted != TRUE
                ]
                metric_summary_table = session.query(SqlMetricSummary).filter(*conditions).first()
                if metric_summary_table is None:
                    return None
                else:
                    return table_to_metric_summary(metric_summary_table)
            except Exception as e:
                raise AIFlowException('Get metric summary failed! Error: {}.'.format(str(e)))

    def list_metric_summaries(self, metric_name=None, metric_key=None, model_version=None, start_time=None,
                              end_time=None) -> Union[None, MetricSummary, List[MetricSummary]]:
        with self.ManagedSessionMaker() as session:
            try:
                conditions = [
                    SqlMetricSummary.is_deleted != TRUE
                ]
                if metric_name is not None:
                    conditions.append(SqlMetricSummary.metric_name == metric_name)
                if metric_key is not None:
                    conditions.append(SqlMetricSummary.metric_key == metric_key)
                if model_version is not None:
                    conditions.append(SqlMetricSummary.model_version == model_version)
                if start_time is not None:
                    conditions.append(SqlMetricSummary.metric_timestamp >= start_time)
                if end_time is not None:
                    conditions.append(SqlMetricSummary.metric_timestamp <= end_time)
                metric_summary_tables = session.query(SqlMetricSummary).filter(*conditions).all()
                if len(metric_summary_tables) == 0:
                    return None
                elif len(metric_summary_tables) == 1:
                    metric_summary_table = metric_summary_tables[0]
                    return table_to_metric_summary(metric_summary_table)
                else:
                    results = []
                    for metric_summary_table in metric_summary_tables:
                        results.append(table_to_metric_summary(metric_summary_table))
                    return results
            except Exception as e:
                raise AIFlowException('List metric summaries failed! Error: {}.'.format(str(e)))

    def list_living_members(self, ttl_ms) -> List[Member]:
        with self.ManagedSessionMaker() as session:
            try:
                member_models = session.query(SqlMember) \
                    .filter(SqlMember.update_time >= time.time_ns() / 1000000 - ttl_ms) \
                    .all()
                return [Member(m.version, m.server_uri, int(m.update_time)) for m in member_models]
            except Exception as e:
                raise AIFlowException("List living AIFlow Member Error.") from e

    def update_member(self, server_uri, server_uuid):
        with self.ManagedSessionMaker() as session:
            try:
                member = session.query(SqlMember) \
                    .filter(SqlMember.server_uri == server_uri).first()
                if member is None:
                    member = SqlMember()
                    member.version = 1
                    member.server_uri = server_uri
                    member.update_time = time.time_ns() / 1000000
                    member.uuid = server_uuid
                    session.add(member)
                else:
                    if member.uuid != server_uuid:
                        raise Exception("The server uri '%s' is already exists in the storage!" %
                                        server_uri)
                    member.version += 1
                    member.update_time = time.time_ns() / 1000000
            except Exception as e:
                raise AIFlowException("Update AIFlow Member Error.") from e

    def clear_dead_members(self, ttl_ms):
        with self.ManagedSessionMaker() as session:
            try:
                session.query(SqlMember) \
                    .filter(SqlMember.update_time < time.time_ns() / 1000000 - ttl_ms) \
                    .delete()
            except Exception as e:
                raise AIFlowException("Clear dead AIFlow Member Error.") from e


def _gen_entity_name_prefix(name):
    return deleted_character + name + deleted_character


def _gen_like_entity_name(name):
    return _gen_entity_name_prefix(name) + '%'


def _gen_delete_entity_name(name, count):
    return _gen_entity_name_prefix(name) + str(count + 1)


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
