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

import events from './events'
import MultiTab from './MultiTab'
import './index.less'

const api = {
  /**
   * open new tab on route fullPath
   * @param config
   */
  open: function (config) {
    events.$emit('open', config)
  },
  rename: function (key, name) {
    events.$emit('rename', { key: key, name: name })
  },
  /**
   * close current page
   */
  closeCurrentPage: function () {
    this.close()
  },
  /**
   * close route fullPath tab
   * @param config
   */
  close: function (config) {
    events.$emit('close', config)
  }
}

MultiTab.install = function (Vue) {
  if (Vue.prototype.$multiTab) {
    return
  }
  api.instance = events
  Vue.prototype.$multiTab = api
  Vue.component('multi-tab', MultiTab)
}

export default MultiTab
