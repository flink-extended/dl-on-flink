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
from ai_flow.workflow.control_edge import ControlEdge, ConditionConfig
from ai_flow.workflow.workflow import Workflow
from ai_flow.workflow.workflow_config import load_workflow_config


class TestWorkflow(unittest.TestCase):

    def test_workflow_config(self):
        workflow_config_file = os.path.join(os.path.dirname(__file__), 'workflow_1.yaml')
        workflow_config = load_workflow_config(workflow_config_file)
        self.assertEqual('workflow_1', workflow_config.workflow_name)
        self.assertEqual('bash', workflow_config.job_configs['task_1'].job_type)

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
                           condition_config=ConditionConfig(sender=jobs[1].job_name, event_key='a', event_value='a'))
        workflow.add_edge(jobs[0].job_name, edge)
        edge = ControlEdge(destination=jobs[0].job_name,
                           condition_config=ConditionConfig(sender=jobs[2].job_name, event_key='b', event_value='b'))
        workflow.add_edge(jobs[0].job_name, edge)
        json_text = json_utils.dumps(workflow)
        w: Workflow = json_utils.loads(json_text)
        self.assertEqual(3, len(w.jobs))
        self.assertEqual(2, len(w.edges.get(jobs[0].job_name)))


if __name__ == '__main__':
    unittest.main()
