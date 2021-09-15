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
import json
import re
from subprocess import Popen, PIPE
from typing import Text, List

from ai_flow.plugin_interface.job_plugin_interface import JobController
from ai_flow.translator.translator import JobGenerator
from ai_flow_plugins.job_plugins.read_only import ReadOnlyJobController, ReadOnlyJob, ReadOnlyJobGenerator, \
    ReadOnlyJobPluginFactory


class ReadOnlyFlinkJobController(ReadOnlyJobController):
    def get_job_label(self, job: ReadOnlyJob) -> Text:
        job_id = job.job_config.properties.get('job_id')
        args = job.job_config.properties.get('args', [])

        output = self._list_flink_job_status(args)
        return self._get_job_label(output, job_id)

    @staticmethod
    def _list_flink_job_status(args: List[Text]):
        bash_command = ['flink', 'list', '-a'] + args
        process = Popen(args=bash_command, stdout=PIPE, stderr=PIPE)
        output = process.stdout.read().decode('utf-8')
        return output

    @staticmethod
    def _get_job_label(output, job_id):
        m = re.search(r"(?P<start_time>.+) : {} : (?P<job_name>.*) \((?P<status>.*)\)".format(job_id), output)
        if m is None:
            return ""
        return json.dumps(m.groupdict())


class ReadOnlyFlinkJobPluginFactory(ReadOnlyJobPluginFactory):

    def job_type(self) -> Text:
        return "read_only_flink"

    def get_job_generator(self) -> JobGenerator:
        return ReadOnlyJobGenerator(required_properties={'job_id'})

    def get_job_controller(self) -> JobController:
        return ReadOnlyFlinkJobController()
