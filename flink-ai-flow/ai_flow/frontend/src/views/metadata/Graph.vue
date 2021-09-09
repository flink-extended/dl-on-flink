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
  <div class="content bsql">
    <div class="baql_content_middle">
      <div class="sql-wrapper-box">
        <relation
          ref="relation"
          @digUp="digUp"
          @toggleDagJobNode="toggleDagJobNode"
          :dagData="dagData"
          :showChooseColor="true"
          :aiflowContentPath="taskProject.aiflowContentPath"
          @operatorContextMenu="operatorContextMenu"></relation>
        <v-contextmenu
          ref="contextmenu"
          class="archer-log-detail-contextmenu"
          @show="contextMenuShow = true"
          @hide="contextMenuShow = false">
          <!-- <v-contextmenu-item
            :disabled="true"
            @click="jumpStream(currentNode)">
            查看
          </v-contextmenu-item>
          <v-contextmenu-item @click="check({  id: currentNode.jobId, jobName: currentNode.name})">
            检查
          </v-contextmenu-item> -->
          <!-- <v-contextmenu-item @click="jumpSaver(currentNode)">
            运维
          </v-contextmenu-item> -->
        </v-contextmenu>
      </div>
    </div>
  </div>
</template>

<script>
import Relation from '@/components/Graph/Relation'
import { getDataView } from '@/api/manage'

export default {
  name: 'Graph',
  components: {
    Relation
  },
  data () {
    return {
      // dagData: [{ id: 2, layer: 1, parent: null, children: [{ id: 1, name: 'shuffle_job_kafka_in', isSignal: 1, dagDataType: 'source', closedLoopNode: false }], nodeType: null, isVirtual: null, name: null, jobTypeName: null, isRealNode: true, jobId: 290, sourceFlag: true, rsuuid: 'd2398a88-7b3e-5060-8cca-2bd6eeedc2cb', dataName: 'kafka_in', sourceType: 'kafka', materialId: null, materialReady: false, materialParentProjectId: null, isShowMaterial: false }, { id: 1, layer: 2, parent: [{ id: 2, name: 'd2398a88-7b3e-5060-8cca-2bd6eeedc2cb', isSignal: 1, dagDataType: 'source', closedLoopNode: false }], children: [{ id: 3, name: 'edc73f5f-4c9f-555a-b14a-5642c20aa252', isSignal: 1, dagDataType: 'sink', closedLoopNode: false }], nodeType: 0, isVirtual: null, name: 'shuffle_job_kafka_in', jobTypeName: 'saber', isRealNode: true, jobId: 290, sourceFlag: false, rsuuid: null, dataName: null, sourceType: null, materialId: null, materialReady: false, materialParentProjectId: null, isShowMaterial: false }, { id: 3, layer: 3, parent: [{ id: 1, name: 'shuffle_job_kafka_in', isSignal: 1, dagDataType: 'sink', closedLoopNode: false }], children: null, nodeType: null, isVirtual: null, name: null, jobTypeName: null, isRealNode: true, jobId: 290, sourceFlag: true, rsuuid: 'edc73f5f-4c9f-555a-b14a-5642c20aa252', dataName: 'kafka_out_shuffle', sourceType: 'kafka', materialId: null, materialReady: false, materialParentProjectId: null, isShowMaterial: false }],
      dagData: [],
      taskProject: {}
    }
  },
  mounted () {
    this.getDagData()
    this.getTaskDetail()
  },
  destroyed () {
    this.clearConsoleTabs()
  },
  computed: {
    sql () {
      return (this.taskProject || {}).aiflowContent || ''
    },
    codeStatus () {
      // 0未执行 1成功 2失败 3运行中 4等待执行 5停止 6固化
      return this.sqlStatus === 0 ? 0 : this.sqlStatus || -1
    },
    isEmpty () {
      return !(this.sql && this.sql.trim())
    },
    isWaiting () {
      return this.codeStatus === 4 || this.codeStatus === 6
    },
    isLoading () {
      return this.codeStatus === 0 || this.codeStatus === 3 || this.isWaiting
    },
    activeBsqlLog () {
      return this.$refs[this.taskProject.jobId] && this.$refs[this.taskProject.jobId][0]
    },
    checkedMaterial () {
      return this.taskProject.dagData.filter(v => v.isShowMaterial === true)
    }
  },
  watch: {
    dagData (dag) {
      this.$nextTick(() => {
        this.$refs.relation && this.$refs.relation.initFlowchart()
      })
    }
  },
  methods: {
    getDagData () {
      const parameters = location.href.split('#')[0].split('/')
      const requestParameters = { 'project_id': parameters[parameters.length - 2], 'workflow_name': parameters[parameters.length - 1] }
      console.log('loadData request parameters:', requestParameters)
      getDataView(requestParameters)
        .then((response) => {
          console.log(response)
          this.dagData = response
        })
        .catch(function (error) {
          console.error(error)
        })
    },
    digUp (item) {
    },
    operatorContextMenu (job, e) {
    },
    getTaskDetail () {
      this.$nextTick(() => {
        this.$refs.relation && this.$refs.relation.initFlowchart()
      })
    },
    // 切换节点和数据源展示
    toggleDagJobNode (node) {
    },
    jumpStream ({ name }) {
    },
    jumpSaver (node) {
    },
    getJobDetail (jobId) {
    },
    getSourceDetail (jobId, rsuuid, nodeType) {
    },
    getJobVersions () {
    },
    getJobVersionDetail (row) {
    },
    setTaskDag () {
    },
    // 验证task
    checkTask () {
    },
    nodeSaved (params) {
    },
    check ({ jobName, id }) {
    },
    sourceSaved (params) {
    }
  }
}
</script>

<style lang="stylus" scoped>
@import '../../components/Graph/color'

.content.bsql
  padding 10px
  box-sizing border-box
  height 100%
  width: calc(100% - 32px)
  >>> .CodeMirror-vscrollbar
    z-index 2 !important
  .form-label
    color $colorExtraLightBlack
    margin-left 10px
    font-size 14px
    em
      color $colorRed
  .sql-header
    height 50px
    padding 10px
    box-sizing border-box
    .outline-sql
      color #475669;
      margin-right 10px;
      font-size 13px;
      border 1px solid #C0C4CC;
      padding 5px;
      border-radius 5px;
  .baql_content_middle
    height calc(100% - 50px)
    flex 1
    display flex
    flex-direction column
    overflow hidden
    .sql-wrapper-box
      flex 1
      overflow hidden
  .sql-wrapper
    height 100%
    box-sizing border-box
    padding 0 10px 10px 10px
    .sql-editor
      height 100%
      border 1px solid #d1dbe5
      >>>.CodeMirror
        height 100%
        font-size inherit
  .right-sidebox
    position absolute
    top 0
    right 0
    width 30px
    height 100%
    background #EFF2F7
    border-left 1px solid #d3dce6
    z-index 10
    >ul
      width 30px
      font-size 15px
      font-weight bold
      letter-spacing 1px
      color #475669
      height 100%
      overflow auto

      li
        width calc(100%)
        transform translateX(-1px)
        padding 20px 5px
        box-sizing border-box
        display flex
        justify-content center
        align-items center
        text-align center
        cursor pointer
        user-select none
        border-left 1px solid #d3dce6
        border-bottom 1px solid #d3dce6

        &:hover
          background #fff
        &.open
          background #fff
          border-left-color #fff
          color #20A0FF
    .sidebox-container
      position absolute
      width 400px
      background #fff
      height 100%
      padding 20px 15px
      overflow-x auto
      overflow-y auto
      box-sizing border-box
      right 32px
      top 0
      border-left 1px solid #d3dce6
      box-shadow -2px 0px 4px rgba(0,0,0,0.12)
      z-index 7
</style>
