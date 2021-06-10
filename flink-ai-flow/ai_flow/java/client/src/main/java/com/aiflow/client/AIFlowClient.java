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
package com.aiflow.client;

import com.aiflow.common.*;
import com.aiflow.entity.*;
import com.aiflow.notification.client.EventWatcher;
import com.aiflow.notification.client.NotificationClient;
import com.aiflow.notification.entity.EventMeta;
import io.grpc.Channel;
import io.grpc.ManagedChannelBuilder;
import org.apache.commons.lang3.StringUtils;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static com.aiflow.common.Constant.DEFAULT_NAMESPACE;
import static com.aiflow.common.Constant.SERVER_URI;

/** Client of AIFlow Rest Endpoint that provides Metadata/Model/Notification function service. */
public class AIFlowClient {

  private final MetadataClient metadataClient;
  private final ModelCenterClient modelCenterClient;
  private final NotificationClient notificationClient;

  public AIFlowClient(
      String target,
      String defaultNamespace,
      Boolean enableHa,
      Integer listMemberIntervalMs,
      Integer retryIntervalMs,
      Integer retryTimeoutMs) {
    this(
        ManagedChannelBuilder.forTarget(target).usePlaintext().build(),
        StringUtils.isEmpty(target) ? SERVER_URI : target,
        StringUtils.isEmpty(defaultNamespace) ? DEFAULT_NAMESPACE : defaultNamespace,
        enableHa,
        listMemberIntervalMs,
        retryIntervalMs,
        retryTimeoutMs);
  }

  public AIFlowClient(
      Channel channel,
      String target,
      String defaultNamespace,
      Boolean enableHa,
      Integer listMemberIntervalMs,
      Integer retryIntervalMs,
      Integer retryTimeoutMs) {
    this.metadataClient = new MetadataClient(channel);
    this.modelCenterClient = new ModelCenterClient(channel);
    this.notificationClient =
        new NotificationClient(
            target,
            defaultNamespace,
            enableHa,
            listMemberIntervalMs,
            retryIntervalMs,
            retryTimeoutMs);
  }

  /**
   * Get a specific example in Metadata Store by example id.
   *
   * @param exampleId Id of example.
   * @return Single ExampleMeta object if example exists, otherwise returns None if example does not
   *     exist.
   */
  public ExampleMeta getExampleById(Long exampleId) throws Exception {
    return this.metadataClient.getExampleById(exampleId);
  }

  /**
   * Get a specific example in Metadata Store by example name.
   *
   * @param exampleName Name of example.
   * @return Single ExampleMeta object if example exists, otherwise returns None if example does not
   *     exist.
   */
  public ExampleMeta getExampleByName(String exampleName) throws Exception {
    return this.metadataClient.getExampleByName(exampleName);
  }

  /**
   * Register a example in Metadata Store.
   *
   * @param name Name of example.
   * @param supportType Example's support type.
   * @param dataFormat Data format of example.
   * @param description Description of example.
   * @param batchUri Batch uri of example.
   * @param streamUri Stream uri of example.
   * @param createTime Time when example is created.
   * @param updateTime Time when example is updated.
   * @param properties Properties of example.
   * @param nameList Name list of example's schema.
   * @param typeList Type list corresponded to name list of example's schema.
   * @return Single ExampleMeta object registered in Metadata Store.
   */
  public ExampleMeta registerExample(
      String name,
      ExecutionType supportType,
      String dataFormat,
      String description,
      String batchUri,
      String streamUri,
      Long createTime,
      Long updateTime,
      Map<String, String> properties,
      List<String> nameList,
      List<DataType> typeList)
      throws Exception {
    return this.metadataClient.registerExample(
        name,
        supportType,
        dataFormat,
        description,
        batchUri,
        streamUri,
        createTime,
        updateTime,
        properties,
        nameList,
        typeList);
  }

  /**
   * Register a example in Metadata Store.
   *
   * @param name Name of example.
   * @param supportType Example's support type.
   * @param catalogName Name of example catalog.
   * @param catalogType Type of example catalog.
   * @param catalogConnectionUri Connection URI of example catalog.
   * @param catalogVersion Version of example catalog.
   * @param catalogTable Table of example catalog.
   * @param catalogDatabase Database of example catalog.
   * @return Single ExampleMeta object registered in Metadata Store.
   */
  public ExampleMeta registerExampleWithCatalog(
      String name,
      ExecutionType supportType,
      String catalogName,
      String catalogType,
      String catalogConnectionUri,
      String catalogVersion,
      String catalogTable,
      String catalogDatabase)
      throws Exception {
    return this.metadataClient.registerExampleWithCatalog(
        name,
        supportType,
        catalogName,
        catalogType,
        catalogConnectionUri,
        catalogVersion,
        catalogTable,
        catalogDatabase);
  }

  /**
   * Register multiple examples in Metadata Store.
   *
   * @param examples List of example registered
   * @return List of ExampleMeta object registered in Metadata Store.
   */
  public List<ExampleMeta> registerExamples(List<ExampleMeta> examples) throws Exception {
    return this.metadataClient.registerExamples(examples);
  }

  /**
   * Update a example in Metadata Store.
   *
   * @param name Name of example.
   * @param supportType Example's support type.
   * @param dataFormat Data format of example.
   * @param description Description of example.
   * @param batchUri Batch uri of example.
   * @param streamUri Stream uri of example.
   * @param updateTime Time when example is updated.
   * @param properties Properties of example.
   * @param nameList Name list of example's schema.
   * @param typeList Type list corresponded to name list of example's schema.
   * @param catalogName Name of example catalog.
   * @param catalogType Type of example catalog.
   * @param catalogConnectionUri Connection URI of example catalog.
   * @param catalogVersion Version of example catalog.
   * @param catalogTable Table of example catalog.
   * @param catalogDatabase Database of example catalog.
   * @return Single ExampleMeta object registered in Metadata Store.
   */
  public ExampleMeta updateExample(
      String name,
      ExecutionType supportType,
      String dataFormat,
      String description,
      String batchUri,
      String streamUri,
      Long updateTime,
      Map<String, String> properties,
      List<String> nameList,
      List<DataType> typeList,
      String catalogName,
      String catalogType,
      String catalogConnectionUri,
      String catalogVersion,
      String catalogTable,
      String catalogDatabase)
      throws Exception {
    return this.metadataClient.updateExample(
        name,
        supportType,
        dataFormat,
        description,
        batchUri,
        streamUri,
        updateTime,
        properties,
        nameList,
        typeList,
        catalogName,
        catalogType,
        catalogConnectionUri,
        catalogVersion,
        catalogTable,
        catalogDatabase);
  }

  /**
   * List registered examples in Metadata Store.
   *
   * @param pageSize Limitation of listed examples.
   * @param offset Offset of listed examples.
   * @return List of ExampleMeta object registered in Metadata Store.
   */
  public List<ExampleMeta> listExample(Long pageSize, Long offset) throws Exception {
    return this.metadataClient.listExample(pageSize, offset);
  }

  /**
   * Delete registered example by example id.
   *
   * @param exampleId Id of example.
   * @return Status.OK if example is successfully deleted, Status.ERROR if example does not exist
   *     otherwise.
   */
  public Status deleteExampleById(Long exampleId) throws Exception {
    return this.metadataClient.deleteExampleById(exampleId);
  }

  /**
   * Delete registered example by example name.
   *
   * @param exampleName Name of example.
   * @return Status.OK if example is successfully deleted, Status.ERROR if example does not exist
   *     otherwise.
   */
  public Status deleteExampleByName(String exampleName) throws Exception {
    return this.metadataClient.deleteExampleByName(exampleName);
  }

  /**
   * Get a specific model relation in Metadata Store by model id.
   *
   * @param modelId Id of model.
   * @return Single ModelRelationMeta object if model relation exists, otherwise returns None if
   *     model relation does not exist.
   */
  public ModelRelationMeta getModelRelationById(Long modelId) throws Exception {
    return this.metadataClient.getModelRelationById(modelId);
  }

  /**
   * Get a specific model relation in Metadata Store by model name.
   *
   * @param modelName Name of model.
   * @return Single ModelRelationMeta object if model relation exists, otherwise returns None if
   *     model relation does not exist.
   */
  public ModelRelationMeta getModelRelationByName(String modelName) throws Exception {
    return this.metadataClient.getModelRelationByName(modelName);
  }

  /**
   * Register a model relation in Metadata Store.
   *
   * @param name Name of model.
   * @param projectId Project id which the model corresponded to.
   * @return Single ModelRelationMeta object registered in Metadata Store.
   */
  public ModelRelationMeta registerModelRelation(String name, Long projectId) throws Exception {
    return this.metadataClient.registerModelRelation(name, projectId);
  }

  /**
   * List registered model relations in Metadata Store.
   *
   * @param pageSize Limitation of listed model relations.
   * @param offset Offset of listed model relations.
   * @return List of ModelRelationMeta object registered in Metadata Store.
   */
  public List<ModelRelationMeta> listModelRelation(Long pageSize, Long offset) throws Exception {
    return this.metadataClient.listModelRelation(pageSize, offset);
  }

  /**
   * Delete registered model relation by model id.
   *
   * @param modelId Id of model.
   * @return Status.OK if model relation is successfully deleted, Status.ERROR if model relation
   *     does not exist otherwise.
   */
  public Status deleteModelRelationById(Long modelId) throws Exception {
    return this.metadataClient.deleteModelRelationById(modelId);
  }

  /**
   * Delete registered model relation by model name.
   *
   * @param modelName Name of model.
   * @return Status.OK if model relation is successfully deleted, Status.ERROR if model relation
   *     does not exist otherwise.
   */
  public Status deleteModelRelationByName(String modelName) throws Exception {
    return this.metadataClient.deleteModelRelationByName(modelName);
  }

  /**
   * Get a specific model in Metadata Store by model id.
   *
   * @param modelId Id of model.
   * @return Single ModelMeta object if model relation exists, otherwise returns None if model
   *     relation does not exist.
   */
  public ModelMeta getModelById(Long modelId) throws Exception {
    return this.metadataClient.getModelById(modelId);
  }

  /**
   * Get a specific model in Metadata Store by model name.
   *
   * @param modelName Name of model.
   * @return Single ModelMeta object if model relation exists, otherwise returns None if model
   *     relation does not exist.
   */
  public ModelMeta getModelByName(String modelName) throws Exception {
    return this.metadataClient.getModelByName(modelName);
  }

  /**
   * Register a model in Metadata Store.
   *
   * @param modelName Name of registered model.
   * @param modelType Type of registered model.
   * @param modelDesc Description of registered model.
   * @param projectId Project id which registered model corresponded to.
   * @return Single ModelMeta object registered in Metadata Store.
   */
  public ModelMeta registerModel(
      String modelName, ModelType modelType, String modelDesc, Long projectId) throws Exception {
    return this.metadataClient.registerModel(modelName, modelType, modelDesc, projectId);
  }

  /**
   * Delete registered model by model id.
   *
   * @param modelId Id of model.
   * @return Status.OK if model is successfully deleted, Status.ERROR if model does not exist
   *     otherwise.
   */
  public Status deleteModelById(Long modelId) throws Exception {
    return this.metadataClient.deleteModelById(modelId);
  }

  /**
   * Delete registered model by model name.
   *
   * @param modelName Name of model.
   * @return Status.OK if model is successfully deleted, Status.ERROR if model does not exist
   *     otherwise.
   */
  public Status deleteModelByName(String modelName) throws Exception {
    return this.metadataClient.deleteModelByName(modelName);
  }

  /**
   * Get a specific model version relation in Metadata Store by model version name.
   *
   * @param version Name of model version.
   * @param modelId Model id corresponded to model version.
   * @return Single ModelVersionRelationMeta object if model relation exists, otherwise returns None
   *     if model relation does not exist.
   */
  public ModelVersionRelationMeta getModelVersionRelationByVersion(String version, Long modelId)
      throws Exception {
    return this.metadataClient.getModelVersionRelationByVersion(version, modelId);
  }

  /**
   * Register a model version relation in Metadata Store.
   *
   * @param version Name of model version.
   * @param modelId Model id corresponded to model version.
   * @param workflowExecutionId Workflow execution id corresponded to model version.
   * @return Single ModelVersionRelationMeta object registered in Metadata Store.
   */
  public ModelVersionRelationMeta registerModelVersionRelation(
      String version, Long modelId, Long workflowExecutionId) throws Exception {
    return this.metadataClient.registerModelVersionRelation(version, modelId, workflowExecutionId);
  }

  /**
   * List registered model version relations in Metadata Store.
   *
   * @param modelId Model id corresponded to model version.
   * @param pageSize Limitation of listed model version relations.
   * @param offset Offset of listed model version relations.
   * @return List of ModelVersionRelationMeta object registered in Metadata Store.
   */
  public List<ModelVersionRelationMeta> listModelVersionRelation(
      Long modelId, Long pageSize, Long offset) throws Exception {
    return this.metadataClient.listModelVersionRelation(modelId, pageSize, offset);
  }

  /**
   * Delete registered model version relation by model name.
   *
   * @param version Name of model version.
   * @param modelId Model id corresponded to model version.
   * @return Status.OK if model version relation is successfully deleted, Status.ERROR if model
   *     version relation does not exist otherwise.
   */
  public Status deleteModelVersionRelationByVersion(String version, Long modelId) throws Exception {
    return this.metadataClient.deleteModelVersionRelationByVersion(version, modelId);
  }

  /**
   * Get a specific model version in Metadata Store by model version name.
   *
   * @param version Name of model version.
   * @param modelId Model id corresponded to model version.
   * @return Single ModelVersionMeta object if model relation exists, otherwise returns None if
   *     model relation does not exist.
   */
  public ModelVersionMeta getModelVersionByVersion(String version, Long modelId) throws Exception {
    return this.metadataClient.getModelVersionByVersion(version, modelId);
  }

  /**
   * Register a model version in Metadata Store.
   *
   * @param modelPath Source path where the AIFlow model is stored.
   * @param modelMetric Metric address from AIFlow metric server of registered model.
   * @param modelFlavor Flavor feature of AIFlow registered model option.
   * @param versionDesc Description of registered model version.
   * @param modelId Model id corresponded to model version.
   * @param workflowExecutionId Workflow execution id corresponded to model version.
   * @return Single ModelVersionRelationMeta object registered in Metadata Store.
   */
  public ModelVersionMeta registerModelVersion(
      String modelPath,
      String modelMetric,
      String modelFlavor,
      String versionDesc,
      Long modelId,
      Long workflowExecutionId)
      throws Exception {
    return this.metadataClient.registerModelVersion(
        modelPath, modelMetric, modelFlavor, versionDesc, modelId, workflowExecutionId);
  }

  /**
   * Delete registered model version by model version and id.
   *
   * @param version Name of model version.
   * @param modelId Model id corresponded to model version.
   * @return Status.OK if model version is successfully deleted, Status.ERROR if model version does
   *     not exist otherwise.
   */
  public Status deleteModelVersionByVersion(String version, Long modelId) throws Exception {
    return this.metadataClient.deleteModelVersionByVersion(version, modelId);
  }

  /**
   * Get a specific workflow execution in Metadata Store by workflow execution id.
   *
   * @param executionId Id of workflow execution.
   * @return Single WorkflowExecutionMeta object if workflow execution exists, otherwise returns
   *     None if workflow execution does not exist.
   */
  public WorkflowExecutionMeta getWorkFlowExecutionById(Long executionId) throws Exception {
    return this.metadataClient.getWorkFlowExecutionById(executionId);
  }

  /**
   * Get a specific workflow execution in Metadata Store by workflow execution name.
   *
   * @param executionName Name of workflow execution.
   * @return Single WorkflowExecutionMeta object if workflow execution exists, otherwise returns
   *     None if workflow execution does not exist.
   */
  public WorkflowExecutionMeta getWorkFlowExecutionByName(String executionName) throws Exception {
    return this.metadataClient.getWorkFlowExecutionByName(executionName);
  }

  /**
   * Register a workflow execution in Metadata Store.
   *
   * @param name Mame of workflow execution.
   * @param executionState State of workflow execution.
   * @param projectId Project id corresponded to workflow execution.
   * @param properties Properties of workflow execution.
   * @param startTime Time when workflow execution started.
   * @param endTime Time when workflow execution ended.
   * @param logUri Log uri of workflow execution.
   * @param workflowJson Workflow json of workflow execution.
   * @param signature Signature of workflow execution.
   * @return Single WorkflowExecutionMeta object registered in Metadata Store.
   */
  public WorkflowExecutionMeta registerWorkFlowExecution(
      String name,
      State executionState,
      Long projectId,
      Map<String, String> properties,
      Long startTime,
      Long endTime,
      String logUri,
      String workflowJson,
      String signature)
      throws Exception {
    return this.metadataClient.registerWorkFlowExecution(
        name,
        executionState,
        projectId,
        properties,
        startTime,
        endTime,
        logUri,
        workflowJson,
        signature);
  }

  /**
   * Update a workflow execution in Metadata Store.
   *
   * @param name Mame of workflow execution.
   * @param executionState State of workflow execution.
   * @param projectId Project id corresponded to workflow execution.
   * @param properties Properties of workflow execution.
   * @param endTime Time when workflow execution ended.
   * @param logUri Log uri of workflow execution.
   * @param workflowJson Workflow json of workflow execution.
   * @param signature Signature of workflow execution.
   * @return Single WorkflowExecutionMeta object registered in Metadata Store.
   */
  public WorkflowExecutionMeta updateWorkFlowExecution(
      String name,
      State executionState,
      Long projectId,
      Map<String, String> properties,
      Long endTime,
      String logUri,
      String workflowJson,
      String signature)
      throws Exception {
    return this.metadataClient.updateWorkFlowExecution(
        name, executionState, projectId, properties, endTime, logUri, workflowJson, signature);
  }

  /**
   * List registered workflow executions in Metadata Store.
   *
   * @param pageSize Limitation of listed workflow executions.
   * @param offset Offset of listed workflow executions.
   * @return List of WorkflowExecutionMeta object registered in Metadata Store.
   */
  public List<WorkflowExecutionMeta> listWorkFlowExecution(Long pageSize, Long offset)
      throws Exception {
    return this.metadataClient.listWorkFlowExecution(pageSize, offset);
  }

  /**
   * Update workflow execution end time in Metadata Store.
   *
   * @param endTime Time when workflow execution ended.
   * @param executionName Name of workflow execution.
   * @return Workflow execution uuid if workflow execution is successfully updated, raise an
   *     exception, if fail to update otherwise.
   */
  public WorkflowExecutionMeta updateWorkflowExecutionEndTime(Long endTime, String executionName)
      throws Exception {
    return this.metadataClient.updateWorkflowExecutionEndTime(endTime, executionName);
  }

  /**
   * Update workflow execution state in Metadata Store.
   *
   * @param executionState State of workflow execution.
   * @param executionName Name of workflow execution.
   * @return Workflow execution uuid if workflow execution is successfully updated, raise an
   *     exception, if fail to update otherwise.
   */
  public WorkflowExecutionMeta updateWorkflowExecutionState(
      State executionState, String executionName) throws Exception {
    return this.metadataClient.updateWorkflowExecutionState(executionState, executionName);
  }

  /**
   * Delete registered workflow execution by workflow execution id.
   *
   * @param executionId Id of workflow execution.
   * @return Status.OK if workflow execution is successfully deleted, Status.ERROR if workflow
   *     execution does not exist otherwise.
   */
  public Status deleteWorkflowExecutionById(Long executionId) throws Exception {
    return this.metadataClient.deleteWorkflowExecutionById(executionId);
  }

  /**
   * Delete registered workflow execution by workflow execution name.
   *
   * @param executionName Name of workflow execution.
   * @return Status.OK if workflow execution is successfully deleted, Status.ERROR if workflow
   *     execution does not exist otherwise.
   */
  public Status deleteWorkflowExecutionByName(String executionName) throws Exception {
    return this.metadataClient.deleteWorkflowExecutionByName(executionName);
  }

  /**
   * Get a specific job in Metadata Store by job id.
   *
   * @param jobId Id of job.
   * @return Single JobMeta object if job exists, otherwise returns None if job does not exist.
   */
  public JobMeta getJobById(Long jobId) throws Exception {
    return this.metadataClient.getJobById(jobId);
  }

  /**
   * Get a specific job in Metadata Store by job name.
   *
   * @param jobName Name of job.
   * @return Single JobMeta object if job exists, otherwise returns None if job does not exist.
   */
  public JobMeta getJobByName(String jobName) throws Exception {
    return this.metadataClient.getJobByName(jobName);
  }

  /**
   * Register a job in Metadata Store.
   *
   * @param name Mame of job.
   * @param jobState State of job.
   * @param workflowExecutionId Workflow execution id corresponded to job.
   * @param properties Properties of job.
   * @param jobId Job id of job.
   * @param startTime Time when job started.
   * @param endTime Time when job ended.
   * @param logUri Log uri of job.
   * @param signature Signature of job.
   * @return Single JobMeta object registered in Metadata Store.
   */
  public JobMeta registerJob(
      String name,
      State jobState,
      Long workflowExecutionId,
      Map<String, String> properties,
      String jobId,
      Long startTime,
      Long endTime,
      String logUri,
      String signature)
      throws Exception {
    return this.metadataClient.registerJob(
        name,
        jobState,
        workflowExecutionId,
        properties,
        jobId,
        startTime,
        endTime,
        logUri,
        signature);
  }

  /**
   * Update a job in Metadata Store.
   *
   * @param name Mame of job.
   * @param jobState State of job.
   * @param workflowExecutionId Workflow execution id corresponded to job.
   * @param properties Properties of job.
   * @param jobId Job id of job.
   * @param endTime Time when job ended.
   * @param logUri Log uri of job.
   * @param signature Signature of job.
   * @return Single JobMeta object registered in Metadata Store.
   */
  public JobMeta updateJob(
      String name,
      State jobState,
      Long workflowExecutionId,
      Map<String, String> properties,
      String jobId,
      Long endTime,
      String logUri,
      String signature)
      throws Exception {
    return this.metadataClient.updateJob(
        name, jobState, workflowExecutionId, properties, jobId, endTime, logUri, signature);
  }

  /**
   * List registered jobs in Metadata Store.
   *
   * @param pageSize Limitation of listed jobs.
   * @param offset Offset of listed jobs.
   * @return List of JobMeta object registered in Metadata Store.
   */
  public List<JobMeta> listJob(Long pageSize, Long offset) throws Exception {
    return this.metadataClient.listJob(pageSize, offset);
  }

  /**
   * Update job end time in Metadata Store.
   *
   * @param endTime Time when job ended.
   * @param jobName Name of job.
   * @return Job uuid if job is successfully updated, raise an exception, if fail to update
   *     otherwise.
   */
  public JobMeta updateJobEndTime(Long endTime, String jobName) throws Exception {
    return this.metadataClient.updateJobEndTime(endTime, jobName);
  }

  /**
   * Update job state in Metadata Store.
   *
   * @param state State of job.
   * @param jobName Name of job.
   * @return Job uuid if job is successfully updated, raise an exception, if fail to update
   *     otherwise.
   */
  public JobMeta updateJobState(State state, String jobName) throws Exception {
    return this.metadataClient.updateJobState(state, jobName);
  }

  /**
   * Delete registered job by job id.
   *
   * @param jobId Id of job.
   * @return Status.OK if job is successfully deleted, Status.ERROR if job does not exist otherwise.
   */
  public Status deleteJobById(Long jobId) throws Exception {
    return this.metadataClient.deleteJobById(jobId);
  }

  /**
   * Delete registered job by job name.
   *
   * @param jobName Name of job.
   * @return Status.OK if job is successfully deleted, Status.ERROR if job does not exist otherwise.
   */
  public Status deleteJobByName(String jobName) throws Exception {
    return this.metadataClient.deleteJobByName(jobName);
  }

  /**
   * Get a specific project in Metadata Store by project id.
   *
   * @param projectId Id of project.
   * @return Single ProjectMeta object if project exists, otherwise returns None if project does not
   *     exist.
   */
  public ProjectMeta getProjectById(Long projectId) throws Exception {
    return this.metadataClient.getProjectById(projectId);
  }

  /**
   * Get a specific project in Metadata Store by project name.
   *
   * @param projectName Name of project.
   * @return Single ProjectMeta object if project exists, otherwise returns None if project does not
   *     exist.
   */
  public ProjectMeta getProjectByName(String projectName) throws Exception {
    return this.metadataClient.getProjectByName(projectName);
  }

  /**
   * Register a project in Metadata Store.
   *
   * @param name Name of project.
   * @param uri Uri of project
   * @param properties Properties of project
   * @return Single ProjectMeta object registered in Metadata Store.
   */
  public ProjectMeta registerProject(
      String name,
      String uri,
      Map<String, String> properties)
      throws Exception {
    return this.metadataClient.registerProject(name, uri, properties);
  }

  /**
   * Update a project in Metadata Store.
   *
   * @param name Name of project.
   * @param uri Uri of project
   * @param properties Properties of project
   * @return Single ProjectMeta object registered in Metadata Store.
   */
  public ProjectMeta updateProject(
      String name,
      String uri,
      Map<String, String> properties)
      throws Exception {
    return this.metadataClient.updateProject(name, uri, properties);
  }

  /**
   * List registered projects in Metadata Store.
   *
   * @param pageSize Limitation of listed projects.
   * @param offset Offset of listed projects.
   * @return List of ProjectMeta object registered in Metadata Store.
   */
  public List<ProjectMeta> listProject(Long pageSize, Long offset) throws Exception {
    return this.metadataClient.listProject(pageSize, offset);
  }

  /**
   * Delete registered project by project id.
   *
   * @param projectId Id of project.
   * @return Status.OK if project is successfully deleted, Status.ERROR if project does not exist
   *     otherwise.
   */
  public Status deleteProjectById(Long projectId) throws Exception {
    return this.metadataClient.deleteProjectById(projectId);
  }

  /**
   * Delete registered project by project name.
   *
   * @param projectName Name of project.
   * @return Status.OK if project is successfully deleted, Status.ERROR if project does not exist
   *     otherwise.
   */
  public Status deleteProjectByName(String projectName) throws Exception {
    return this.metadataClient.deleteProjectByName(projectName);
  }

  /**
   * Get a specific artifact in Metadata Store by artifact id.
   *
   * @param artifactId Id of artifact.
   * @return Single ArtifactMeta object if artifact exists, otherwise returns None if artifact does
   *     not exist.
   */
  public ArtifactMeta getArtifactById(Long artifactId) throws Exception {
    return this.metadataClient.getArtifactById(artifactId);
  }

  /**
   * Get a specific artifact in Metadata Store by artifact name.
   *
   * @param artifactName Name of artifact.
   * @return Single ArtifactMeta object if artifact exists, otherwise returns None if artifact does
   *     not exist.
   */
  public ArtifactMeta getArtifactByName(String artifactName) throws Exception {
    return this.metadataClient.getArtifactByName(artifactName);
  }

  /**
   * Register a artifact in Metadata Store.
   *
   * @param name Name of artifact.
   * @param dataFormat Data format of artifact.
   * @param description Description of artifact.
   * @param batchUri Batch uri of artifact.
   * @param streamUri Stream uri of artifact.
   * @param createTime Time when artifact is created.
   * @param updateTime Time when artifact is updated.
   * @param properties Properties of artifact.
   * @return Single ArtifactMeta object registered in Metadata Store.
   */
  public ArtifactMeta registerArtifact(
      String name,
      String dataFormat,
      String description,
      String batchUri,
      String streamUri,
      Long createTime,
      Long updateTime,
      Map<String, String> properties)
      throws Exception {
    return this.metadataClient.registerArtifact(
        name, dataFormat, description, batchUri, streamUri, createTime, updateTime, properties);
  }

  /**
   * Update a artifact in Metadata Store.
   *
   * @param name Name of artifact.
   * @param dataFormat Data format of artifact.
   * @param description Description of artifact.
   * @param batchUri Batch uri of artifact.
   * @param streamUri Stream uri of artifact.
   * @param updateTime Time when artifact is updated.
   * @param properties Properties of artifact.
   * @return Single ArtifactMeta object registered in Metadata Store.
   */
  public ArtifactMeta updateArtifact(
      String name,
      String dataFormat,
      String description,
      String batchUri,
      String streamUri,
      Long updateTime,
      Map<String, String> properties)
      throws Exception {
    return this.metadataClient.updateArtifact(
        name, dataFormat, description, batchUri, streamUri, updateTime, properties);
  }

  /**
   * List registered artifacts in Metadata Store.
   *
   * @param pageSize Limitation of listed artifacts.
   * @param offset Offset of listed artifacts.
   * @return List of ArtifactMeta object registered in Metadata Store.
   */
  public List<ArtifactMeta> listArtifact(Long pageSize, Long offset) throws Exception {
    return this.metadataClient.listArtifact(pageSize, offset);
  }

  /**
   * Delete registered artifact by artifact id.
   *
   * @param artifactId Id of artifact.
   * @return Status.OK if artifact is successfully deleted, Status.ERROR if artifact does not exist
   *     otherwise.
   */
  public Status deleteArtifactById(Long artifactId) throws Exception {
    return this.metadataClient.deleteArtifactById(artifactId);
  }

  /**
   * Delete registered artifact by artifact name.
   *
   * @param artifactName Name of artifact.
   * @return Status.OK if artifact is successfully deleted, Status.ERROR if artifact does not exist
   *     otherwise.
   */
  public Status deleteArtifactByName(String artifactName) throws Exception {
    return this.metadataClient.deleteArtifactByName(artifactName);
  }

  /**
   * Create a new registered model from given type in Model Center.
   *
   * @param modelName Name of registered model. This is expected to be unique in the backend store.
   * @param modelType Type of registered model.
   * @param modelDesc (Optional) Description of registered model.
   * @return Object of RegisteredModel created in Model Center.
   */
  public RegisteredModel createRegisteredModel(
      String modelName, ModelType modelType, String modelDesc) throws Exception {
    return this.modelCenterClient.createRegisteredModel(modelName, modelType, modelDesc);
  }

  /**
   * Update metadata for RegisteredModel entity backend. Either ``modelName`` or ``modelType`` or
   * ``modelDesc`` should be non-None. Backend raises exception if a registered model with given
   * name does not exist.
   *
   * @param modelName Name of registered model. This is expected to be unique in the backend store.
   * @param newName (Optional) New proposed name for the registered model.
   * @param modelType (Optional) Type of registered model.
   * @param modelDesc (Optional) Description of registered model.
   * @return Object of RegisteredModel updated in Model Center.
   */
  public RegisteredModel updateRegisteredModel(
      String modelName, String newName, ModelType modelType, String modelDesc) throws Exception {
    return this.modelCenterClient.updateRegisteredModel(modelName, newName, modelType, modelDesc);
  }

  /**
   * Delete registered model by model name in Model Center backend.
   *
   * @param modelName Name of registered model. This is expected to be unique in the backend store.
   * @return Object of RegisteredModel deleted in Model Center.
   */
  public RegisteredModel deleteRegisteredModel(String modelName) throws Exception {
    return this.modelCenterClient.deleteRegisteredModel(modelName);
  }

  /**
   * List of all registered models in Model Center backend.
   *
   * @return List of RegisteredModel created in Model Center.
   */
  public List<RegisteredModel> listRegisteredModels() throws Exception {
    return this.modelCenterClient.listRegisteredModels();
  }

  /**
   * Get registered model detail filter by model name for Model Center.
   *
   * @param modelName Name of registered model. This is expected to be unique in the backend store.
   * @return Object of RegisteredModel created in Model Center.
   */
  public RegisteredModel getRegisteredModelDetail(String modelName) throws Exception {
    return this.modelCenterClient.getRegisteredModelDetail(modelName);
  }

  /**
   * Create a new registered model from given type in Model Center.
   *
   * @param modelName Name of registered model. This is expected to be unique in the backend store.
   * @param modelPath Source path where the AIFlow model is stored.
   * @param modelMetric Metric address from AIFlow metric server of registered model.
   * @param modelFlavor (Optional) Flavor feature of AIFlow registered model option.
   * @param versionDesc (Optional) Description of registered model version.
   * @return Object of ModelVersion created in Model Center.
   */
  public ModelVersion createModelVersion(
      String modelName,
      String modelPath,
      String modelMetric,
      String modelFlavor,
      String versionDesc)
      throws Exception {
    return this.modelCenterClient.createModelVersion(
        modelName, modelPath, modelMetric, modelFlavor, versionDesc);
  }

  /**
   * Update metadata for ModelVersion entity and metadata associated with a model version in
   * backend. Either ``modelPath`` or ``modelMetric`` or ``modelFlavor`` or ``versionDesc`` should
   * be non-None. Backend raises exception if a registered model with given name does not exist.
   *
   * @param modelName Name of registered model. This is expected to be unique in the backend store.
   * @param modelVersion User-defined version of registered model.
   * @param modelPath (Optional) Source path where the AIFlow model is stored.
   * @param modelMetric (Optional) Metric address from AIFlow metric server of registered model.
   * @param modelFlavor (Optional) Flavor feature of AIFlow registered model option.
   * @param versionDesc (Optional) Description of registered model version.
   * @param currentStage (Optional) Current stage for registered model version.
   * @return Object of ModelVersion updated in Model Center.
   */
  public ModelVersion updateModelVersion(
      String modelName,
      String modelVersion,
      String modelPath,
      String modelMetric,
      String modelFlavor,
      String versionDesc,
      ModelStage currentStage)
      throws Exception {
    return this.modelCenterClient.updateModelVersion(
        modelName, modelVersion, modelPath, modelMetric, modelFlavor, versionDesc, currentStage);
  }

  /**
   * Delete model version by model name and version in Model Center backend.
   *
   * @param modelName Name of registered model. This is expected to be unique in the backend store.
   * @param modelVersion User-defined version of registered model.
   * @return Object of ModelVersion deleted in Model Center.
   */
  public ModelVersion deleteModelVersion(String modelName, String modelVersion) throws Exception {
    return this.modelCenterClient.deleteModelVersion(modelName, modelVersion);
  }

  /**
   * Get model version detail filter by model name and model version for Model Center.
   *
   * @param modelName Name of registered model. This is expected to be unique in the backend store.
   * @param modelVersion User-defined version of registered model.
   * @return Object of ModelVersion created in Model Center.
   */
  public ModelVersion getModelVersionDetail(String modelName, String modelVersion)
      throws Exception {
    return this.modelCenterClient.getModelVersionDetail(modelName, modelVersion);
  }

    /**
     * Send the event to Notification Service.
     *
     * @param namespace Namespace of event updated in Notification Service.
     * @param key Key of event updated in Notification Service.
     * @param value Value of event updated in Notification Service.
     * @param eventType Type of event updated in Notification Service.
     * @param context Context of event updated in Notification Service.
     * @return Object of Event created in Notification Service.
     */
    public EventMeta sendEvent(
            String namespace, String key, String value, String eventType, String context)
            throws Exception {
        return this.notificationClient.sendEvent(namespace, key, value, eventType, context);
    }

    /**
     * List specific `key` or `version` notifications in Notification Service.
     *
     * @param namespace Namespace of notification for listening.
     * @param keys Keys of notification for listening.
     * @param version (Optional) Version of notification for listening.
     * @param eventType (Optional) Type of event for listening.
     * @param startTime (Optional) Type of event for listening.
     * @return List of Notification updated in Notification Service.
     */
    public List<EventMeta> listEvents(
            String namespace, List<String> keys, long version, String eventType, long startTime)
            throws Exception {
        return this.notificationClient.listEvents(namespace, keys, version, eventType, startTime);
    }

    /**
     * Start listen specific `key` or `version` notifications in Notification Service.
     *
     * @param namespace Namespace of notification for listening.
     * @param key Key of notification for listening.
     * @param watcher Watcher instance for listening notification.
     * @param version (Optional) Version of notification for listening.
     * @param eventType (Optional) Type of event for listening.
     * @param startTime (Optional) Type of event for listening.
     */
    public void startListenEvent(
            String namespace,
            String key,
            EventWatcher watcher,
            long version,
            String eventType,
            long startTime) {
        this.notificationClient.startListenEvent(
                namespace, key, watcher, version, eventType, startTime);
    }

    /**
     * Stop listen specific `key` notifications in Notification Service.
     *
     * @param key Key of notification for listening.
     */
    public void stopListenEvent(String namespace, String key) {
        this.notificationClient.stopListenEvent(namespace, key);
    }

    /**
     * Get latest version of specific `key` notifications in Notification Service.
     *
     * @param namespace Namespace of notification for listening.
     * @param key Key of notification for listening.
     */
    public long getLatestVersion(String namespace, String key) throws Exception {
        return this.notificationClient.getLatestVersion(namespace, key);
    }
}
