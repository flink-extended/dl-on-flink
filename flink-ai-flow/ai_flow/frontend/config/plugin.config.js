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

const ThemeColorReplacer = require('webpack-theme-color-replacer')
const generate = require('@ant-design/colors/lib/generate').default

const getAntdSerials = (color) => {
  const lightens = new Array(9).fill().map((t, i) => {
    return ThemeColorReplacer.varyColor.lighten(color, i / 10)
  })
  const colorPalettes = generate(color)
  const rgb = ThemeColorReplacer.varyColor.toNum3(color.replace('#', '')).join(',')
  return lightens.concat(colorPalettes).concat(rgb)
}

const themePluginOption = {
  fileName: 'css/theme-colors-[contenthash:8].css',
  matchColors: getAntdSerials('#1890ff'),
  changeSelector (selector) {
    switch (selector) {
      case '.ant-calendar-today .ant-calendar-date':
        return ':not(.ant-calendar-selected-date):not(.ant-calendar-selected-day)' + selector
      case '.ant-btn:focus,.ant-btn:hover':
        return '.ant-btn:focus:not(.ant-btn-primary):not(.ant-btn-danger),.ant-btn:hover:not(.ant-btn-primary):not(.ant-btn-danger)'
      case '.ant-btn.active,.ant-btn:active':
        return '.ant-btn.active:not(.ant-btn-primary):not(.ant-btn-danger),.ant-btn:active:not(.ant-btn-primary):not(.ant-btn-danger)'
      case '.ant-steps-item-process .ant-steps-item-icon > .ant-steps-icon':
      case '.ant-steps-item-process .ant-steps-item-icon>.ant-steps-icon':
        return ':not(.ant-steps-item-process)' + selector
      // fixed https://github.com/vueComponent/ant-design-vue-pro/issues/876
      case '.ant-steps-item-process .ant-steps-item-icon':
        return ':not(.ant-steps-item-custom)' + selector
      case '.ant-menu-horizontal>.ant-menu-item-active,.ant-menu-horizontal>.ant-menu-item-open,.ant-menu-horizontal>.ant-menu-item-selected,.ant-menu-horizontal>.ant-menu-item:hover,.ant-menu-horizontal>.ant-menu-submenu-active,.ant-menu-horizontal>.ant-menu-submenu-open,.ant-menu-horizontal>.ant-menu-submenu-selected,.ant-menu-horizontal>.ant-menu-submenu:hover':
      case '.ant-menu-horizontal > .ant-menu-item-active,.ant-menu-horizontal > .ant-menu-item-open,.ant-menu-horizontal > .ant-menu-item-selected,.ant-menu-horizontal > .ant-menu-item:hover,.ant-menu-horizontal > .ant-menu-submenu-active,.ant-menu-horizontal > .ant-menu-submenu-open,.ant-menu-horizontal > .ant-menu-submenu-selected,.ant-menu-horizontal > .ant-menu-submenu:hover':
        return '.ant-menu-horizontal > .ant-menu-item-active,.ant-menu-horizontal > .ant-menu-item-open,.ant-menu-horizontal > .ant-menu-item-selected,.ant-menu-horizontal:not(.ant-menu-dark) > .ant-menu-item:hover,.ant-menu-horizontal > .ant-menu-submenu-active,.ant-menu-horizontal > .ant-menu-submenu-open,.ant-menu-horizontal:not(.ant-menu-dark) > .ant-menu-submenu-selected,.ant-menu-horizontal:not(.ant-menu-dark) > .ant-menu-submenu:hover'
      case '.ant-menu-horizontal > .ant-menu-item-selected > a':
      case '.ant-menu-horizontal>.ant-menu-item-selected>a':
        return '.ant-menu-horizontal:not(ant-menu-light):not(.ant-menu-dark) > .ant-menu-item-selected > a'
      case '.ant-menu-horizontal > .ant-menu-item > a:hover':
      case '.ant-menu-horizontal>.ant-menu-item>a:hover':
        return '.ant-menu-horizontal:not(ant-menu-light):not(.ant-menu-dark) > .ant-menu-item > a:hover'
      default :
        return selector
    }
  }
}

const createThemeColorReplacerPlugin = () => new ThemeColorReplacer(themePluginOption)

module.exports = createThemeColorReplacerPlugin
