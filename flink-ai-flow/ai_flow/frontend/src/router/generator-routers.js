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
import * as loginService from '@/api/login'
// eslint-disable-next-line
import { BasicLayout, BlankLayout, PageView, RouteView } from '@/layouts'

const constantRouterComponents = {
  BasicLayout: BasicLayout,
  BlankLayout: BlankLayout,
  RouteView: RouteView,
  PageView: PageView,
  '403': () => import(/* webpackChunkName: "error" */ '@/views/exception/403'),
  '404': () => import(/* webpackChunkName: "error" */ '@/views/exception/404'),
  '500': () => import(/* webpackChunkName: "error" */ '@/views/exception/500'),

  Project: () => import('@/views/metadata/Project'),
  Workflow: () => import('@/views/metadata/Workflow'),
  WorkflowExecution: () => import('@/views/metadata/WorkflowExecution'),
  JobExecution: () => import('@/views/metadata/JobExecution'),
  Dataset: () => import('@/views/metadata/Dataset'),
  Model: () => import('@/views/metadata/Model'),
  ModelVersion: () => import('@/views/metadata/ModelVersion'),
  Artifact: () => import('@/views/metadata/Artifact'),
  Graph: () => import('@/views/metadata/Graph'),

  Exception403: () => import(/* webpackChunkName: "fail" */ '@/views/exception/403'),
  Exception404: () => import(/* webpackChunkName: "fail" */ '@/views/exception/404'),
  Exception500: () => import(/* webpackChunkName: "fail" */ '@/views/exception/500')
}

const notFoundRouter = {
  path: '*',
  redirect: '/404',
  hidden: true
}

const rootRouter = {
  key: '',
  name: 'index',
  path: '',
  component: 'BasicLayout',
  redirect: '/metadata',
  meta: {
    title: 'Home'
  },
  children: []
}

export const generatorDynamicRouter = token => {
  return new Promise((resolve, reject) => {
    loginService
      .getCurrentUserNav(token)
      .then(res => {
        console.log('generatorDynamicRouter response:', res)
        const { result } = res
        const menuNav = []
        const childrenNav = []
        listToTree(result, childrenNav, 0)
        rootRouter.children = childrenNav
        menuNav.push(rootRouter)
        console.log('menuNav', menuNav)
        const routers = generator(menuNav)
        routers.push(notFoundRouter)
        console.log('routers', routers)
        resolve(routers)
      })
      .catch(err => {
        reject(err)
      })
  })
}

export const generator = (routerMap, parent) => {
  return routerMap.map(item => {
    const { title, show, hideChildren, hiddenHeaderContent, target, icon } = item.meta || {}
    const currentRouter = {
      path: item.path || `${(parent && parent.path) || ''}/${item.key}`,
      name: item.name || item.key || '',
      component: constantRouterComponents[item.component || item.key] || (() => import(`@/views/${item.component}`)),

      meta: {
        title: title,
        icon: icon || undefined,
        hiddenHeaderContent: hiddenHeaderContent,
        target: target,
        permission: item.name
      }
    }
    if (show === false) {
      currentRouter.hidden = true
    }
    if (hideChildren) {
      currentRouter.hideChildrenInMenu = true
    }
    if (!currentRouter.path.startsWith('http')) {
      currentRouter.path = currentRouter.path.replace('//', '/')
    }
    item.redirect && (currentRouter.redirect = item.redirect)
    if (item.children && item.children.length > 0) {
      currentRouter.children = generator(item.children, currentRouter)
    }
    return currentRouter
  })
}

const listToTree = (list, tree, parentId) => {
  list.forEach(item => {
    if (item.parentId === parentId) {
      const child = {
        ...item,
        key: item.key || item.name,
        children: []
      }
      listToTree(list, child.children, item.id)
      if (child.children.length <= 0) {
        delete child.children
      }
      tree.push(child)
    }
  })
}
