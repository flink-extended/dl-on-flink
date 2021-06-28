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

import com.aiflow.common.ModelStage;
import com.aiflow.entity.ModelVersion;
import com.aiflow.entity.RegisteredModel;
import com.aiflow.proto.Message.*;
import com.aiflow.proto.ModelCenterServiceGrpc;
import com.aiflow.proto.ModelCenterServiceGrpc.ModelCenterServiceBlockingStub;
import com.aiflow.proto.ModelCenterServiceOuterClass.*;
import com.google.protobuf.util.JsonFormat.Parser;
import io.grpc.Channel;
import io.grpc.ManagedChannelBuilder;
import org.apache.commons.lang3.StringUtils;

import java.util.List;

import static com.aiflow.common.Constant.SERVER_URI;
import static com.aiflow.entity.ModelVersion.buildModelVersion;
import static com.aiflow.entity.RegisteredModel.buildRegisteredModel;
import static com.aiflow.entity.RegisteredModel.buildRegisteredModels;
import static com.aiflow.util.Transform.buildResponse;
import static com.aiflow.util.Transform.stringValue;
import static com.google.protobuf.util.JsonFormat.parser;

/**
 * Client of AIFlow Rest Endpoint that provides Model Center function service.
 */
public class ModelCenterClient {

    private final ModelCenterServiceBlockingStub modelCenterServiceStub;

    private final Parser parser = parser().ignoringUnknownFields();

    public ModelCenterClient() {
        this(SERVER_URI);
    }

    public ModelCenterClient(String target) {
        this(ManagedChannelBuilder.forTarget(target).usePlaintext().build());
    }

    public ModelCenterClient(Channel channel) {
        this.modelCenterServiceStub = ModelCenterServiceGrpc.newBlockingStub(channel);
    }

    /**
     * Create a new registered model from given type in Model Center.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend store.
     * @param modelDesc (Optional) Description of registered model.
     * @return Object of RegisteredModel created in Model Center.
     */
    public RegisteredModel createRegisteredModel(String modelName, String modelDesc) throws Exception {
        RegisteredModelParam.Builder modelParam = RegisteredModelParam.newBuilder().setModelName(stringValue(modelName)).setModelDesc(stringValue(modelDesc));
        CreateRegisteredModelRequest request = CreateRegisteredModelRequest.newBuilder().setRegisteredModel(modelParam).build();
        Response response = this.modelCenterServiceStub.createRegisteredModel(request);
        RegisteredModelMeta.Builder builder = RegisteredModelMeta.newBuilder();
        return StringUtils.isEmpty(buildResponse(response, this.parser, builder)) ? null : buildRegisteredModel(builder.build());
    }

    /**
     * Update metadata for RegisteredModel entity backend. Either ``modelName``  or ``modelDesc``
     * should be non-None. Backend raises exception if a registered model with given name does not exist.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend store.
     * @param newName   (Optional) New proposed name for the registered model.
     * @param modelDesc (Optional) Description of registered model.
     * @return Object of RegisteredModel updated in Model Center.
     */
    public RegisteredModel updateRegisteredModel(String modelName, String newName, String modelDesc) throws Exception {
        RegisteredModelParam.Builder param = RegisteredModelParam.newBuilder().setModelName(stringValue(newName))
                .setModelDesc(stringValue(modelDesc));
        UpdateRegisteredModelRequest request = UpdateRegisteredModelRequest.newBuilder()
                .setModelMeta(ModelMetaParam.newBuilder().setModelName(stringValue(modelName))).setRegisteredModel(param).build();
        Response response = this.modelCenterServiceStub.updateRegisteredModel(request);
        RegisteredModelMeta.Builder builder = RegisteredModelMeta.newBuilder();
        return StringUtils.isEmpty(buildResponse(response, this.parser, builder)) ? null : buildRegisteredModel(builder.build());
    }

    /**
     * Delete registered model by model name in Model Center backend.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend store.
     * @return Object of RegisteredModel deleted in Model Center.
     */
    public RegisteredModel deleteRegisteredModel(String modelName) throws Exception {
        DeleteRegisteredModelRequest request = DeleteRegisteredModelRequest.newBuilder()
                .setModelMeta(ModelMetaParam.newBuilder().setModelName(stringValue(modelName))).build();
        Response response = this.modelCenterServiceStub.deleteRegisteredModel(request);
        ModelMetaParam.Builder builder = ModelMetaParam.newBuilder();
        return StringUtils.isEmpty(buildResponse(response, this.parser, builder)) ? null : buildRegisteredModel(builder.build());
    }

    /**
     * List of all registered models in Model Center backend.
     *
     * @return List of RegisteredModel created in Model Center.
     */
    public List<RegisteredModel> listRegisteredModels() throws Exception {
        ListRegisteredModelsRequest request = ListRegisteredModelsRequest.newBuilder().build();
        Response response = modelCenterServiceStub.listRegisteredModels(request);
        RegisteredModelMetas.Builder builder = RegisteredModelMetas.newBuilder();
        return StringUtils.isEmpty(buildResponse(response, this.parser, builder)) ? null : buildRegisteredModels(builder.build());
    }

    /**
     * Get registered model detail filter by model name for Model Center.
     *
     * @param modelName Name of registered model. This is expected to be unique in the backend store.
     * @return Object of RegisteredModel created in Model Center.
     */
    public RegisteredModel getRegisteredModelDetail(String modelName) throws Exception {
        GetRegisteredModelDetailRequest request = GetRegisteredModelDetailRequest.newBuilder()
                .setModelMeta(ModelMetaParam.newBuilder().setModelName(stringValue(modelName))).build();
        Response response = this.modelCenterServiceStub.getRegisteredModelDetail(request);
        RegisteredModelDetail.Builder builder = RegisteredModelDetail.newBuilder();
        return StringUtils.isEmpty(buildResponse(response, this.parser, builder)) ? null : buildRegisteredModel(builder.build());
    }

    /**
     * Create a new registered model from given type in Model Center.
     *
     * @param modelName   Name of registered model. This is expected to be unique in the backend store.
     * @param modelPath   Source path where the AIFlow model is stored.
     * @param modelType (Optional) Type of AIFlow registered model option.
     * @param versionDesc (Optional) Description of registered model version.
     * @return Object of ModelVersion created in Model Center.
     */
    public ModelVersion createModelVersion(String modelName, String modelPath, String modelType, String versionDesc) throws Exception {
        CreateModelVersionRequest request = CreateModelVersionRequest.newBuilder()
                .setModelMeta(ModelMetaParam.newBuilder().setModelName(stringValue(modelName)))
                .setModelVersion(ModelVersionParam.newBuilder().setModelPath(stringValue(modelPath))
                        .setModelType(stringValue(modelType)).setVersionDesc(stringValue(versionDesc))
                        .setCurrentStage(ModelStage.GENERATED.getModelStage())).build();
        Response response = this.modelCenterServiceStub.createModelVersion(request);
        ModelVersionMeta.Builder builder = ModelVersionMeta.newBuilder();
        return StringUtils.isEmpty(buildResponse(response, this.parser, builder)) ? null : buildModelVersion(builder.build());
    }

    /**
     * Update metadata for ModelVersion entity and metadata associated with a model version in backend.
     * Either ``modelPath`` or ``modelType`` or ``versionDesc`` should be non-None.
     * Backend raises exception if a registered model with given name does not exist.
     *
     * @param modelName    Name of registered model. This is expected to be unique in the backend store.
     * @param modelVersion User-defined version of registered model.
     * @param modelPath    (Optional) Source path where the AIFlow model is stored.
     * @param modelType    (Optional) Type of AIFlow registered model option.
     * @param versionDesc  (Optional) Description of registered model version.
     * @param currentStage (Optional) Current stage for registered model version.
     * @return Object of ModelVersion updated in Model Center.
     */
    public ModelVersion updateModelVersion(String modelName, String modelVersion, String modelPath, String modelType, String versionDesc, ModelStage currentStage) throws Exception {
        ModelVersionParam.Builder param = ModelVersionParam.newBuilder().setModelPath(stringValue(modelPath))
                .setModelType(stringValue(modelType)).setVersionDesc(stringValue(versionDesc));
        if (currentStage != null) {
            param.setCurrentStage(currentStage.getModelStage());
        }
        UpdateModelVersionRequest request = UpdateModelVersionRequest.newBuilder()
                .setModelMeta(ModelMetaParam.newBuilder().setModelName(stringValue(modelName)).setModelVersion(stringValue(modelVersion)))
                .setModelVersion(param).build();
        Response response = this.modelCenterServiceStub.updateModelVersion(request);
        ModelVersionMeta.Builder builder = ModelVersionMeta.newBuilder();
        return StringUtils.isEmpty(buildResponse(response, this.parser, builder)) ? null : buildModelVersion(builder.build());
    }

    /**
     * Delete model version by model name and version in Model Center backend.
     *
     * @param modelName    Name of registered model. This is expected to be unique in the backend store.
     * @param modelVersion User-defined version of registered model.
     * @return Object of ModelVersion deleted in Model Center.
     */
    public ModelVersion deleteModelVersion(String modelName, String modelVersion) throws Exception {
        DeleteModelVersionRequest request = DeleteModelVersionRequest.newBuilder()
                .setModelMeta(ModelMetaParam.newBuilder().setModelName(stringValue(modelName)).setModelVersion(stringValue(modelVersion))).build();
        Response response = this.modelCenterServiceStub.deleteModelVersion(request);
        ModelMetaParam.Builder builder = ModelMetaParam.newBuilder();
        return StringUtils.isEmpty(buildResponse(response, this.parser, builder)) ? null : buildModelVersion(builder.build());
    }

    /**
     * Get model version detail filter by model name and model version for Model Center.
     *
     * @param modelName    Name of registered model. This is expected to be unique in the backend store.
     * @param modelVersion User-defined version of registered model.
     * @return Object of ModelVersion created in Model Center.
     */
    public ModelVersion getModelVersionDetail(String modelName, String modelVersion) throws Exception {
        GetModelVersionDetailRequest request = GetModelVersionDetailRequest.newBuilder()
                .setModelMeta(ModelMetaParam.newBuilder().setModelName(stringValue(modelName)).setModelVersion(stringValue(modelVersion))).build();
        Response response = this.modelCenterServiceStub.getModelVersionDetail(request);
        ModelVersionMeta.Builder builder = ModelVersionMeta.newBuilder();
        return StringUtils.isEmpty(buildResponse(response, this.parser, builder)) ? null : buildModelVersion(builder.build());
    }
}