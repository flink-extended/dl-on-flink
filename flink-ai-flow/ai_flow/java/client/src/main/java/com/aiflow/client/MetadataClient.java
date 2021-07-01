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
package com.aiflow.client;

import com.aiflow.common.*;
import com.aiflow.entity.ModelVersionMeta;
import com.aiflow.entity.*;
import com.aiflow.proto.Message.*;
import com.aiflow.proto.MetadataServiceGrpc;
import com.aiflow.proto.MetadataServiceOuterClass.*;
import com.google.protobuf.util.JsonFormat.Parser;
import io.grpc.Channel;
import io.grpc.ManagedChannelBuilder;
import org.apache.commons.lang3.StringUtils;

import java.util.List;
import java.util.Map;

import static com.aiflow.common.Constant.SERVER_URI;
import static com.aiflow.entity.ArtifactMeta.buildArtifactMeta;
import static com.aiflow.entity.ArtifactMeta.buildArtifactMetas;
import static com.aiflow.entity.DatasetMeta.*;
import static com.aiflow.entity.ModelMeta.buildModelMeta;
import static com.aiflow.entity.ModelRelationMeta.buildModelRelationMeta;
import static com.aiflow.entity.ModelRelationMeta.buildModelRelationMetas;
import static com.aiflow.entity.ModelVersionMeta.buildModelVersionMeta;
import static com.aiflow.entity.ModelVersionRelationMeta.buildModelVersionRelationMeta;
import static com.aiflow.entity.ModelVersionRelationMeta.buildModelVersionRelationMetas;
import static com.aiflow.entity.ProjectMeta.buildProjectMeta;
import static com.aiflow.entity.ProjectMeta.buildProjectMetas;
import static com.aiflow.entity.WorkflowMeta.buildWorkflowMeta;
import static com.aiflow.entity.WorkflowMeta.buildWorkflowMetas;
import static com.aiflow.util.Transform.*;
import static com.google.protobuf.util.JsonFormat.parser;

/**
 * Client of AIFlow Rest Endpoint that provides Metadata Store function service.
 */
public class MetadataClient {

    private final MetadataServiceGrpc.MetadataServiceBlockingStub metadataServiceStub;

    private final Parser parser = parser().ignoringUnknownFields();

    public MetadataClient() {
        this(SERVER_URI);
    }

    public MetadataClient(String target) {
        this(ManagedChannelBuilder.forTarget(target).usePlaintext().build());
    }

    public MetadataClient(Channel channel) {
        this.metadataServiceStub = MetadataServiceGrpc.newBlockingStub(channel);
    }

    /**
     * Get a specific dataset in Metadata Store by dataset id.
     *
     * @param datasetId Id of dataset.
     * @return Single DatasetMeta object if dataset exists, otherwise returns None if dataset does not exist.
     */
    public DatasetMeta getDatasetById(Long datasetId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(datasetId).build();
        Response response = metadataServiceStub.getDatasetById(request);
        DatasetProto.Builder builder = DatasetProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildDatasetMeta(builder.build());
    }

    /**
     * Get a specific dataset in Metadata Store by dataset name.
     *
     * @param datasetName Name of dataset.
     * @return Single DatasetMeta object if dataset exists, otherwise returns None if dataset does not exist.
     */
    public DatasetMeta getDatasetByName(String datasetName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(datasetName).build();
        Response response = metadataServiceStub.getDatasetByName(request);
        DatasetProto.Builder builder = DatasetProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildDatasetMeta(builder.build());
    }

    /**
     * Register a dataset in Metadata Store.
     *
     * @param name        Name of dataset.
     * @param dataFormat  Data format of dataset.
     * @param description Description of dataset.
     * @param uri    Uri of dataset.
     * @param properties  Properties of dataset.
     * @param nameList    Name list of dataset's schema.
     * @param typeList    Type list corresponded to name list of dataset's schema.
     * @return Single DatasetMeta object registered in Metadata Store.
     */
    public DatasetMeta registerDataset(String name, String dataFormat, String description,
                                       String uri, Map<String, String> properties,
                                       List<String> nameList, List<DataType> typeList) throws Exception {
        DatasetProto.Builder dataset = DatasetProto.newBuilder().setName(name).setDataFormat(stringValue(dataFormat))
                .setDescription(stringValue(description)).setUri(stringValue(uri))
                .putAllProperties(properties).setSchema(SchemaProto.newBuilder().addAllNameList(nameList).addAllTypeList(dataTypeList(typeList)))
                .setCatalogName(stringValue(null)).setCatalogType(stringValue(null)).setCatalogDatabase(stringValue(null))
                .setCatalogConnectionUri(stringValue(null)).setCatalogTable(stringValue(null));
        RegisterDatasetRequest request = RegisterDatasetRequest.newBuilder().setDataset(dataset).build();
        Response response = metadataServiceStub.registerDataset(request);
        DatasetProto.Builder builder = DatasetProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildDatasetMeta(builder.build());
    }

    /**
     * Register a dataset in Metadata Store.
     *
     * @param name                 Name of dataset.
     * @param catalogName          Name of dataset catalog.
     * @param catalogType          Type of dataset catalog.
     * @param catalogConnectionUri Connection URI of dataset catalog.
     * @param catalogTable         Table of dataset catalog.
     * @param catalogDatabase      Database of dataset catalog.
     * @return Single DatasetMeta object registered in Metadata Store.
     */
    public DatasetMeta registerDatasetWithCatalog(String name, String catalogName, String catalogType,
                                                  String catalogConnectionUri, String catalogTable, String catalogDatabase) throws Exception {
        DatasetProto.Builder dataset = DatasetProto.newBuilder().setName(name).setDataFormat(stringValue(null))
                .setDescription(stringValue(null)).setUri(stringValue(null))
                .putAllProperties(null).setSchema(SchemaProto.newBuilder().addAllNameList(null).addAllTypeList(null))
                .setCatalogName(stringValue(catalogName)).setCatalogType(stringValue(catalogType)).setCatalogDatabase(stringValue(catalogDatabase))
                .setCatalogConnectionUri(stringValue(catalogConnectionUri)).setCatalogTable(stringValue(catalogTable));
        RegisterDatasetRequest request = RegisterDatasetRequest.newBuilder().setDataset(dataset).build();
        Response response = metadataServiceStub.registerDataset(request);
        DatasetProto.Builder builder = DatasetProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildDatasetMeta(builder.build());
    }

    /**
     * Register multiple datasets in Metadata Store.
     *
     * @param datasets List of dataset registered
     * @return List of DatasetMeta object registered in Metadata Store.
     */
    public List<DatasetMeta> registerDatasets(List<DatasetMeta> datasets) throws Exception {
        RegisterDatasetsRequest request = RegisterDatasetsRequest.newBuilder().addAllDatasets(buildDatasetProtos(datasets)).build();
        Response response = metadataServiceStub.registerDatasets(request);
        DatasetListProto.Builder builder = DatasetListProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildDatasetMetas(builder.build());
    }

    /**
     * Update a dataset in Metadata Store.
     *
     * @param name                 Name of dataset.
     * @param dataFormat           Data format of dataset.
     * @param description          Description of dataset.
     * @param uri                  Uri of dataset.
     * @param properties           Properties of dataset.
     * @param nameList             Name list of dataset's schema.
     * @param typeList             Type list corresponded to name list of dataset's schema.
     * @param catalogName          Name of dataset catalog.
     * @param catalogType          Type of dataset catalog.
     * @param catalogConnectionUri Connection URI of dataset catalog.
     * @param catalogTable         Table of dataset catalog.
     * @param catalogDatabase      Database of dataset catalog.
     * @return Single DatasetMeta object registered in Metadata Store.
     */
    public DatasetMeta updateDataset(String name, String dataFormat, String description,
                                     String uri, Map<String, String> properties,
                                     List<String> nameList, List<DataType> typeList, String catalogName, String catalogType,
                                     String catalogConnectionUri, String catalogTable, String catalogDatabase) throws Exception {
        UpdateDatasetRequest.Builder dataset = UpdateDatasetRequest.newBuilder().setName(name).setDataFormat(stringValue(dataFormat)).setDescription(stringValue(description))
                .setUri(stringValue(uri)).putAllProperties(properties)
                .addAllNameList(nameList).addAllTypeList(dataTypeList(typeList)).setCatalogName(stringValue(catalogName)).setCatalogType(stringValue(catalogType))
                .setCatalogDatabase(stringValue(catalogDatabase)).setCatalogConnectionUri(stringValue(catalogConnectionUri))
                .setCatalogTable(stringValue(catalogTable));
        UpdateDatasetRequest request = dataset.build();
        Response response = metadataServiceStub.updateDataset(request);
        DatasetProto.Builder builder = DatasetProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildDatasetMeta(builder.build());
    }

    /**
     * List registered datasets in Metadata Store.
     *
     * @param pageSize Limitation of listed datasets.
     * @param offset   Offset of listed datasets.
     * @return List of DatasetMeta object registered in Metadata Store.
     */
    public List<DatasetMeta> listDatasets(Long pageSize, Long offset) throws Exception {
        ListRequest request = ListRequest.newBuilder().setPageSize(pageSize).setOffset(offset).build();
        Response response = metadataServiceStub.listDatasets(request);
        DatasetListProto.Builder builder = DatasetListProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildDatasetMetas(builder.build());
    }

    /**
     * Delete registered dataset by dataset id.
     *
     * @param datasetId Id of dataset.
     * @return Status.OK if dataset is successfully deleted, Status.ERROR if dataset does not exist otherwise.
     */
    public Status deleteDatasetById(Long datasetId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(datasetId).build();
        Response response = metadataServiceStub.deleteDatasetById(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Delete registered dataset by dataset name.
     *
     * @param datasetName Name of dataset.
     * @return Status.OK if dataset is successfully deleted, Status.ERROR if dataset does not exist otherwise.
     */
    public Status deleteDatasetByName(String datasetName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(datasetName).build();
        Response response = metadataServiceStub.deleteDatasetByName(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Get a specific model relation in Metadata Store by model id.
     *
     * @param modelId Id of model.
     * @return Single ModelRelationMeta object if model relation exists, otherwise returns None if model relation does not exist.
     */
    public ModelRelationMeta getModelRelationById(Long modelId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(modelId).build();
        Response response = metadataServiceStub.getModelRelationById(request);
        ModelRelationProto.Builder builder = ModelRelationProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelRelationMeta(builder.build());
    }

    /**
     * Get a specific model relation in Metadata Store by model name.
     *
     * @param modelName Name of model.
     * @return Single ModelRelationMeta object if model relation exists, otherwise returns None if model relation does not exist.
     */
    public ModelRelationMeta getModelRelationByName(String modelName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(modelName).build();
        Response response = metadataServiceStub.getModelRelationByName(request);
        ModelRelationProto.Builder builder = ModelRelationProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelRelationMeta(builder.build());
    }

    /**
     * Register a model relation in Metadata Store.
     *
     * @param name      Name of model.
     * @param projectId Project id which the model corresponded to.
     * @return Single ModelRelationMeta object registered in Metadata Store.
     */
    public ModelRelationMeta registerModelRelation(String name, Long projectId) throws Exception {
        ModelRelationProto modelRelationProto = ModelRelationProto.newBuilder().setName(name).setProjectId(int64Value(projectId)).build();
        RegisterModelRelationRequest request = RegisterModelRelationRequest.newBuilder().setModelRelation(modelRelationProto).build();
        Response response = metadataServiceStub.registerModelRelation(request);
        ModelRelationProto.Builder builder = ModelRelationProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelRelationMeta(builder.build());
    }

    /**
     * List registered model relations in Metadata Store.
     *
     * @param pageSize Limitation of listed model relations.
     * @param offset   Offset of listed model relations.
     * @return List of ModelRelationMeta object registered in Metadata Store.
     */
    public List<ModelRelationMeta> listModelRelation(Long pageSize, Long offset) throws Exception {
        ListRequest request = ListRequest.newBuilder().setPageSize(pageSize).setOffset(offset).build();
        Response response = metadataServiceStub.listModelRelation(request);
        ModelRelationListProto.Builder builder = ModelRelationListProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelRelationMetas(builder.build());
    }

    /**
     * Delete registered model relation by model id.
     *
     * @param modelId Id of model.
     * @return Status.OK if model relation is successfully deleted, Status.ERROR if model relation does not exist otherwise.
     */
    public Status deleteModelRelationById(Long modelId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(modelId).build();
        Response response = metadataServiceStub.deleteModelRelationById(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Delete registered model relation by model name.
     *
     * @param modelName Name of model.
     * @return Status.OK if model relation is successfully deleted, Status.ERROR if model relation does not exist otherwise.
     */
    public Status deleteModelRelationByName(String modelName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(modelName).build();
        Response response = metadataServiceStub.deleteModelRelationByName(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Get a specific model in Metadata Store by model id.
     *
     * @param modelId Id of model.
     * @return Single ModelMeta object if model relation exists, otherwise returns None if model relation does not exist.
     */
    public ModelMeta getModelById(Long modelId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(modelId).build();
        Response response = metadataServiceStub.getModelById(request);
        ModelProto.Builder builder = ModelProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelMeta(builder.build());
    }

    /**
     * Get a specific model in Metadata Store by model name.
     *
     * @param modelName Name of model.
     * @return Single ModelMeta object if model relation exists, otherwise returns None if model relation does not exist.
     */
    public ModelMeta getModelByName(String modelName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(modelName).build();
        Response response = metadataServiceStub.getModelByName(request);
        ModelProto.Builder builder = ModelProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelMeta(builder.build());
    }

    /**
     * Register a model in Metadata Store.
     *
     * @param modelName Name of registered model.
     * @param modelDesc Description of registered model.
     * @param projectId Project id which registered model corresponded to.
     * @return Single ModelMeta object registered in Metadata Store.
     */
    public ModelMeta registerModel(String modelName, String modelDesc, Long projectId) throws Exception {
        ModelProto modelProto = ModelProto.newBuilder().setName(modelName).setModelDesc(stringValue(modelDesc))
                .setProjectId(int64Value(projectId)).build();
        RegisterModelRequest request = RegisterModelRequest.newBuilder().setModel(modelProto).build();
        Response response = metadataServiceStub.registerModel(request);
        ModelProto.Builder builder = ModelProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelMeta(builder.build());
    }

    /**
     * Delete registered model by model id.
     *
     * @param modelId Id of model.
     * @return Status.OK if model is successfully deleted, Status.ERROR if model does not exist otherwise.
     */
    public Status deleteModelById(Long modelId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(modelId).build();
        Response response = metadataServiceStub.deleteModelById(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Delete registered model by model name.
     *
     * @param modelName Name of model.
     * @return Status.OK if model is successfully deleted, Status.ERROR if model does not exist otherwise.
     */
    public Status deleteModelByName(String modelName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(modelName).build();
        Response response = metadataServiceStub.deleteModelByName(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Get a specific model version relation in Metadata Store by model version name.
     *
     * @param version Name of model version.
     * @param modelId Model id corresponded to model version.
     * @return Single ModelVersionRelationMeta object if model relation exists, otherwise returns None if model relation does not exist.
     */
    public ModelVersionRelationMeta getModelVersionRelationByVersion(String version, Long modelId) throws Exception {
        ModelVersionNameRequest request = ModelVersionNameRequest.newBuilder().setName(version).setModelId(modelId).build();
        Response response = metadataServiceStub.getModelVersionRelationByVersion(request);
        ModelVersionRelationProto.Builder builder = ModelVersionRelationProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelVersionRelationMeta(builder.build());
    }

    /**
     * Register a model version relation in Metadata Store.
     *
     * @param version             Name of model version.
     * @param modelId             Model id corresponded to model version.
     * @param projectSnapshotId   Project snapshot id corresponded to model version.
     * @return Single ModelVersionRelationMeta object registered in Metadata Store.
     */
    public ModelVersionRelationMeta registerModelVersionRelation(String version, Long modelId, Long projectSnapshotId) throws Exception {
        ModelVersionRelationProto modelVersionRelationProto = ModelVersionRelationProto.newBuilder().setVersion(stringValue(version)).setModelId(int64Value(modelId))
                .setProjectSnapshotId(int64Value(projectSnapshotId)).build();
        RegisterModelVersionRelationRequest request = RegisterModelVersionRelationRequest.newBuilder().setModelVersionRelation(modelVersionRelationProto).build();
        Response response = metadataServiceStub.registerModelVersionRelation(request);
        ModelVersionRelationProto.Builder builder = ModelVersionRelationProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelVersionRelationMeta(builder.build());
    }

    /**
     * List registered model version relations in Metadata Store.
     *
     * @param modelId  Model id corresponded to model version.
     * @param pageSize Limitation of listed model version relations.
     * @param offset   Offset of listed model version relations.
     * @return List of ModelVersionRelationMeta object registered in Metadata Store.
     */
    public List<ModelVersionRelationMeta> listModelVersionRelation(Long modelId, Long pageSize, Long offset) throws Exception {
        ListModelVersionRelationRequest request = ListModelVersionRelationRequest.newBuilder().setModelId(modelId).setPageSize(pageSize).setOffset(offset).build();
        Response response = metadataServiceStub.listModelVersionRelation(request);
        ModelVersionRelationListProto.Builder builder = ModelVersionRelationListProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelVersionRelationMetas(builder.build());
    }

    /**
     * Delete registered model version relation by model name.
     *
     * @param version Name of model version.
     * @param modelId Model id corresponded to model version.
     * @return Status.OK if model version relation is successfully deleted, Status.ERROR if model version relation does not exist otherwise.
     */
    public Status deleteModelVersionRelationByVersion(String version, Long modelId) throws Exception {
        ModelVersionNameRequest request = ModelVersionNameRequest.newBuilder().setName(version).setModelId(modelId).build();
        Response response = metadataServiceStub.deleteModelVersionRelationByVersion(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Get a specific model version in Metadata Store by model version name.
     *
     * @param version Name of model version.
     * @param modelId Model id corresponded to model version.
     * @return Single ModelVersionMeta object if model relation exists, otherwise returns None if model relation does not exist.
     */
    public ModelVersionMeta getModelVersionByVersion(String version, Long modelId) throws Exception {
        ModelVersionNameRequest request = ModelVersionNameRequest.newBuilder().setName(version).setModelId(modelId).build();
        Response response = metadataServiceStub.getModelVersionByVersion(request);
        ModelVersionProto.Builder builder = ModelVersionProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelVersionMeta(builder.build());
    }

    /**
     * Register a model version in Metadata Store.
     *
     * @param modelPath           Source path where the AIFlow model is stored.
     * @param modelType           Type of AIFlow registered model option.
     * @param versionDesc         Description of registered model version.
     * @param modelId             Model id corresponded to model version.
     * @param projectSnapshotId   Project snapshot id corresponded to model version.
     * @return Single ModelVersionRelationMeta object registered in Metadata Store.
     */
    public ModelVersionMeta registerModelVersion(String modelPath, String modelType, String versionDesc, Long modelId, Long projectSnapshotId) throws Exception {
        ModelVersionProto modelVersionProto = ModelVersionProto.newBuilder().setModelPath(stringValue(modelPath))
                .setModelType(stringValue(modelType))
                .setVersionDesc(stringValue(versionDesc)).setModelId(int64Value(modelId)).setProjectSnapshotId(int64Value(projectSnapshotId)).build();
        RegisterModelVersionRequest request = RegisterModelVersionRequest.newBuilder().setModelVersion(modelVersionProto).build();
        Response response = metadataServiceStub.registerModelVersion(request);
        ModelVersionProto.Builder builder = ModelVersionProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildModelVersionMeta(builder.build());
    }

    /**
     * Delete registered model version by model version and id.
     *
     * @param version Name of model version.
     * @param modelId Model id corresponded to model version.
     * @return Status.OK if model version is successfully deleted, Status.ERROR if model version does not exist otherwise.
     */
    public Status deleteModelVersionByVersion(String version, Long modelId) throws Exception {
        ModelVersionNameRequest request = ModelVersionNameRequest.newBuilder().setName(version).setModelId(modelId).build();
        Response response = metadataServiceStub.deleteModelVersionByVersion(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Get a specific project in Metadata Store by project id.
     *
     * @param projectId Id of project.
     * @return Single ProjectMeta object if project exists, otherwise returns None if project does not exist.
     */
    public ProjectMeta getProjectById(Long projectId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(projectId).build();
        Response response = metadataServiceStub.getProjectById(request);
        ProjectProto.Builder builder = ProjectProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildProjectMeta(builder.build());
    }

    /**
     * Get a specific project in Metadata Store by project name.
     *
     * @param projectName Name of project.
     * @return Single ProjectMeta object if project exists, otherwise returns None if project does not exist.
     */
    public ProjectMeta getProjectByName(String projectName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(projectName).build();
        Response response = metadataServiceStub.getProjectByName(request);
        ProjectProto.Builder builder = ProjectProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildProjectMeta(builder.build());
    }

    /**
     * Register a project in Metadata Store.
     *
     * @param name        Name of project.
     * @param uri         Uri of project
     * @param properties  Properties of project
     * @return Single ProjectMeta object registered in Metadata Store.
     */
    public ProjectMeta registerProject(String name, String uri, Map<String, String> properties) throws Exception {
        ProjectProto projectProto = ProjectProto.newBuilder().setName(name).setUri(stringValue(uri))
                .putAllProperties(properties).build();
        RegisterProjectRequest request = RegisterProjectRequest.newBuilder().setProject(projectProto).build();
        Response response = metadataServiceStub.registerProject(request);
        ProjectProto.Builder builder = ProjectProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildProjectMeta(builder.build());
    }

    /**
     * Update a project in Metadata Store.
     *
     * @param name        Name of project.
     * @param uri         Uri of project
     * @param properties  Properties of project
     * @return Single ProjectMeta object registered in Metadata Store.
     */
    public ProjectMeta updateProject(String name, String uri, Map<String, String> properties) throws Exception {
        UpdateProjectRequest.Builder projectProto = UpdateProjectRequest.newBuilder().setName(name).setUri(stringValue(uri)).putAllProperties(properties);
        UpdateProjectRequest request = projectProto.build();
        Response response = metadataServiceStub.updateProject(request);
        ProjectProto.Builder builder = ProjectProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildProjectMeta(builder.build());
    }

    /**
     * List registered projects in Metadata Store.
     *
     * @param pageSize Limitation of listed projects.
     * @param offset   Offset of listed projects.
     * @return List of ProjectMeta object registered in Metadata Store.
     */
    public List<ProjectMeta> listProject(Long pageSize, Long offset) throws Exception {
        ListRequest request = ListRequest.newBuilder().setPageSize(pageSize).setOffset(offset).build();
        Response response = metadataServiceStub.listProject(request);
        ProjectListProto.Builder builder = ProjectListProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildProjectMetas(builder.build());
    }

    /**
     * Delete registered project by project id.
     *
     * @param projectId Id of project.
     * @return Status.OK if project is successfully deleted, Status.ERROR if project does not exist otherwise.
     */
    public Status deleteProjectById(Long projectId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(projectId).build();
        Response response = metadataServiceStub.deleteProjectById(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Delete registered project by project name.
     *
     * @param projectName Name of project.
     * @return Status.OK if project is successfully deleted, Status.ERROR if project does not exist otherwise.
     */
    public Status deleteProjectByName(String projectName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(projectName).build();
        Response response = metadataServiceStub.deleteProjectByName(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Get a specific artifact in Metadata Store by artifact id.
     *
     * @param artifactId Id of artifact.
     * @return Single ArtifactMeta object if artifact exists, otherwise returns None if artifact does not exist.
     */
    public ArtifactMeta getArtifactById(Long artifactId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(artifactId).build();
        Response response = metadataServiceStub.getArtifactById(request);
        ArtifactProto.Builder builder = ArtifactProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildArtifactMeta(builder.build());
    }

    /**
     * Get a specific artifact in Metadata Store by artifact name.
     *
     * @param artifactName Name of artifact.
     * @return Single ArtifactMeta object if artifact exists, otherwise returns None if artifact does not exist.
     */
    public ArtifactMeta getArtifactByName(String artifactName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(artifactName).build();
        Response response = metadataServiceStub.getArtifactByName(request);
        ArtifactProto.Builder builder = ArtifactProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildArtifactMeta(builder.build());
    }

    /**
     * Register a artifact in Metadata Store.
     *
     * @param name         Name of artifact.
     * @param artifactType Type of artifact.
     * @param description  Description of artifact.
     * @param uri          Uri of artifact.
     * @param properties   Properties of artifact.
     * @return Single ArtifactMeta object registered in Metadata Store.
     */
    public ArtifactMeta registerArtifact(String name, String artifactType, String description, String uri,
                                         Map<String, String> properties) throws Exception {
        ArtifactProto artifactProto = ArtifactProto.newBuilder().setName(name).setArtifactType(stringValue(artifactType)).setDescription(stringValue(description))
                .setUri(stringValue(uri))
                .putAllProperties(properties).build();
        RegisterArtifactRequest request = RegisterArtifactRequest.newBuilder().setArtifact(artifactProto).build();
        Response response = metadataServiceStub.registerArtifact(request);
        ArtifactProto.Builder builder = ArtifactProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildArtifactMeta(builder.build());
    }

    /**
     * Update a artifact in Metadata Store.
     *
     * @param name         Name of artifact.
     * @param artifactType Type of artifact.
     * @param description  Description of artifact.
     * @param uri          Uri of artifact.
     * @param properties   Properties of artifact.
     * @return Single ArtifactMeta object registered in Metadata Store.
     */
    public ArtifactMeta updateArtifact(String name, String artifactType, String description, String uri,
                                       Map<String, String> properties) throws Exception {
        UpdateArtifactRequest.Builder artifactProto = UpdateArtifactRequest.newBuilder().setName(name).setArtifactType(stringValue(artifactType)).setDescription(stringValue(description))
                .setUri(stringValue(uri)).putAllProperties(properties);
        UpdateArtifactRequest request = artifactProto.build();
        Response response = metadataServiceStub.updateArtifact(request);
        ArtifactProto.Builder builder = ArtifactProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildArtifactMeta(builder.build());
    }

    /**
     * List registered artifacts in Metadata Store.
     *
     * @param pageSize Limitation of listed artifacts.
     * @param offset   Offset of listed artifacts.
     * @return List of ArtifactMeta object registered in Metadata Store.
     */
    public List<ArtifactMeta> listArtifact(Long pageSize, Long offset) throws Exception {
        ListRequest request = ListRequest.newBuilder().setPageSize(pageSize).setOffset(offset).build();
        Response response = metadataServiceStub.listArtifact(request);
        ArtifactListProto.Builder builder = ArtifactListProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildArtifactMetas(builder.build());
    }

    /**
     * Delete registered artifact by artifact id.
     *
     * @param artifactId Id of artifact.
     * @return Status.OK if artifact is successfully deleted, Status.ERROR if artifact does not exist otherwise.
     */
    public Status deleteArtifactById(Long artifactId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(artifactId).build();
        Response response = metadataServiceStub.deleteArtifactById(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Delete registered artifact by artifact name.
     *
     * @param artifactName Name of artifact.
     * @return Status.OK if artifact is successfully deleted, Status.ERROR if artifact does not exist otherwise.
     */
    public Status deleteArtifactByName(String artifactName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(artifactName).build();
        Response response = metadataServiceStub.deleteArtifactByName(request);
        return metadataDeleteResponse(response);
    }

    /***
     * Register a workflow in metadata store.
     *
     * @param name       The workflow name
     * @param projectId  The id of project which contains the workflow
     * @param properties The workflow properties
     * @return WorkflowMeta object registered in Metadata Store
     */
    public WorkflowMeta registerWorkflow(String name, Long projectId,
                                         Map<String, String> properties) throws Exception {
        WorkflowMetaProto workflowProto = WorkflowMetaProto.newBuilder().setName(name).setProjectId(int64Value(projectId))
                .putAllProperties(properties).build();
        RegisterWorkflowRequest request = RegisterWorkflowRequest.newBuilder().setWorkflow(workflowProto).build();
        Response response = metadataServiceStub.registerWorkflow(request);
        WorkflowMetaProto.Builder builder = WorkflowMetaProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildWorkflowMeta(builder.build());
    }

    /***
     * Get a workflow by specific project name and workflow name
     *
     * @param projectName   The name of project which contains the workflow
     * @param workflowName  The workflow name
     * @return WorkflowMeta object registered in Metadata Store
     */
    public WorkflowMeta getWorkflowByName(String projectName, String workflowName) throws Exception {
        WorkflowNameRequest request = WorkflowNameRequest.newBuilder().setProjectName(projectName).setWorkflowName(workflowName).build();
        Response response = metadataServiceStub.getWorkflowByName(request);
        WorkflowMetaProto.Builder builder = WorkflowMetaProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ?
                null: buildWorkflowMeta(builder.build());
    }

    /***
     * Get a workflow by uuid
     *
     * @param workflowId The workflow id
     * @return WorkflowMeta object registered in Metadata Store
     */
    public WorkflowMeta getWorkflowById(Long workflowId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(workflowId).build();
        Response response = metadataServiceStub.getWorkflowById(request);
        WorkflowMetaProto.Builder builder = WorkflowMetaProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ?
                null : buildWorkflowMeta(builder.build());
    }

    /***
     * List all workflows of the specific project
     *
     * @param projectName  The name of project which contains the workflow
     * @param pageSize     Limitation of listed workflows.
     * @param offset       Offset of listed workflows.
     * @return
     */
    public List<WorkflowMeta> listWorkflows(String projectName, Long pageSize, Long offset) throws Exception {
        ListWorkflowsRequest request = ListWorkflowsRequest.newBuilder()
                .setProjectName(projectName).setPageSize(pageSize).setOffset(offset).build();
        Response response = metadataServiceStub.listWorkflows(request);
        WorkflowListProto.Builder builder = WorkflowListProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildWorkflowMetas(builder.build());
    }

    /***
     * Delete the workflow by specific project and workflow name
     *
     * @param projectName  The name of project which contains the workflow
     * @param workflowName The workflow name
     * @return Status.OK if workflow is successfully deleted, Status.ERROR if workflow does not exist otherwise.
     */
    public Status deleteWorkflowByName(String projectName, String workflowName) throws Exception {
        WorkflowNameRequest request = WorkflowNameRequest.newBuilder()
                .setProjectName(projectName).setWorkflowName(workflowName).build();
        Response response = metadataServiceStub.deleteWorkflowByName(request);
        return metadataDeleteResponse(response);
    }


    /**
     * Delete the workflow by specific uuid.
     *
     * @param workflowId Id of worflow.
     * @return Status.OK if workflow is successfully deleted, Status.ERROR if workflow does not exist otherwise.
     */
    public Status deleteWorkflowById(Long workflowId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(workflowId).build();
        Response response = metadataServiceStub.deleteWorkflowById(request);
        return metadataDeleteResponse(response);
    }

    /***
     * Update the workflow
     *
     * @param workflowName The workflow name
     * @param projectName  The name of project which contains the workflow
     * @param properties   Properties needs to be updated
     * @return WorkflowMeta object registered in Metadata Store
     */
    public WorkflowMeta updateWorkflow(String workflowName, String projectName, Map<String,
            String> properties) throws Exception {
        UpdateWorkflowRequest request = UpdateWorkflowRequest.newBuilder().setWorkflowName(workflowName)
                .setProjectName(projectName).putAllProperties(properties).build();
        Response response = metadataServiceStub.updateWorkflow(request);
        WorkflowMetaProto.Builder builder = WorkflowMetaProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildWorkflowMeta(builder.build());
    }
}