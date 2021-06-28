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
import static com.aiflow.entity.JobMeta.buildJobMeta;
import static com.aiflow.entity.JobMeta.buildJobMetas;
import static com.aiflow.entity.ModelMeta.buildModelMeta;
import static com.aiflow.entity.ModelRelationMeta.buildModelRelationMeta;
import static com.aiflow.entity.ModelRelationMeta.buildModelRelationMetas;
import static com.aiflow.entity.ModelVersionMeta.buildModelVersionMeta;
import static com.aiflow.entity.ModelVersionRelationMeta.buildModelVersionRelationMeta;
import static com.aiflow.entity.ModelVersionRelationMeta.buildModelVersionRelationMetas;
import static com.aiflow.entity.ProjectMeta.buildProjectMeta;
import static com.aiflow.entity.ProjectMeta.buildProjectMetas;
import static com.aiflow.entity.WorkflowExecutionMeta.buildWorkflowExecutionMeta;
import static com.aiflow.entity.WorkflowExecutionMeta.buildWorkflowExecutionMetas;
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
     * Get a specific workflow execution in Metadata Store by workflow execution id.
     *
     * @param executionId Id of workflow execution.
     * @return Single WorkflowExecutionMeta object if workflow execution exists, otherwise returns None if workflow execution does not exist.
     */
    public WorkflowExecutionMeta getWorkFlowExecutionById(Long executionId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(executionId).build();
        Response response = metadataServiceStub.getWorkFlowExecutionById(request);
        WorkflowExecutionProto.Builder builder = WorkflowExecutionProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildWorkflowExecutionMeta(builder.build());
    }

    /**
     * Get a specific workflow execution in Metadata Store by workflow execution name.
     *
     * @param executionName Name of workflow execution.
     * @return Single WorkflowExecutionMeta object if workflow execution exists, otherwise returns None if workflow execution does not exist.
     */
    public WorkflowExecutionMeta getWorkFlowExecutionByName(String executionName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(executionName).build();
        Response response = metadataServiceStub.getWorkFlowExecutionByName(request);
        WorkflowExecutionProto.Builder builder = WorkflowExecutionProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildWorkflowExecutionMeta(builder.build());
    }

    /**
     * Register a workflow execution in Metadata Store.
     *
     * @param name           Mame of workflow execution.
     * @param executionState State of workflow execution.
     * @param projectId      Project id corresponded to workflow execution.
     * @param properties     Properties of workflow execution.
     * @param startTime      Time when workflow execution started.
     * @param endTime        Time when workflow execution ended.
     * @param logUri         Log uri of workflow execution.
     * @param workflowJson   Workflow json of workflow execution.
     * @param signature      Signature of workflow execution.
     * @return Single WorkflowExecutionMeta object registered in Metadata Store.
     */
    public WorkflowExecutionMeta registerWorkFlowExecution(String name, State executionState, Long projectId,
                                                           Map<String, String> properties, Long startTime, Long endTime, String logUri, String workflowJson, String signature) throws Exception {
        WorkflowExecutionProto.Builder workflowExecutionProto = WorkflowExecutionProto.newBuilder().setName(name).setProjectId(int64Value(projectId)).putAllProperties(properties)
                .setStartTime(int64Value(startTime)).setEndTime(int64Value(endTime)).setLogUri(stringValue(logUri)).setWorkflowJson(stringValue(workflowJson)).setSignature(stringValue(signature));
        if (executionState != null) {
            workflowExecutionProto.setExecutionState(executionState.getExecutionState());
        }
        RegisterWorkFlowExecutionRequest request = RegisterWorkFlowExecutionRequest.newBuilder().setWorkflowExecution(workflowExecutionProto).build();
        Response response = metadataServiceStub.registerWorkFlowExecution(request);
        WorkflowExecutionProto.Builder builder = WorkflowExecutionProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildWorkflowExecutionMeta(builder.build());
    }

    /**
     * Update a workflow execution in Metadata Store.
     *
     * @param name           Mame of workflow execution.
     * @param executionState State of workflow execution.
     * @param projectId      Project id corresponded to workflow execution.
     * @param properties     Properties of workflow execution.
     * @param endTime        Time when workflow execution ended.
     * @param logUri         Log uri of workflow execution.
     * @param workflowJson   Workflow json of workflow execution.
     * @param signature      Signature of workflow execution.
     * @return Single WorkflowExecutionMeta object registered in Metadata Store.
     */
    public WorkflowExecutionMeta updateWorkFlowExecution(String name, State executionState, Long projectId,
                                                         Map<String, String> properties, Long endTime, String logUri, String workflowJson, String signature) throws Exception {
        UpdateWorkflowExecutionRequest.Builder workflowExecutionProto = UpdateWorkflowExecutionRequest.newBuilder().setName(name).setProjectId(int64Value(projectId)).putAllProperties(properties)
                .setEndTime(int64Value(endTime)).setLogUri(stringValue(logUri)).setWorkflowJson(stringValue(workflowJson)).setSignature(stringValue(signature));
        if (executionState != null) {
            workflowExecutionProto.setExecutionState(executionState.getExecutionState());
        }
        UpdateWorkflowExecutionRequest request = workflowExecutionProto.build();
        Response response = metadataServiceStub.updateWorkflowExecution(request);
        WorkflowExecutionProto.Builder builder = WorkflowExecutionProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildWorkflowExecutionMeta(builder.build());
    }

    /**
     * List registered workflow executions in Metadata Store.
     *
     * @param pageSize Limitation of listed workflow executions.
     * @param offset   Offset of listed workflow executions.
     * @return List of WorkflowExecutionMeta object registered in Metadata Store.
     */
    public List<WorkflowExecutionMeta> listWorkFlowExecution(Long pageSize, Long offset) throws Exception {
        ListRequest request = ListRequest.newBuilder().setPageSize(pageSize).setOffset(offset).build();
        Response response = metadataServiceStub.listWorkFlowExecution(request);
        WorkFlowExecutionListProto.Builder builder = WorkFlowExecutionListProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildWorkflowExecutionMetas(builder.build());
    }

    /**
     * Update workflow execution end time in Metadata Store.
     *
     * @param endTime       Time when workflow execution ended.
     * @param executionName Name of workflow execution.
     * @return Workflow execution uuid if workflow execution is successfully updated, raise an exception, if fail to update otherwise.
     */
    public WorkflowExecutionMeta updateWorkflowExecutionEndTime(Long endTime, String executionName) throws Exception {
        UpdateWorkflowExecutionEndTimeRequest request = UpdateWorkflowExecutionEndTimeRequest.newBuilder().setEndTime(endTime).setName(executionName).build();
        Response response = metadataServiceStub.updateWorkflowExecutionEndTime(request);
        WorkflowExecutionProto.Builder builder = WorkflowExecutionProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildWorkflowExecutionMeta(builder.build());
    }

    /**
     * Update workflow execution state in Metadata Store.
     *
     * @param executionState State of workflow execution.
     * @param executionName  Name of workflow execution.
     * @return Workflow execution uuid if workflow execution is successfully updated, raise an exception, if fail to update otherwise.
     */
    public WorkflowExecutionMeta updateWorkflowExecutionState(State executionState, String executionName) throws Exception {
        UpdateWorkflowExecutionStateRequest request = UpdateWorkflowExecutionStateRequest.newBuilder().setState(executionState.getExecutionState()).setName(executionName).build();
        Response response = metadataServiceStub.updateWorkflowExecutionState(request);
        WorkflowExecutionProto.Builder builder = WorkflowExecutionProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildWorkflowExecutionMeta(builder.build());
    }

    /**
     * Delete registered workflow execution by workflow execution id.
     *
     * @param executionId Id of workflow execution.
     * @return Status.OK if workflow execution is successfully deleted, Status.ERROR if workflow execution does not exist otherwise.
     */
    public Status deleteWorkflowExecutionById(Long executionId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(executionId).build();
        Response response = metadataServiceStub.deleteWorkflowExecutionById(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Delete registered workflow execution by workflow execution name.
     *
     * @param executionName Name of workflow execution.
     * @return Status.OK if workflow execution is successfully deleted, Status.ERROR if workflow execution does not exist otherwise.
     */
    public Status deleteWorkflowExecutionByName(String executionName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(executionName).build();
        Response response = metadataServiceStub.deleteWorkflowExecutionByName(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Get a specific job in Metadata Store by job id.
     *
     * @param jobId Id of job.
     * @return Single JobMeta object if job exists, otherwise returns None if job does not exist.
     */
    public JobMeta getJobById(Long jobId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(jobId).build();
        Response response = metadataServiceStub.getJobById(request);
        JobProto.Builder builder = JobProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildJobMeta(builder.build());
    }

    /**
     * Get a specific job in Metadata Store by job name.
     *
     * @param jobName Name of job.
     * @return Single JobMeta object if job exists, otherwise returns None if job does not exist.
     */
    public JobMeta getJobByName(String jobName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(jobName).build();
        Response response = metadataServiceStub.getJobByName(request);
        JobProto.Builder builder = JobProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildJobMeta(builder.build());
    }

    /**
     * Register a job in Metadata Store.
     *
     * @param name                Mame of job.
     * @param jobState            State of job.
     * @param workflowExecutionId Workflow execution id corresponded to job.
     * @param properties          Properties of job.
     * @param jobId               Job id of job.
     * @param startTime           Time when job started.
     * @param endTime             Time when job ended.
     * @param logUri              Log uri of job.
     * @param signature           Signature of job.
     * @return Single JobMeta object registered in Metadata Store.
     */
    public JobMeta registerJob(String name, State jobState, Long workflowExecutionId, Map<String, String> properties,
                               String jobId, Long startTime, Long endTime, String logUri, String signature) throws Exception {
        JobProto jobProto = JobProto.newBuilder().setName(name).setJobState(jobState.getExecutionState())
                .setWorkflowExecutionId(int64Value(workflowExecutionId)).putAllProperties(properties).setJobId(stringValue(jobId))
                .setStartTime(int64Value(startTime)).setEndTime(int64Value(endTime)).setLogUri(stringValue(logUri))
                .setSignature(stringValue(signature)).build();
        RegisterJobRequest request = RegisterJobRequest.newBuilder().setJob(jobProto).build();
        Response response = metadataServiceStub.registerJob(request);
        JobProto.Builder builder = JobProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildJobMeta(builder.build());
    }

    /**
     * Update a job in Metadata Store.
     *
     * @param name                Mame of job.
     * @param jobState            State of job.
     * @param workflowExecutionId Workflow execution id corresponded to job.
     * @param properties          Properties of job.
     * @param jobId               Job id of job.
     * @param endTime             Time when job ended.
     * @param logUri              Log uri of job.
     * @param signature           Signature of job.
     * @return Single JobMeta object registered in Metadata Store.
     */
    public JobMeta updateJob(String name, State jobState, Long workflowExecutionId, Map<String, String> properties,
                             String jobId, Long endTime, String logUri, String signature) throws Exception {
        UpdateJobRequest.Builder jobProto = UpdateJobRequest.newBuilder().setName(name).setJobState(jobState.getExecutionState())
                .setWorkflowExecutionId(int64Value(workflowExecutionId)).putAllProperties(properties).setJobId(stringValue(jobId))
                .setEndTime(int64Value(endTime)).setLogUri(stringValue(logUri)).setSignature(stringValue(signature));
        UpdateJobRequest request = jobProto.build();
        Response response = metadataServiceStub.updateJob(request);
        JobProto.Builder builder = JobProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildJobMeta(builder.build());
    }

    /**
     * List registered jobs in Metadata Store.
     *
     * @param pageSize Limitation of listed jobs.
     * @param offset   Offset of listed jobs.
     * @return List of JobMeta object registered in Metadata Store.
     */
    public List<JobMeta> listJob(Long pageSize, Long offset) throws Exception {
        ListRequest request = ListRequest.newBuilder().setPageSize(pageSize).setOffset(offset).build();
        Response response = metadataServiceStub.listJob(request);
        JobListProto.Builder builder = JobListProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildJobMetas(builder.build());
    }

    /**
     * Update job end time in Metadata Store.
     *
     * @param endTime Time when job ended.
     * @param jobName Name of job.
     * @return Job uuid if job is successfully updated, raise an exception, if fail to update otherwise.
     */
    public JobMeta updateJobEndTime(Long endTime, String jobName) throws Exception {
        UpdateJobEndTimeRequest request = UpdateJobEndTimeRequest.newBuilder().setEndTime(endTime).setName(jobName).build();
        Response response = metadataServiceStub.updateJobEndTime(request);
        JobProto.Builder builder = JobProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildJobMeta(builder.build());
    }

    /**
     * Update job state in Metadata Store.
     *
     * @param state   State of job.
     * @param jobName Name of job.
     * @return Job uuid if job is successfully updated, raise an exception, if fail to update otherwise.
     */
    public JobMeta updateJobState(State state, String jobName) throws Exception {
        UpdateJobStateRequest request = UpdateJobStateRequest.newBuilder().setState(state.getExecutionState()).setName(jobName).build();
        Response response = metadataServiceStub.updateJobState(request);
        JobProto.Builder builder = JobProto.newBuilder();
        return StringUtils.isEmpty(metadataDetailResponse(response, this.parser, builder)) ? null : buildJobMeta(builder.build());
    }

    /**
     * Delete registered job by job id.
     *
     * @param jobId Id of job.
     * @return Status.OK if job is successfully deleted, Status.ERROR if job does not exist otherwise.
     */
    public Status deleteJobById(Long jobId) throws Exception {
        IdRequest request = IdRequest.newBuilder().setId(jobId).build();
        Response response = metadataServiceStub.deleteJobById(request);
        return metadataDeleteResponse(response);
    }

    /**
     * Delete registered job by job name.
     *
     * @param jobName Name of job.
     * @return Status.OK if job is successfully deleted, Status.ERROR if job does not exist otherwise.
     */
    public Status deleteJobByName(String jobName) throws Exception {
        NameRequest request = NameRequest.newBuilder().setName(jobName).build();
        Response response = metadataServiceStub.deleteJobByName(request);
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
}