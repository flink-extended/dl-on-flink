/*!
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

import request from '@/utils/request'

const api = {
  role: '/role',
  project: '/project',
  workflow: '/workflow',
  dataView: '/workflow/data-view',
  taskView: '/workflow/task-view',
  workflowExecution: '/workflow-execution',
  jobExecution: '/job-execution',
  dataset: '/dataset',
  model: '/model',
  modelVersion: '/model-version',
  artifact: '/artifact'
}

export default api

export function getRoleList (parameter) {
  return request({
    url: api.role,
    method: 'get',
    params: parameter
  })
}

export function getProjects (parameter) {
  return request({
    url: api.project,
    method: 'get',
    params: parameter
  })
}

export function getWorkflows (parameter) {
  return request({
    url: api.workflow,
    method: 'get',
    params: parameter
  })
}

export function getWorkflowExecutions (parameter) {
  return request({
    url: api.workflowExecution,
    method: 'get',
    params: parameter
  })
}

export function getJobExecutions (parameter) {
  return request({
    url: api.jobExecution,
    method: 'get',
    params: parameter
  })
}

export function getDatasets (parameter) {
  return request({
    url: api.dataset,
    method: 'get',
    params: parameter
  })
}

export function getModels (parameter) {
  return request({
    url: api.model,
    method: 'get',
    params: parameter
  })
}

export function getModelVersions (parameter) {
  return request({
    url: api.modelVersion,
    method: 'get',
    params: parameter
  })
}

export function getArtifacts (parameter) {
  return request({
    url: api.artifact,
    method: 'get',
    params: parameter
  })
}

export function getDataView (parameter) {
  return request({
    url: api.dataView,
    method: 'get',
    params: parameter
  })
}

export function getTaskView (parameter) {
  return request({
    url: api.taskView,
    method: 'get',
    params: parameter
  })
}
