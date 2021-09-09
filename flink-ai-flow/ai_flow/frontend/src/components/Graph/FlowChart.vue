<!-- Licensed to the Apache Software Foundation (ASF) under one or more
contributor license agreements.  See the NOTICE file distributed with
this work for additional information regarding copyright ownership.
The ASF licenses this file to You under the Apache License, Version 2.0
(the "License"); you may not use this file except in compliance with
the License.  You may obtain a copy of the License at
  http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. -->

<template>
  <div class="flowchart flowchart-wrapper" @mousemove="mousemove">
    <div class="flowchart-links">
      <!-- 节点图路径path -->
      <svg ref="svg">
        <path
          v-for="(link, index) in chartLinks"
          :key="index"
          :style="{'stroke-width': linkWidth, 'stroke-dasharray': isSignal(link, index), stroke: highlightLink(link) }"
          :class="[
            'link', 'link' + index,
            {
              source: link.sourceFlag,
              noedit: canUserEditLinks
            }]"
          @click.stop="selectLink(index)"
          @contextmenu="contextLink(index, $event)">
        </path>
      </svg>
    </div>
    <!-- 节点内容 -->
    <ul class="flowchart-ops">
      <li
        class="flowchart-operator"
        :class="[{
                   horizontal: horizontal,
                   fixed: fixedWidth,
                   subtitle: op.properties.subtitle,
                   selected: op.id === selectedOperator.id
                 },
                 ...op.properties.class]"
        v-for="(op, index) in chartOperators"
        :key="index"
        :ref="'op' + index"
        :style="{top: op.top + 'px', left: op.left + 'px'}">
        <slot name="other" :data="op.properties">
        </slot>
        <div class="flowchart-operator-inputs-outputs">
          <div class="flowchart-operator-inputs" v-if="op.properties.inputs">
            <div class="flowchart-operator-connector">
              <div
                class="flowchart-operator-connector-arrow"
                :ref="'ins' + index"
                @click.stop="clickIns(op, $event)"
                :class="{noedit: !canUserEditLinks}">
              </div>
            </div>
          </div>
          <div class="flowchart-operator-outputs" v-if="op.properties.outputs">
            <div class="flowchart-operator-connector">
              <div
                class="flowchart-operator-connector-arrow"
                :ref="'outs' + index"
                @click.stop="clickOuts(op, $event)"
                :class="{noedit: !canUserEditLinks}">
              </div>
            </div>
          </div>
        </div>
        <div
          v-if="!op.properties.sourceFlag"
          :class="{ 'flowchart-operator-title': true, nomove: !canUserMoveOperators, custom: customTitle, 'virtual-node': !op.properties.isRealNode }"
          @click.stop="clickOperator(op)"
          @dblclick.stop="dbclickOperator(op)"
          @contextmenu="contextOperator(op, $event)">
          <slot :data="op.properties" name="node">
            {{ op.properties.title }}
            <div class="flowchart-operator-subtitle">{{ op.properties.subtitle }}</div>
          </slot>
        </div>
        <div
          v-else-if="op.properties.sourceFlag"
          class="operator-source"
          :class="{nomove: !canUserMoveOperators, custom: customTitle}"
          @click.stop="clickOperator(op)"
          @dblclick.stop="dbclickOperator(op)">
          <slot :data="op.properties" name="source">
            <div class="flowchart-operator-subtitle">{{ op.properties.dataName }}</div>
          </slot>
        </div>
      </li>
    </ul>
    <svg class="flowchart-links-tmp" v-if="drawing">
      <line class="link dash" :x1="line.x1" :y1="line.y1" :x2="line.x2" :y2="line.y2"></line>
    </svg>
    <v-contextmenu ref="linkcontextmenu">
      <v-contextmenu-item @click="delLink(selectedLinkId)">删除</v-contextmenu-item>
    </v-contextmenu>
  </div>
</template>

<script>
const MAPCOLOR = {
  source: 'rgb(230, 217, 76)',
  sink: 'rgb(101, 159, 252)',
  event: 'rgb(136, 193, 73)'
}

export default {
  props: {
    // 节点是否水平展示
    horizontal: {
      type: Boolean,
      default: false
    },
    fixedWidth: {
      type: Boolean,
      default: false
    },
    // 是否可选值
    selectable: {
      type: Boolean,
      default: false
    },
    // 双击
    dblclick: {
      type: Boolean,
      default: false
    },
    customTitle: {
      type: Boolean,
      default: false
    },
    canUserEditLinks: {
      type: Boolean,
      default: true
    },
    canUserMoveOperators: {
      type: Boolean,
      default: true
    },
    highlight: {
      type: Boolean,
      default: false
    },
    linkWidth: {
      type: Number,
      default: 6
    },
    linkBending: {
      type: Number,
      default: 100
    },
    // 节点数据
    operators: {
      type: Array,
      // eslint-disable-next-line vue/require-valid-default-prop
      default: []
    },
    grid: {
      type: Number,
      default: 20
    }
  },

  data () {
    return {
      name: 'FlowChart',
      selectedOperator: { id: -1 },
      selectedLinkId: -1,
      updated: false,
      drawing: null,
      drags: [],
      line: {
        x1: 0,
        y1: 0,
        x2: 0,
        y2: 0
      }
    }
  },

  computed: {
    _operators () {
      return this.operators.map(o => {
        return {
          ...o
        }
      })
    },
    // 节点数据
    chartOperators () {
      const result = {}
      this._operators.forEach((o, i) => {
        result[o.id] = {
          id: o.id,
          top: o.top,
          left: o.left,
          properties: {
            id: o.id || 0,
            title: o.title || '',
            dataName: o.dataName || '',
            sourceType: o.sourceType || '',
            isRealNode: o.isRealNode || false,
            sourceFlag: o.sourceFlag || false,
            isShowMaterial: o.isShowMaterial || false,
            subtitle: o.subtitle || '',
            materialParentProjectId: o.materialParentProjectId,
            class: 'flowchart-operator-' + (o.id || 0) + (' ' + o.class || ''),
            data: o.data || {},
            inputs: o.ins,
            outputs: o.outs
          }
        }
        this.$nextTick(_ => {
          if (this.canUserMoveOperators) {
            // this.drags[o.id] = this.drags[o.id] || new Draggable(this.$refs['op' + o.id][0])
            // this.drags[o.id].element = this.$refs['op' + o.id][0]
            // this.drags[o.id].handle = this.$refs['op' + o.id][0]
            this.drags[o.id].setOption('limit', this.$el)
            this.drags[o.id].setOption('threshold', 5)
            this.drags[o.id].setOption('onDrag', (el, x, y) => {
              this.dragOperator(x, y, o.id)
            })
            this.drags[o.id].setOption('onDragEnd', (el, x, y) => {
              this.update()
            })
          }
        })
      })
      return result
    },
    // svg path数据
    chartLinks () {
      const result = {}
      var linkNum = 0
      this._operators.forEach((o, index) => {
        o.parents.forEach((p, i) => {
          const { id, closedLoopNode } = p
          const parent = this._operators.find(op => op.id === id)
          const isSignal = ((o.signals || []).find(v => v.id === id) || {}).isSignal === 1
          if (parent && parent.outs && o.ins) {
            result[linkNum] = {
              fromOperator: id,
              close: closedLoopNode || false,
              fromConnector: 'outs',
              fromSubConnector: index,
              toOperator: o.id,
              toConnector: 'ins',
              subtitle: o.subtitle,
              sourceFlag: o.sourceFlag || parent.sourceFlag || false,
              toSubConnector: i,
              signal: isSignal || false
            }
            this.drawLink(linkNum, { ...p, close: closedLoopNode || false }, o.id)
            linkNum = linkNum + 1
          } else {
            const link = this.$refs.svg && this.$refs.svg.querySelector('link' + linkNum)
            link && link.remove()
          }
        })
      })
      return result
    }
  },

  watch: {
    horizontal (val) {
      this.refreshLink()
      this.update()
    },
    _operators: {
      handler () {
        this.update()
      },
      deep: true
    }
  },

  mounted () {
    document.addEventListener('click', this.docClick)
    if (this.canUserEditLinks) {
      this.$nextTick(_ => {
        document.addEventListener('keyup', this.keyup)
      })
    }
  },

  beforeDestroy () {
    document.removeEventListener('keyup', this.keyup)
    document.removeEventListener('click', this.docClick)
    this.drags.forEach(d => d.destory)
  },

  methods: {
    digUp (item) {
      this.$emit('digUp', item)
    },
    keyup (e) {
      if (e.keyCode === 8 || e.keyCode === 46) {
        if (this.selectedLinkId >= 0) {
          this.delLink()
        }
      }
    },
    docClick () {
      this.unselectOperator()
      this.unselectLink()
      this.drawing = null
    },
    clickOperator (data) {
      if (this.selectable) {
        this.selectedOperator = data
        this.$emit('operatorClick', (data.properties && data.properties.data) || null)
      }
    },
    dbclickOperator (data) {
      this.dblclick && this.$emit('operatorSelect', (data.properties && data.properties.data) || null)
    },
    contextOperator (data, e) {
      this.$emit('operatorContextMenu', (data.properties && data.properties.data) || null, e)
    },
    unselectOperator () {
      this.selectedOperator = { id: -1 }
    },
    dragOperator (x, y, id) {
      const operator = this._operators.find(o => o.id === id)
      const chartOperator = this.chartOperators[id]
      if (operator && chartOperator && x && y) {
        operator.top = y
        chartOperator.top = y
        operator.left = x
        chartOperator.left = x
        this.refreshLink()
      }
    },
    clickOuts (from, ev) {
      if (!this.drawing && this.canUserEditLinks) {
        this.drawing = from
        const domOperator = (this.$refs['op' + from.id] && this.$refs['op' + from.id][0]) || {
          offsetWidth: 84,
          offsetHeight: 50
        }
        this.line.x1 = this.horizontal ? from.left + domOperator.offsetWidth + ev.target.offsetWidth / 2 - 5 : from.left + ev.target.offsetLeft
        this.line.y1 = this.horizontal ? from.top + domOperator.offsetHeight / 2 : from.top + domOperator.offsetHeight + ev.target.offsetHeight / 2 - 5
        this.line.x2 = this.line.x1
        this.line.y2 = this.line.y1
        this.selectedLinkId = -1
      }
    },
    clickIns (to, ev) {
      if (this.drawing && this.drawing !== to) {
        this.addLink(this.drawing, to)
        this.drawing = null
      }
    },
    mousemove (ev) {
      if (this.drawing) {
        const pos = this.$el.getBoundingClientRect()
        this.line.x2 = ev.clientX - pos.x
        this.line.y2 = ev.clientY - pos.y
      }
    },
    // 绘画path路径
    drawLink (id, from, to) {
      const { close } = from
      from = this._operators.find(o => o.id === from.id)
      to = this._operators.find(o => o.id === to)
      if (from && to) {
        this.$nextTick(_ => {
          var opo = this.$refs['op' + from.id]
          opo = opo && opo[0]
          var outs = this.$refs['outs' + from.id]
          outs = outs && outs[0]
          var opi = this.$refs['op' + to.id]
          opi = opi && opi[0]
          var ins = this.$refs['ins' + to.id]
          ins = ins && ins[0]
          if (opo && outs && opi && ins) {
            var inset = 2
            var fromX = 0
            var fromY = 0
            var toX1 = 0
            var toY1 = 0
            var toX2 = 0
            var toY2 = 0
            var toX3 = 0
            var toY3 = 0
            toX1 = fromX = this.horizontal ? from.left + opo.offsetWidth + outs.offsetWidth / 2 - inset : from.left + opo.offsetWidth / 2
            toY1 = fromY = this.horizontal ? from.top + opo.offsetHeight / 2 : from.top + opo.offsetHeight + outs.offsetHeight / 2 - inset
            toX2 = toX3 = this.horizontal ? to.left - outs.offsetWidth / 2 + inset : to.left + opi.offsetWidth / 2
            toY2 = toY3 = this.horizontal ? to.top + opi.offsetHeight / 2 : to.top - ins.offsetHeight / 2 + inset
            const bezierIntensity = Math.min(this.linkBending, Math.max(Math.abs(fromY - toY2), Math.abs(fromX - toX2)))
            const svg = this.$refs.svg
            const path = svg.querySelector('.link' + id)
            // 闭环节点
            if (close) {
              const isLeft = from.left === to.left ? -1 : 0
              toX1 = toX1 + isLeft * (this.linkBending * 2 + (from.left - to.left) / 2)
              toX2 = toX2 + isLeft * (this.linkBending * 2 + (from.left - to.left) / 2)
            }
            if (path) {
              if (this.horizontal) {
                path.setAttribute(
                  'd',
                  'M' + fromX + ',' + fromY + ' C' + (toX1 + bezierIntensity) + ',' + toY1 + ' ' + (toX2 - bezierIntensity) + ',' + toY2 + ' ' + toX3 + ',' + toY3
                )
              } else {
                path.setAttribute(
                  'd',
                  'M' + fromX + ',' + fromY + ' C' + toX1 + ',' + (toY1 + bezierIntensity) + ' ' + toX2 + ',' + (toY2 - bezierIntensity) + ' ' + toX3 + ',' + toY3
                )
              }
            }
          }
        })
      }
    },
    selectLink (linkId) {
      if (this.canUserEditLinks) this.selectedLinkId = linkId
    },
    unselectLink () {
      this.selectedLinkId = -1
    },
    contextLink (linkId, e) {
      if (this.canUserEditLinks) {
        e.preventDefault()
        this.selectedLinkId = linkId
        this.$refs.linkcontextmenu.show({
          top: e.pageY,
          left: e.pageX
        })
        return true
      } else {
        return false
      }
    },
    // 设置path虚实
    isSignal ({ fromOperator, toOperator }, index) {
      if (this.selectedLinkId === index || (fromOperator === this.selectedOperator.id || toOperator === this.selectedOperator.id)) {
        return '0'
      } else {
        return '5'
      }
    },
    // 设置path颜色
    highlightLink ({ fromOperator, toOperator }, index) {
      var color = MAPCOLOR.event
      // 根据不同的数据源类型设置不同颜色标识
      const parent = this.chartOperators[toOperator].properties.data.parent || []
      const child = this.chartOperators[fromOperator].properties.data.children || []
      parent.forEach(v => {
        if (fromOperator === v.id && v.dagDataType) {
          color = MAPCOLOR[v.dagDataType]
        }
      })
      child.forEach(v => {
        if (toOperator === v.id && v.dagDataType) {
          color = MAPCOLOR[v.dagDataType]
        }
      })
      return color
    },
    addLink (parent, child) {
      this.$emit('addLink', parent.properties, child.properties, success => {
        this.docClick()
      })
    },
    delLink (linkId = this.selectedLinkId) {
      const linkData = this.chartLinks[linkId]
      if (linkData) {
        const parent = this.chartOperators[linkData.fromOperator].properties
        const child = this.chartOperators[linkData.toOperator].properties
        this.$emit('delLink', parent, child, success => {
          this.docClick()
        })
      }
    },
    refreshLink () {
      Object.keys(this.chartLinks).forEach(k => {
        const l = this.chartLinks[k]
        this.drawLink(k, { id: l.fromOperator, close: l.closedLoopNode || false }, l.toOperator)
      })
    },
    update () {
      this.$nextTick(_ => {
        this.$emit('updated', {
          operators: this.chartOperators,
          links: this.chartLinks,
          horizontal: this.horizontal
        })
      })
    }
  }
}
</script>

<style lang="stylus" scoped>
@import './color'

@keyframes primary
  0%
    opacity 1

  100%
    opacity 0.7

.flowchart-wrapper
  width 100%
  height 100%
  position relative

  .flowchart-links, .flowchart-links-tmp, .flowchart-ops, svg
    width 100%
    height 100%
    position absolute

  .link
    stroke-width 6
    fill none
    stroke rgb(32, 160, 255)
    transition stroke 0.5s

    &:hover
      stroke rgb(19, 96, 153)

      &.noedit
        stroke rgb(32, 160, 255)

    &.source
      stroke #67C23A

    &.selected
      stroke rgb(50, 64, 87)

    &.dash
      stroke-dasharray 6, 6
      stroke-width 4
      stroke rgb(85, 85, 85)

  .flowchart-links-tmp, .flowchart-ops
    pointer-events none

  .flowchart-operator
    position absolute
    pointer-events initial
    text-align center
    font-family PingFang-SC-Regular, Helvetica Neue, Helvetica, microsoft yahei, sans-serif
    transition opacity 0.5s

    .flowchart-operator-subtitle
      display none

    .flowchart-operator-title, .operator-source
      position relative
      width 100%
      height 50px
      box-sizing border-box
      border 2px solid #CCCCCC
      border-radius 5px
      background #F0F0F0
      padding 5px 10px
      font-size 14px
      display flex
      flex-direction column
      justify-content center
      align-items center
      transition all 0.5s
      cursor pointer
      user-select none
      white-space nowrap

      &.nomove
        cursor default

      &.virtual-node
        border 2px dashed #CCCCCC

    .operator-source
      width 160px
      text-overflow ellipsis
      white-space nowrap
      border-color transparent
      border none
      background transparent
      padding 0

    //background rgb(237, 248, 230)

    &.subtitle
      .flowchart-operator-title
        display block
        padding 0px 10px
        height 50px
        line-height 60px
        position relative

      .flowchart-operator-subtitle
        display inline-block
        position absolute
        top 6px
        left 0
        width 100%
        height 12px
        line-height 12px
        font-size 12px
        color #475669
        text-align center
        overflow hidden
        text-overflow ellipsis

    &.fixed
      .flowchart-operator-title
        width 160px
        text-overflow ellipsis
        white-space nowrap

        overflow hidden
          div
            width 100%
            overflow hidden
            text-overflow ellipsis
            white-space nowrap

    &.selected
      .flowchart-operator-title
        border-color #555

    &.primary
      animation primary 0.5s linear infinite alternate

      .flowchart-operator-title
        background rgba(32, 160, 255, 1)
        color #fff

    &.success .flowchart-operator-title
      background rgba(19, 206, 102, 1)
      color #fff

    &.danger .flowchart-operator-title
      background rgba(255, 73, 73, 1)
      color #fff

    &.primary .flowchart-operator-title, &.normal .flowchart-operator-title
      background rgba(32, 160, 255, 1)
      color #fff

    &.warning .flowchart-operator-title
      background rgba(247, 186, 42, 1)
      color #fff

    &.has-warning-job .flowchart-operator-title
      background rgba(247, 129, 4, 1)
      color #fff

    &.disabled .flowchart-operator-title
      background #F5F5F5
      color #DFDFDF

    &.primary .flowchart-operator-subtitle, &.normal .flowchart-operator-title, &.success .flowchart-operator-subtitle, &.danger .flowchart-operator-subtitle, &.warning .flowchart-operator-subtitle
      color #F9FAFC

    &.disabled .flowchart-operator-subtitle
      color #DFDFDF

    .flowchart-operator-inputs-outputs
      width 100%

    .flowchart-operator-inputs, .flowchart-operator-outputs
      width 100%
      height 0
      display flex
      justify-content center

      .flowchart-operator-connector-arrow
        width 0px
        height 0px
        border 15px solid rgb(204, 204, 204)
        border-radius 4px
        position absolute
        left 50%
        cursor pointer

        &.noedit
          cursor default

      .flowchart-operator-connector:hover
        .flowchart-operator-connector-arrow
          border-color rgb(153, 153, 153)

          &.noedit
            border-color rgb(204, 204, 204)

    .flowchart-operator-inputs
      .flowchart-operator-connector-arrow
        top 3px
        transform translate(-50%, -50%) rotate(45deg)

    .flowchart-operator-outputs
      .flowchart-operator-connector-arrow
        bottom 3px
        transform translate(-50%, 50%) rotate(45deg)

    &.horizontal
      .flowchart-operator-inputs
        .flowchart-operator-connector-arrow
          top 50%
          left 3px

      .flowchart-operator-outputs
        .flowchart-operator-connector-arrow
          bottom 50%
          left auto
          right 3px
          transform translate(50%, 50%) rotate(45deg)
</style>
