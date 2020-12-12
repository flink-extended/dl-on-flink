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

import com.aiflow.proto.Message.ModelVersionProto;

public class ModelVersionMeta {

    private String version;
    private String modelPath;
    private String modelMetric;
    private String modelFlavor;
    private String versionDesc;
    private Long modelId;
    private Long workflowExecutionId;

    public ModelVersionMeta() {
    }

    public ModelVersionMeta(String version, String modelPath, String modelMetric, String modelFlavor, String versionDesc, Long modelId, Long workflowExecutionId) {
        this.version = version;
        this.modelPath = modelPath;
        this.modelMetric = modelMetric;
        this.modelFlavor = modelFlavor;
        this.versionDesc = versionDesc;
        this.modelId = modelId;
        this.workflowExecutionId = workflowExecutionId;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getModelPath() {
        return modelPath;
    }

    public void setModelPath(String modelPath) {
        this.modelPath = modelPath;
    }

    public String getModelMetric() {
        return modelMetric;
    }

    public void setModelMetric(String modelMetric) {
        this.modelMetric = modelMetric;
    }

    public String getModelFlavor() {
        return modelFlavor;
    }

    public void setModelFlavor(String modelFlavor) {
        this.modelFlavor = modelFlavor;
    }

    public String getVersionDesc() {
        return versionDesc;
    }

    public void setVersionDesc(String versionDesc) {
        this.versionDesc = versionDesc;
    }

    public Long getModelId() {
        return modelId;
    }

    public void setModelId(Long modelId) {
        this.modelId = modelId;
    }

    public Long getWorkflowExecutionId() {
        return workflowExecutionId;
    }

    public void setWorkflowExecutionId(Long workflowExecutionId) {
        this.workflowExecutionId = workflowExecutionId;
    }

    @Override
    public String toString() {
        return "ModelVersionMeta{" +
                "version='" + version + '\'' +
                ", modelPath='" + modelPath + '\'' +
                ", modelMetric='" + modelMetric + '\'' +
                ", modelFlavor='" + modelFlavor + '\'' +
                ", versionDesc='" + versionDesc + '\'' +
                ", modelId=" + modelId +
                ", workflowExecutionId=" + workflowExecutionId +
                '}';
    }

    public static ModelVersionMeta buildModelVersionMeta(ModelVersionProto modelVersionProto) {
        return modelVersionProto == null ? null : new ModelVersionMeta(modelVersionProto.getVersion().getValue(),
                modelVersionProto.getModelPath().getValue(), modelVersionProto.getModelMetric().getValue(),
                modelVersionProto.getModelFlavor().getValue(), modelVersionProto.getVersionDesc().getValue(),
                modelVersionProto.getModelId().getValue(), modelVersionProto.getWorkflowExecutionId().getValue());
    }
}