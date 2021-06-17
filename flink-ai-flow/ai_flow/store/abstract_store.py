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

from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.endpoint.server.high_availability import Member
from typing import Text, Union, List, Optional

from ai_flow.meta.metric_meta import MetricMeta, MetricSummary


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
    def register_model_version_relation(self, version, model_id,
                                        workflow_execution_id):
        """
        register a model version relation in metadata store.

        :param version: the specific model version
        :param model_id: the model id corresponded to the model version
        :param workflow_execution_id: the workflow execution id corresponded to the model version
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
    def list_datasets(self, page_size, offset):
        """
        List registered datasets in metadata store.

        :param page_size: the limitation of the listed datasets.
        :param offset: the offset of listed datasets.
        :return: List of :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` objects,
                 return None if no datasets to be listed.
        """
        pass

    @abstractmethod
    def register_dataset(self, name, data_format,
                         description, uri,
                         create_time, update_time, properties,
                         name_list, type_list):
        """
        register an dataset in metadata store.

        :param name: the name of the dataset
        :param data_format: the data_format of the dataset
        :param description: the description of the dataset
        :param uri: the uri of the dataset
        :param create_time: the time when the dataset is created
        :param update_time: the time when the dataset is updated
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
    def list_project(self, page_size, offset):
        """
        List registered projects in metadata store.

        :param page_size: the limitation of the listed projects.
        :param offset: the offset of listed projects.
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

    '''
        job api
    '''

    @abstractmethod
    def get_job_by_id(self, job_id):
        """
        get a specific job in metadata store by job id.

        :param job_id: the job id
        :return: A single :py:class:`ai_flow.meta.job_meta.JobMeta` object
                 if the job exists, Otherwise, returns None if the job does not exist.
        """
        pass

    @abstractmethod
    def get_job_by_name(self, job_name):
        """
        get a specific job in metadata store by job name.

        :param job_name: the job name
        :return: A single :py:class:`ai_flow.meta.job_meta.JobMeta` object
                 if the job exists, Otherwise, returns None if the job does not exist.
        """
        pass

    @abstractmethod
    def register_job(self, name: Text, job_state, workflow_execution_id,
                     properties, job_id, start_time, end_time,
                     log_uri, signature):
        """
        register a job in metadata store.

        :param name: the name of the job
        :param job_state: the state of the job
        :param workflow_execution_id: the workflow execution id corresponded to the job
        :param properties: the properties of the job
        :param job_id: the job_id of the job
        :param start_time: the time when the job started
        :param end_time: the time when the job ended
        :param log_uri: the log uri of the job
        :param signature: the signature of the job
        :return: A single :py:class:`ai_flow.meta.job_meta.JobMeta` object.
        """
        pass

    @abstractmethod
    def list_job(self, page_size, offset):
        """
        List registered jobs in metadata store.

        :param page_size: the limitation of the listed jobs.
        :param offset: the offset of listed jobs.
        :return: List of :py:class:`ai_flow.meta.job_meta.JobMeta` objects,
                 return None if no jobs to be listed.
        """
        pass

    @abstractmethod
    def update_job_state(self, state, job_id):
        """
        update the job state in metadata store.

        :param state: the state of the job.
        :param job_id: the job id
        :return: the job uuid if the job is successfully updated, raise an exception if fail to update otherwise.
        """
        pass

    def update_job_end_time(self, end_time, job_name):
        """
        update the job end time in metadata store.

        :param end_time: the time when the job ended.
        :param job_name: the job name
        :return: the job uuid if the job is successfully updated, raise an exception if fail to update otherwise.
        """
        pass

    '''
        workflow execution api
    '''

    @abstractmethod
    def get_workflow_execution_by_id(self, execution_id):
        """
        get a specific workflow execution in metadata store by workflow execution id.

        :param execution_id: the workflow execution id
        :return: A single :py:class:`ai_flow.meta.workflow_execution_meta.WorkflowExecutionMeta` object
                 if the workflow execution exists, Otherwise, returns None if the workflow execution does not exist.
        """
        pass

    @abstractmethod
    def get_workflow_execution_by_name(self, execution_name):
        """
        get a specific workflow execution in metadata store by workflow execution name.

        :param execution_name: the workflow execution name
        :return: A single :py:class:`ai_flow.meta.workflow_execution_meta.WorkflowExecutionMeta` object
                 if the workflow execution exists, Otherwise, returns None if the workflow execution does not exist.
        """
        pass

    @abstractmethod
    def register_workflow_execution(self, name: Text,
                                    execution_state, project_id,
                                    properties, start_time,
                                    end_time, log_uri,
                                    workflow_json, signature):
        """
        register a workflow execution in metadata store.

        :param name: the name of the workflow execution
        :param execution_state: the execution state of the workflow execution
        :param project_id: the project id corresponded to the workflow execution
        :param properties: the properties of the workflow execution
        :param start_time: the time when the workflow execution started
        :param end_time: the time when the workflow execution ended
        :param log_uri: the log uri of the workflow execution
        :param workflow_json: the workflow json of the workflow execution
        :param signature: the signature of the workflow execution
        :return: A single :py:class:`ai_flow.meta.workflow_execution_meta.WorkflowExecutionMeta` object.
        """
        pass

    @abstractmethod
    def list_workflow_execution(self, page_size, offset):
        """
        List registered workflow executions in metadata store.

        :param page_size: the limitation of the listed workflow executions.
        :param offset: the offset of listed workflow executions.
        :return: List of :py:class:`ai_flow.meta.workflow_execution_meta.WorkflowExecutionMeta` object,
                 return None if no workflow executions to be listed.
        """
        pass

    @abstractmethod
    def update_workflow_execution_end_time(self, end_time, execution_name):
        """
        update the workflow execution end time in metadata store.

        :param end_time: the time when the workflow execution ended.
        :param execution_name: the execution name
        :return: the workflow execution uuid if the workflow execution is successfully updated, raise an exception
                 if fail to update otherwise.
        """
        pass

    @abstractmethod
    def update_workflow_execution_state(self, state, execution_name):
        """
        update the workflow execution end time in metadata store.

        :param state: the state of the workflow execution.
        :param execution_name: the execution name
        :return: the workflow execution uuid if the workflow execution is successfully updated, raise an exception
                 if fail to update otherwise.
        """

    @abstractmethod
    def delete_workflow_execution_by_id(self, execution_id):
        """
        Delete the registered workflow execution by workflow execution id .

        :param execution_id: the workflow execution id
        :return: Status.OK if the workflow execution is successfully deleted,
                 Status.ERROR if the workflow execution does not exist otherwise.
        """
        pass

    @abstractmethod
    def delete_workflow_execution_by_name(self, execution_name):
        """
        Delete the registered workflow execution by workflow execution name .

        :param execution_name: the workflow execution name
        :return: Status.OK if the workflow execution is successfully deleted,
                 Status.ERROR if the workflow execution does not exist otherwise.
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
                          uri, create_time, update_time, properties):
        """
        register an artifact in metadata store.

        :param name: the name of the artifact
        :param artifact_type: the type of the artifact
        :param description: the description of the artifact
        :param uri: the uri of the artifact
        :param create_time: the time when the artifact is created represented as milliseconds since epoch.
        :param update_time: the time when the artifact is updated represented as milliseconds since epoch.
        :param properties: the properties of the artifact
        :return: A single :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` object.
        """

    def update_artifact(self, name: Text, artifact_type: Text, description: Text,
                        uri, update_time, properties) -> Optional[ArtifactMeta]:
        """
        Update an artifact in metadata store.

        :param name: the name of the artifact
        :param artifact_type: the type of the artifact
        :param description: the description of the artifact
        :param uri: the uri of the artifact
        :param update_time: the time when the artifact is updated represented as milliseconds since epoch.
        :param properties: the properties of the artifact
        :return: A single :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` object.
        """

    def list_artifact(self, page_size, offset):
        """
        List registered artifacts in metadata store.

        :param page_size: the limitation of the listed artifacts.
        :param offset: the offset of listed artifacts.
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
    def create_registered_model(self, model_name, model_type, model_desc=None):
        """
        Create a new registered model in model repository.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.
        :param model_type: Type of registered model.
        :param model_desc: (Optional) Description of registered model.

        :return: A single object of :py:class:`ai_flow.model_center.entity.RegisteredModel` created in model
        repository.
        """
        pass

    @abstractmethod
    def update_registered_model(self, registered_model, model_name=None, model_type=None, model_desc=None):
        """
        Update metadata for RegisteredModel entity. Either ``model_name`` or ``model_type`` or ``model_desc``
        should be non-None. Backend raises exception if a registered model with given name does not exist.

        :param registered_model: :py:class:`ai_flow.model_center.entity.RegisteredModel` object.
        :param model_name: (Optional) New proposed name for the registered model.
        :param model_type: (Optional) Type of registered model.
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
    def list_registered_models(self):
        """
        List of all registered models in model repository.

        :return: List of :py:class:`ai_flow.model_center.entity.RegisteredModel` objects.
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
    def create_model_version(self, model_name, model_version, model_path, model_metric, model_flavor=None,
                             version_desc=None):
        """
        Create a new model version from given model source and model metric.

        :param model_name: Name for containing registered model.
        :param model_version: User-defined version of registered model.
        :param model_path: Source path where the AIFlow model is stored.
        :param model_metric: Metric address from AIFlow metric server of registered model.
        :param model_flavor: (Optional) Flavor feature of AIFlow registered model option.
        :param version_desc: (Optional) Description of registered model version.

        :return: A single object of :py:class:`ai_flow.model_center.entity.ModelVersion`
        created in model repository.
        """
        pass

    @abstractmethod
    def update_model_version(self, model_version, model_path=None, model_metric=None, model_flavor=None,
                             version_desc=None, version_stage=None):
        """
        Update metadata associated with a model version in model repository.

        :param model_version: :py:class:`ai_flow.model_center.entity.ModelVersion` object.
        :param model_path: (Optional) New Source path where AIFlow model is stored.
        :param model_metric: (Optional) New Metric address AIFlow metric server of registered model provided.
        :param model_flavor: (Optional) Flavor feature of AIFlow registered model option.
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
    def get_model_version_detail(self, model_version):
        """
        :param model_version: :py:class:`ai_flow.model_center.entity.ModelVersion` object.

        :return: A single :py:class:`ai_flow.model_center.entity.ModelVersionDetail` object.
        """
        pass

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
        pass

    def delete_metric_meta(self, uuid: int):
        pass

    def register_metric_summary(self,
                                metric_id,
                                metric_key,
                                metric_value)->MetricSummary:
        """
        register metric summary
        :param metric_id: associate with metric meta uuid
        :param metric_key:
        :param metric_value:
        :return:
        """
        pass

    def delete_metric_summary(self, uuid: int):
        pass

    def update_metric_meta(self,
                           uuid,
                           dataset_id=None,
                           model_version_id=None,
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
        :param dataset_id: the dataset id of the metric or model metric associate with dataset id
        :param model_version_id: if then model metric, associate with model version id
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
        pass

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
        pass

    def get_dataset_metric_meta(self, dataset_id) -> Union[None, MetricMeta, List[MetricMeta]]:
        """
        get dataset metric
        :param dataset_id:
        :return:
        """
        pass

    def get_model_metric_meta(self, model_name, model_version) -> Union[None, MetricMeta, List[MetricMeta]]:
        """
        get model metric
        :param model_name:
        :param model_version:
        :return:
        """
        pass

    def get_metric_summary(self, metric_id) -> Optional[List[MetricSummary]]:
        """
        get metric summary
        :param metric_id:
        :return:
        """
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
