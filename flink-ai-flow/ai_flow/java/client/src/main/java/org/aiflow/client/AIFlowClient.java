/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package org.aiflow.client;

import org.aiflow.client.common.DataType;
import org.aiflow.client.common.ModelStage;
import org.aiflow.client.common.Status;
import org.aiflow.client.entity.ArtifactMeta;
import org.aiflow.client.entity.DatasetMeta;
import org.aiflow.client.entity.MetricMeta;
import org.aiflow.client.entity.MetricSummary;
import org.aiflow.client.entity.MetricType;
import org.aiflow.client.entity.ModelMeta;
import org.aiflow.client.entity.ModelRelationMeta;
import org.aiflow.client.entity.ModelVersion;
import org.aiflow.client.entity.ModelVersionMeta;
import org.aiflow.client.entity.ModelVersionRelationMeta;
import org.aiflow.client.entity.ProjectMeta;
import org.aiflow.client.entity.RegisteredModel;
import org.aiflow.client.entity.WorkflowMeta;
import org.aiflow.client.exception.AIFlowException;
import org.aiflow.client.proto.Message;

import org.aiflow.notification.client.EventWatcher;
import org.aiflow.notification.client.NotificationClient;

import io.grpc.Channel;
import io.grpc.ManagedChannelBuilder;
import org.aiflow.notification.entity.EventMeta;
import org.apache.commons.lang3.StringUtils;

import java.util.List;
import java.util.Map;

import static org.aiflow.client.common.Constant.DEFAULT_NAMESPACE;
import static org.aiflow.client.common.Constant.SERVER_URI;

/** Client of AIFlow Rest Endpoint that provides Metadata/Model/Notification function service. */
public class AIFlowClient {

    private final MetadataClient metadataClient;
    private final ModelCenterClient modelCenterClient;
    private final NotificationClient notificationClient;
    private final MetricClient metricClient;

    public AIFlowClient(
            String target,
            String defaultNamespace,
            String sender,
            Boolean enableHa,
            Integer listMemberIntervalMs,
            Integer retryIntervalMs,
            Integer retryTimeoutMs) {
        this(
                ManagedChannelBuilder.forTarget(target).usePlaintext().build(),
                StringUtils.isEmpty(target) ? SERVER_URI : target,
                StringUtils.isEmpty(defaultNamespace) ? DEFAULT_NAMESPACE : defaultNamespace,
                sender,
                enableHa,
                listMemberIntervalMs,
                retryIntervalMs,
                retryTimeoutMs);
    }

    public AIFlowClient(
            Channel channel,
            String target,
            String defaultNamespace,
            String sender,
            Boolean enableHa,
            Integer listMemberIntervalMs,
            Integer retryIntervalMs,
            Integer retryTimeoutMs) {
        this.metadataClient = new MetadataClient(channel);
        this.modelCenterClient = new ModelCenterClient(channel);
        this.notificationClient =
                new NotificationClient(
                        target,
                        defaultNamespace,
                        sender,
                        enableHa,
                        listMemberIntervalMs,
                        retryIntervalMs,
                        retryTimeoutMs);
        this.metricClient = new MetricClient(channel);
    }

    /**
     * Get a specific dataset in Metadata Store by dataset id.
     *
     * @param datasetId Id of dataset.
     * @return Single DatasetMeta object if dataset exists, otherwise returns None if dataset does
     *     not exist.
     */
    public DatasetMeta getDatasetById(Long datasetId) throws Exception {
        return this.metadataClient.getDatasetById(datasetId);
    }

    /**
     * Get a specific dataset in Metadata Store by dataset name.
     *
     * @param datasetName Name of dataset.
     * @return Single DatasetMeta object if dataset exists, otherwise returns None if dataset does
     *     not exist.
     */
    public DatasetMeta getDatasetByName(String datasetName) throws Exception {
        return this.metadataClient.getDatasetByName(datasetName);
    }

    /**
     * Register a dataset in Metadata Store.
     *
     * @param name Name of dataset.
     * @param dataFormat Data format of dataset.
     * @param description Description of dataset.
     * @param uri Uri of dataset.
     * @param properties Properties of dataset.
     * @param nameList Name list of dataset's schema.
     * @param typeList Type list corresponded to name list of dataset's schema.
     * @return Single DatasetMeta object registered in Metadata Store.
     */
    public DatasetMeta registerDataset(
            String name,
            String dataFormat,
            String description,
            String uri,
            Map<String, String> properties,
            List<String> nameList,
            List<DataType> typeList)
            throws Exception {
        return this.metadataClient.registerDataset(
                name, dataFormat, description, uri, properties, nameList, typeList);
    }

    /**
     * Register a dataset in Metadata Store.
     *
     * @param name Name of dataset.
     * @param catalogName Name of dataset catalog.
     * @param catalogType Type of dataset catalog.
     * @param catalogConnectionUri Connection URI of dataset catalog.
     * @param catalogTable Table of dataset catalog.
     * @param catalogDatabase Database of dataset catalog.
     * @return Single DatasetMeta object registered in Metadata Store.
     */
    public DatasetMeta registerDatasetWithCatalog(
            String name,
            String catalogName,
            String catalogType,
            String catalogConnectionUri,
            String catalogTable,
            String catalogDatabase)
            throws Exception {
        return this.metadataClient.registerDatasetWithCatalog(
                name,
                catalogName,
                catalogType,
                catalogConnectionUri,
                catalogTable,
                catalogDatabase);
    }

    /**
     * Register multiple datasets in Metadata Store.
     *
     * @param datasets List of dataset registered
     * @return List of DatasetMeta object registered in Metadata Store.
     */
    public List<DatasetMeta> registerDatasets(List<DatasetMeta> datasets) throws Exception {
        return this.metadataClient.registerDatasets(datasets);
    }

    /**
     * Update a dataset in Metadata Store.
     *
     * @param name Name of dataset.
     * @param dataFormat Data format of dataset.
     * @param description Description of dataset.
     * @param uri uri of dataset.
     * @param properties Properties of dataset.
     * @param nameList Name list of dataset's schema.
     * @param typeList Type list corresponded to name list of dataset's schema.
     * @param catalogName Name of dataset catalog.
     * @param catalogType Type of dataset catalog.
     * @param catalogConnectionUri Connection URI of dataset catalog.
     * @param catalogTable Table of dataset catalog.
     * @param catalogDatabase Database of dataset catalog.
     * @return Single DatasetMeta object registered in Metadata Store.
     */
    public DatasetMeta updateDataset(
            String name,
            String dataFormat,
            String description,
            String uri,
            Map<String, String> properties,
            List<String> nameList,
            List<DataType> typeList,
            String catalogName,
            String catalogType,
            String catalogConnectionUri,
            String catalogTable,
            String catalogDatabase)
            throws Exception {
        return this.metadataClient.updateDataset(
                name,
                dataFormat,
                description,
                uri,
                properties,
                nameList,
                typeList,
                catalogName,
                catalogType,
                catalogConnectionUri,
                catalogTable,
                catalogDatabase);
    }

    /**
     * List registered datasets in Metadata Store.
     *
     * @param pageSize Limitation of listed datasets.
     * @param offset Offset of listed datasets.
     * @return List of DatasetMeta object registered in Metadata Store.
     */
    public List<DatasetMeta> listDatasets(Long pageSize, Long offset) throws Exception {
        return this.metadataClient.listDatasets(pageSize, offset);
    }

    /**
     * Delete registered dataset by dataset id.
     *
     * @param datasetId Id of dataset.
     * @return Status.OK if dataset is successfully deleted, Status.ERROR if dataset does not exist
     *     otherwise.
     */
    public Status deleteDatasetById(Long datasetId) throws Exception {
        return this.metadataClient.deleteDatasetById(datasetId);
    }

    /**
     * Delete registered dataset by dataset name.
     *
     * @param datasetName Name of dataset.
     * @return Status.OK if dataset is successfully deleted, Status.ERROR if dataset does not exist
     *     otherwise.
     */
    public Status deleteDatasetByName(String datasetName) throws Exception {
        return this.metadataClient.deleteDatasetByName(datasetName);
    }

    /**
     * Get a specific model relation in Metadata Store by model id.
     *
     * @param modelId Id of model.
     * @return Single ModelRelationMeta object if model relation exists, otherwise returns None if
     *     model relation does not exist.
     */
    public ModelRelationMeta getModelRelationById(Long modelId) throws Exception {
        return this.metadataClient.getModelRelationById(modelId);
    }

    /**
     * Get a specific model relation in Metadata Store by model name.
     *
     * @param modelName Name of model.
     * @return Single ModelRelationMeta object if model relation exists, otherwise returns None if
     *     model relation does not exist.
     */
    public ModelRelationMeta getModelRelationByName(String modelName) throws Exception {
        return this.metadataClient.getModelRelationByName(modelName);
    }

    /**
     * Register a model relation in Metadata Store.
     *
     * @param name Name of model.
     * @param projectId Project id which the model corresponded to.
     * @return Single ModelRelationMeta object registered in Metadata Store.
     */
    public ModelRelationMeta registerModelRelation(String name, Long projectId) throws Exception {
        return this.metadataClient.registerModelRelation(name, projectId);
    }

    /**
     * List registered model relations in Metadata Store.
     *
     * @param pageSize Limitation of listed model relations.
     * @param offset Offset of listed model relations.
     * @return List of ModelRelationMeta object registered in Metadata Store.
     */
    public List<ModelRelationMeta> listModelRelation(Long pageSize, Long offset) throws Exception {
        return this.metadataClient.listModelRelation(pageSize, offset);
    }

    /**
     * Delete registered model relation by model id.
     *
     * @param modelId Id of model.
     * @return Status.OK if model relation is successfully deleted, Status.ERROR if model relation
     *     does not exist otherwise.
     */
    public Status deleteModelRelationById(Long modelId) throws Exception {
        return this.metadataClient.deleteModelRelationById(modelId);
    }

    /**
     * Delete registered model relation by model name.
     *
     * @param modelName Name of model.
     * @return Status.OK if model relation is successfully deleted, Status.ERROR if model relation
     *     does not exist otherwise.
     */
    public Status deleteModelRelationByName(String modelName) throws Exception {
        return this.metadataClient.deleteModelRelationByName(modelName);
    }

    /**
     * Get a specific model in Metadata Store by model id.
     *
     * @param modelId Id of model.
     * @return Single ModelMeta object if model relation exists, otherwise returns None if model
     *     relation does not exist.
     */
    public ModelMeta getModelById(Long modelId) throws Exception {
        return this.metadataClient.getModelById(modelId);
    }

    /**
     * Get a specific model in Metadata Store by model name.
     *
     * @param modelName Name of model.
     * @return Single ModelMeta object if model relation exists, otherwise returns None if model
     *     relation does not exist.
     */
    public ModelMeta getModelByName(String modelName) throws Exception {
        return this.metadataClient.getModelByName(modelName);
    }

    /**
     * Register a model in Metadata Store.
     *
     * @param modelName Name of registered model.
     * @param modelDesc Description of registered model.
     * @param projectId Project id which registered model corresponded to.
     * @return Single ModelMeta object registered in Metadata Store.
     */
    public ModelMeta registerModel(String modelName, String modelDesc, Long projectId)
            throws Exception {
        return this.metadataClient.registerModel(modelName, modelDesc, projectId);
    }

    /**
     * Delete registered model by model id.
     *
     * @param modelId Id of model.
     * @return Status.OK if model is successfully deleted, Status.ERROR if model does not exist
     *     otherwise.
     */
    public Status deleteModelById(Long modelId) throws Exception {
        return this.metadataClient.deleteModelById(modelId);
    }

    /**
     * Delete registered model by model name.
     *
     * @param modelName Name of model.
     * @return Status.OK if model is successfully deleted, Status.ERROR if model does not exist
     *     otherwise.
     */
    public Status deleteModelByName(String modelName) throws Exception {
        return this.metadataClient.deleteModelByName(modelName);
    }

    /**
     * Get a specific model version relation in Metadata Store by model version name.
     *
     * @param version Name of model version.
     * @param modelId Model id corresponded to model version.
     * @return Single ModelVersionRelationMeta object if model relation exists, otherwise returns
     *     None if model relation does not exist.
     */
    public ModelVersionRelationMeta getModelVersionRelationByVersion(String version, Long modelId)
            throws Exception {
        return this.metadataClient.getModelVersionRelationByVersion(version, modelId);
    }

    /**
     * Register a model version relation in Metadata Store.
     *
     * @param version Name of model version.
     * @param modelId Model id corresponded to model version.
     * @param projectSnapshotId Project snapshot id corresponded to model version.
     * @return Single ModelVersionRelationMeta object registered in Metadata Store.
     */
    public ModelVersionRelationMeta registerModelVersionRelation(
            String version, Long modelId, Long projectSnapshotId) throws Exception {
        return this.metadataClient.registerModelVersionRelation(
                version, modelId, projectSnapshotId);
    }

    /**
     * List registered model version relations in Metadata Store.
     *
     * @param modelId Model id corresponded to model version.
     * @param pageSize Limitation of listed model version relations.
     * @param offset Offset of listed model version relations.
     * @return List of ModelVersionRelationMeta object registered in Metadata Store.
     */
    public List<ModelVersionRelationMeta> listModelVersionRelation(
            Long modelId, Long pageSize, Long offset) throws Exception {
        return this.metadataClient.listModelVersionRelation(modelId, pageSize, offset);
    }

    /**
     * Delete registered model version relation by model name.
     *
     * @param version Name of model version.
     * @param modelId Model id corresponded to model version.
     * @return Status.OK if model version relation is successfully deleted, Status.ERROR if model
     *     version relation does not exist otherwise.
     */
    public Status deleteModelVersionRelationByVersion(String version, Long modelId)
            throws Exception {
        return this.metadataClient.deleteModelVersionRelationByVersion(version, modelId);
    }

    /**
     * Get a specific model version in Metadata Store by model version name.
     *
     * @param version Name of model version.
     * @param modelId Model id corresponded to model version.
     * @return Single ModelVersionMeta object if model relation exists, otherwise returns None if
     *     model relation does not exist.
     */
    public ModelVersionMeta getModelVersionByVersion(String version, Long modelId)
            throws Exception {
        return this.metadataClient.getModelVersionByVersion(version, modelId);
    }

    /**
     * Register a model version in Metadata Store.
     *
     * @param modelPath Source path where the AIFlow model is stored.
     * @param modelType Type of AIFlow registered model option.
     * @param versionDesc Description of registered model version.
     * @param modelId Model id corresponded to model version.
     * @param projectSnapshotId Project snapshot id corresponded to model version.
     * @return Single ModelVersionRelationMeta object registered in Metadata Store.
     */
    public ModelVersionMeta registerModelVersion(
            String modelPath,
            String modelType,
            String versionDesc,
            Long modelId,
            Message.ModelVersionStage currentStage,
            Long projectSnapshotId)
            throws Exception {
        return this.metadataClient.registerModelVersion(
                modelPath, modelType, versionDesc, modelId, currentStage, projectSnapshotId);
    }

    /**
     * Delete registered model version by model version and id.
     *
     * @param version Name of model version.
     * @param modelId Model id corresponded to model version.
     * @return Status.OK if model version is successfully deleted, Status.ERROR if model version
     *     does not exist otherwise.
     */
    public Status deleteModelVersionByVersion(String version, Long modelId) throws Exception {
        return this.metadataClient.deleteModelVersionByVersion(version, modelId);
    }

    /**
     * Get a specific project in Metadata Store by project id.
     *
     * @param projectId Id of project.
     * @return Single ProjectMeta object if project exists, otherwise returns None if project does
     *     not exist.
     */
    public ProjectMeta getProjectById(Long projectId) throws Exception {
        return this.metadataClient.getProjectById(projectId);
    }

    /**
     * Get a specific project in Metadata Store by project name.
     *
     * @param projectName Name of project.
     * @return Single ProjectMeta object if project exists, otherwise returns None if project does
     *     not exist.
     */
    public ProjectMeta getProjectByName(String projectName) throws Exception {
        return this.metadataClient.getProjectByName(projectName);
    }

    /**
     * Register a project in Metadata Store.
     *
     * @param name Name of project.
     * @param uri Uri of project
     * @param properties Properties of project
     * @return Single ProjectMeta object registered in Metadata Store.
     */
    public ProjectMeta registerProject(String name, String uri, Map<String, String> properties)
            throws Exception {
        return this.metadataClient.registerProject(name, uri, properties);
    }

    /**
     * Update a project in Metadata Store.
     *
     * @param name Name of project.
     * @param uri Uri of project
     * @param properties Properties of project
     * @return Single ProjectMeta object registered in Metadata Store.
     */
    public ProjectMeta updateProject(String name, String uri, Map<String, String> properties)
            throws Exception {
        return this.metadataClient.updateProject(name, uri, properties);
    }

    /**
     * List registered projects in Metadata Store.
     *
     * @param pageSize Limitation of listed projects.
     * @param offset Offset of listed projects.
     * @return List of ProjectMeta object registered in Metadata Store.
     */
    public List<ProjectMeta> listProject(Long pageSize, Long offset) throws Exception {
        return this.metadataClient.listProject(pageSize, offset);
    }

    /**
     * Delete registered project by project id.
     *
     * @param projectId Id of project.
     * @return Status.OK if project is successfully deleted, Status.ERROR if project does not exist
     *     otherwise.
     */
    public Status deleteProjectById(Long projectId) throws Exception {
        return this.metadataClient.deleteProjectById(projectId);
    }

    /**
     * Delete registered project by project name.
     *
     * @param projectName Name of project.
     * @return Status.OK if project is successfully deleted, Status.ERROR if project does not exist
     *     otherwise.
     */
    public Status deleteProjectByName(String projectName) throws Exception {
        return this.metadataClient.deleteProjectByName(projectName);
    }

    /**
     * * Register a workflow in metadata store.
     *
     * @param name The workflow name
     * @param projectId The id of project which contains the workflow
     * @param properties The workflow properties
     * @return WorkflowMeta object registered in Metadata Store
     */
    public WorkflowMeta registerWorkflow(
            String name, Long projectId, Map<String, String> properties) throws Exception {
        return this.metadataClient.registerWorkflow(name, projectId, properties);
    }

    /**
     * * Get a workflow by specific project name and workflow name
     *
     * @param projectName The name of project which contains the workflow
     * @param workflowName The workflow name
     * @return WorkflowMeta object registered in Metadata Store
     */
    public WorkflowMeta getWorkflowByName(String projectName, String workflowName)
            throws Exception {
        return this.metadataClient.getWorkflowByName(projectName, workflowName);
    }

    /**
     * * Get a workflow by uuid
     *
     * @param workflowId The workflow id
     * @return WorkflowMeta object registered in Metadata Store
     */
    public WorkflowMeta getWorkflowById(Long workflowId) throws Exception {
        return this.metadataClient.getWorkflowById(workflowId);
    }

    /**
     * * List all workflows of the specific project
     *
     * @param projectName The name of project which contains the workflow
     * @param pageSize Limitation of listed workflows.
     * @param offset Offset of listed workflows.
     * @return
     */
    public List<WorkflowMeta> listWorkflows(String projectName, Long pageSize, Long offset)
            throws Exception {
        return this.metadataClient.listWorkflows(projectName, pageSize, offset);
    }

    /**
     * * Delete the workflow by specific project and workflow name
     *
     * @param projectName The name of project which contains the workflow
     * @param workflowName The workflow name
     * @return Status.OK if workflow is successfully deleted, Status.ERROR if workflow does not
     *     exist otherwise.
     */
    public Status deleteWorkflowByName(String projectName, String workflowName) throws Exception {
        return this.metadataClient.deleteWorkflowByName(projectName, workflowName);
    }

    /**
     * Delete the workflow by specific uuid.
     *
     * @param workflowId Id of worflow.
     * @return Status.OK if workflow is successfully deleted, Status.ERROR if workflow does not
     *     exist otherwise.
     */
    public Status deleteWorkflowById(Long workflowId) throws Exception {
        return this.metadataClient.deleteWorkflowById(workflowId);
    }

    /**
     * * Update the workflow
     *
     * @param workflowName The workflow name
     * @param projectName The name of project which contains the workflow
     * @param properties Properties needs to be updated
     * @return WorkflowMeta object registered in Metadata Store
     */
    public WorkflowMeta updateWorkflow(
            String workflowName, String projectName, Map<String, String> properties)
            throws Exception {
        return this.metadataClient.updateWorkflow(workflowName, projectName, properties);
    }

    /**
     * Get a specific artifact in Metadata Store by artifact id.
     *
     * @param artifactId Id of artifact.
     * @return Single ArtifactMeta object if artifact exists, otherwise returns None if artifact
     *     does not exist.
     */
    public ArtifactMeta getArtifactById(Long artifactId) throws Exception {
        return this.metadataClient.getArtifactById(artifactId);
    }

    /**
     * Get a specific artifact in Metadata Store by artifact name.
     *
     * @param artifactName Name of artifact.
     * @return Single ArtifactMeta object if artifact exists, otherwise returns None if artifact
     *     does not exist.
     */
    public ArtifactMeta getArtifactByName(String artifactName) throws Exception {
        return this.metadataClient.getArtifactByName(artifactName);
    }

    /**
     * Register a artifact in Metadata Store.
     *
     * @param name Name of artifact.
     * @param artifactType Data format of artifact.
     * @param description Description of artifact.
     * @param uri Uri of artifact.
     * @param properties Properties of artifact.
     * @return Single ArtifactMeta object registered in Metadata Store.
     */
    public ArtifactMeta registerArtifact(
            String name,
            String artifactType,
            String description,
            String uri,
            Map<String, String> properties)
            throws Exception {
        return this.metadataClient.registerArtifact(
                name, artifactType, description, uri, properties);
    }

    /**
     * Update a artifact in Metadata Store.
     *
     * @param name Name of artifact.
     * @param artifactType Type of artifact.
     * @param uri Uri of artifact.
     * @param properties Properties of artifact.
     * @return Single ArtifactMeta object registered in Metadata Store.
     */
    public ArtifactMeta updateArtifact(
            String name,
            String artifactType,
            String description,
            String uri,
            Map<String, String> properties)
            throws Exception {
        return this.metadataClient.updateArtifact(name, artifactType, description, uri, properties);
    }

    /**
     * List registered artifacts in Metadata Store.
     *
     * @param pageSize Limitation of listed artifacts.
     * @param offset Offset of listed artifacts.
     * @return List of ArtifactMeta object registered in Metadata Store.
     */
    public List<ArtifactMeta> listArtifact(Long pageSize, Long offset) throws Exception {
        return this.metadataClient.listArtifact(pageSize, offset);
    }

    /**
     * Delete registered artifact by artifact id.
     *
     * @param artifactId Id of artifact.
     * @return Status.OK if artifact is successfully deleted, Status.ERROR if artifact does not
     *     exist otherwise.
     */
    public Status deleteArtifactById(Long artifactId) throws Exception {
        return this.metadataClient.deleteArtifactById(artifactId);
    }

    /**
     * Delete registered artifact by artifact name.
     *
     * @param artifactName Name of artifact.
     * @return Status.OK if artifact is successfully deleted, Status.ERROR if artifact does not
     *     exist otherwise.
     */
    public Status deleteArtifactByName(String artifactName) throws Exception {
        return this.metadataClient.deleteArtifactByName(artifactName);
    }

    /**
     * Create a new registered model from given type in Model Center.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend
     *     store.
     * @param modelDesc (Optional) Description of registered model.
     * @return Object of RegisteredModel created in Model Center.
     */
    public RegisteredModel createRegisteredModel(String modelName, String modelDesc)
            throws Exception {
        return this.modelCenterClient.createRegisteredModel(modelName, modelDesc);
    }

    /**
     * Update metadata for RegisteredModel entity backend. Either ``modelName`` or ``modelDesc``
     * should be non-None. Backend raises exception if a registered model with given name does not
     * exist.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend
     *     store.
     * @param newName (Optional) New proposed name for the registered model.
     * @param modelDesc (Optional) Description of registered model.
     * @return Object of RegisteredModel updated in Model Center.
     */
    public RegisteredModel updateRegisteredModel(String modelName, String newName, String modelDesc)
            throws Exception {
        return this.modelCenterClient.updateRegisteredModel(modelName, newName, modelDesc);
    }

    /**
     * Delete registered model by model name in Model Center backend.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend
     *     store.
     * @return Object of RegisteredModel deleted in Model Center.
     */
    public RegisteredModel deleteRegisteredModel(String modelName) throws Exception {
        return this.modelCenterClient.deleteRegisteredModel(modelName);
    }

    /**
     * List of all registered models in Model Center backend.
     *
     * @return List of RegisteredModel created in Model Center.
     */
    public List<RegisteredModel> listRegisteredModels() throws Exception {
        return this.modelCenterClient.listRegisteredModels();
    }

    /**
     * Get registered model detail filter by model name for Model Center.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend
     *     store.
     * @return Object of RegisteredModel created in Model Center.
     */
    public RegisteredModel getRegisteredModelDetail(String modelName) throws Exception {
        return this.modelCenterClient.getRegisteredModelDetail(modelName);
    }

    /**
     * Create a new registered model from given type in Model Center.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend
     *     store.
     * @param modelPath Source path where the AIFlow model is stored.
     * @param modelType (Optional) Type of AIFlow registered model option.
     * @param versionDesc (Optional) Description of registered model version.
     * @return Object of ModelVersion created in Model Center.
     */
    public ModelVersion createModelVersion(
            String modelName, String modelPath, String modelType, String versionDesc)
            throws Exception {
        return this.modelCenterClient.createModelVersion(
                modelName, modelPath, modelType, versionDesc);
    }

    /**
     * Update metadata for ModelVersion entity and metadata associated with a model version in
     * backend. Either ``modelPath`` or ``modelMetric`` or ``modelFlavor`` or ``versionDesc`` should
     * be non-None. Backend raises exception if a registered model with given name does not exist.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend
     *     store.
     * @param modelVersion User-defined version of registered model.
     * @param modelPath (Optional) Source path where the AIFlow model is stored.
     * @param modelType (Optional) Type of AIFlow registered model option.
     * @param versionDesc (Optional) Description of registered model version.
     * @param currentStage (Optional) Current stage for registered model version.
     * @return Object of ModelVersion updated in Model Center.
     */
    public ModelVersion updateModelVersion(
            String modelName,
            String modelVersion,
            String modelPath,
            String modelType,
            String versionDesc,
            ModelStage currentStage)
            throws Exception {
        return this.modelCenterClient.updateModelVersion(
                modelName, modelVersion, modelPath, modelType, versionDesc, currentStage);
    }

    /**
     * Delete model version by model name and version in Model Center backend.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend
     *     store.
     * @param modelVersion User-defined version of registered model.
     * @return Object of ModelVersion deleted in Model Center.
     */
    public ModelVersion deleteModelVersion(String modelName, String modelVersion) throws Exception {
        return this.modelCenterClient.deleteModelVersion(modelName, modelVersion);
    }

    /**
     * Get model version detail filter by model name and model version for Model Center.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend
     *     store.
     * @param modelVersion User-defined version of registered model.
     * @return Object of ModelVersion created in Model Center.
     */
    public ModelVersion getModelVersionDetail(String modelName, String modelVersion)
            throws Exception {
        return this.modelCenterClient.getModelVersionDetail(modelName, modelVersion);
    }

    /**
     * Send the event to Notification Service.
     *
     * @param key Key of event updated in Notification Service.
     * @param value Value of event updated in Notification Service.
     * @param eventType Type of event updated in Notification Service.
     * @param context Context of event updated in Notification Service.
     * @return Object of Event created in Notification Service.
     */
    public EventMeta sendEvent(String key, String value, String eventType, String context)
            throws Exception {
        return this.notificationClient.sendEvent(key, value, eventType, context);
    }

    /**
     * List specific `key` or `version` notifications in Notification Service.
     *
     * @param namespace Namespace of notification for listening.
     * @param keys Keys of notification for listening.
     * @param version (Optional) Version of notification for listening.
     * @param eventType (Optional) Type of event for listening.
     * @param startTime (Optional) Type of event for listening.
     * @return List of Notification updated in Notification Service.
     */
    public List<EventMeta> listEvents(
            String namespace,
            List<String> keys,
            long version,
            String eventType,
            long startTime,
            String sender)
            throws Exception {
        return this.notificationClient.listEvents(
                namespace, keys, version, eventType, startTime, sender);
    }

    /**
     * Start listen specific `key` or `version` notifications in Notification Service.
     *
     * @param namespace Namespace of notification for listening.
     * @param key Key of notification for listening.
     * @param watcher Watcher instance for listening notification.
     * @param version (Optional) Version of notification for listening.
     * @param eventType (Optional) Type of event for listening.
     * @param startTime (Optional) Type of event for listening.
     */
    public void startListenEvent(
            String namespace,
            String key,
            EventWatcher watcher,
            long version,
            String eventType,
            long startTime,
            String sender) {
        this.notificationClient.startListenEvent(
                namespace, key, watcher, version, eventType, startTime, sender);
    }

    /**
     * Stop listen specific `key` notifications in Notification Service.
     *
     * @param key Key of notification for listening.
     */
    public void stopListenEvent(String namespace, String key, String eventType, String sender) {
        this.notificationClient.stopListenEvent(namespace, key, eventType, sender);
    }

    /**
     * Get latest version of specific `key` notifications in Notification Service.
     *
     * @param namespace Namespace of notification for listening.
     * @param key Key of notification for listening.
     */
    public long getLatestVersion(String namespace, String key) throws Exception {
        return this.notificationClient.getLatestVersion(namespace, key);
    }

    /**
     * Register a MetricMeta in metric center.
     *
     * @param name Name of registered metric meta. This is expected to be unique in the backend
     *     store.
     * @param metricType Type of registered metric meta.
     * @param projectName Name of the project associated with the registered metric meta.
     * @param description Name of registered model.
     * @param datasetName Name of the dataset associated with the registered metric meta.
     * @param modelName Name of the model associated with the registered metric meta.
     * @param jobName Name of the job associated with the registered metric meta.
     * @param startTime Start time of registered metric meta.
     * @param endTime End time of registered metric meta.
     * @param uri Uri of registered metric meta.
     * @param tags Tags of registered metric meta.
     * @param properties Properties of registered metric meta.
     * @return The {@link MetricMeta} object that is registered.
     */
    public MetricMeta registerMetricMeta(
            String name,
            MetricType metricType,
            String projectName,
            String description,
            String datasetName,
            String modelName,
            String jobName,
            long startTime,
            long endTime,
            String uri,
            String tags,
            Map<String, String> properties)
            throws AIFlowException {
        return this.metricClient.registerMetricMeta(
                name,
                metricType,
                projectName,
                description,
                datasetName,
                modelName,
                jobName,
                startTime,
                endTime,
                uri,
                tags,
                properties);
    }

    /**
     * Update a MetricMeta in Metric Center.
     *
     * @param name Name of registered metric meta. This is expected to be unique in the backend
     *     store.
     * @param projectName Name of the project associated with the registered metric meta.
     * @param description Name of registered model.
     * @param datasetName Name of the dataset associated with the registered metric meta.
     * @param modelName Name of the model associated with the registered metric meta.
     * @param jobName Name of the job associated with the registered metric meta.
     * @param startTime Start time of registered metric meta.
     * @param endTime End time of registered metric meta.
     * @param uri Uri of registered metric meta.
     * @param tags Tags of registered metric meta.
     * @param properties Properties of registered metric meta.
     * @return The {@link MetricMeta} object that is updated.
     */
    public MetricMeta updateMetricMeta(
            String name,
            String projectName,
            String description,
            String datasetName,
            String modelName,
            String jobName,
            long startTime,
            long endTime,
            String uri,
            String tags,
            Map<String, String> properties)
            throws AIFlowException {
        return this.metricClient.updateMetricMeta(
                name,
                projectName,
                description,
                datasetName,
                modelName,
                jobName,
                startTime,
                endTime,
                uri,
                tags,
                properties);
    }

    /**
     * * Delete metric metadata by metric name in Metric Center backend.
     *
     * @param metricName Name of registered metric meta. This is expected to be unique in the
     *     backend store.
     * @return True if successfully deleting the given metric metadata, false if not success.
     */
    public boolean deleteMetricMeta(String metricName) {
        return this.metricClient.deleteMetricMeta(metricName);
    }

    /**
     * * Get metric metadata detail filter by metric name for Metric Center.
     *
     * @param metricName Name of registered metric meta. This is expected to be unique in the
     *     backend store.
     * @return A {@link MetricMeta} object.
     * @throws AIFlowException
     */
    public MetricMeta getMetricMeta(String metricName) throws AIFlowException {
        return this.metricClient.getMetricMeta(metricName);
    }

    /**
     * * List dataset metric metadata filter by dataset name and project name for Metric Center.
     *
     * @param datasetName Name of the dataset associated with the registered metric meta.
     * @param projectName Name of the project associated with the registered metric meta.
     * @return List of {@link MetricMeta} objects.
     * @throws AIFlowException
     */
    public List<MetricMeta> listDatasetMetricMetas(String datasetName, String projectName)
            throws AIFlowException {
        return this.metricClient.listDatasetMetricMetas(datasetName, projectName);
    }

    /**
     * * List model metric metadata filter by model name and project name for Metric Center.
     *
     * @param modelName Name of the model associated with the registered metric meta.
     * @param projectName Name of the project associated with the registered metric meta.
     * @return List of {@link MetricMeta} objects.
     * @throws AIFlowException
     */
    public List<MetricMeta> listModelMetricMetas(String modelName, String projectName)
            throws AIFlowException {
        return this.metricClient.listModelMetricMetas(modelName, projectName);
    }

    /**
     * * Register metric summary in Metric Center.
     *
     * @param metricName Name of registered metric summary.
     * @param metricKey Key of registered metric summary.
     * @param metricValue Value of registered metric summary.
     * @param metricTimestamp Timestamp of registered metric summary.
     * @param modelVersion Version of the model version associated with the registered metric
     *     summary.
     * @param jobExecutionId ID of the job execution associated with the registered metric summary.
     * @return The {@link MetricSummary} object that is registered.
     * @throws AIFlowException
     */
    public MetricSummary registerMetricSummary(
            String metricName,
            String metricKey,
            String metricValue,
            long metricTimestamp,
            String modelVersion,
            String jobExecutionId)
            throws AIFlowException {
        return this.metricClient.registerMetricSummary(
                metricName, metricKey, metricValue, metricTimestamp, modelVersion, jobExecutionId);
    }

    /**
     * * Update metric summary in Metric Center.
     *
     * @param uuid UUID of registered metric summary.
     * @param metricName Name of registered metric summary.
     * @param metricKey Key of registered metric summary.
     * @param metricValue Value of registered metric summary.
     * @param metricTimestamp Timestamp of registered metric summary.
     * @param modelVersion Version of the model version associated with the registered metric
     *     summary.
     * @param jobExecutionId ID of the job execution associated with the registered metric summary.
     * @return The {@link MetricSummary} object that is updated.
     * @throws AIFlowException
     */
    public MetricSummary updateMetricSummary(
            long uuid,
            String metricName,
            String metricKey,
            String metricValue,
            long metricTimestamp,
            String modelVersion,
            String jobExecutionId)
            throws AIFlowException {
        return this.metricClient.updateMetricSummary(
                uuid,
                metricName,
                metricKey,
                metricValue,
                metricTimestamp,
                modelVersion,
                jobExecutionId);
    }

    /**
     * * Delete metric summary by metric uuid in Metric Center backend.
     *
     * @param uuid UUID of registered metric summary.
     * @return Whether to delete the given metric summary.
     */
    public boolean deleteMetricSummary(long uuid) {
        return this.metricClient.deleteMetricSummary(uuid);
    }

    /**
     * * Get metric summary detail filter by summary uuid for Metric Center.
     *
     * @param uuid UUID of registered metric summary.
     * @return A {@link MetricSummary} object.
     * @throws AIFlowException
     */
    public MetricSummary getMetricSummary(long uuid) throws AIFlowException {
        return this.metricClient.getMetricSummary(uuid);
    }

    /**
     * * List of metric summaries filter by metric summary fields for Metric Center.
     *
     * @param metricName Name of filtered metric summary.
     * @param metricKey Key of filtered metric summary.
     * @param modelVersion Version of the model version associated with the registered metric
     *     summary.
     * @param startTime Start time for timestamp filtered metric summary.
     * @param endTime End time for timestamp filtered metric summary.
     * @return List of {@link MetricSummary} objects.
     * @throws AIFlowException
     */
    public List<MetricSummary> listMetricSummaries(
            String metricName, String metricKey, String modelVersion, long startTime, long endTime)
            throws AIFlowException {
        return this.metricClient.listMetricSummaries(
                metricName, metricKey, modelVersion, startTime, endTime);
    }
}
