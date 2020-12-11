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

import com.aiflow.proto.Message.ArtifactProto;
import com.aiflow.proto.MetadataServiceOuterClass.ArtifactListProto;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class ArtifactMeta {

    private Long uuid;
    private String name;
    private String dataFormat;
    private String description;
    private String batchUri;
    private String streamUri;
    private Long createTime;
    private Long updateTime;
    private Map<String, String> properties;

    public ArtifactMeta() {
    }

    public ArtifactMeta(Long uuid, String name, String dataFormat, String description, String batchUri, String streamUri, Long createTime, Long updateTime, Map<String, String> properties) {
        this.uuid = uuid;
        this.name = name;
        this.dataFormat = dataFormat;
        this.description = description;
        this.batchUri = batchUri;
        this.streamUri = streamUri;
        this.createTime = createTime;
        this.updateTime = updateTime;
        this.properties = properties;
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

    public String getDataFormat() {
        return dataFormat;
    }

    public void setDataFormat(String dataFormat) {
        this.dataFormat = dataFormat;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getBatchUri() {
        return batchUri;
    }

    public void setBatchUri(String batchUri) {
        this.batchUri = batchUri;
    }

    public String getStreamUri() {
        return streamUri;
    }

    public void setStreamUri(String streamUri) {
        this.streamUri = streamUri;
    }

    public Long getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Long createTime) {
        this.createTime = createTime;
    }

    public Long getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(Long updateTime) {
        this.updateTime = updateTime;
    }

    public Map<String, String> getProperties() {
        return properties;
    }

    public void setProperties(Map<String, String> properties) {
        this.properties = properties;
    }

    @Override
    public String toString() {
        return "ArtifactMeta{" +
                "uuid=" + uuid +
                ", name='" + name + '\'' +
                ", dataFormat='" + dataFormat + '\'' +
                ", description='" + description + '\'' +
                ", batchUri='" + batchUri + '\'' +
                ", streamUri='" + streamUri + '\'' +
                ", createTime=" + createTime +
                ", updateTime=" + updateTime +
                ", properties=" + properties +
                '}';
    }

    public static ArtifactMeta buildArtifactMeta(ArtifactProto artifactProto) {
        return artifactProto == null ? null : new ArtifactMeta(artifactProto.getUuid(),
                artifactProto.getName(),
                artifactProto.getDataFormat().getValue(),
                artifactProto.getDescription().getValue(),
                artifactProto.getBatchUri().getValue(),
                artifactProto.getStreamUri().getValue(),
                artifactProto.getCreateTime().getValue(),
                artifactProto.getUpdateTime().getValue(),
                artifactProto.getPropertiesMap());
    }

    public static List<ArtifactMeta> buildArtifactMetas(ArtifactListProto artifactListProto) {
        if (artifactListProto == null) {
            return null;
        } else {
            List<ArtifactMeta> artifactMetas = new ArrayList<>();
            for (ArtifactProto artifactProto : artifactListProto.getArtifactsList()) {
                artifactMetas.add(buildArtifactMeta(artifactProto));
            }
            return artifactMetas;
        }
    }
}

