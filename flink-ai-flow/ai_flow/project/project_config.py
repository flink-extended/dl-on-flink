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
from ai_flow.common.configuration import AIFlowConfiguration


class ProjectConfig(AIFlowConfiguration):
    def get_master_ip(self):
        return self["master_ip"]

    def set_master_ip(self, value):
        self["master_ip"] = value

    def get_master_port(self):
        return self["master_port"]

    def set_master_port(self, value):
        self["master_port"] = value

    def get_master_uri(self):
        return "{}:{}".format(self["master_ip"], self["master_port"])

    def get_project_name(self):
        return self["project_name"]

    def set_project_name(self, value):
        self["project_name"] = value

    def get_project_uuid(self):
        return self["project_uuid"]

    def set_project_uuid(self, value):
        self["project_uuid"] = value

    def get_airflow_deploy_path(self):
        if "airflow_deploy_path" in self:
            return self["airflow_deploy_path"]
        else:
            return None

    def set_airflow_deploy_path(self, path):
        self["airflow_deploy_path"] = path

    def get_notification_service_uri(self):
        if "notification_uri" in self:
            return self["notification_uri"]
        else:
            return None

    def set_notification_service_uri(self, uri):
        self["notification_uri"] = uri

    def get_schedule_interval(self):
        if "schedule_interval" in self:
            return self["schedule_interval"]
        else:
            return '@deploy'

    def set_schedule_interval(self, schedule_interval):
        self["schedule_interval"] = schedule_interval


_default_project_config = ProjectConfig()
