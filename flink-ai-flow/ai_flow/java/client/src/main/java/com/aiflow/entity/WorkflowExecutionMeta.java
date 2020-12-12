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

import com.aiflow.common.State;
import com.aiflow.proto.Message.WorkflowExecutionProto;
import com.aiflow.proto.MetadataServiceOuterClass.WorkFlowExecutionListProto;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class WorkflowExecutionMeta {

    private Long uuid;
    private String name;
    private State executionState;
    private Long projectId;
    private Map<String, String> properties;
    private Long startTime;
    private Long endTime;
    private String logUri;
    private String workflowJson;
    private String signature;

    public WorkflowExecutionMeta() {
    }

    public WorkflowExecutionMeta(Long uuid, String name, State executionState, Long projectId, Map<String, String> properties, Long startTime, Long endTime, String logUri, String workflowJson, String signature) {
        this.uuid = uuid;
        this.name = name;
        this.executionState = executionState;
        this.projectId = projectId;
        this.properties = properties;
        this.startTime = startTime;
        this.endTime = endTime;
        this.logUri = logUri;
        this.workflowJson = workflowJson;
        this.signature = signature;
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

    public State getExecutionState() {
        return executionState;
    }

    public void setExecutionState(State executionState) {
        this.executionState = executionState;
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

    public Long getStartTime() {
        return startTime;
    }

    public void setStartTime(Long startTime) {
        this.startTime = startTime;
    }

    public Long getEndTime() {
        return endTime;
    }

    public void setEndTime(Long endTime) {
        this.endTime = endTime;
    }

    public String getLogUri() {
        return logUri;
    }

    public void setLogUri(String logUri) {
        this.logUri = logUri;
    }

    public String getWorkflowJson() {
        return workflowJson;
    }

    public void setWorkflowJson(String workflowJson) {
        this.workflowJson = workflowJson;
    }

    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }

    @Override
    public String toString() {
        return "WorkflowExecutionMeta{" +
                "uuid=" + uuid +
                ", name='" + name + '\'' +
                ", executionState=" + executionState +
                ", projectId=" + projectId +
                ", properties=" + properties +
                ", startTime=" + startTime +
                ", endTime=" + endTime +
                ", logUri='" + logUri + '\'' +
                ", workflowJson='" + workflowJson + '\'' +
                ", signature='" + signature + '\'' +
                '}';
    }

    public static WorkflowExecutionMeta buildWorkflowExecutionMeta(WorkflowExecutionProto workflowExecutionProto) {
        return workflowExecutionProto == null ? null : new WorkflowExecutionMeta(workflowExecutionProto.getUuid(),
                workflowExecutionProto.getName(),
                State.valueOf(workflowExecutionProto.getExecutionState().name()),
                workflowExecutionProto.getProjectId().getValue(),
                workflowExecutionProto.getPropertiesMap(),
                workflowExecutionProto.getStartTime().getValue(),
                workflowExecutionProto.getEndTime().getValue(),
                workflowExecutionProto.getLogUri().getValue(),
                workflowExecutionProto.getWorkflowJson().getValue(),
                workflowExecutionProto.getSignature().getValue());
    }

    public static List<WorkflowExecutionMeta> buildWorkflowExecutionMetas(WorkFlowExecutionListProto workFlowExecutionListProto) {
        if (workFlowExecutionListProto == null) {
            return null;
        } else {
            List<WorkflowExecutionMeta> workflowExecutionMetas = new ArrayList<>();
            for (WorkflowExecutionProto workflowExecutionProto : workFlowExecutionListProto.getWorkflowExecutionsList()) {
                workflowExecutionMetas.add(buildWorkflowExecutionMeta(workflowExecutionProto));
            }
            return workflowExecutionMetas;
        }
    }
}