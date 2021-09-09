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
  <page-header-wrapper>
    <a-card :bordered="false">
      <div class="table-page-search-wrapper">
        <a-form layout="inline">
          <a-row :gutter="48">
            <a-col :md="8" :sm="24">
              <a-form-item label="Project Name">
                <a-input v-model="queryParam.project_name" placeholder=""/>
              </a-form-item>
            </a-col>
            <a-col :md="8" :sm="24">
              <a-form-item label="Workflow Name">
                <a-input v-model="queryParam.workflow_name" placeholder=""/>
              </a-form-item>
            </a-col>
            <a-col :md="!advanced && 8 || 24" :sm="24">
              <span class="table-page-search-submitButtons" :style="advanced && { float: 'right', overflow: 'hidden' } || {} ">
                <a-button type="primary" @click="$refs.table.refresh(true)">Query</a-button>
                <a-button style="margin-left: 8px" @click="() => this.queryParam = {}">Reset</a-button>
              </span>
            </a-col>
          </a-row>
        </a-form>
      </div>
      <s-table
        ref="table"
        size="default"
        rowKey="key"
        :columns="columns"
        :data="loadData"
        showPagination="auto"
      >
        <span slot="_properties" slot-scope="text">
          <ellipsis :length="32" tooltip>{{ text }}</ellipsis>
        </span>
        <span slot="_context" slot-scope="text">
          <ellipsis :length="32" tooltip>{{ text }}</ellipsis>
        </span>
      </s-table>
    </a-card>
  </page-header-wrapper>
</template>

<script>
import moment from 'moment'
import { STable, Ellipsis } from '@/components'
import { getWorkflowExecutions, getRoleList } from '@/api/manage'

function formateDate (date, fmt) {
  if (/(Y+)/.test(fmt)) {
    fmt = fmt.replace(RegExp.$1, date.getFullYear() + '')
  }
  const o = {
    'M+': date.getMonth() + 1,
    'd+': date.getDate(),
    'h+': date.getHours(),
    'm+': date.getMinutes(),
    's+': date.getSeconds()
  }
  for (const k in o) {
    if (new RegExp(`(${k})`).test(fmt)) {
      const str = o[k] + ''
      fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1) ? str : padLeftZero(str))
    }
  }
  return fmt
}

function padLeftZero (str) {
  return ('00' + str).substr(str.length)
}

const columns = [
  {
    title: 'Workflow Execution ID',
    dataIndex: '_workflow_execution_id',
    sorter: true
  },
  {
    title: 'Status',
    dataIndex: '_status'
  },
  {
    title: 'Properties',
    dataIndex: '_properties',
    scopedSlots: { customRender: '_properties' }
  },
  {
    title: 'Context',
    dataIndex: '_context',
    scopedSlots: { customRender: '_context' }
  },
  {
    title: 'Start Date',
    dataIndex: '_start_date',
    sorter: true,
    customRender: (t) => formateDate(new Date(parseInt(t)), 'YYYY-MM-dd hh:mm')
  },
  {
    title: 'End Date',
    dataIndex: '_end_date',
    sorter: true,
    customRender: (t) => formateDate(new Date(parseInt(t)), 'YYYY-MM-dd hh:mm')
  }
]

export default {
  name: 'WorkflowExecution',
  components: {
    STable,
    Ellipsis
  },
  data () {
    this.columns = columns
    return {
      confirmLoading: false,
      advanced: false,
      queryParam: {},
      loadData: parameter => {
        const requestParameters = Object.assign({}, parameter, this.queryParam)
        console.log('loadData request parameters:', requestParameters)
        return getWorkflowExecutions(requestParameters)
          .then(res => {
            console.log(res)
            return res
          })
      }
    }
  },
  created () {
    getRoleList({ t: new Date() })
  },
  methods: {
    resetSearchForm () {
      this.queryParam = {
        date: moment(new Date())
      }
    }
  }
}
</script>
