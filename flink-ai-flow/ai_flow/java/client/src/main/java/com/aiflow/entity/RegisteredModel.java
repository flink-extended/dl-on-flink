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
package com.aiflow.entity;

import com.aiflow.common.ModelType;
import com.aiflow.proto.Message.ModelMetaParam;
import com.aiflow.proto.Message.RegisteredModelDetail;
import com.aiflow.proto.Message.RegisteredModelMeta;
import com.aiflow.proto.Message.RegisteredModelMetas;

import java.util.ArrayList;
import java.util.List;

public class RegisteredModel {

    private String modelName;
    private ModelType modelType;
    private String modelDesc;
    private ModelVersion modelVersion;

    public RegisteredModel() {
    }

    public RegisteredModel(String modelName) {
        this.modelName = modelName;
    }

    public RegisteredModel(String modelName, ModelType modelType, String modelDesc) {
        this.modelName = modelName;
        this.modelType = modelType;
        this.modelDesc = modelDesc;
    }

    public RegisteredModel(String modelName, ModelType modelType, String modelDesc, ModelVersion modelVersion) {
        this.modelName = modelName;
        this.modelType = modelType;
        this.modelDesc = modelDesc;
        this.modelVersion = modelVersion;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public ModelType getModelType() {
        return modelType;
    }

    public void setModelType(ModelType modelType) {
        this.modelType = modelType;
    }

    public String getModelDesc() {
        return modelDesc;
    }

    public void setModelDesc(String modelDesc) {
        this.modelDesc = modelDesc;
    }

    public ModelVersion getModelVersion() {
        return modelVersion;
    }

    public void setModelVersion(ModelVersion modelVersion) {
        this.modelVersion = modelVersion;
    }

    @Override
    public String toString() {
        return "RegisteredModel{" +
                "modelName='" + modelName + '\'' +
                ", modelType=" + modelType +
                ", modelDesc='" + modelDesc + '\'' +
                ", modelVersion=" + modelVersion +
                '}';
    }

    public static RegisteredModel buildRegisteredModel(ModelMetaParam modelMetaParam) {
        return modelMetaParam == null ? null : new RegisteredModel(modelMetaParam.getModelName().getValue());
    }

    public static RegisteredModel buildRegisteredModel(RegisteredModelMeta registeredModelMeta) {
        return registeredModelMeta == null ? null : new RegisteredModel(registeredModelMeta.getModelName(),
                ModelType.getModelType(registeredModelMeta.getModelType()),
                registeredModelMeta.getModelDesc().getValue());
    }

    public static RegisteredModel buildRegisteredModel(RegisteredModelDetail registeredModelDetail) {
        return registeredModelDetail == null ? null : new RegisteredModel(registeredModelDetail.getRegisteredModel().getModelName(),
                ModelType.getModelType(registeredModelDetail.getRegisteredModel().getModelType()),
                registeredModelDetail.getRegisteredModel().getModelDesc().getValue(),
                ModelVersion.buildModelVersion(registeredModelDetail.getModelVersion()));
    }

    public static List<RegisteredModel> buildRegisteredModels(RegisteredModelMetas registeredModelMetas) {
        if (registeredModelMetas == null) {
            return null;
        } else {
            List<RegisteredModel> registeredModels = new ArrayList<>();
            for (RegisteredModelMeta registeredModelMeta : registeredModelMetas.getRegisteredModelsList()) {
                registeredModels.add(buildRegisteredModel(registeredModelMeta));
            }
            return registeredModels;
        }
    }
}