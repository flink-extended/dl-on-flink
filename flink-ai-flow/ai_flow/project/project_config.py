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
    """
    Configuration information of ai flow project.
    """
    def get_server_ip(self):
        """
        return: The ai_flow.endpoint.server.server.AIFlowServer ip.
        """
        return self["server_ip"]

    def set_server_ip(self, value):
        self["server_ip"] = value

    def get_server_port(self):
        """
        return: The ai_flow.endpoint.server.server.AIFlowServer port.
        """
        return self["server_port"]

    def set_server_port(self, value):
        self["server_port"] = value

    def get_server_uri(self):
        """
        return: The ai_flow.endpoint.server.server.AIFlowServer uri(ip:port,ip:port).
        """
        ips = self["server_ip"].split(',')
        ports = self["server_port"].split(',')
        if len(ips) != len(ports):
            raise Exception('The number of ip and port must be the same! ip number({}) port number({})'
                            .format(len(ips), len(ports)))
        uris = []
        for i in range(len(ips)):
            uri = "{}:{}".format(ips[i], ports[i])
            uris.append(uri)

        return ','.join(uris)

    def get_project_name(self):
        """
        return: The name of an ai flow project.
        """
        return self["project_name"]

    def set_project_name(self, value):
        self["project_name"] = value

    def get_project_uuid(self):
        """
        return: The unique id of the ai flow project, it is generated by ai flow meta service.
        """
        if "project_uuid" in self:
            return self["project_uuid"]
        else:
            return None

    def set_project_uuid(self, value):
        self["project_uuid"] = value

    def get_notification_service_uri(self):
        """
        return: The notification service(notification_service.master.NotificationMaster) uri.
        """
        if "notification_uri" in self:
            return self["notification_uri"]
        else:
            return self.get_server_uri()

    def set_notification_service_uri(self, uri):
        self["notification_uri"] = uri

    def get_enable_ha(self):
        """
        Use ai_flow.endpoint.server.server.AIFlowServer ha mode or not.
        If use AIFlowServer ha return True else return False
        """
        if "enable_ha" in self:
            raw = self["enable_ha"]
            assert str(raw).strip().lower() in {"true", "false"}
            return bool(str(raw).strip().lower())
        else:
            return False

    def set_enable_ha(self, enable_ha):
        assert str(enable_ha).strip().lower() in {"true", "false"}
        self["enable_ha"] = enable_ha

    def _get_time_interval_ms(self, key, default):
        if key in self:
            raw = self[key]
            assert int(str(raw).strip()) >= 0
            return int(str(raw).strip())
        else:
            return default

    def _set_time_interval_ms(self, key, value):
        assert int(str(value).strip()) >= 0
        self[key] = value

    def get_list_member_interval_ms(self):
        """
        If in ha mode, the ai flow client (ai_flow.client.ai_flow_client.AIFlowClient)
        will periodic find ai flow server(ai_flow.endpoint.server.server.AIFlowServer).
        This parameter represents the time interval(millisecond) between two searches for the server.
        """
        return self._get_time_interval_ms("list_member_interval_ms", 5000)

    def set_list_member_interval_ms(self, list_member_interval_ms):
        self._set_time_interval_ms("list_member_interval_ms", list_member_interval_ms)

    def get_retry_interval_ms(self):
        """
        In ha mode, if the ai flow client (ai_flow.client.ai_flow_client.AIFlowClient) lose the
        ai flow server(ai_flow.endpoint.server.server.AIFlowServer), it will try to connect the server.
        This parameter represents the time interval(millisecond) between two trying to connect the server.
        """
        return self._get_time_interval_ms("retry_interval_ms", 1000)

    def set_retry_interval_ms(self, retry_interval_ms):
        self._set_time_interval_ms("retry_interval_ms", retry_interval_ms)

    def get_retry_timeout_ms(self):
        """
        In ha mode, if the ai flow client (ai_flow.client.ai_flow_client.AIFlowClient) lose the
        ai flow server(ai_flow.endpoint.server.server.AIFlowServer), it will try to connect the server.
        This parameter indicates the maximum time the client attempts to connect to the server.
        If this time is exceeded, the client will throw an error.
        """
        return self._get_time_interval_ms("retry_timeout_ms", 10000)

    def set_retry_timeout_ms(self, retry_timeout_ms):
        self._set_time_interval_ms("retry_timeout_ms", retry_timeout_ms)

