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

package org.aiflow.client;

import org.aiflow.client.entity.MetricMeta;
import org.aiflow.client.entity.MetricSummary;
import org.aiflow.client.entity.MetricType;
import org.aiflow.client.exception.AIFlowException;
import org.aiflow.client.proto.Message;
import org.aiflow.client.proto.Message.MetricMetaProto;
import org.aiflow.client.proto.MetricServiceGrpc;
import org.aiflow.client.proto.MetricServiceOuterClass;
import org.aiflow.client.proto.MetricServiceOuterClass.MetricMetaRequest;
import org.aiflow.client.proto.MetricServiceOuterClass.MetricSummaryRequest;

import io.grpc.Channel;
import io.grpc.ManagedChannelBuilder;

import java.util.List;
import java.util.Map;

import static org.aiflow.client.common.Constant.SERVER_URI;
import static org.aiflow.client.util.Transform.int64Value;
import static org.aiflow.client.util.Transform.stringValue;

public class MetricClient {

    private final MetricServiceGrpc.MetricServiceBlockingStub metricServiceStub;

    public MetricClient() {
        this(SERVER_URI);
    }

    public MetricClient(String target) {
        this(ManagedChannelBuilder.forTarget(target).usePlaintext().build());
    }

    public MetricClient(Channel channel) {
        this.metricServiceStub = MetricServiceGrpc.newBlockingStub(channel);
    }

    /**
     * Register a MetricMeta in metric center.
     *
     * @param name Name of registered metric meta. This is expected to be unique in the backend
     *     store.
     * @param metricType Type of registered metric meta.
     * @param projectName Name of the project associated with the registered metric meta.
     * @param description Name of registered model.
     * @param datasetName Name of the dataset associated with the registered metric meta.
     * @param modelName Name of the model associated with the registered metric meta.
     * @param jobName Name of the job associated with the registered metric meta.
     * @param startTime Start time of registered metric meta.
     * @param endTime End time of registered metric meta.
     * @param uri Uri of registered metric meta.
     * @param tags Tags of registered metric meta.
     * @param properties Properties of registered metric meta.
     * @return The {@link MetricMeta} object that is registered.
     */
    public MetricMeta registerMetricMeta(
            String name,
            MetricType metricType,
            String projectName,
            String description,
            String datasetName,
            String modelName,
            String jobName,
            long startTime,
            long endTime,
            String uri,
            String tags,
            Map<String, String> properties)
            throws AIFlowException {
        MetricMetaProto metricMetaProto =
                MetricMetaProto.newBuilder()
                        .setMetricName(stringValue(name))
                        .setMetricType(metricType.getMetricType())
                        .setProjectName(stringValue(projectName))
                        .setMetricDesc(stringValue(description))
                        .setDatasetName(stringValue(datasetName))
                        .setModelName(stringValue(modelName))
                        .setJobName(stringValue(jobName))
                        .setStartTime(int64Value(startTime))
                        .setEndTime(int64Value(endTime))
                        .setUri(stringValue(uri))
                        .setTags(stringValue(tags))
                        .putAllProperties(properties)
                        .build();
        MetricMetaRequest request =
                MetricMetaRequest.newBuilder().setMetricMeta(metricMetaProto).build();
        MetricServiceOuterClass.MetricMetaResponse response =
                metricServiceStub.registerMetricMeta(request);

        if (0 == response.getReturnCode()) {
            return MetricMeta.buildMetricMeta(response.getMetricMeta());
        } else {
            throw new AIFlowException(
                    String.valueOf(response.getReturnCode()), response.getReturnMsg());
        }
    }

    /**
     * Update a MetricMeta in Metric Center.
     *
     * @param name Name of registered metric meta. This is expected to be unique in the backend
     *     store.
     * @param projectName Name of the project associated with the registered metric meta.
     * @param description Name of registered model.
     * @param datasetName Name of the dataset associated with the registered metric meta.
     * @param modelName Name of the model associated with the registered metric meta.
     * @param jobName Name of the job associated with the registered metric meta.
     * @param startTime Start time of registered metric meta.
     * @param endTime End time of registered metric meta.
     * @param uri Uri of registered metric meta.
     * @param tags Tags of registered metric meta.
     * @param properties Properties of registered metric meta.
     * @return The {@link MetricMeta} object that is updated.
     */
    public MetricMeta updateMetricMeta(
            String name,
            String projectName,
            String description,
            String datasetName,
            String modelName,
            String jobName,
            long startTime,
            long endTime,
            String uri,
            String tags,
            Map<String, String> properties)
            throws AIFlowException {
        MetricMetaProto metricMetaProto =
                MetricMetaProto.newBuilder()
                        .setMetricName(stringValue(name))
                        .setProjectName(stringValue(projectName))
                        .setMetricDesc(stringValue(description))
                        .setDatasetName(stringValue(datasetName))
                        .setModelName(stringValue(modelName))
                        .setJobName(stringValue(jobName))
                        .setStartTime(int64Value(startTime))
                        .setEndTime(int64Value(endTime))
                        .setUri(stringValue(uri))
                        .setTags(stringValue(tags))
                        .putAllProperties(properties)
                        .build();
        MetricMetaRequest request =
                MetricMetaRequest.newBuilder().setMetricMeta(metricMetaProto).build();
        MetricServiceOuterClass.MetricMetaResponse response =
                metricServiceStub.updateMetricMeta(request);

        if (0 == response.getReturnCode()) {
            return MetricMeta.buildMetricMeta(response.getMetricMeta());
        } else {
            throw new AIFlowException(
                    String.valueOf(response.getReturnCode()), response.getReturnMsg());
        }
    }

    /**
     * * Delete metric metadata by metric name in Metric Center backend.
     *
     * @param metricName Name of registered metric meta. This is expected to be unique in the
     *     backend store.
     * @return True if successfully deleting the given metric metadata, false if not success.
     */
    public boolean deleteMetricMeta(String metricName) {
        MetricServiceOuterClass.MetricNameRequest request =
                MetricServiceOuterClass.MetricNameRequest.newBuilder()
                        .setMetricName(metricName)
                        .build();
        Message.Response response = metricServiceStub.deleteMetricMeta(request);
        if (Message.ReturnCode.SUCCESS.getNumber() == Integer.parseInt(response.getReturnCode())) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * * Get metric metadata detail filter by metric name for Metric Center.
     *
     * @param metricName Name of registered metric meta. This is expected to be unique in the
     *     backend store.
     * @return A {@link MetricMeta} object.
     * @throws AIFlowException
     */
    public MetricMeta getMetricMeta(String metricName) throws AIFlowException {
        MetricServiceOuterClass.MetricNameRequest request =
                MetricServiceOuterClass.MetricNameRequest.newBuilder()
                        .setMetricName(metricName)
                        .build();
        MetricServiceOuterClass.MetricMetaResponse response =
                metricServiceStub.getMetricMeta(request);
        if (0 == response.getReturnCode()) {
            return MetricMeta.buildMetricMeta(response.getMetricMeta());
        } else {
            throw new AIFlowException(
                    String.valueOf(response.getReturnCode()), response.getReturnMsg());
        }
    }

    /**
     * * List dataset metric metadata filter by dataset name and project name for Metric Center.
     *
     * @param datasetName Name of the dataset associated with the registered metric meta.
     * @param projectName Name of the project associated with the registered metric meta.
     * @return List of {@link MetricMeta} objects.
     * @throws AIFlowException
     */
    public List<MetricMeta> listDatasetMetricMetas(String datasetName, String projectName)
            throws AIFlowException {
        MetricServiceOuterClass.ListDatasetMetricMetasRequest request =
                MetricServiceOuterClass.ListDatasetMetricMetasRequest.newBuilder()
                        .setDatasetName(datasetName)
                        .setProjectName(stringValue(projectName))
                        .build();
        MetricServiceOuterClass.ListMetricMetasResponse response =
                metricServiceStub.listDatasetMetricMetas(request);
        if (0 == response.getReturnCode()) {
            return MetricMeta.buildMetricMetas(response.getMetricMetasList());
        } else {
            throw new AIFlowException(
                    String.valueOf(response.getReturnCode()), response.getReturnMsg());
        }
    }

    /**
     * * List model metric metadata filter by model name and project name for Metric Center.
     *
     * @param modelName Name of the model associated with the registered metric meta.
     * @param projectName Name of the project associated with the registered metric meta.
     * @return List of {@link MetricMeta} objects.
     * @throws AIFlowException
     */
    public List<MetricMeta> listModelMetricMetas(String modelName, String projectName)
            throws AIFlowException {
        MetricServiceOuterClass.ListModelMetricMetasRequest request =
                MetricServiceOuterClass.ListModelMetricMetasRequest.newBuilder()
                        .setModelName(modelName)
                        .setProjectName(stringValue(projectName))
                        .build();
        MetricServiceOuterClass.ListMetricMetasResponse response =
                metricServiceStub.listModelMetricMetas(request);
        if (0 == response.getReturnCode()) {
            return MetricMeta.buildMetricMetas(response.getMetricMetasList());
        } else {
            throw new AIFlowException(
                    String.valueOf(response.getReturnCode()), response.getReturnMsg());
        }
    }

    /**
     * * Register metric summary in Metric Center.
     *
     * @param metricName Name of registered metric summary.
     * @param metricKey Key of registered metric summary.
     * @param metricValue Value of registered metric summary.
     * @param metricTimestamp Timestamp of registered metric summary.
     * @param modelVersion Version of the model version associated with the registered metric
     *     summary.
     * @param jobExecutionId ID of the job execution associated with the registered metric summary.
     * @return The {@link MetricSummary} object that is registered.
     * @throws AIFlowException
     */
    public MetricSummary registerMetricSummary(
            String metricName,
            String metricKey,
            String metricValue,
            long metricTimestamp,
            String modelVersion,
            String jobExecutionId)
            throws AIFlowException {
        Message.MetricSummaryProto metricSummaryProto =
                Message.MetricSummaryProto.newBuilder()
                        .setMetricName(stringValue(metricName))
                        .setMetricKey(stringValue(metricKey))
                        .setMetricValue(stringValue(metricValue))
                        .setMetricTimestamp(int64Value(metricTimestamp))
                        .setModelVersion(stringValue(modelVersion))
                        .setJobExecutionId(stringValue(jobExecutionId))
                        .build();
        MetricSummaryRequest request =
                MetricSummaryRequest.newBuilder().setMetricSummary(metricSummaryProto).build();
        MetricServiceOuterClass.MetricSummaryResponse response =
                metricServiceStub.registerMetricSummary(request);

        if (0 == response.getReturnCode()) {
            return MetricSummary.buildMetricSummary(response.getMetricSummary());
        } else {
            throw new AIFlowException(
                    String.valueOf(response.getReturnCode()), response.getReturnMsg());
        }
    }

    /**
     * * Update metric summary in Metric Center.
     *
     * @param uuid UUID of registered metric summary.
     * @param metricName Name of registered metric summary.
     * @param metricKey Key of registered metric summary.
     * @param metricValue Value of registered metric summary.
     * @param metricTimestamp Timestamp of registered metric summary.
     * @param modelVersion Version of the model version associated with the registered metric
     *     summary.
     * @param jobExecutionId ID of the job execution associated with the registered metric summary.
     * @return The {@link MetricSummary} object that is updated.
     * @throws AIFlowException
     */
    public MetricSummary updateMetricSummary(
            long uuid,
            String metricName,
            String metricKey,
            String metricValue,
            long metricTimestamp,
            String modelVersion,
            String jobExecutionId)
            throws AIFlowException {
        Message.MetricSummaryProto metricSummaryProto =
                Message.MetricSummaryProto.newBuilder()
                        .setUuid(uuid)
                        .setMetricName(stringValue(metricName))
                        .setMetricKey(stringValue(metricKey))
                        .setMetricValue(stringValue(metricValue))
                        .setMetricTimestamp(int64Value(metricTimestamp))
                        .setModelVersion(stringValue(modelVersion))
                        .setJobExecutionId(stringValue(jobExecutionId))
                        .build();
        MetricSummaryRequest request =
                MetricSummaryRequest.newBuilder().setMetricSummary(metricSummaryProto).build();
        MetricServiceOuterClass.MetricSummaryResponse response =
                metricServiceStub.updateMetricSummary(request);

        if (0 == response.getReturnCode()) {
            return MetricSummary.buildMetricSummary(response.getMetricSummary());
        } else {
            throw new AIFlowException(
                    String.valueOf(response.getReturnCode()), response.getReturnMsg());
        }
    }

    /**
     * * Delete metric summary by metric uuid in Metric Center backend.
     *
     * @param uuid UUID of registered metric summary.
     * @return Whether to delete the given metric summary.
     */
    public boolean deleteMetricSummary(long uuid) {
        MetricServiceOuterClass.UuidRequest request =
                MetricServiceOuterClass.UuidRequest.newBuilder().setUuid(uuid).build();
        Message.Response response = metricServiceStub.deleteMetricSummary(request);
        if (Message.ReturnCode.SUCCESS.getNumber() == Integer.parseInt(response.getReturnCode())) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * * Get metric summary detail filter by summary uuid for Metric Center.
     *
     * @param uuid UUID of registered metric summary.
     * @return A {@link MetricSummary} object.
     * @throws AIFlowException
     */
    public MetricSummary getMetricSummary(long uuid) throws AIFlowException {
        MetricServiceOuterClass.UuidRequest request =
                MetricServiceOuterClass.UuidRequest.newBuilder().setUuid(uuid).build();
        MetricServiceOuterClass.MetricSummaryResponse response =
                metricServiceStub.getMetricSummary(request);
        if (0 == response.getReturnCode()) {
            return MetricSummary.buildMetricSummary(response.getMetricSummary());
        } else {
            throw new AIFlowException(
                    String.valueOf(response.getReturnCode()), response.getReturnMsg());
        }
    }

    /**
     * * List of metric summaries filter by metric summary fields for Metric Center.
     *
     * @param metricName Name of filtered metric summary.
     * @param metricKey Key of filtered metric summary.
     * @param modelVersion Version of the model version associated with the registered metric
     *     summary.
     * @param startTime Start time for timestamp filtered metric summary.
     * @param endTime End time for timestamp filtered metric summary.
     * @return List of {@link MetricSummary} objects.
     * @throws AIFlowException
     */
    public List<MetricSummary> listMetricSummaries(
            String metricName, String metricKey, String modelVersion, long startTime, long endTime)
            throws AIFlowException {
        MetricServiceOuterClass.ListMetricSummariesRequest.Builder builder =
                MetricServiceOuterClass.ListMetricSummariesRequest.newBuilder();
        if (metricName != null) {
            builder.setMetricName(stringValue(metricName));
        }
        if (metricKey != null) {
            builder.setMetricKey(stringValue(metricKey));
        }
        if (modelVersion != null) {
            builder.setModelVersion(stringValue(modelVersion));
        }
        MetricServiceOuterClass.ListMetricSummariesRequest request =
                builder.setStartTime(int64Value(startTime)).setEndTime(int64Value(endTime)).build();
        MetricServiceOuterClass.ListMetricSummariesResponse response =
                metricServiceStub.listMetricSummaries(request);
        if (0 == response.getReturnCode()) {
            return MetricSummary.buildMetricSummaries(response.getMetricSummariesList());
        } else {
            throw new AIFlowException(
                    String.valueOf(response.getReturnCode()), response.getReturnMsg());
        }
    }
}
