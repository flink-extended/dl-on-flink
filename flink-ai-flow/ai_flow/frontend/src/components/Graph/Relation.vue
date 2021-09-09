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
  <div class="slideBox">
    <div class="relation-ship">
      <div class="content table">
        <div class="control-line" v-if="showNodeType">
          <div class="line-operate">
            <div class="tooltip" v-if="canChoose">
              <i class="el-icon-warning"></i>
              <span>虚拟节点不会参与实际调度，请设置本项目的实体节点</span>
            </div>
            <div class="icons">
              <i @click="zoomIn" @dblclick.stop.prevent>
                <i class="el-icon-zoom-in" name="search-minus"></i>
              </i>
              <i @click="zoomOut" @dblclick.stop.prevent>
                <i class="el-icon-zoom-out" name="search-minus"></i>
              </i>
              <i @click="returnOrigin" style="font-size: 12px;" @dblclick.stop.prevent>Restore State</i>
              <i
                @click="toggleDagJobNode('dag')"
                style="font-size: 12px;"
                :class="{ active: activeDag === 'dag' }"
                @dblclick.stop.prevent>Data View</i>
              <i
                @click="redictDagGraphView('dagJobNode')"
                style="font-size: 12px;"
                :class="{ active: activeDag === 'dagJobNode' }"
                @dblclick.stop.prevent>Task View</i>
            </div>
            <div class="node-color">
              <div v-for="(value, key) in MAPCOLOR" :key="value" class="color-item">
                <span class="border" :style="{ 'border-top': `8px solid ${value}` }"></span>
                <span class="txt" v-text="key === 'default' ? 'event' : key"></span>
              </div>
            </div>
          </div>
        </div>
        <el-row class="body" ef="body" type="flex" justify="space-between">
          <div ref="canvas" class="canvas">
            <flowchart
              ref="flowchart"
              selectable
              id="flowchart"
              fixedWidth
              :linkWidth="3"
              :linkBending="75"
              :grid="0"
              @operatorClick="operatorClick"
              @operatorContextMenu="operatorContextMenu"
              :canUserEditLinks="false"
              :canUserMoveOperators="false"
              :operators="operators">
              <!--     数据源节点       -->
              <template slot-scope="scope" slot="source">
                <div class="source-item">
                  <div
                    class="item-content"
                    :class="{'selected-op': showChooseColor && isSelectNode(scope.data, 'rsuuid'), 'virtual-node': !scope.data.isRealNode && !isSelectNode(scope.data, 'rsuuid') && isShowBorder }">
                    <div v-text="scope.data.dataName" class="source" :title="scope.data.dataName"></div>
                    <p v-text="scope.data.sourceType"></p>
                  </div>
                  <div
                    class="flowchart-dig-up"
                    @click.stop="digUp(scope.data)"
                    v-if="scope.data.materialParentProjectId"
                    v-text="scope.data.isShowMaterial ? '-' : '+'">
                  </div>
                </div>
              </template>
              <!--     计算节点       -->
              <template slot-scope="scope" slot="node">
                <div
                  class="flowchart-op"
                  :class="{'selected-op': showChooseColor && isSelectNode(scope.data, 'id')}">
                  <p
                    style="user-select: all; display: inline-block; width: 100%; overflow: hidden;text-overflow: ellipsis; height: 20px; line-height: 20px; margin-top: 20px;">
                    <span :title="scope.data.title">{{ scope.data.title }}</span>
                    <template v-if="showNodeType">
                      <template v-if="canChoose">
                        <el-checkbox
                          v-model="scope.data.data.isRealNode"
                          @change="nodeTypeChange($event, scope.data.data)">
                          {{ scope.data.data.isRealNode ? '实体' : '虚拟' }}
                        </el-checkbox>
                      </template>
                    </template>
                  </p>
                  <div class="flowchart-operator-subtitle" :title="scope.data.subtitle">
                    <span>{{ scope.data.subtitle }}</span>
                  </div>
                </div>
              </template>
            </flowchart>
          </div>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script>
import cloneDeep from 'lodash/cloneDeep'
import panzoom from 'panzoom'
import flowchart from '@/components/Graph/FlowChart'
import { getTaskView } from '@/api/manage'

const MAPCOLOR = {
  source: 'rgb(230, 217, 76)',
  sink: 'rgb(101, 159, 252)',
  event: 'rgb(136, 193, 73)'
}

export default {
  components: {
    flowchart
  },
  props: {
    dagData: {
      type: Array,
      // eslint-disable-next-line vue/require-valid-default-prop
      default: []
    },
    // 是否显示虚实边框
    isShowBorder: {
      type: Boolean,
      default: true
    },
    canChoose: {
      type: Boolean,
      default: false
    },
    showNodeType: {
      type: Boolean,
      default: true
    },
    showChooseColor: {
      type: Boolean,
      default: false
    },
    aiflowContentPath: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      name: 'Dag',
      MAPCOLOR,
      flowchart: null,
      self: {},
      preTasks: [],
      preTables: [],
      node: {
        id: 0,
        layer: 0,
        parents: []
      },
      nodeTemplate: {},
      items: [],
      operators: [],
      width: 0,
      height: 0,
      opWidth: 160,
      opHeight: 50,
      zoomer: null,
      minLayer: 0,
      maxLayer: 0,
      jobContent: {},
      nodeChecked: false,
      activeDag: 'dag'
    }
  },

  computed: {
    center () {
      return {
        x: this.width / 2,
        y: this.height / 3,
        clientX: window.innerWidth - this.$el.offsetWidth / 2,
        clientY: window.innerHeight - (this.$el.offsetHeight - 120) / 2
      }
    },
    itemsPosed () {
      const result = this.items.map(m => {
        const siblings = this.items.filter(i => i.layer === m.layer)
        const index = siblings.findIndex(s => s.id === m.id)
        const mid = Math.max(0, (siblings.length - 1) / 2)
        // if (m.layer < this.minLayer) {
        //   this.minLayer = m.layer
        // }
        // if (m.layer > this.maxLayer) {
        //   this.maxLayer = m.layer
        // }
        return {
          ...m,
          top: this.center.y - 120 * m.layer - this.opHeight / 2,
          left: this.center.x - 200 * (mid - index) - this.opWidth / 2
        }
      })
      return result
    },
    _operators () {
      const result = this.itemsPosed.map((i, index) => {
        return {
          id: i.id,
          title: i.jobTypeName,
          isRealNode: i.isRealNode || false,
          dataName: i.dataName || '',
          sourceType: i.sourceType || '',
          sourceFlag: i.sourceFlag || false, // 是否是数据源节点
          subtitle: i.name,
          materialParentProjectId: i.materialParentProjectId,
          parents: i.parent || [],
          signals: i.parent || [],
          isShowMaterial: i.isShowMaterial || false,
          class: i.state ? ((this.projectStatus.find(v => v.value === i.state) || {}).class || ' has-warning-job') : 'flowchart-task',
          left: i.left || this.center.x - this.opWidth / 2,
          top: i.top || this.center.y - this.opHeight / 2,
          data: {
            ...i
          },
          ins: true,
          outs: true
        }
      })
      return result
    }
  },
  created () {
    this.nodeTemplate = {
      ...this.node
    }
  },
  mounted () {
    window.addEventListener('resize', this.setZoom)
    // this.initFlowchart()
  },
  watch: {
    _operators (arr) {
      console.log(arr)
      this.operators = cloneDeep(arr)
    }
  },
  beforeDestroy () {
    window.removeEventListener('resize', this.setZoom)
  },
  methods: {
    digUp (item) {
      this.$emit('digUp', item)
    },
    returnOrigin () {
      this.setZoom()
    },
    toggleDagJobNode (node) {
      this.activeDag = node
      this.$emit('toggleDagJobNode', node)
    },
    redictDagGraphView (node) {
      this.activeDag = node
      const parameters = location.href.split('#')[0].split('/')
      const requestParameters = { 'project_id': parameters[parameters.length - 2], 'workflow_name': parameters[parameters.length - 1] }
      console.log('loadData request parameters:', requestParameters)
      getTaskView(requestParameters)
        .then((response) => {
          console.log(response)
          window.location.href = response
        })
        .catch(function (error) {
          console.error(error)
        })
    },
    nodeTypeChange (val, data) {
      const nodeObj = this.items.find(p => p.id === data.id) || {}
      this.$set(nodeObj, 'isRealNode', val)
      // 设置相关节点，规则：
      // 当计算节点设置为实节点后，子依赖的所有节点均设置为实节点
      // 当计算节点设置为虚节点后，父依赖的所有节点均设置为虚节点
      const nodeList = this.getRelationNode(data, val ? 'children' : 'parent')
      nodeList.forEach(v => {
        const index = this.items.findIndex(p => p.id === v)
        this.$set(this.items[index], 'isRealNode', val)
      })
      this.$nextTick(() => {
        this.$emit('getNodeType', this.items)
      })
    },
    /**
     * @description 查找相关节点
     * @param data 当前节点
     * @param key 节点关系属性（children | parent）
     * */
    getRelationNode (data, key) {
      const nodeList = []
      if (data[key] && data[key].length) {
        data[key].forEach(v => {
          nodeList.push(v.id)
          const node = this.items.find(p => p.id === v.id) || {}
          nodeList.push(...this.getRelationNode(node, key))
        })
      }
      return nodeList
    },
    initFlowchart () {
      this.orginData()
      this.setZoom()
    },
    isSelectNode (row, key) {
      return this.jobContent[key] === row.data[key]
    },
    operatorContextMenu (job, e) {
      this.$emit('operatorContextMenu', job, e)
    },
    operatorClick (job) {
      const jobId = job.jobId
      if (jobId && this.showChooseColor) {
        this.jobContent = job
      }
      this.$emit('jobInfoInit', job)
    },
    orginData () {
      this.items = this.dagData.map((p, index) => {
        return {
          ...this.nodeTemplate,
          ...p,
          layer: -(p.layer - 1) || 0
        }
      })
    },
    zoomIn () {
      if (this.zoomer) {
        this.zoomer.zoomTo(this.center.clientX, this.center.clientY, 1.2)
      }
    },
    zoomOut () {
      if (this.zoomer) {
        this.zoomer.zoomTo(this.center.clientX, this.center.clientY, 0.8)
      }
    },
    addClassName (preClass = '', newClass) {
      return preClass ? preClass + ' ' + newClass : newClass
    },
    setZoom (s) {
      this.$nextTick(_ => {
        const canvas = this.$refs.canvas
        const flowchart = this.$refs.flowchart.$el
        this.width = flowchart.offsetWidth || 10000
        this.height = flowchart.offsetHeight || 10000
        this.zoomer = panzoom(canvas, {
          maxZoom: 2,
          minZoom: 0.5,
          smoothScroll: false,
          enableTextSelection: true,
          beforeWheel: () => {
            return true
          }
        })
        this.zoomer.zoomAbs(this.center.x, this.center.y, isNaN(s) ? 1 : s || 1)
      })
    }
  }
}
</script>
<style lang="stylus" scoped>
@import './color'

.slideBox
  padding 0px 20px 0

.relation-ship
  // padding 20px 0
.content
  .body
    height 700px
    position relative
    overflow hidden
    background #fff
    outline 0

  .control-line
    .line-operate
      display flex
      justify-content space-around

      .tooltip
        flex 1
        font-size 14px
        color $colorExtraLightSilver
        cursor pointer
        z-index 10

        i
          margin-right 5px

      .icons
        // padding 10px
        text-align center
        flex 1
        z-index 10

        i
          color $colorSilver
          cursor pointer
          margin 0 5px
          vertical-align middle

          &:hover
            color $colorBlue

          &.active
            color $colorBlue

      .node-color
        flex 1
        display flex

        .color-item
          margin-left 14px

          .border
            display inline-block
            width 30px
            border-radius 4px

          .txt
            display inline-block
            min-width 26px
            color $colorSilver
            font-size 12px

  .node-type
    display inline-block
    margin-left 15px
    color grey

  .node-blue
    color #01a0e4

  .canvas
    width 100%
    height 100%
    background white
    z-index 1
    cursor move
    // transform-origin -650px -240px !important

    .source-item
      width 100%
      height 50px
      background transparent
      cursor pointer

      .flowchart-dig-up
        position absolute
        top -50%
        left 50%
        width 26px
        height 26px
        text-align center
        font-size 20px
        line-height 18px
        background-color #f5f5f5
        color #ddd
        border 2px solid #f5f5f5
        cursor auto
        box-sizing border-box
        border-radius 50px
        transform translate(-50%, -10%)
        border 2px solid #ccc
        cursor pointer

        &.abled
          color $colorExtraLightSilver
          border 2px solid #ccc
          background white
          cursor pointer

          &:hover
            color $colorLightGray
            background $colorExtraLightSilver

      .item-content
        position relative
        box-sizing border-box
        width: 160px
        left 0
        height: 50px
        font-size 12px
        background: rgb(218, 241, 207)
        border 2px solid rgb(218, 241, 207)
        border-radius: 50% / 50%

        &.selected-op
          background-color $colorYellow
          border 2px solid $colorYellow

        &.virtual-node
          border 2px dashed #67c23a

        div
          transform translateY(8px)
          color rgb(71, 86, 105)
          overflow hidden

        p
          transform translateY(100%)
          font-size 14px
          color rgb(31, 45, 61)
          overflow hidden

    #flowchart
      width 1000px
      height 1000px
      position absolute
      top 50%
      left 50%
      transform translate(-50%, -50%)

      >>> svg
        overflow visible

      >>> .flowchart-center .flowchart-operator-title
        border-color $colorYellow

      >>> .flowchart-table .flowchart-operator-title
        background-color #fff

      >>> .flowchart-task .flowchart-operator-connector-arrow
        visibility visible

      >>> .flowchart-task
        &.selected
          .flowchart-operator-title
            border-color $colorYellow
            background $colorYellow

        .flowchart-operator-title
          padding 0
          border-color #ccc
          background-color #f0f0f0

          .flowchart-op
            cursor pointer
            width 100%
            height 100%

          .selected-op
            background-color $colorYellow

      .flowchart-dig-down
        top auto
        bottom -28px

      svg
        width auto
        height auto
        color inherit
        position absolute
        right 5px
        top 10px

  >>> .flowchart-wrapper
    .flowchart-operator
      .flowchart-operator-connector-arrow
        visibility hidden

  // .flowchart-operator-title
  //   background $colorWhite
  //   overflow visible
  //   padding 5px 20px

  .edit-div
    position absolute
    top 20px
    right 20px

  >>> .el-icon-star, >>> .recommend-icon
    display inline-block
    width 30px
    height 36px
    line-height 36px
    color #F7BA2A
    cursor pointer
    font-size 18px
    text-align center

  >>> .recommend-icon
    color #80A4EC
    cursor unset

    .fa-icon
      vertical-align text-bottom

  >>> .recommend-text
    color #80A4EC

  >>> .header-form
    color #8492A6

    .el-form-item
      margin-bottom 8px

      span
        word-break break-word

    .header-form-label
      font-size 18px

  >>> .relation-sql
    .relation-sql-title
      width 100%
      display inline-block
      font-size 16px
      color #1F2D3D
      padding 10px 0px 10px 12px
      border-width 1px 0px
      border-color #DFE4ED
      border-style solid
      box-sizing border-box

  >>> .el-tabs__content
    overflow auto
    box-sizing border-box

  >>> .CodeMirror
    height calc(100% - 38px)

  >>> .self
    .flowchart-operator-title
      background-color #E6FEFF

  >>> .table
    .flowchart-operator-title
      background-color #FDF99E

  >>> .task
    .flowchart-operator-title
      background-color #ffffff

  >>> .task.selected
    .flowchart-operator-title
      border-color #999898

  >>> .self.selected
    .flowchart-operator-title
      border-color #CCCCCC

  >>> .table.selected
    .flowchart-operator-title
      border-color #CCCCCC

  h2
    font-size 20px
    text-align center
    margin 10px 0 30px
    color #68738b
    font-weight bold

</style>
