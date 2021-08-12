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
import argparse

from typing import Text
from ai_flow.endpoint.server.server import AIFlowServer
from ai_flow.endpoint.server.server_config import AIFlowServerConfig
from ai_flow.client.ai_flow_client import get_ai_flow_client
import logging

_SQLITE_DB_FILE = 'aiflow.db'
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)
_MYSQL_DB_URI = 'mysql+pymysql://root:aliyunmysql@localhost:3306/aiflow'
_PORT = '50051'
GLOBAL_MASTER_CONFIG = {}


class AIFlowServerRunner(object):
    """
    AI flow server runner. This class is the runner class for the AIFlowServer. It parse the server configuration and
    manage the live cycle of the AIFlowServer.
    """

    def __init__(self, config_file: Text = None, enable_ha=False, server_uri: str = None, ttl_ms=10000) -> None:
        """
        Set the server attribute according to the server config file.

        :param config_file: server configuration file.
        """
        super().__init__()
        self.config_file = config_file
        self.server = None
        self.server_config = AIFlowServerConfig()
        self.enable_ha = enable_ha
        self.server_uri = server_uri
        self.ttl_ms = ttl_ms

    def start(self,
              is_block=False) -> None:
        """
        Start the AI flow runner.

        :param is_block: AI flow runner will run non-stop if True.
        """
        if self.config_file is not None:
            self.server_config.load_from_file(self.config_file)
        else:
            self.server_config.set_server_port(str(_PORT))
        global GLOBAL_MASTER_CONFIG
        GLOBAL_MASTER_CONFIG = self.server_config
        logging.info("AI Flow Master Config {}".format(GLOBAL_MASTER_CONFIG))
        self.server = AIFlowServer(
            store_uri=self.server_config.get_db_uri(),
            port=str(self.server_config.get_server_port()),
            start_default_notification=self.server_config.start_default_notification(),
            notification_uri=self.server_config.get_notification_uri(),
            start_meta_service=self.server_config.start_meta_service(),
            start_model_center_service=self.server_config.start_model_center_service(),
            start_metric_service=self.server_config.start_metric_service(),
            start_scheduler_service=self.server_config.start_scheduler_service(),
            scheduler_service_config=self.server_config.get_scheduler_service_config(),
            enabled_ha=self.server_config.get_enable_ha(),
            ha_server_uri=self.server_config.get_server_ip() + ":" + str(self.server_config.get_server_port()),
            ttl_ms=self.server_config.get_ha_ttl_ms())
        self.server.run(is_block=is_block)

    def stop(self, clear_sql_lite_db_file=True) -> None:
        """
        Stop the AI flow runner.

        :param clear_sql_lite_db_file: If True, the sqlite database files will be deleted When the server stops working.
        """
        self.server.stop(clear_sql_lite_db_file)

    def _clear_db(self):
        self.server._clear_db()


def set_master_config():
    code, config, message = get_ai_flow_client().get_master_config()
    for k, v in config.items():
        GLOBAL_MASTER_CONFIG[k] = v


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, help='master config file')
    args = parser.parse_args()
    logging.info(args.config)
    config_file = args.config
    master = AIFlowServerRunner(
        config_file=config_file)
    master.start(is_block=True)
