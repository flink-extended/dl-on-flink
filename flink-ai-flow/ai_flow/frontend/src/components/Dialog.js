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

import Modal from 'ant-design-vue/es/modal'
export default (Vue) => {
  function dialog (component, componentProps, modalProps) {
    const _vm = this
    modalProps = modalProps || {}
    if (!_vm || !_vm._isVue) {
      return
    }
    let dialogDiv = document.querySelector('body>div[type=dialog]')
    if (!dialogDiv) {
      dialogDiv = document.createElement('div')
      dialogDiv.setAttribute('type', 'dialog')
      document.body.appendChild(dialogDiv)
    }

    const handle = function (checkFunction, afterHandel) {
      if (checkFunction instanceof Function) {
        const res = checkFunction()
        if (res instanceof Promise) {
          res.then(c => {
            c && afterHandel()
          })
        } else {
          res && afterHandel()
        }
      } else {
        // checkFunction && afterHandel()
        checkFunction || afterHandel()
      }
    }

    const dialogInstance = new Vue({
      data () {
        return {
          visible: true
        }
      },
      router: _vm.$router,
      store: _vm.$store,
      mounted () {
        this.$on('close', (v) => {
          this.handleClose()
        })
      },
      methods: {
        handleClose () {
          handle(this.$refs._component.onCancel, () => {
            this.visible = false
            this.$refs._component.$emit('close')
            this.$refs._component.$emit('cancel')
            dialogInstance.$destroy()
          })
        },
        handleOk () {
          handle(this.$refs._component.onOK || this.$refs._component.onOk, () => {
            this.visible = false
            this.$refs._component.$emit('close')
            this.$refs._component.$emit('ok')
            dialogInstance.$destroy()
          })
        }
      },
      render: function (h) {
        const that = this
        const modalModel = modalProps && modalProps.model
        if (modalModel) {
          delete modalProps.model
        }
        const ModalProps = Object.assign({}, modalModel && { model: modalModel } || {}, {
          attrs: Object.assign({}, {
            ...(modalProps.attrs || modalProps)
          }, {
            visible: this.visible
          }),
          on: Object.assign({}, {
            ...(modalProps.on || modalProps)
          }, {
            ok: () => {
              that.handleOk()
            },
            cancel: () => {
              that.handleClose()
            }
          })
        })

        const componentModel = componentProps && componentProps.model
        if (componentModel) {
          delete componentProps.model
        }
        const ComponentProps = Object.assign({}, componentModel && { model: componentModel } || {}, {
          ref: '_component',
          attrs: Object.assign({}, {
            ...((componentProps && componentProps.attrs) || componentProps)
          }),
          on: Object.assign({}, {
            ...((componentProps && componentProps.on) || componentProps)
          })
        })

        return h(Modal, ModalProps, [h(component, ComponentProps)])
      }
    }).$mount(dialogDiv)
  }

  Object.defineProperty(Vue.prototype, '$dialog', {
    get: () => {
      return function () {
        dialog.apply(this, arguments)
      }
    }
  })
}
