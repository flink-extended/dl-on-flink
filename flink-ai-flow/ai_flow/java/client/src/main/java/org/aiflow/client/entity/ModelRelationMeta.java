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
package org.aiflow.client.entity;

import org.aiflow.proto.Message.ModelRelationProto;
import org.aiflow.proto.MetadataServiceOuterClass.ModelRelationListProto;

import java.util.ArrayList;
import java.util.List;

public class ModelRelationMeta {

    private Long uuid;
    private String name;
    private Long projectId;

    public ModelRelationMeta() {
    }

    public ModelRelationMeta(Long uuid, String name, Long projectId) {
        this.uuid = uuid;
        this.name = name;
        this.projectId = projectId;
    }

    public Long getUuid() {
        return uuid;
    }

    public void setUuid(Long uuid) {
        this.uuid = uuid;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Long getProjectId() {
        return projectId;
    }

    public void setProjectId(Long projectId) {
        this.projectId = projectId;
    }

    @Override
    public String toString() {
        return "ModelRelationMeta{" +
                "uuid=" + uuid +
                ", name='" + name + '\'' +
                ", projectId=" + projectId +
                '}';
    }

    public static ModelRelationMeta buildModelRelationMeta(ModelRelationProto modelRelationProto) {
        return modelRelationProto == null ? null : new ModelRelationMeta(modelRelationProto.getUuid(),
                modelRelationProto.getName(), modelRelationProto.getProjectId().getValue());
    }

    public static List<ModelRelationMeta> buildModelRelationMetas(ModelRelationListProto modelRelationListProto) {
        if (modelRelationListProto == null) {
            return null;
        } else {
            List<ModelRelationMeta> modelRelationMetas = new ArrayList<>();
            for (ModelRelationProto modelRelationProto : modelRelationListProto.getModelRelationsList()) {
                modelRelationMetas.add(buildModelRelationMeta(modelRelationProto));
            }
            return modelRelationMetas;
        }
    }
}