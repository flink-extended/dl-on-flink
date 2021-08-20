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
from typing import List, Dict, Text

from ai_flow.workflow.workflow_config import WorkflowConfig
from ai_flow.workflow.control_edge import ControlEdge
from ai_flow.workflow.job import Job
from ai_flow.graph.graph import Graph


class Workflow(Graph):
    """
    Workflow defines the execution logic of a set of jobs(ai_flow.workflow.job.Job)
    Workflow is composed of jobs(ai_flow.workflow.job.Job) and control edges(ai_flow.workflow.control_edge.ControlEdge).
    """

    def __init__(self) -> None:
        super().__init__()
        # The workflow_config is the configuration information of the workflow.
        self.workflow_config: WorkflowConfig = None
        # The unique id generated every time a workflow is generated.
        self.workflow_snapshot_id: Text = None
        # The project package uri is used to download the project package.
        self.project_uri = None


    @property
    def workflow_name(self):
        """Return the name of workflow."""
        return self.workflow_config.workflow_name

    @property
    def jobs(self) -> Dict[Text, Job]:
        """Return the jobs in the workflow."""
        return self.nodes

    @property
    def control_edges(self) -> Dict[Text, List[ControlEdge]]:
        """Return the control edges of the workflow"""
        return self.edges

    def add_job(self, job: Job):
        """Add a job to the workflow."""
        self.nodes[job.job_config.job_name] = job

    def add_edges(self, job_name: Text, edges: List[ControlEdge]):
        """
        Add control edges to workflow.
        :param job_name: The name of the job that depends on edges.
        :param edges: A list of control edges that the job depends on.
        """
        if job_name not in self.edges:
            self.edges[job_name] = []
        self.edges[job_name].extend(edges)

    def add_edge(self, job_name: Text, edge: ControlEdge):
        """
        Add control edges to workflow.
        :param job_name: The name of the job that depends on edges.
        :param edge: A control edge that the job depends on.
        """
        if job_name not in self.edges:
            self.edges[job_name] = []
        self.edges[job_name].append(edge)


class WorkflowPropertyKeys(object):
    BLOB = "blob"
    JOB_PLUGINS = "job_plugins"
