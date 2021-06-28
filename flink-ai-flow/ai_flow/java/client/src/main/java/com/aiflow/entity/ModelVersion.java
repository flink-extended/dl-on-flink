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

import com.aiflow.common.ModelStage;
import com.aiflow.proto.Message.ModelMetaParam;
import com.aiflow.proto.Message.ModelVersionMeta;
import com.aiflow.proto.Message.ModelVersionStatus;

public class ModelVersion {

    private String modelName;
    private String modelVersion;
    private String modelPath;
    private String modelType;
    private String versionDesc;
    private ModelVersionStatus versionStatus;
    private ModelStage currentStage;

    public ModelVersion() {
    }

    public ModelVersion(String modelName, String modelVersion) {
        this.modelName = modelName;
        this.modelVersion = modelVersion;
    }

    public ModelVersion(String modelName, String modelVersion, String modelPath, String modelType, String versionDesc, ModelVersionStatus versionStatus, ModelStage currentStage) {
        this.modelName = modelName;
        this.modelVersion = modelVersion;
        this.modelPath = modelPath;
        this.modelType = modelType;
        this.versionDesc = versionDesc;
        this.versionStatus = versionStatus;
        this.currentStage = currentStage;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public String getModelVersion() {
        return modelVersion;
    }

    public void setModelVersion(String modelVersion) {
        this.modelVersion = modelVersion;
    }

    public String getModelPath() {
        return modelPath;
    }

    public void setModelPath(String modelPath) {
        this.modelPath = modelPath;
    }

    public String getModelType() {
        return modelType;
    }

    public void setModelType(String modelType) {
        this.modelType = modelType;
    }

    public String getVersionDesc() {
        return versionDesc;
    }

    public void setVersionDesc(String versionDesc) {
        this.versionDesc = versionDesc;
    }

    public ModelVersionStatus getVersionStatus() {
        return versionStatus;
    }

    public void setVersionStatus(ModelVersionStatus versionStatus) {
        this.versionStatus = versionStatus;
    }

    public ModelStage getCurrentStage() {
        return currentStage;
    }

    public void setCurrentStage(ModelStage currentStage) {
        this.currentStage = currentStage;
    }

    @Override
    public String toString() {
        return "ModelVersion{" +
                "modelName='" + modelName + '\'' +
                ", modelVersion='" + modelVersion + '\'' +
                ", modelPath='" + modelPath + '\'' +
                ", modelType='" + modelType + '\'' +
                ", versionDesc='" + versionDesc + '\'' +
                ", versionStatus=" + versionStatus +
                ", currentStage=" + currentStage +
                '}';
    }

    public static ModelVersion buildModelVersion(ModelMetaParam modelMetaParam) {
        return modelMetaParam == null ? null : new ModelVersion(modelMetaParam.getModelName().getValue(),
                modelMetaParam.getModelVersion().getValue());
    }

    public static ModelVersion buildModelVersion(ModelVersionMeta modelVersionMeta) {
        return modelVersionMeta == null ? null : new ModelVersion(modelVersionMeta.getModelName(),
                modelVersionMeta.getModelVersion(), modelVersionMeta.getModelPath().getValue(),
                modelVersionMeta.getModelType().getValue(), modelVersionMeta.getVersionDesc().getValue(),
                modelVersionMeta.getVersionStatus(), ModelStage.getModelStage(modelVersionMeta.getCurrentStage()));
    }
}