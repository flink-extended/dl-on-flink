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
    Workflow defines the execution logic of a set of jobs(ai_flow.workflow.job.Job).
    Workflow is made up of jobs and edges(ai_flow.workflow.control_edge.ControlEdge)
    between jobs(ai_flow.workflow.job.Job).
    """

    def __init__(self) -> None:
        super().__init__()
        self.workflow_config: WorkflowConfig = None
        self.workflow_snapshot_id: Text = None
        self.project_uri = None

    @property
    def workflow_name(self):
        return self.workflow_config.workflow_name

    @property
    def jobs(self) -> Dict[Text, Job]:
        return self.nodes

    @property
    def control_edges(self) -> Dict[Text, List[ControlEdge]]:
        return self.edges

    def add_job(self, job: Job):
        self.nodes[job.job_config.job_name] = job

    def add_edges(self, job_name: Text, dependencies: List[ControlEdge]):
        if job_name not in self.edges:
            self.edges[job_name] = []
        self.edges[job_name].extend(dependencies)

    def add_edge(self, job_name: Text, edge: ControlEdge):
        if job_name not in self.edges:
            self.edges[job_name] = []
        self.edges[job_name].append(edge)


class WorkflowPropertyKeys(object):
    BLOB = "blob"
    JOB_PLUGINS = "job_plugins"
