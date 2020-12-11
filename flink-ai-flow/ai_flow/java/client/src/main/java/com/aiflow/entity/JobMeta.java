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
import com.aiflow.proto.Message.JobProto;
import com.aiflow.proto.MetadataServiceOuterClass.JobListProto;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class JobMeta {

    private Long uuid;
    private String name;
    private Long workflowExecutionId;
    private Map<String, String> properties;
    private String jobId;
    private Long startTime;
    private Long endTime;
    private State jobState;
    private String logUri;
    private String signature;

    public JobMeta() {
    }

    public JobMeta(Long uuid, String name, Long workflowExecutionId, Map<String, String> properties, String jobId, Long startTime, Long endTime, State jobState, String logUri, String signature) {
        this.uuid = uuid;
        this.name = name;
        this.workflowExecutionId = workflowExecutionId;
        this.properties = properties;
        this.jobId = jobId;
        this.startTime = startTime;
        this.endTime = endTime;
        this.jobState = jobState;
        this.logUri = logUri;
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

    public Long getWorkflowExecutionId() {
        return workflowExecutionId;
    }

    public void setWorkflowExecutionId(Long workflowExecutionId) {
        this.workflowExecutionId = workflowExecutionId;
    }

    public Map<String, String> getProperties() {
        return properties;
    }

    public void setProperties(Map<String, String> properties) {
        this.properties = properties;
    }

    public String getJobId() {
        return jobId;
    }

    public void setJobId(String jobId) {
        this.jobId = jobId;
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

    public State getJobState() {
        return jobState;
    }

    public void setJobState(State jobState) {
        this.jobState = jobState;
    }

    public String getLogUri() {
        return logUri;
    }

    public void setLogUri(String logUri) {
        this.logUri = logUri;
    }

    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }

    @Override
    public String toString() {
        return "JobMeta{" +
                "uuid=" + uuid +
                ", name='" + name + '\'' +
                ", workflowExecutionId=" + workflowExecutionId +
                ", properties=" + properties +
                ", jobId=" + jobId +
                ", startTime=" + startTime +
                ", endTime=" + endTime +
                ", jobState=" + jobState +
                ", logUri='" + logUri + '\'' +
                ", signature='" + signature + '\'' +
                '}';
    }

    public static JobMeta buildJobMeta(JobProto jobProto) {
        return jobProto == null ? null : new JobMeta(jobProto.getUuid(),
                jobProto.getName(),
                jobProto.getWorkflowExecutionId().getValue(),
                jobProto.getPropertiesMap(),
                jobProto.getJobId().getValue(),
                jobProto.getStartTime().getValue(),
                jobProto.getEndTime().getValue(),
                State.valueOf(jobProto.getJobState().name()),
                jobProto.getLogUri().getValue(),
                jobProto.getSignature().getValue());
    }

    public static List<JobMeta> buildJobMetas(JobListProto jobListProto) {
        if (jobListProto == null) {
            return null;
        } else {
            List<JobMeta> jobMetas = new ArrayList<>();
            for (JobProto jobProto : jobListProto.getJobsList()) {
                jobMetas.add(buildJobMeta(jobProto));
            }
            return jobMetas;
        }
    }
}