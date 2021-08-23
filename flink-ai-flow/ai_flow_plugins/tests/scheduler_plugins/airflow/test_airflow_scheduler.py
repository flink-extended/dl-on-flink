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
import logging
import unittest
import tempfile
import os

import cloudpickle
from ai_flow.api.context_extractor import BroadcastAllContextExtractor

from ai_flow.project.project_config import ProjectConfig

from ai_flow.workflow.workflow_config import WorkflowConfig

from ai_flow.context.project_context import ProjectContext

from ai_flow.workflow.workflow import Workflow
from mock import Mock

from ai_flow_plugins.scheduler_plugins.airflow.airflow_scheduler import AirFlowScheduler


class TestAirflowScheduler(unittest.TestCase):
    logger = logging.getLogger('TestAirflowScheduler')

    def setUp(self) -> None:
        self.temp_deploy_path = tempfile.TemporaryDirectory().name
        self.logger.info("temp airflow deploy path: {}".format(self.temp_deploy_path))
        self.scheduler = AirFlowScheduler({'airflow_deploy_path': self.temp_deploy_path,
                                           'notification_service_uri': 'localhost:50051'})
        self.scheduler._airflow_client = Mock()
        self.scheduler.dag_generator = Mock()

    def test_airflow_scheduler_submit_workflow(self):
        workflow_name = 'test_workflow'
        workflow = self._get_workflow(workflow_name)

        project_name = 'test_project'
        project_context = self._get_project_context(project_name)

        mock_generated_code = 'mock generated code'
        self.scheduler.dag_generator.generate.return_value = mock_generated_code

        context_extractor = BroadcastAllContextExtractor()
        self.scheduler.submit_workflow(workflow, context_extractor=context_extractor,
                                       project_context=project_context)

        dag_file_path = os.path.join(self.temp_deploy_path, '.'.join([project_name, workflow_name, 'py']))
        self.assertTrue(os.path.exists(dag_file_path))
        with open(dag_file_path, 'rt') as f:
            self.assertEqual(mock_generated_code, f.read())

        context_extractor_pickle_path = \
            os.path.join(self.temp_deploy_path, '.'.join([project_name, workflow_name, 'context_extractor', 'pickle']))
        self.assertTrue(os.path.exists(context_extractor_pickle_path))
        with open(context_extractor_pickle_path, 'rb') as f:
            extractor = cloudpickle.load(f)
            self.assertEqual(context_extractor.__class__, extractor.__class__)

    def test_airflow_scheduler_submit_workflow_with_customized_context_extractor(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'context_extractor_pickle_maker.py')
        os.system('python {}'.format(script_path))
        context_extractor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'context_extractor.pickle')

        try:
            workflow_name = 'test_workflow_with_context_extractor'
            workflow = self._get_workflow(workflow_name)
            with open(context_extractor_path, 'rb') as f:
                context_extractor = cloudpickle.load(f)

            project_name = 'test_project'
            project_context = self._get_project_context(project_name)

            mock_generated_code = 'mock generated code'
            self.scheduler.dag_generator.generate.return_value = mock_generated_code

            self.scheduler.submit_workflow(workflow, context_extractor=context_extractor, project_context=project_context)

            dag_file_path = os.path.join(self.temp_deploy_path, '.'.join([project_name, workflow_name, 'py']))
            self.assertTrue(os.path.exists(dag_file_path))
            with open(dag_file_path, 'rt') as f:
                self.assertEqual(mock_generated_code, f.read())

            context_extractor_pickle_path = \
                os.path.join(self.temp_deploy_path, '.'.join([project_name, workflow_name, 'context_extractor', 'pickle']))
            self.assertTrue(os.path.exists(context_extractor_pickle_path))
            with open(context_extractor_pickle_path, 'rb') as f:
                extractor = cloudpickle.load(f)
                self.assertEqual(context_extractor.__class__, extractor.__class__)
        finally:
            os.remove(context_extractor_path)

    @staticmethod
    def _get_project_context(project_name):
        project_context: ProjectContext = ProjectContext()
        project_context.project_config = ProjectConfig()
        project_context.project_config.set_project_name(project_name)
        return project_context

    @staticmethod
    def _get_workflow(workflow_name):
        workflow = Workflow()
        workflow.workflow_config = WorkflowConfig(workflow_name=workflow_name)
        return workflow
