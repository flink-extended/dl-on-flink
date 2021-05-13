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

/* global window, dagTZ, moment, convertSecsToHumanReadable */

// We don't re-import moment again, otherwise webpack will include it twice in the bundle!
import { escapeHtml } from './main';

export default function eTooltip(e, { includeTryNumber = false } = {}) {
  let tt = '';
  tt += `<strong>Namespace:</strong> ${escapeHtml(e[0])}<br><br>`;
  tt += `Event_Key: ${escapeHtml(e[1])}<br>`;
  tt += `Event_Type: ${escapeHtml(e[2])}<br><br>`;
  tt +=`<em><strong>Send_Count:</strong> ${escapeHtml(e[3])}</em>`;
  return tt;
}

window.eTooltip = eTooltip;
