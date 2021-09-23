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
from notification_service.base_notification import BaseEvent
from sqlalchemy import (
    Column, String, ForeignKey, Integer, PrimaryKeyConstraint, BigInteger, UniqueConstraint, Text, Boolean)
from sqlalchemy.orm import relationship, backref
from mongoengine import (Document, StringField, IntField, LongField, ReferenceField,
                         BooleanField, ListField, ObjectIdField, SequenceField)

from ai_flow.meta.metric_meta import MetricType
from ai_flow.model_center.entity.model_version_detail import ModelVersionDetail
from ai_flow.model_center.entity.model_version_stage import STAGE_DELETED, STAGE_GENERATED
from ai_flow.model_center.entity.model_version_status import ModelVersionStatus
from ai_flow.model_center.entity.registered_model_detail import RegisteredModelDetail
from ai_flow.store import MONGO_DB_ALIAS_META_SERVICE
from ai_flow.store.db.base_model import base, Base


class SqlDataset(base, Base):
    """
    SQL table of dataset in metadata backend storage.
    """
    __tablename__ = 'dataset'

    name = Column(String(255), unique=True, nullable=False)
    format = Column(String(256))
    description = Column(String(1000))
    uri = Column(String(1000))
    create_time = Column(BigInteger)
    update_time = Column(BigInteger)
    properties = Column(String(1000))
    name_list = Column(String(1000))
    type_list = Column(String(1000))
    catalog_name = Column(String(1000))
    catalog_type = Column(String(1000))
    catalog_database = Column(String(1000))
    catalog_connection_uri = Column(String(1000))
    catalog_table = Column(String(1000))
    is_deleted = Column(String(256), default='False')

    def __repr__(self):
        return '<Document dataset ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})>'.format(
            self.uuid,
            self.name,
            self.properties,
            self.name_list,
            self.type_list,
            self.format,
            self.uri,
            self.catalog_name,
            self.catalog_type,
            self.catalog_database,
            self.catalog_table)


class SqlProject(base, Base):
    """
    SQL table of project in metadata backend storage.
    """
    __tablename__ = 'project'

    name = Column(String(255), unique=True)
    properties = Column(String(1000))
    uri = Column(String(1000))
    is_deleted = Column(String(256), default='False')

    def __repr__(self):
        return '<project ({}, {}, {}, {})>'.format(self.uuid, self.name, self.properties, self.uri)


class SqlProjectSnapshot(base, Base):
    """
    SQL table of project snapshot in metadata backend storage
    """
    __tablename__ = 'project_snapshot'

    project_id = Column(BigInteger, ForeignKey('project.uuid', onupdate='cascade'))
    signature = Column(String(255))
    create_time = Column(BigInteger)

    project = relationship("SqlProject", backref=backref('project_snapshot', cascade='all'))


class SqlModelRelation(base, Base):
    """
    SQL table of model relation in metadata backend storage.
    """
    __tablename__ = 'model_relation'

    name = Column(String(255), unique=True)
    project_id = Column(BigInteger, ForeignKey('project.uuid', onupdate='cascade'))
    is_deleted = Column(String(256), default='False')

    project = relationship("SqlProject", backref=backref('model_relation', cascade='all'))

    def __repr__(self):
        return '<model_relation ({}, {}, {})>'.format(self.uuid, self.name, self.project_id)


class SqlWorkflow(base, Base):
    """
    SQL table of workflow in metadata backend storage.
    """
    __tablename__ = 'workflow'

    name = Column(String(255), nullable=False)
    project_id = Column(BigInteger, ForeignKey('project.uuid', onupdate='cascade'))
    properties = Column(String(1000))
    create_time = Column(BigInteger)
    update_time = Column(BigInteger)
    is_deleted = Column(Boolean, default=False)

    UniqueConstraint(project_id, name)

    project = relationship("SqlProject", backref=backref('workflow', cascade='all'))

    def __repr__(self):
        return '<workflow ({}, {}, {}, {}, {}, {}, {})>'.format(self.uuid, self.name, self.project_id, self.properties,
                                                                self.create_time, self.update_time, self.is_deleted)


class SqlModelVersionRelation(base):
    """
    SQL table of model version relation in metadata backend storage.
    """
    __tablename__ = 'model_version_relation'

    version = Column(String(255), primary_key=True)
    model_id = Column(BigInteger, ForeignKey('model_relation.uuid', onupdate='cascade'), primary_key=True)
    project_snapshot_id = Column(BigInteger, ForeignKey('project_snapshot.uuid', onupdate='cascade'))
    is_deleted = Column(String(256), default='False')

    model_relation = relationship("SqlModelRelation", backref=backref('model_version_relation', cascade='all'))
    project_snapshot = relationship("SqlProjectSnapshot", backref=backref('project_snapshot', cascade='all'))

    def __repr__(self):
        return '<model_version_relation ({}, {}, {})>'.format(self.version, self.model_id,
                                                              self.workflow_execution_id)


class SqlArtifact(base, Base):
    """
    SQL table of artifact in metadata backend storage.
    """

    __tablename__ = 'artifact'

    name = Column(String(255), unique=True, nullable=False)
    artifact_type = Column(String(256))
    description = Column(String(1000))
    uri = Column(String(1000))
    create_time = Column(BigInteger)
    update_time = Column(BigInteger)
    properties = Column(String(1000))
    is_deleted = Column(String(256), default='False')

    def __repr__(self):
        return '<SqlArtifact ({}, {}, {}, {}, {}, {}, {}, {}, {})>'.format(self.uuid, self.name, self.artifact_type,
                                                                           self.description, self.uri,
                                                                           self.create_time, self.update_time,
                                                                           self.properties, self.is_deleted)


class SqlRegisteredModel(base):
    """
    SQL model of registered model in Model Center backend storage.
    """
    __tablename__ = 'registered_model'

    model_name = Column(String(255), unique=True, nullable=False)
    model_desc = Column(String(1000), nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('model_name', name='registered_model_pk'),
    )

    def __repr__(self):
        return '<SqlRegisteredModel ({}, {}, {})>'.format(self.model_name, self.model_desc)

    # entity mappers
    def to_meta_entity(self):
        return RegisteredModelDetail(self.model_name, self.model_desc)

    def to_detail_entity(self):
        # SqlRegisteredModel has backref to all "model_version". Filter latest version of registered model.
        latest_version = None
        for model_version in reversed(self.model_version):
            if model_version.current_stage != STAGE_DELETED:
                latest_version = model_version.to_meta_entity()
                break
        return RegisteredModelDetail(self.model_name, self.model_desc, latest_version)


class SqlModelVersion(base):
    """
    SQL model of model version in Model Center backend storage.
    """
    __tablename__ = 'model_version'

    model_name = Column(String(255), ForeignKey('registered_model.model_name', onupdate='cascade', ondelete='cascade'))
    model_version = Column(String(10), nullable=False)
    model_path = Column(String(500), nullable=True, default=None)
    model_type = Column(String(500), nullable=True, default=None)
    version_desc = Column(String(1000), nullable=True)
    version_status = Column(String(20),
                            default=ModelVersionStatus.to_string(ModelVersionStatus.READY))
    current_stage = Column(String(20), default=STAGE_GENERATED)

    # linked entities
    registered_model = relationship('SqlRegisteredModel', backref=backref('model_version', cascade='all'))

    __table_args__ = (
        PrimaryKeyConstraint('model_name', 'model_version', 'current_stage', name='model_version_pk'),
    )

    def __repr__(self):
        return '<SqlModelVersion ({}, {}, {}, {}, {}, {}, {})>'.format(self.model_name, self.model_version,
                                                                       self.model_path, self.model_type,
                                                                       self.version_desc, self.version_status,
                                                                       self.current_stage)

    # entity mappers
    def to_meta_entity(self):
        return ModelVersionDetail(self.model_name, self.model_version,
                                  self.model_path, self.model_type, self.version_desc,
                                  self.version_status, self.current_stage)


class SqlEvent(base):
    """
    SQL model of event in Notification Service backend storage.
    """
    __tablename__ = 'event'

    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key = Column(String(1024), nullable=False)
    version = Column(Integer, nullable=False)
    value = Column(String(1024))
    event_type = Column(String(256))
    create_time = Column(BigInteger)

    def __repr__(self):
        return '<SqlEvent ({}, {}, {}, {}, {} {})>'.format(self.id, self.key, self.value, self.version,
                                                           self.event_type, self.create_time)

    # entity mappers
    def to_event(self):
        return BaseEvent(self.key, self.value, self.event_type, self.version, self.create_time, self.id)


class SqlMetricMeta(base, Base):
    """
    SQL model of metric meta
    """
    __tablename__ = 'metric_meta'

    metric_name = Column(String(256), unique=True, nullable=False)
    metric_type = Column(String(256), default=MetricType.DATASET.value)
    metric_desc = Column(String(4096))
    project_name = Column(String(256), nullable=False)
    dataset_name = Column(String(256))
    model_name = Column(String(256))
    job_name = Column(String(256))
    start_time = Column(BigInteger)
    end_time = Column(BigInteger)
    uri = Column(String(1024))
    tags = Column(String(256))
    properties = Column(String(1024))
    is_deleted = Column(String(128), default='False')

    def __repr__(self):
        return '<SqlMetricMeta ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})>' \
            .format(self.uuid, self.metric_name, self.metric_type, self.metric_desc, self.project_name,
                    self.dataset_name, self.model_name, self.start_time, self.end_time, self.uri, self.tags,
                    self.properties)


class SqlMetricSummary(base, Base):
    """
    SQL model of metric summary
    """
    __tablename__ = 'metric_summary'

    metric_name = Column(String(256), ForeignKey('metric_meta.metric_name', onupdate='cascade'), nullable=False)
    metric_key = Column(String(256), nullable=False)
    metric_value = Column(String(2048), nullable=False)
    metric_timestamp = Column(BigInteger, nullable=False)
    model_version = Column(String(256))
    job_execution_id = Column(String(256))
    is_deleted = Column(String(128), default='False')

    metric_summary = relationship("SqlMetricMeta", backref=backref('metric_summary', cascade='all'))

    def __repr__(self):
        return '<SqlMetricSummary ({}, {}, {}, {}, {}, {}, {})>'.format(self.uuid, self.metric_name, self.metric_key,
                                                                        self.metric_value, self.metric_timestamp,
                                                                        self.model_version, self.job_execution_id)


class SqlMember(base):
    """
    SQL model of cluster member.
    """
    __tablename__ = 'aiflow_member'
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    version = Column(BigInteger(), nullable=False)
    server_uri = Column(String(767), nullable=False, unique=True)
    update_time = Column(BigInteger(), nullable=False)
    uuid = Column(String(128), nullable=False, unique=True)

    def __repr__(self):
        return '<SqlMember ({}, {}, {}, {}, {})>'.format(
            self.id, self.version, self.server_uri, self.update_time, self.uuid)


class MongoDataset(Document):
    """
    Document of dataset in metadata backend storage.
    """

    uuid = SequenceField(db_alias=MONGO_DB_ALIAS_META_SERVICE)
    name = StringField(max_length=255, required=True, unique=True)
    format = StringField(max_length=256)
    description = StringField(max_length=1000)
    uri = StringField(max_length=1000)
    create_time = LongField()
    update_time = LongField()
    properties = StringField(max_length=1000)
    name_list = StringField(max_length=1000)
    type_list = StringField(max_length=1000)
    catalog_name = StringField(max_length=1000)
    catalog_type = StringField(max_length=1000)
    catalog_database = StringField(max_length=1000)
    catalog_connection_uri = StringField(max_length=1000)
    catalog_table = StringField(max_length=1000)
    is_deleted = BooleanField(default=False)

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __repr__(self):
        return '<Document dataset ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})>'.format(
            self.uuid,
            self.name,
            self.properties,
            self.name_list,
            self.type_list,
            self.format,
            self.uri,
            self.catalog_name,
            self.catalog_type,
            self.catalog_database,
            self.catalog_table)


class MongoModelVersionRelation(Document):
    """
    Document of model version relation in metadata backend storage.
    """

    version = StringField(max_length=255, required=True, unique=True)
    model_id = IntField()
    project_snapshot_id = IntField()
    version_model_id_unique = StringField(max_length=1000, required=True, unique=True)
    is_deleted = BooleanField(default=False)

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __init__(self, *args, **kwargs):
        version = kwargs['version']
        model_id = kwargs['model_id']
        kwargs['version_model_id_unique'] = f'{version}-{model_id}'
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<Document ModelVersionRelation ({}, {}, {})>'.format(
            self.version,
            self.model_id,
            self.project_snapshot_id)


class MongoModelRelation(Document):
    """
    Document of model relation in metadata backend storage.
    """

    uuid = SequenceField(db_alias=MONGO_DB_ALIAS_META_SERVICE)
    name = StringField(max_length=255, required=True, unique=True)
    project_id = IntField()
    is_deleted = BooleanField(default=False)

    model_version_relation = ListField(ReferenceField(MongoModelVersionRelation))

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}
    
    def __repr__(self):
        return '<Document ModelRelation ({}, {}, {})>'.format(
            self.uuid,
            self.name,
            self.project_id)


class MongoProject(Document):
    """
    Document of project in metadata backend storage.
    """
    
    uuid = SequenceField(db_alias=MONGO_DB_ALIAS_META_SERVICE)
    name = StringField(max_length=255, required=True, unique=True)
    properties = StringField(max_length=1000)
    uri = StringField(max_length=1000)
    is_deleted = BooleanField(default=False)

    model_relation = ListField(ReferenceField(MongoModelRelation))

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __repr__(self):
        return '<Document Project ({}, {}, {}, {})>'.format(
            self.uuid,
            self.name,
            self.properties,
            self.uri)


class MongoProjectSnapshot(Document):
    """
    Document of project snapshot in metadata backend storage
    """

    uuid = SequenceField(db_alias=MONGO_DB_ALIAS_META_SERVICE)
    project_id = IntField()
    signature = StringField(max_length=255)
    create_time = LongField()

    model_version_relation = ListField(ReferenceField(MongoModelVersionRelation))

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __repr__(self):
        return '<Document ProjectSnapshot ({}, {}, {}, {})>'.format(
            self.uuid,
            self.project_id,
            self.signature,
            self.create_time)


class MongoWorkflow(Document):
    """
    Document of workflow in metadata backend storage.
    """

    uuid = SequenceField(db_alias=MONGO_DB_ALIAS_META_SERVICE)
    name = StringField(max_length=255, required=True, unique=True)
    project_id = IntField()
    properties = StringField(max_length=1000)
    create_time = Column(BigInteger)
    update_time = Column(BigInteger)
    is_deleted = BooleanField(default=False)

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __repr__(self):
        return '<Document Workflow ({}, {}, {}, {}, {}, {}, {})>'.format(
            self.uuid,
            self.name,
            self.project_id,
            self.properties,
            self.create_time,
            self.update_time,
            self.is_deleted)


class MongoModelVersion(Document):
    """
    Document of model version in Model Center backend storage.
    """

    model_name = StringField(max_length=255, required=True)
    model_version = StringField(max_length=10, required=True)
    model_path = StringField(max_length=500, default=None)
    model_type = StringField(max_length=500, default=None)
    version_desc = StringField(max_length=1000)
    version_status = StringField(max_length=20,
                                 default=ModelVersionStatus.to_string(ModelVersionStatus.READY))
    current_stage = StringField(max_length=20, default=STAGE_GENERATED)
    name_version_current_stage_unique = StringField(max_length=1000, required=True, unique=True)

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __init__(self, *args, **kwargs):
        n = kwargs['model_name']
        v = kwargs['model_version']
        c = kwargs['current_stage']
        name_version_current_stage = f'{n}-{v}-{c}'
        kwargs['name_version_current_stage_unique'] = name_version_current_stage
        super().__init__(*args, **kwargs)
    
    def __repr__(self):
        return '<Document ModelVersion ({}, {}, {}, {}, {}, {}, {}, {})>'.format(
            self.model_name,
            self.model_version,
            self.model_path,
            self.model_type,
            self.version_desc,
            self.version_status,
            self.current_stage)

    def to_meta_entity(self):
        return ModelVersionDetail(self.model_name,
                                  self.model_version,
                                  self.model_path,
                                  self.model_type,
                                  self.version_desc,
                                  self.version_status,
                                  self.current_stage)


class MongoRegisteredModel(Document):
    """
    Document of registered model in Model Center backend storage.
    """

    model_name = StringField(max_length=255, required=True, unique=True)
    model_desc = StringField(max_length=1000)

    model_version = ListField(ReferenceField(MongoModelVersion))

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __repr__(self):
        return '<Document RegisteredModel ({}, {}, {})>'.format(
            self.model_name,
            self.model_desc)

    def to_meta_entity(self):
        return RegisteredModelDetail(self.model_name, self.model_desc)

    def to_detail_entity(self):
        latest_version = None
        for model_version in reversed(self.model_version):
            if model_version.current_stage != STAGE_DELETED:
                latest_version = model_version.to_meta_entity()
                break
        return RegisteredModelDetail(self.model_name, self.model_desc, latest_version)


class MongoArtifact(Document):
    """
    Document of artifact in metadata backend storage.
    """

    uuid = SequenceField(db_alias=MONGO_DB_ALIAS_META_SERVICE)
    name = StringField(max_length=255, required=True, unique=True)
    artifact_type = StringField(max_length=256)
    description = StringField(max_length=1000)
    uri = StringField(max_length=1000)
    create_time = LongField()
    update_time = LongField()
    properties = StringField(max_length=1000)
    is_deleted = BooleanField(default=False)

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __repr__(self):
        return '<Document Artifact ({}, {}, {}, {}, {}, {}, {}, {}, {})>'.format(
            self.pk,
            self.name,
            self.artifact_type,
            self.description,
            self.uri,
            self.create_time,
            self.update_time,
            self.properties,
            self.is_deleted)


class MongoMetricMeta(Document):
    """
    Document of metric meta
    """

    uuid = SequenceField(db_alias=MONGO_DB_ALIAS_META_SERVICE)
    metric_name = StringField(max_length=256, required=True, unique=True)
    metric_type = StringField(max_length=256, default=MetricType.DATASET.value)
    metric_desc = StringField(max_length=4096)
    project_name = StringField(max_length=256, required=True)
    dataset_name = StringField(max_length=256)
    model_name = StringField(max_length=256)
    job_name = StringField(max_length=256)
    start_time = LongField()
    end_time = LongField()
    uri = StringField(max_length=1024)
    tags = StringField(max_length=256)
    properties = StringField(max_length=1024)
    is_deleted = BooleanField(default=False)

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __repr__(self):
        return '<Document MetricMeta ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})>' \
            .format(self.uuid, self.metric_name, self.metric_type, self.metric_desc, self.project_name,
                    self.dataset_name, self.model_name, self.start_time, self.end_time, self.uri, self.tags,
                    self.properties)


class MongoMetricSummary(Document):
    """
    Document of metric summary
    """

    uuid = SequenceField(db_alias=MONGO_DB_ALIAS_META_SERVICE)
    metric_name = StringField(max_length=256, required=True)
    metric_key = StringField(max_length=256, required=True)
    metric_value = StringField(max_length=2048, required=True)
    metric_timestamp = LongField()
    model_version = StringField(max_length=256)
    job_execution_id = StringField(max_length=256)
    is_deleted = BooleanField(default=False)

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __repr__(self):
        return '<Document MetricSummary ({}, {}, {})>'.format(self.uuid, self.metric_name, self.metric_key,
                                                                        self.metric_value, self.metric_timestamp,
                                                                        self.model_version, self.job_execution_id)


class MongoMember(Document):
    """
    Document of cluster member.
    """

    version = LongField(required=True)
    server_uri = StringField(max_length=767, required=True, unique=True)
    update_time = LongField(required=True)
    uuid = StringField(max_length=128, required=True, unique=True)

    meta = {'db_alias': MONGO_DB_ALIAS_META_SERVICE}

    def __repr__(self):
        return '<Document Member ({}, {}, {}, {}, {})>'.format(
            self.id, self.version, self.server_uri, self.update_time, self.uuid)
