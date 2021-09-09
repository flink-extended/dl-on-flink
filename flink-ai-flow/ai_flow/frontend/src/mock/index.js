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

import { isIE } from '@/utils/util'

if (process.env.NODE_ENV !== 'production' || process.env.VUE_APP_PREVIEW === 'true') {
  if (isIE()) {
    console.error('[Flink AI Flow] ERROR: `mockjs` NOT SUPPORT `IE` PLEASE DO NOT USE IN `production` ENV.')
  }
  console.log('[Flink AI Flow] mock mounting')
  const Mock = require('mockjs2')
  require('./services/auth')
  require('./services/user')
  require('./services/other')

  Mock.setup({
    timeout: 800
  })
  console.log('[Flink AI Flow] mock mounted')
}
