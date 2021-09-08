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
import unittest
import os
from ai_flow.util import json_utils
from ai_flow.workflow.job import Job
from ai_flow.workflow.control_edge import ControlEdge, JobSchedulingRule, MeetAnyEventCondition, \
    JobAction
from ai_flow.workflow.workflow import Workflow
from ai_flow.workflow.workflow_config import load_workflow_config


class TestWorkflow(unittest.TestCase):

    def test_workflow_config(self):
        workflow_config_file = os.path.join(os.path.dirname(__file__), 'workflow_1.yaml')
        workflow_config = load_workflow_config(workflow_config_file)
        self.assertEqual("2020,1,1,1,1,1,",
                         workflow_config.periodic_config.trigger_config['start_date'])
        self.assertEqual("1,1,1,1",
                         workflow_config.periodic_config.trigger_config['interval'])
        self.assertEqual(1, len(workflow_config.properties))
        self.assertEqual(1, len(workflow_config.dependencies))
        self.assertEqual(2, len(workflow_config.dependencies['jars']))

        self.assertEqual('workflow_1', workflow_config.workflow_name)
        self.assertEqual('bash', workflow_config.job_configs['task_1'].job_type)
        self.assertEqual(60.0, workflow_config.job_configs['task_1'].job_label_report_interval)
        self.assertEqual("2020,1,1,1,1,1,",
                         workflow_config.job_periodic_config_dict.get('task_2').trigger_config['start_date'])
        self.assertEqual(5.0, workflow_config.job_configs['task_2'].job_label_report_interval)
        self.assertEqual("* * * * * * *",
                         workflow_config.job_periodic_config_dict.get('task_2').trigger_config['cron'])
        self.assertEqual("1,1,1,1",
                         workflow_config.job_periodic_config_dict.get('task_3').trigger_config['interval'])

    def test_workflow_serde(self):
        workflow_config_file = os.path.join(os.path.dirname(__file__), 'workflow_1.yaml')
        workflow_config = load_workflow_config(workflow_config_file)
        workflow = Workflow()
        workflow.workflow_config = workflow_config
        jobs = []
        for job_config in workflow_config.job_configs.values():
            job = Job(job_config=job_config)
            workflow.add_job(job)
            jobs.append(job)
        edge = ControlEdge(destination=jobs[0].job_name,
                           scheduling_rule=JobSchedulingRule(MeetAnyEventCondition().add_event('a', 'a'),
                                                             JobAction.START))
        workflow.add_edge(jobs[0].job_name, edge)
        edge = ControlEdge(destination=jobs[0].job_name,
                           scheduling_rule=JobSchedulingRule(MeetAnyEventCondition().add_event('b', 'b'),
                                                             JobAction.START))
        workflow.add_edge(jobs[0].job_name, edge)
        json_text = json_utils.dumps(workflow)
        w: Workflow = json_utils.loads(json_text)
        self.assertEqual(3, len(w.jobs))
        self.assertEqual(2, len(w.edges.get(jobs[0].job_name)))


if __name__ == '__main__':
    unittest.main()
