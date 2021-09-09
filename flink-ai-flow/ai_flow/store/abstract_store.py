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
from abc import abstractmethod, ABCMeta
from typing import Text, Union, List, Optional, Any, Tuple

import cloudpickle

from ai_flow.api.context_extractor import BroadcastAllContextExtractor
from ai_flow.endpoint.server.high_availability import Member
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.metric_meta import MetricMeta, MetricSummary
from ai_flow.scheduler_service.service.workflow_execution_event_handler_state import WorkflowContextEventHandlerState

BROADCAST_ALL_CONTEXT_EXTRACTOR = cloudpickle.dumps(BroadcastAllContextExtractor())


class BaseFilter(object):
    column_name = None

    def __init__(self, column_name):
        self.column_name = column_name

    def apply(self, criterion, query, value):
        raise NotImplementedError


class Filters(object):
    filters: List[Tuple[BaseFilter, Any]] = None

    def __init__(self, filters: List[Tuple[BaseFilter, Any]] = None):
        self.filters = filters if filters else []

    def add_filter(self, f: Tuple[BaseFilter, Any]):
        self.filters.append(f)

    def apply_all(self, criterion, query):
        for flt, value in self.filters:
            query = flt.apply(criterion, query, value)
        return query

    def __repr__(self):
        ret_str = 'Filters:'
        for flt, value in self.filters:
            ret_str = ret_str + '%s:%s\n' % (
                str(flt.column_name),
                str(value),
            )
        return ret_str


class AbstractStore(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    '''
        model api
    '''

    @abstractmethod
    def get_model_relation_by_id(self, model_id):
        """
        get a specific model relation in metadata store by model id.

        :param model_id: the model id
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` object if the model relation
                 exists, Otherwise, returns None if the model relation does not exist.
        """
        pass

    @abstractmethod
    def get_model_relation_by_name(self, model_name):
        """
        get a specific model relation in metadata store by model name.

        :param model_name: the model name
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` object if the model relation
                 exists, Otherwise, returns None if the model relation does not exist.
        """
        pass

    @abstractmethod
    def list_model_relation(self, page_size, offset):
        """
        List registered model relations in metadata store.

        :param page_size: the limitation of the listed model relations.
        :param offset: the offset of listed model relations.
        :return: List of :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` objects,
                 return None if no model relations to be listed.
        """
        pass

    @abstractmethod
    def register_model_relation(self, name: Text,
                                project_id: int):
        """
        register a model relation in metadata store

        :param name: the name of the model
        :param project_id: the project id which the model corresponded to.
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` object.
        """
        pass

    def delete_model_relation_by_id(self, model_id):
        """
        Delete the registered model by model id .

        :param model_id: the model id
        :return: Status.OK if the model is successfully deleted, Status.ERROR if the model does not exist otherwise.
        """
        pass

    def delete_model_relation_by_name(self, model_name):
        """
        Delete the registered model by model name .

        :param model_name: the model name
        :return: Status.OK if the model is successfully deleted, Status.ERROR if the model does not exist otherwise.
        """
        pass

    '''
        model version api
    '''

    @abstractmethod
    def get_model_version_relation_by_version(self, version_name, model_id):
        """
        get a specific model version relation in metadata store by the model version name.

        :param version_name: the model version name
        :param model_id: the model id corresponded to the model version
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelVersionRelationMeta` object
                 if the model version exists, Otherwise, returns None if the model version does not exist.
        """
        pass

    @abstractmethod
    def register_model_version_relation(self, version, model_id, project_snapshot_id):
        """
        register a model version relation in metadata store.

        :param version: the specific model version
        :param model_id: the model id corresponded to the model version
        :param project_snapshot_id: the project snapshot id corresponded to the model version
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelVersionRelationMeta` object.
        """
        pass

    @abstractmethod
    def list_model_version_relation(self, model_id, page_size, offset):
        """
        List registered model version relations in metadata store.

        :param model_id: the model id corresponded to the model version
        :param page_size: the limitation of the listed model version relations.
        :param offset: the offset of listed model version relations.
        :return: List of :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` objects,
                 return None if no model version relations to be listed.
        """
        pass

    @abstractmethod
    def delete_model_version_relation_by_version(self, version, model_id):
        """
        Delete the registered model version by model version name .

        :param version: the model version name
        :param model_id: the model id corresponded to the model version
        :return: Status.OK if the model version is successfully deleted,
                 Status.ERROR if the model version does not exist otherwise.
        """
        pass

    '''
        dataset api
    '''

    @abstractmethod
    def get_dataset_by_id(self, dataset_id):
        """
        get a specific dataset in metadata store by dataset id.

        :param dataset_id: the dataset id
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object if the dataset exists,
                 Otherwise, returns None if the dataset does not exist.
        """
        pass

    @abstractmethod
    def get_dataset_by_name(self, dataset_name):
        """
        get a specific dataset in metadata store by dataset name.

        :param dataset_name: the dataset name
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object if the dataset exists,,
                 Otherwise, returns None if the dataset does not exist.
        """
        pass

    @abstractmethod
    def list_datasets(self, page_size=None, offset=None, filters: Filters = None):
        """
        List registered datasets in metadata store.

        :param page_size: The limitation of the listed datasets.
        :param offset: The offset of listed datasets.
        :param filters: A Filter class that contains all filters to apply.
        :return: List of :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` objects,
                 return None if no datasets to be listed.
        """
        pass

    @abstractmethod
    def register_dataset(self, name, data_format,
                         description, uri,
                         properties,
                         name_list, type_list):
        """
        register an dataset in metadata store.

        :param name: the name of the dataset
        :param data_format: the data_format of the dataset
        :param description: the description of the dataset
        :param uri: the uri of the dataset
        :param properties: the properties of the dataset
        :param name_list: the name list of dataset's schema
        :param type_list: the type list corresponded to the name list of dataset's schema
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object.
        """
        pass

    def delete_dataset_by_id(self, dataset_id):
        """
        Delete the registered dataset by dataset id .

        :param dataset_id: the dataset id
        :return: Status.OK if the dataset is successfully deleted, Status.ERROR if the dataset does not exist otherwise.
        """
        pass

    def delete_dataset_by_name(self, dataset_name):
        """
        Delete the registered dataset by dataset name .

        :param dataset_name: the dataset name
        :return: Status.OK if the dataset is successfully deleted, Status.ERROR if the dataset does not exist otherwise.
        """
        pass

    '''
        project api
    '''

    @abstractmethod
    def get_project_by_id(self, project_id):
        """
        get a specific project in metadata store by project id

        :param project_id: the project id
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object if the project exists,
                 Otherwise, returns None if the project does not exist.
        """
        pass

    @abstractmethod
    def get_project_by_name(self, project_name):
        """
        get a specific project in metadata store by project name
        :param project_name: the project name
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object if the project exists,
                 Otherwise, returns None if the project does not exist.
        """
        pass

    @abstractmethod
    def register_project(self, name, uri, properties):
        """
        register a project in metadata store.

        :param name: the name of the project
        :param uri: the uri of the project
        :param properties: the properties of the project
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object.
        """
        pass

    @abstractmethod
    def list_projects(self, page_size=None, offset=None, filters: Filters = None):
        """
        List registered projects in metadata store.

        :param page_size: The limitation of the listed projects.
        :param offset: The offset of listed projects.
        :param filters: A Filter class that contains all filters to apply.
        :return: List of :py:class:`ai_flow.meta.project_meta.ProjectMeta` objects,
                 return None if no projects to be listed.
        """
        pass

    @abstractmethod
    def delete_project_by_id(self, project_id):
        """
        Delete the registered project by project id .

        :param project_id: the project id
        :return: Status.OK if the project is successfully deleted, Status.ERROR if the project does not exist otherwise.
        """
        pass

    def delete_project_by_name(self, project_name):
        """
        Delete the registered project by project name .

        :param project_name: the project name
        :return: Status.OK if the project is successfully deleted, Status.ERROR if the project does not exist otherwise.
        """
        pass

    def update_project(self, project_name, uri, properties=None):
        """
        Update a project in metadata store.

        :param project_name: the name of the project
        :param uri: the uri of the project
        :param properties: the properties of the project
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object.
        """
        pass

    '''
        workflow api
    '''

    def register_workflow(self, name, project_id, context_extractor_in_bytes: bytes = BROADCAST_ALL_CONTEXT_EXTRACTOR,
                          properties=None):
        """
        Register a workflow in metadata store.

        :param name: the workflow name
        :param project_id: the id of project which contains the workflow:
        :param context_extractor_in_bytes: serialized context extractor in bytes
        :param properties: the workflow properties
        """
        pass

    def get_workflow_by_name(self, project_name, workflow_name):
        """
        Get a workflow by specific project name and workflow name

        :param project_name: the name of project which contains the workflow
        :param workflow_name: the workflow name
        """
        pass

    def get_workflow_by_id(self, workflow_id):
        """
        Get a workflow by specific uuid

        :param workflow_id: the uuid of workflow
        """
        pass

    def list_workflows(self, project_name=None, page_size=None, offset=None, filters: Filters = None):
        """
        List registered workflows in metadata store.

        :param project_name: The name of project which contains the workflow.
        :param page_size: The limitation of the listed workflows.
        :param offset: The offset of listed workflows.
        :param filters: A Filter class that contains all filters to apply.
        :return: List of :py:class:`ai_flow.meta.workflow_meta.WorkflowMeta` objects,
                 return None if no workflows to be listed.
        """
        pass

    def delete_workflow_by_name(self, project_name, workflow_name):
        """
        Delete the workflow by specific project and workflow name

        :param project_name: the name of project which contains the workflow
        :param workflow_name: the workflow name
        """
        pass

    def delete_workflow_by_id(self, workflow_id):
        """
        Delete the workflow by specific id

        :param workflow_id: the uuid of workflow
        """
        pass

    def update_workflow(self, workflow_name, project_name, context_extractor_in_bytes, scheduling_rules,
                        properties=None):
        """
        Update the workflow

        :param workflow_name: the workflow name
        :param project_name: the name of project which contains the workflow
        :param context_extractor_in_bytes: the serialized context extractor in bytes
        :param scheduling_rules: the scheduling rules of the workflow
        :param properties: (Optional) the properties need to be updated
        """
        pass

    '''
    workflow context event handler state api
    '''

    def register_workflow_context_event_handler_state(self,
                                                      project_name: Text,
                                                      workflow_name: Text,
                                                      context: Text,
                                                      workflow_execution_id=None,
                                                      state=None) -> WorkflowContextEventHandlerState:
        """
        Register a new workflow context event handler state

        :param project_name: the project name.
        :param workflow_name: the workflow name.
        :param context: context of the state belongs to.
        :param workflow_execution_id: the id of workflow execution under the context.
        :param state: the event handler state.
        """
        pass

    def list_workflow_context_event_handler_states(self, project_name: Text,
                                                   workflow_name: Text) -> List[WorkflowContextEventHandlerState]:
        """
        List all the workflow context event handler state for the workflow.
        :param project_name: the project name.
        :param workflow_name: the workflow name.
        """
        pass

    def get_workflow_context_event_handler_state(self,
                                                 project_name: Text,
                                                 workflow_name: Text,
                                                 context: Text) -> Optional[WorkflowContextEventHandlerState]:
        """
        Get the workflow context event handler state belongs to the given context.

        :param project_name: the project name.
        :param workflow_name: the workflow name.
        :param context:
        """
        pass

    def update_workflow_context_event_handler_state(self,
                                                    project_name: Text,
                                                    workflow_name: Text,
                                                    context: Text,
                                                    workflow_execution_id=None,
                                                    state=None) -> Optional[WorkflowContextEventHandlerState]:
        """
        Update the workflow context event handler state belongs to the given context.

        :param project_name: the project name.
        :param workflow_name: the workflow name.
        :param context: context of the state belongs to.
        :param workflow_execution_id: the id of workflow execution under the context.
        :param state: the event handler state.
        """
        pass

    '''
        artifact api
    '''

    def get_artifact_by_id(self, artifact_id):
        """
        get a specific artifact in metadata store by artifact id.

        :param artifact_id: the artifact id
        :return: A single :py:class:`ai_flow.meta.artifact_meta.ArtifactMeta` object
                 if the artifact exists, Otherwise, returns None if the artifact does not exist.
        """

    def get_artifact_by_name(self, artifact_name):
        """
        get a specific artifact in metadata store by artifact name.

        :param artifact_name: the artifact name
        :return: A single :py:class:`ai_flow.meta.artifact_meta.ArtifactMeta` object
                 if the artifact exists, Otherwise, returns None if the artifact does not exist.
        """

    def register_artifact(self, name: Text, artifact_type, description,
                          uri, properties):
        """
        register an artifact in metadata store.

        :param name: the name of the artifact
        :param artifact_type: the type of the artifact
        :param description: the description of the artifact
        :param uri: the uri of the artifact
        :param properties: the properties of the artifact
        :return: A single :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` object.
        """

    def update_artifact(self, name: Text, artifact_type: Text, description: Text,
                        uri, properties) -> Optional[ArtifactMeta]:
        """
        Update an artifact in metadata store.

        :param name: the name of the artifact
        :param artifact_type: the type of the artifact
        :param description: the description of the artifact
        :param uri: the uri of the artifact
        :param properties: the properties of the artifact
        :return: A single :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` object.
        """

    def list_artifacts(self, page_size=None, offset=None, filters: Filters = None):
        """
        List registered artifacts in metadata store.

        :param page_size: The limitation of the listed artifacts.
        :param offset: The offset of listed artifacts.
        :param filters: A Filter class that contains all filters to apply.
        :return: List of :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` objects,
                 return None if no artifacts to be listed.
        """

    def delete_artifact_by_id(self, artifact_id):
        """
        Delete the registered artifact by artifact id .

        :param artifact_id: the artifact id
        :return: Status.OK if the artifact is successfully deleted,
                 Status.ERROR if the artifact does not exist otherwise.
        """

    def delete_artifact_by_name(self, artifact_name):
        """
        Delete the registered artifact by artifact name .

        :param artifact_name: the artifact name
        :return: Status.OK if the artifact is successfully deleted,
                 Status.ERROR if the artifact does not exist otherwise.
        """

    @abstractmethod
    def create_registered_model(self, model_name, model_desc=None):
        """
        Create a new registered model in model repository.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.
        :param model_desc: (Optional) Description of registered model.

        :return: A single object of :py:class:`ai_flow.model_center.entity.RegisteredModel` created in model
        repository.
        """
        pass

    @abstractmethod
    def update_registered_model(self, registered_model, model_name=None, model_desc=None):
        """
        Update metadata for RegisteredModel entity. Either ``model_name`` or ``model_desc``
        should be non-None. Backend raises exception if a registered model with given name does not exist.

        :param registered_model: :py:class:`ai_flow.model_center.entity.RegisteredModel` object.
        :param model_name: (Optional) New proposed name for the registered model.
        :param model_desc: (Optional) Description of registered model.

        :return: A single updated :py:class:`ai_flow.model_center.entity.RegisteredModel` object.
        """
        pass

    @abstractmethod
    def delete_registered_model(self, registered_model):
        """
        Delete registered model.
        Backend raises exception if a registered model with given name does not exist.

        :param registered_model: :py:class:`ai_flow.model_center.entity.RegisteredModel` object.

        :return: None
        """
        pass

    @abstractmethod
    def list_registered_models(self, page_size=None, offset=None, filters: Filters = None):
        """
        List of all registered models in model repository.

        :param page_size: The limitation of the listed models.
        :param offset: The offset of listed models.
        :param filters: A Filter class that contains all filters to apply.
        :return: List of :py:class:`ai_flow.model_center.entity.RegisteredModel` objects,
                 return None if no models to be listed.
        """
        pass

    @abstractmethod
    def get_registered_model_detail(self, registered_model):
        """
        :param registered_model: :py:class:`ai_flow.model_center.entity.RegisteredModel` object.

        :return: A single :py:class:`ai_flow.model_center.entity.RegisteredModelDetail` object.
        """
        pass

    @abstractmethod
    def create_model_version(self, model_name, model_version, model_path,
                             model_type=None, version_desc=None):
        """
        Create a new model version from given model source and model metric.

        :param model_name: Name for containing registered model.
        :param model_version: User-defined version of registered model.
        :param model_path: Source path where the AIFlow model is stored.
        :param model_type: (Optional) Type of AIFlow model option.
        :param version_desc: (Optional) Description of registered model version.

        :return: A single object of :py:class:`ai_flow.model_center.entity.ModelVersion`
        created in model repository.
        """
        pass

    @abstractmethod
    def update_model_version(self, model_version, model_path=None, model_type=None,
                             version_desc=None, version_stage=None):
        """
        Update metadata associated with a model version in model repository.

        :param model_version: :py:class:`ai_flow.model_center.entity.ModelVersion` object.
        :param model_path: (Optional) New Source path where AIFlow model is stored.
        :param model_type: (Optional) Type of AIFlow registered model option.
        :param version_desc: (Optional) New Description of registered model version.
        :param version_stage: (Optional) New desired stage for this model version.

        :return: A single updated :py:class:`ai_flow.model_center.entity.ModelVersion` object.
        """
        pass

    @abstractmethod
    def delete_model_version(self, model_version):
        """
        Delete model version in model repository.

        :param model_version: :py:class:`ai_flow.model_center.entity.ModelVersion` object.

        :return: None
        """
        pass

    @abstractmethod
    def list_model_versions(self, page_size=None, offset=None, filters: Filters = None):
        """
        List of all model versions in model repository.

        :param page_size: The limitation of the listed model versions.
        :param offset: The offset of listed model versions.
        :param filters: A Filter class that contains all filters to apply.
        :return: List of :py:class:`ai_flow.model_center.entity.ModelVersionDetail` objects,
                 return None if no model versions to be listed.
        """
        pass

    @abstractmethod
    def get_model_version_detail(self, model_version):
        """
        :param model_version: :py:class:`ai_flow.model_center.entity.ModelVersion` object.

        :return: A single :py:class:`ai_flow.model_center.entity.ModelVersionDetail` object.
        """
        pass

    @abstractmethod
    def register_metric_meta(self, metric_name, metric_type, project_name, metric_desc=None, dataset_name=None,
                             model_name=None, job_name=None, start_time=None, end_time=None, uri=None, tags=None,
                             properties=None) -> MetricMeta:
        pass

    @abstractmethod
    def update_metric_meta(self, metric_name, metric_desc=None, project_name=None, dataset_name=None,
                           model_name=None, job_name=None, start_time=None, end_time=None, uri=None, tags=None,
                           properties=None) -> MetricMeta:
        pass

    @abstractmethod
    def delete_metric_meta(self, metric_name):
        pass

    @abstractmethod
    def get_metric_meta(self, metric_name) -> Union[None, MetricMeta]:
        pass

    @abstractmethod
    def list_dataset_metric_metas(self, dataset_name, project_name=None) -> Union[None, MetricMeta, List[MetricMeta]]:
        pass

    @abstractmethod
    def list_model_metric_metas(self, model_name, project_name=None) -> Union[None, MetricMeta, List[MetricMeta]]:
        pass

    @abstractmethod
    def register_metric_summary(self, metric_name, metric_key, metric_value, metric_timestamp, model_version=None,
                                job_execution_id=None) -> MetricSummary:
        pass

    @abstractmethod
    def update_metric_summary(self, uuid, metric_name=None, metric_key=None, metric_value=None, metric_timestamp=None,
                              model_version=None, job_execution_id=None) -> MetricSummary:
        pass

    @abstractmethod
    def delete_metric_summary(self, uuid: int):
        pass

    @abstractmethod
    def get_metric_summary(self, uuid) -> Union[None, MetricSummary]:
        pass

    @abstractmethod
    def list_metric_summaries(self, metric_name=None, metric_key=None, model_version=None, start_time=None,
                              end_time=None) -> Union[None, MetricSummary, List[MetricSummary]]:
        pass

    """For high availability:"""

    @abstractmethod
    def list_living_members(self, ttl_ms) -> List['Member']:
        pass

    @abstractmethod
    def update_member(self, server_uri, server_uuid):
        pass

    @abstractmethod
    def clear_dead_members(self, ttl_ms):
        pass
