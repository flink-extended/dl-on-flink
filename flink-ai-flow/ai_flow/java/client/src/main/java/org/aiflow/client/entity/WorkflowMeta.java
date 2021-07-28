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

import org.aiflow.client.proto.Message;
import org.aiflow.client.proto.MetadataServiceOuterClass;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class WorkflowMeta {
    private Long uuid;
    private String name;
    private Long projectId;
    private Map<String, String> properties;
    private Long createTime;
    private Long updateTime;

    public WorkflowMeta() {}

    public WorkflowMeta(Long uuid, String name, Long projectId, Map<String, String> properties, Long createTime, Long updateTime) {
        this.uuid = uuid;
        this.name = name;
        this.projectId = projectId;
        this.properties = properties;
        this.createTime = createTime;
        this.updateTime = updateTime;
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

    public Map<String, String> getProperties() {
        return properties;
    }

    public void setProperties(Map<String, String> properties) {
        this.properties = properties;
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

    @Override
    public String toString() {
        return "WorkflowMeta{" +
                "uuid=" + uuid +
                ", name='" + name + '\'' +
                ", projectId=" + projectId +
                ", properties=" + properties +
                ", createTime=" + createTime +
                ", updateTime=" + updateTime +
                '}';
    }

    public static WorkflowMeta buildWorkflowMeta(Message.WorkflowMetaProto workflowMetaProto) {
        return workflowMetaProto == null ? null : new WorkflowMeta(workflowMetaProto.getUuid(),
                workflowMetaProto.getName(), workflowMetaProto.getProjectId().getValue(), workflowMetaProto.getPropertiesMap(),
                workflowMetaProto.getCreateTime().getValue(), workflowMetaProto.getUpdateTime().getValue());
    }

    public static List<WorkflowMeta> buildWorkflowMetas(MetadataServiceOuterClass.WorkflowListProto workflowListProto) {
        if (workflowListProto == null) {
            return null;
        } else {
            List<WorkflowMeta> workflowMetas = new ArrayList<>();
            for (Message.WorkflowMetaProto workflowMetaProto: workflowListProto.getWorkflowsList()) {
                workflowMetas.add(buildWorkflowMeta(workflowMetaProto));
            }
            return workflowMetas;
        }
    }
}