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

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class MetricMeta {

    private String name;
    private MetricType metricType;
    private String description;
    private String projectName;
    private String datasetName;
    private String modelName;
    private String jobName;
    private long startTime;
    private long endTime;
    private String uri;
    private String tags;
    private Map<String, String> properties;

    public MetricMeta() {}

    public MetricMeta(String name, MetricType metricType, String description, String projectName, String datasetName, String modelName, String jobName, long startTime, long endTime, String uri, String tags, Map<String, String> properties) {
        this.name = name;
        this.metricType = metricType;
        this.description = description;
        this.projectName = projectName;
        this.datasetName = datasetName;
        this.modelName = modelName;
        this.jobName = jobName;
        this.startTime = startTime;
        this.endTime = endTime;
        this.uri = uri;
        this.tags = tags;
        this.properties = properties;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public MetricType getMetricType() {
        return metricType;
    }

    public void setMetricType(MetricType metricType) {
        this.metricType = metricType;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getProjectName() {
        return projectName;
    }

    public void setProjectName(String projectName) {
        this.projectName = projectName;
    }

    public String getDatasetName() {
        return datasetName;
    }

    public void setDatasetName(String datasetName) {
        this.datasetName = datasetName;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public String getJobName() {
        return jobName;
    }

    public void setJobName(String jobName) {
        this.jobName = jobName;
    }

    public long getStartTime() {
        return startTime;
    }

    public void setStartTime(long startTime) {
        this.startTime = startTime;
    }

    public long getEndTime() {
        return endTime;
    }

    public void setEndTime(long endTime) {
        this.endTime = endTime;
    }

    public String getUri() {
        return uri;
    }

    public void setUri(String uri) {
        this.uri = uri;
    }

    public String getTags() {
        return tags;
    }

    public void setTags(String tags) {
        this.tags = tags;
    }

    public Map<String, String> getProperties() {
        return properties;
    }

    public void setProperties(Map<String, String> properties) {
        this.properties = properties;
    }

    public static MetricMeta buildMetricMeta(Message.MetricMetaProto metricMetaProto) {
        return metricMetaProto == null ? null : new MetricMeta(
                metricMetaProto.getMetricName().getValue(),
                MetricType.getMetricTypeFromValue(metricMetaProto.getMetricType()),
                metricMetaProto.getMetricDesc().getValue(),
                metricMetaProto.getProjectName().getValue(),
                metricMetaProto.getDatasetName().getValue(),
                metricMetaProto.getModelName().getValue(),
                metricMetaProto.getJobName().getValue(),
                metricMetaProto.getStartTime().getValue(),
                metricMetaProto.getEndTime().getValue(),
                metricMetaProto.getUri().getValue(),
                metricMetaProto.getTags().getValue(),
                metricMetaProto.getPropertiesMap()
        );
    }

    public static List<MetricMeta> buildMetricMetas(List<Message.MetricMetaProto> metricMetaProtos) {
        if (metricMetaProtos == null) {
            return null;
        } else {
            List<MetricMeta> metricMetas = new ArrayList<>();
            for (Message.MetricMetaProto metricMetaProto : metricMetaProtos) {
                metricMetas.add(buildMetricMeta(metricMetaProto));
            }
            return metricMetas;
        }
    }
}