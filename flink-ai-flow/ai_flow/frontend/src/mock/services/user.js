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

import Mock from 'mockjs2'
import { builder } from '../util'

const info = options => {
  console.log('options', options)
  const userInfo = {
    id: '4291d7da9005377ec9aec4a71ea837f',
    name: 'AIFlow',
    username: 'admin',
    password: '',
    avatar: '/avatar2.jpg',
    status: 1,
    telephone: '',
    lastLoginIp: '27.154.74.117',
    lastLoginTime: 1534837621348,
    creatorId: 'admin',
    createTime: 1497160610259,
    merchantCode: 'TLif2btpzg079h15bk',
    deleted: 0,
    roleId: 'admin',
    role: {}
  }
  // role
  const roleObj = {
    id: 'admin',
    name: 'admin',
    describe: 'all permission',
    status: 1,
    creatorId: 'system',
    createTime: 1497160610259,
    deleted: 0,
    permissions: [
      {
        roleId: 'admin',
        permissionId: 'exception',
        permissionName: 'ExceptionPermission',
        actions:
          '[{"action":"add","defaultCheck":false,"describe":"add"},{"action":"query","defaultCheck":false,"describe":"查询"},{"action":"get","defaultCheck":false,"describe":"get"},{"action":"update","defaultCheck":false,"describe":"update"},{"action":"delete","defaultCheck":false,"describe":"删除"}]',
        actionEntitySet: [
          {
            action: 'add',
            describe: 'add',
            defaultCheck: false
          },
          {
            action: 'query',
            describe: 'query',
            defaultCheck: false
          },
          {
            action: 'get',
            describe: 'get',
            defaultCheck: false
          },
          {
            action: 'update',
            describe: 'update',
            defaultCheck: false
          },
          {
            action: 'delete',
            describe: 'delete',
            defaultCheck: false
          }
        ],
        actionList: null,
        dataAccess: null
      },
      {
        roleId: 'admin',
        permissionId: 'table',
        permissionName: 'TablePermission',
        actions:
          '[{"action":"add","defaultCheck":false,"describe":"add"},{"action":"import","defaultCheck":false,"describe":"import"},{"action":"get","defaultCheck":false,"describe":"get"},{"action":"update","defaultCheck":false,"describe":"update"}]',
        actionEntitySet: [
          {
            action: 'add',
            describe: 'add',
            defaultCheck: false
          },
          {
            action: 'import',
            describe: 'import',
            defaultCheck: false
          },
          {
            action: 'get',
            describe: 'get',
            defaultCheck: false
          },
          {
            action: 'update',
            describe: 'update',
            defaultCheck: false
          }
        ],
        actionList: null,
        dataAccess: null
      }
    ]
  }

  userInfo.role = roleObj
  return builder(userInfo)
}

const userNav = options => {
  const nav = [
    {
      name: 'metadata',
      parentId: 0,
      id: 10010,
      meta: {
        icon: 'table',
        title: 'Metadata',
        show: true
      },
      redirect: '/metadata/project',
      component: 'RouteView'
    },
    {
      name: 'project',
      parentId: 10010,
      id: 10011,
      path: '/metadata/project/:pageNo([1-9]\\d*)?',
      meta: {
        title: 'Project',
        show: true
      },
      component: 'Project'
    },
    {
      name: 'workflow',
      parentId: 10010,
      id: 10012,
      path: '/metadata/workflow/:pageNo([1-9]\\d*)?',
      meta: {
        title: 'Workflow',
        show: true
      },
      component: 'Workflow'
    },
    {
      name: 'workflow-execution',
      parentId: 10010,
      id: 10013,
      path: '/metadata/workflow-execution/:pageNo([1-9]\\d*)?',
      meta: {
        title: 'WorkflowExecution',
        show: true
      },
      component: 'WorkflowExecution'
    },
    {
      name: 'job-execution',
      parentId: 10010,
      id: 10014,
      path: '/metadata/job-execution/:pageNo([1-9]\\d*)?',
      meta: {
        title: 'JobExecution',
        show: true
      },
      component: 'JobExecution'
    },
    {
      name: 'dataset',
      parentId: 10010,
      id: 10015,
      path: '/metadata/dataset/:pageNo([1-9]\\d*)?',
      meta: {
        title: 'Dataset',
        show: true
      },
      component: 'Dataset'
    },
    {
      name: 'model',
      parentId: 10010,
      id: 10016,
      path: '/metadata/model/:pageNo([1-9]\\d*)?',
      meta: {
        title: 'Model',
        show: true
      },
      component: 'Model'
    },
    {
      name: 'model-version',
      parentId: 10010,
      id: 10017,
      path: '/metadata/model-version/:pageNo([1-9]\\d*)?',
      meta: {
        title: 'ModelVersion',
        show: true
      },
      component: 'ModelVersion'
    },
    {
      name: 'artifact',
      parentId: 10010,
      id: 10018,
      path: '/metadata/artifact/:pageNo([1-9]\\d*)?',
      meta: {
        title: 'Artifact',
        show: true
      },
      component: 'Artifact'
    },
    {
      name: 'graph',
      parentId: 10010,
      id: 10019,
      path: '/graph/*',
      meta: {
        title: 'Graph',
        show: false
      },
      component: 'Graph'
    }
  ]
  const json = builder(nav)
  console.log('json', json)
  return json
}

Mock.mock(/\/api\/user\/info/, 'get', info)
Mock.mock(/\/api\/user\/nav/, 'get', userNav)
