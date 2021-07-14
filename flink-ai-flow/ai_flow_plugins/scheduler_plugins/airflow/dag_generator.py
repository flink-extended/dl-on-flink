#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
from typing import Text, List, Dict
from ai_flow.workflow.job import Job
from ai_flow.util import json_utils
from ai_flow.workflow.control_edge import ConditionConfig, AIFlowInternalEventType, TaskAction
from ai_flow.workflow.periodic_config import PeriodicConfig
from ai_flow.workflow.workflow import Workflow, WorkflowPropertyKeys
from airflow.events.scheduler_events import SchedulerInnerEventType

def import_job_plugins_text(workflow: Workflow):
    text = ''
    plugins: Dict = workflow.properties.get(WorkflowPropertyKeys.JOB_PLUGINS)
    for module, name in plugins.values():
        text += 'from {} import {}\n'.format(module, name)
    return text


class DAGTemplate(object):
    AIRFLOW_IMPORT = """
from datetime import datetime, timedelta
from pytz import timezone
from airflow.models.dag import DAG
from ai_flow_plugins.scheduler_plugins.airflow.event_handler import AIFlowHandler
from ai_flow_plugins.scheduler_plugins.airflow.ai_flow_operator import AIFlowOperator
from ai_flow.util import json_utils

"""
    LOAD_CONFIG = """
workflow_json = '{}'
workflow = json_utils.loads(workflow_json)
"""
    DATETIME = """datetime(year={0},month={1},day={2},hour={3},minute={4},second={5})"""
    DATETIME_WITH_TZ = """datetime(year={0},month={1},day={2},hour={3},minute={4},second={5},tzinfo=timezone('{6}'))"""
    DELTA_TIME = """timedelta(days={0}, hours={1}, minutes={2}, seconds={3})"""

    DEFAULT_ARGS = """default_args = {0}\n"""
    DEFAULT_ARGS_VALUE = {'schedule_interval': 'None', 'start_date': 'datetime.utcnow()'}

    DAG_DEFINE = """dag = DAG(dag_id='{0}', default_args=default_args)\n"""

    PERIODIC_CONFIG = """{0}.executor_config = {{'periodic_config': {1}}}\n"""

    UPSTREAM_OP = """{0}.set_upstream({1})\n"""

    EVENT_DEPS = """{0}.subscribe_event('{1}', '{2}', '{3}', '{4}')\n"""

    MET_HANDLER = """configs_{0}='{1}'
{0}.set_events_handler(AIFlowHandler(configs_{0}))\n"""


class DAGGenerator(object):
    """
    DAGGenerator generates an airflow dag file based on workflow.
    """
    def __init__(self):
        self.op_count = -1

    def generate_op_code(self, job):
        self.op_count += 1
        OP_DEFINE = """
job_json_{0} = '{1}'
job_{0} = json_utils.loads(job_json_{0})
op_{0} = AIFlowOperator(task_id='{2}', job=job_{0}, workflow=workflow, dag=dag)
"""
        return 'op_{}'.format(self.op_count), OP_DEFINE.format(self.op_count,
                                                               json_utils.dumps(job),
                                                               job.job_name)

    def generate_upstream(self, op_1, op_2):
        return DAGTemplate.UPSTREAM_OP.format(op_1, op_2)

    def generate_event_deps(self, op, from_task_id, met_config):
        if met_config.sender is not None and '' != met_config.sender:
            sender = met_config.sender
        else:
            sender = from_task_id
        return DAGTemplate.EVENT_DEPS.format(op, met_config.event_key, met_config.event_type,
                                             met_config.namespace, sender)

    def generate_handler(self, op, configs: List[ConditionConfig]):
        return DAGTemplate.MET_HANDLER.format(op, json_utils.dumps(configs))

    def generate(self,
                 workflow: Workflow,
                 project_name: Text) -> Text:
        code_text = DAGTemplate.AIRFLOW_IMPORT
        code_text += import_job_plugins_text(workflow)
        code_text += DAGTemplate.LOAD_CONFIG.format(json_utils.dumps(workflow))

        def dict_code_text(data: Dict)-> Text:
            code_t = "{\n"
            for k, v in data.items():
                code_t += """   '{}': {},\n""".format(k, v)
            code_t = code_t[:-2]
            code_t += "\n}"
            return code_t

        if workflow.workflow_config.periodic_config is None:
            exec_args = DAGTemplate.DEFAULT_ARGS_VALUE
        else:
            exec_args = {}
            periodic_config: PeriodicConfig = workflow.workflow_config.periodic_config
            self.set_periodic_config(exec_args, periodic_config)
        self.op_count = -1

        code_text += DAGTemplate.DEFAULT_ARGS.format(dict_code_text(exec_args))

        dag_id = '{}.{}'.format(project_name, workflow.workflow_name)
        code_text += DAGTemplate.DAG_DEFINE.format(dag_id)

        task_map = {}
        for name, job in workflow.jobs.items():
            op_name, code = self.generate_op_code(job)
            code_text += code
            task_map[job.job_name] = op_name
            if name in workflow.workflow_config.job_periodic_config_dict:
                periodic_config: PeriodicConfig = workflow.workflow_config.job_periodic_config_dict.get(name)
                if periodic_config.trigger_config.get('cron') is not None:
                    code_text += \
                        DAGTemplate.PERIODIC_CONFIG.format(op_name,
                                                           str({'cron': periodic_config.trigger_config.get(
                                                               'cron')}))
                elif periodic_config.trigger_config.get('interval') is not None:
                    code_text += DAGTemplate. \
                        PERIODIC_CONFIG.format(op_name,
                                               str({'interval': ','.join(
                                                   ['0', periodic_config.trigger_config.get('interval')])}))
                else:
                    raise Exception('periodic_config must set one of interval config or cron config!')

        for job_name, edges in workflow.control_edges.items():
            if job_name in task_map:
                op_name = task_map[job_name]
                configs = []
                for edge in edges:
                    condition_config: ConditionConfig = edge.condition_config
                    if AIFlowInternalEventType.JOB_STATUS_CHANGED == condition_config.event_type:
                        condition_config.event_type = SchedulerInnerEventType.TASK_STATUS_CHANGED.value

                    def reset_met_config():
                        if condition_config.sender is None or '' == condition_config.sender:
                            target_node_id = edge.source
                            if target_node_id is not None and '' != target_node_id:
                                target_job: Job = workflow.jobs.get(target_node_id)
                                if target_job.job_name is not None:
                                    condition_config.sender = target_job.job_name
                            else:
                                condition_config.sender = '*'
                    reset_met_config()

                    if edge.source in task_map:
                        from_op_name = task_map[edge.source]
                    else:
                        from_op_name = ''
                    code = self.generate_event_deps(op_name, from_op_name, condition_config)
                    code_text += code
                    configs.append(condition_config)

                if len(configs) > 0:
                    code = self.generate_handler(op_name, configs)
                    code_text += code

        return code_text

    def set_periodic_config(self, exec_args, periodic_config):
        if periodic_config.trigger_config.get('start_date') is not None:
            stat_date_items = periodic_config.get_start_date_items()
            if stat_date_items[6] is None:
                exec_args['start_date'] = DAGTemplate.DATETIME.format(stat_date_items[0],
                                                                      stat_date_items[1],
                                                                      stat_date_items[2],
                                                                      stat_date_items[3],
                                                                      stat_date_items[4],
                                                                      stat_date_items[5])
            else:
                exec_args['start_date'] = DAGTemplate.DATETIME_WITH_TZ.format(stat_date_items[0],
                                                                              stat_date_items[1],
                                                                              stat_date_items[2],
                                                                              stat_date_items[3],
                                                                              stat_date_items[4],
                                                                              stat_date_items[5],
                                                                              stat_date_items[6])
        else:
            exec_args['start_date'] = 'datetime.utcnow()'
        if periodic_config.trigger_config.get('cron') is not None:
            cron_items = periodic_config.get_cron_items()
            # airflow cron: minutes hours days months years weeks seconds
            cron_airflow = ' '.join([cron_items[1], cron_items[2], cron_items[4],
                                     cron_items[6], cron_items[5], cron_items[0]])
            exec_args['schedule_interval'] = """'{}'""".format(cron_airflow)
        elif periodic_config.trigger_config.get('interval') is not None:
            items = periodic_config.get_interval_items()
            exec_args['schedule_interval'] = DAGTemplate.DELTA_TIME.format(items[0], items[1], items[2], items[3])
        else:
            pass

