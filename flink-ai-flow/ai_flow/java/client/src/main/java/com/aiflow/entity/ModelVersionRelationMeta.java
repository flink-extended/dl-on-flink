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

import com.aiflow.proto.Message.ModelVersionRelationProto;
import com.aiflow.proto.MetadataServiceOuterClass.ModelVersionRelationListProto;

import java.util.ArrayList;
import java.util.List;

public class ModelVersionRelationMeta {

    private String version;
    private Long modelId;
    private Long projectSnapshotId;

    public ModelVersionRelationMeta() {
    }

    public ModelVersionRelationMeta(String version, Long modelId, Long projectSnapshotId) {
        this.version = version;
        this.modelId = modelId;
        this.projectSnapshotId = projectSnapshotId;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public Long getModelId() {
        return modelId;
    }

    public void setModelId(Long modelId) {
        this.modelId = modelId;
    }

    public Long getProjectSnapshotId() {
        return projectSnapshotId;
    }

    public void setProjectSnapshotId(Long projectSnapshotId) {
        this.projectSnapshotId = projectSnapshotId;
    }

    @Override
    public String toString() {
        return "ModelVersionRelationMeta{" +
                "version='" + version + '\'' +
                ", modelId=" + modelId +
                ", projectSnapshotId=" + projectSnapshotId +
                '}';
    }

    public static ModelVersionRelationMeta buildModelVersionRelationMeta(ModelVersionRelationProto modelVersionRelationProto) {
        return modelVersionRelationProto == null ? null : new ModelVersionRelationMeta(modelVersionRelationProto.getVersion().getValue(),
                modelVersionRelationProto.getModelId().getValue(), modelVersionRelationProto.getProjectSnapshotId().getValue());
    }

    public static List<ModelVersionRelationMeta> buildModelVersionRelationMetas(ModelVersionRelationListProto modelVersionRelationListProto) {
        if (modelVersionRelationListProto == null) {
            return null;
        } else {
            List<ModelVersionRelationMeta> modelVersionRelationMetas = new ArrayList<>();
            for (ModelVersionRelationProto modelRelationProto : modelVersionRelationListProto.getModelVersionsList()) {
                modelVersionRelationMetas.add(buildModelVersionRelationMeta(modelRelationProto));
            }
            return modelVersionRelationMetas;
        }
    }
}