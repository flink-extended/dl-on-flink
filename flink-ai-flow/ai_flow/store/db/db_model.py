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
    Column, String, ForeignKey, Integer, PrimaryKeyConstraint, BigInteger, UniqueConstraint)
from sqlalchemy.orm import relationship, backref

from ai_flow.meta.metric_meta import MetricType
from ai_flow.model_center.entity.model_version_detail import ModelVersionDetail
from ai_flow.model_center.entity.model_version_stage import STAGE_DELETED, STAGE_GENERATED
from ai_flow.model_center.entity.model_version_status import ModelVersionStatus
from ai_flow.model_center.entity.registered_model_detail import RegisteredModelDetail
from ai_flow.store.db.base_model import base, Base


class SqlExample(base, Base):
    """
    SQL table of example in metadata backend storage.
    """
    __tablename__ = 'example'

    name = Column(String(255), unique=True, nullable=False)
    support_type = Column(String(256), nullable=False)
    data_type = Column(String(256))
    format = Column(String(256))
    description = Column(String(1000))
    batch_uri = Column(String(1000))
    stream_uri = Column(String(1000))
    create_time = Column(BigInteger)
    update_time = Column(BigInteger)
    properties = Column(String(1000))
    name_list = Column(String(1000))
    type_list = Column(String(1000))
    catalog_name = Column(String(1000))
    catalog_type = Column(String(1000))
    catalog_database = Column(String(1000))
    catalog_connection_uri = Column(String(1000))
    catalog_version = Column(String(1000))
    catalog_table = Column(String(1000))
    is_deleted = Column(String(256), default='False')

    def __repr__(self):
        return '<example ({}, {}, {}, {}, {}, {}, {}, {}, {})>'.format(self.uuid, self.name, self.properties,
                                                                       self.support_type, self.name_list,
                                                                       self.type_list,
                                                                       self.format, self.batch_uri, self.stream_uri)


class SqlProject(base, Base):
    """
    SQL table of project in metadata backend storage.
    """
    __tablename__ = 'project'

    name = Column(String(255), unique=True)
    properties = Column(String(1000))
    project_type = Column(String(1000))
    user = Column(String(1000))
    password = Column(String(1000))
    uri = Column(String(1000))
    is_deleted = Column(String(256), default='False')

    def __repr__(self):
        return '<project ({}, {}, {}, {}, {}, {}, {})>'.format(self.uuid, self.name, self.properties, self.project_type,
                                                               self.user, self.password, self.uri)


class SqlModelRelation(base, Base):
    """
    SQL table of model relation in metadata backend storage.
    """
    __tablename__ = 'model_relation'

    name = Column(String(255), unique=True)
    project_id = Column(BigInteger, ForeignKey('project.uuid', onupdate='cascade'))
    is_deleted = Column(String(256), default='False')

    model_relation = relationship("SqlProject", backref=backref('model_relation', cascade='all'))

    def __repr__(self):
        return '<model_relation ({}, {}, {})>'.format(self.uuid, self.name, self.project_id)


class SqlWorkflow(base, Base):
    """
    SQL table of workflow in metadata backend storage.
    """
    __tablename__ = 'workflow'

    uuid = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    properties = Column(String(1000))
    project_id = Column(BigInteger, ForeignKey('project.uuid'))
    is_deleted = Column(String(256), default='False')

    def __repr__(self):
        return '<workflow ({}, {}, {}, {})>'.format(self.uuid, self.name, self.properties, self.project_id)


class SqlWorkflowExecution(base, Base):
    """
    SQL table of workflow execution in metadata backend storage.
    """
    __tablename__ = 'workflow_execution'

    name = Column(String(255), unique=True, nullable=False)
    properties = Column(String(1000))
    start_time = Column(BigInteger)
    end_time = Column(BigInteger)
    execution_state = Column(String(256))
    log_uri = Column(String(1000))
    workflow_json = Column(String(1000))
    signature = Column(String(1000))
    project_id = Column(BigInteger, ForeignKey('project.uuid', onupdate='cascade'))
    is_deleted = Column(String(256), default='False')

    workflow_execution = relationship("SqlProject", backref=backref('workflow_execution', cascade='all'))

    def __repr__(self):
        return '<workflow_execution ({}, {}, {}, {}, {}, {}, {}, {}, {}, {})>'.format(self.uuid, self.name,
                                                                                      self.properties,
                                                                                      self.start_time,
                                                                                      self.end_time,
                                                                                      self.execution_state,
                                                                                      self.log_uri,
                                                                                      self.workflow_json,
                                                                                      self.signature,
                                                                                      self.project_id)


class SqlModelVersionRelation(base):
    """
    SQL table of model version relation in metadata backend storage.
    """
    __tablename__ = 'model_version_relation'

    version = Column(String(255), primary_key=True)
    model_id = Column(BigInteger, ForeignKey('model_relation.uuid', onupdate='cascade'))
    workflow_execution_id = Column(BigInteger, ForeignKey('workflow_execution.uuid', onupdate='cascade'))
    is_deleted = Column(String(256), default='False')

    UniqueConstraint(version, model_id)
    UniqueConstraint(version, workflow_execution_id)

    model_version_relations = relationship("SqlModelRelation", backref=backref('model_version_relation', cascade='all'))
    model_version_relation = relationship("SqlWorkflowExecution",
                                          backref=backref('model_version_relation', cascade='all'))

    def __repr__(self):
        return '<model_version_relation ({}, {}, {})>'.format(self.version, self.model_id,
                                                              self.workflow_execution_id)


class SqlJob(base, Base):
    """
    SQL table of job in metadata backend storage.
    """
    __tablename__ = 'job_info'

    name = Column(String(255), unique=True)
    job_id = Column(String(1000))
    properties = Column(String(1000))
    start_time = Column(BigInteger)
    end_time = Column(BigInteger)
    job_state = Column(String(256))
    log_uri = Column(String(256))
    signature = Column(String(1000))
    workflow_execution_id = Column(BigInteger, ForeignKey('workflow_execution.uuid', onupdate='cascade'))
    is_deleted = Column(String(256), default='False')

    job = relationship("SqlWorkflowExecution", backref=backref('job_info', cascade='all'))

    def __repr__(self):
        return '<SqlJob ({}, {}, {}, {}, {}, {}, {}, {}, {}, {})>'.format(self.uuid, self.job_id, self.name,
                                                                          self.properties, self.start_time,
                                                                          self.end_time,
                                                                          self.job_state, self.log_uri, self.signature,
                                                                          self.workflow_execution_id)


class SqlArtifact(base, Base):
    """
    SQL table of artifact in metadata backend storage.
    """

    __tablename__ = 'artifact'

    name = Column(String(255), unique=True, nullable=False)
    data_format = Column(String(256))
    description = Column(String(1000))
    batch_uri = Column(String(1000))
    stream_uri = Column(String(1000))
    create_time = Column(BigInteger)
    update_time = Column(BigInteger)
    properties = Column(String(1000))
    is_deleted = Column(String(256), default='False')

    def __repr__(self):
        return '<SqlArtifact ({}, {}, {}, {}, {}, {}, {}, {}, {}, {})>'.format(self.uuid, self.name, self.data_format,
                                                                               self.description, self.batch_uri,
                                                                               self.stream_uri,
                                                                               self.create_time, self.update_time,
                                                                               self.properties,
                                                                               self.is_deleted)


class SqlRegisteredModel(base):
    """
    SQL model of registered model in Model Center backend storage.
    """
    __tablename__ = 'registered_model'

    model_name = Column(String(255), unique=True, nullable=False)
    model_type = Column(String(500), nullable=True)
    model_desc = Column(String(1000), nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('model_name', name='registered_model_pk'),
    )

    def __repr__(self):
        return '<SqlRegisteredModel ({}, {}, {})>'.format(self.model_name, self.model_type, self.model_desc)

    # entity mappers
    def to_meta_entity(self):
        return RegisteredModelDetail(self.model_name, self.model_type, self.model_desc)

    def to_detail_entity(self):
        # SqlRegisteredModel has backref to all "model_version". Filter latest version of registered model.
        latest_version = None
        for model_version in reversed(self.model_version):
            if model_version.current_stage != STAGE_DELETED:
                latest_version = model_version.to_meta_entity()
                break
        return RegisteredModelDetail(self.model_name, self.model_type, self.model_desc, latest_version)


class SqlModelVersion(base):
    """
    SQL model of model version in Model Center backend storage.
    """
    __tablename__ = 'model_version'

    model_name = Column(String(255), ForeignKey('registered_model.model_name', onupdate='cascade', ondelete='cascade'))
    model_version = Column(String(10), nullable=False)
    model_path = Column(String(500), nullable=True, default=None)
    model_metric = Column(String(500), nullable=True, default=None)
    model_flavor = Column(String(500), nullable=True, default=None)
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
        return '<SqlModelVersion ({}, {}, {}, {}, {}, {}, {}, {})>'.format(self.model_name, self.model_version,
                                                                           self.model_path, self.model_metric,
                                                                           self.model_flavor, self.version_desc,
                                                                           self.version_status, self.current_stage)

    # entity mappers
    def to_meta_entity(self):
        return ModelVersionDetail(self.model_name, self.model_version,
                                  self.model_path, self.model_metric,
                                  self.model_flavor, self.version_desc,
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
    name = Column(String(255), unique=True, nullable=False)
    dataset_id = Column(BigInteger, nullable=True)
    model_name = Column(String(256), nullable=True)
    model_version = Column(String(500), nullable=True)
    job_id = Column(BigInteger, nullable=True)
    start_time = Column(BigInteger)
    end_time = Column(BigInteger)
    metric_type = Column(String(256), default=MetricType.DATASET.value)
    uri = Column(String(1000))
    tags = Column(String(256))
    metric_description = Column(String(4096))
    properties = Column(String(1000))
    is_deleted = Column(String(128), default='False')

    def __repr__(self):
        return '<SqlMetricMeta ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})>' \
            .format(self.name,
                    self.dataset_id,
                    self.model_name,
                    self.model_version,
                    self.job_id,
                    self.start_time,
                    self.end_time,
                    self.metric_type,
                    self.metric_description,
                    self.uri,
                    self.tags,
                    self.properties)


class SqlMetricSummary(base, Base):
    """
    SQL model of metric summary
    """
    __tablename__ = 'metric_summary'
    metric_id = Column(BigInteger, nullable=False)
    metric_key = Column(String(128), unique=True, nullable=False)
    metric_value = Column(String(2048), nullable=False)
    is_deleted = Column(String(128), default='False')

    def __repr__(self):
        return '<SqlMetricSummary ({}, {}, {})>'.format(self.metric_id, self.metric_key, self.metric_value)


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
