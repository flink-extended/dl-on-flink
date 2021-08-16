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

public class MetricSummary {

    private long uuid;
    private String metricName;
    private String metricKey;
    private String metricValue;
    private long metricTimestamp;
    private String modelVersion;
    private String jobExecutionId;

    public MetricSummary(
            long uuid,
            String metricName,
            String metricKey,
            String metricValue,
            long metricTimestamp,
            String modelVersion,
            String jobExecutionId) {
        this.uuid = uuid;
        this.metricName = metricName;
        this.metricKey = metricKey;
        this.metricValue = metricValue;
        this.metricTimestamp = metricTimestamp;
        this.modelVersion = modelVersion;
        this.jobExecutionId = jobExecutionId;
    }

    public long getUuid() {
        return uuid;
    }

    public void setUuid(long uuid) {
        this.uuid = uuid;
    }

    public String getMetricName() {
        return metricName;
    }

    public void setMetricName(String metricName) {
        this.metricName = metricName;
    }

    public String getMetricKey() {
        return metricKey;
    }

    public void setMetricKey(String metricKey) {
        this.metricKey = metricKey;
    }

    public String getMetricValue() {
        return metricValue;
    }

    public void setMetricValue(String metricValue) {
        this.metricValue = metricValue;
    }

    public long getMetricTimestamp() {
        return metricTimestamp;
    }

    public void setMetricTimestamp(long metricTimestamp) {
        this.metricTimestamp = metricTimestamp;
    }

    public String getModelVersion() {
        return modelVersion;
    }

    public void setModelVersion(String modelVersion) {
        this.modelVersion = modelVersion;
    }

    public String getJobExecutionId() {
        return jobExecutionId;
    }

    public void setJobExecutionId(String jobExecutionId) {
        this.jobExecutionId = jobExecutionId;
    }

    public static MetricSummary buildMetricSummary(Message.MetricSummaryProto metricSummaryProto) {
        return metricSummaryProto == null
                ? null
                : new MetricSummary(
                        metricSummaryProto.getUuid(),
                        metricSummaryProto.getMetricName().getValue(),
                        metricSummaryProto.getMetricKey().getValue(),
                        metricSummaryProto.getMetricValue().getValue(),
                        metricSummaryProto.getMetricTimestamp().getValue(),
                        metricSummaryProto.getModelVersion().getValue(),
                        metricSummaryProto.getJobExecutionId().getValue());
    }

    public static List<MetricSummary> buildMetricSummaries(
            List<Message.MetricSummaryProto> metricSummaryProtos) {
        if (metricSummaryProtos == null) {
            return null;
        } else {
            List<MetricSummary> metricSummaries = new ArrayList<>();
            for (Message.MetricSummaryProto metricSummaryProto : metricSummaryProtos) {
                metricSummaries.add(buildMetricSummary(metricSummaryProto));
            }
            return metricSummaries;
        }
    }
}
