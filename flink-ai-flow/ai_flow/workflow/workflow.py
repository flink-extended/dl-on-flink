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
from ai_flow.graph.node import BaseNode
from ai_flow.graph.edge import JobControlEdge
from ai_flow.workflow.job import BaseJob
from ai_flow.graph.graph import _get_id_generator
from ai_flow.project.project_description import ProjectDesc


class Workflow(BaseNode):

    def __init__(self) -> None:
        super().__init__()
        self.workflow_id: int = None
        self.workflow_name: Text = None
        self.execution_name: Text = None
        self.jobs: Dict[Text, BaseJob] = {}
        self.edges: Dict[Text, List[JobControlEdge]] = {}
        self.workflow_phase = None
        self.start_time = None
        self.end_time = None
        self.project_desc: ProjectDesc = None

    def add_job(self, job: BaseJob):
        if job.instance_id is None:
            instance_id = _get_id_generator(self).generate_id(job)
            job.set_instance_id(instance_id)
        self.jobs[job.instance_id] = job

    def add_edges(self, job_instance_id: Text, dependencies: List[JobControlEdge]):
        self.edges[job_instance_id] = dependencies

    def add_edge(self, job_instance_id: Text, edge: JobControlEdge):
        if job_instance_id not in self.edges:
            self.edges[job_instance_id] = []
        self.edges[job_instance_id].append(edge)

