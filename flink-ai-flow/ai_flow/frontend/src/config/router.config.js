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

// eslint-disable-next-line
import { UserLayout, BasicLayout, BlankLayout } from '@/layouts'

const RouteView = {
  name: 'RouteView',
  render: h => h('router-view')
}

export const asyncRouterMap = [
  {
    path: '/',
    name: 'index',
    component: BasicLayout,
    meta: { title: 'menu.home' },
    redirect: '/metadata',
    children: [
      // metadata
      {
        path: '/metadata',
        name: 'metadata',
        component: RouteView,
        redirect: '/metadata/project',
        meta: { title: 'menu.metadata', icon: 'table', permission: ['table'] },
        children: [
          {
            path: '/metadata/project/:pageNo([1-9]\\d*)?',
            name: 'project',
            hideChildrenInMenu: true,
            component: () => import('@/views/metadata/Project'),
            meta: { title: 'menu.metadata.project', keepAlive: true, permission: ['table'] }
          },
          {
            path: '/metadata/workflow/:pageNo([1-9]\\d*)?',
            name: 'workflow',
            hideChildrenInMenu: true,
            component: () => import('@/views/metadata/Workflow'),
            meta: { title: 'menu.metadata.workflow', keepAlive: true, permission: ['table'] }
          },
          {
            path: '/metadata/workflow-execution/:pageNo([1-9]\\d*)?',
            name: 'workflow-execution',
            hideChildrenInMenu: true,
            component: () => import('@/views/metadata/WorkflowExecution'),
            meta: { title: 'menu.metadata.workflow-execution', keepAlive: true, permission: ['table'] }
          },
          {
            path: '/metadata/job-execution/:pageNo([1-9]\\d*)?',
            name: 'job-execution',
            hideChildrenInMenu: true,
            component: () => import('@/views/metadata/JobExecution'),
            meta: { title: 'menu.metadata.job-execution', keepAlive: true, permission: ['table'] }
          },
          {
            path: '/metadata/dataset/:pageNo([1-9]\\d*)?',
            name: 'dataset',
            hideChildrenInMenu: true,
            component: () => import('@/views/metadata/Dataset'),
            meta: { title: 'menu.metadata.dataset', keepAlive: true, permission: ['table'] }
          },
          {
            path: '/metadata/model/:pageNo([1-9]\\d*)?',
            name: 'model',
            hideChildrenInMenu: true,
            component: () => import('@/views/metadata/Model'),
            meta: { title: 'menu.metadata.model', keepAlive: true, permission: ['table'] }
          },
          {
            path: '/metadata/model-version/:pageNo([1-9]\\d*)?',
            name: 'model-version',
            hideChildrenInMenu: true,
            component: () => import('@/views/metadata/ModelVersion'),
            meta: { title: 'menu.metadata.model-version', keepAlive: true, permission: ['table'] }
          },
          {
            path: '/metadata/artifact/:pageNo([1-9]\\d*)?',
            name: 'artifact',
            hideChildrenInMenu: true,
            component: () => import('@/views/metadata/Artifact'),
            meta: { title: 'menu.metadata.artifact', keepAlive: true, permission: ['table'] }
          }
        ]
      }
    ]
  },
  {
    path: '*',
    redirect: '/404',
    hidden: true
  }
]

export const constantRouterMap = [
  {
    path: '/user',
    component: UserLayout,
    redirect: '/user/login',
    hidden: true,
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/Login')
      },
      {
        path: 'recover',
        name: 'recover',
        component: undefined
      }
    ]
  },
  {
    path: '/404',
    component: () => import(/* webpackChunkName: "fail" */ '@/views/exception/404')
  }
]
