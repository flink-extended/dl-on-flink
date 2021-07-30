#!/usr/bin/env python
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
import logging
import os

from typing import Dict

import ai_flow
from airflow.logging_config import configure_logging


def create_default_sever_config(root_dir_path, param: Dict[str, str]):
    """
    Generate default server config which use Apache Airflow as scheduler.
    """
    import ai_flow.config_templates
    if not os.path.exists(root_dir_path):
        logging.info("{} does not exist, creating the directory".format(root_dir_path))
        os.makedirs(root_dir_path, exist_ok=False)
    aiflow_server_config_path = os.path.join(
        os.path.dirname(ai_flow.config_templates.__file__), "default_aiflow_server.yaml"
    )
    if not os.path.exists(aiflow_server_config_path):
        raise Exception("default aiflow server config is not found at {}.".format(aiflow_server_config_path))

    aiflow_server_config_target_path = os.path.join(root_dir_path, "aiflow_server.yaml")
    with open(aiflow_server_config_path, encoding='utf-8') as config_file:
        default_config = config_file.read().format(**param)
    with open(aiflow_server_config_target_path, mode='w', encoding='utf-8') as f:
        f.write(default_config)
    return aiflow_server_config_target_path


def start_master(config_file):
    server_runner = ai_flow.AIFlowServerRunner(config_file=config_file)
    server_runner.start(is_block=True)
    return server_runner


if __name__ == '__main__':
    configure_logging()
    if "AIFLOW_HOME" not in os.environ:
        os.environ["AIFLOW_HOME"] = os.environ["HOME"] + "/aiflow"
        logging.info("Set env variable AIFLOW_HOME to {}".format(os.environ["AIFLOW_HOME"]))
    logging.info("Looking for aiflow_server.yaml at {}".format(os.environ["AIFLOW_HOME"]))
    aiflow_server_config = os.environ["AIFLOW_HOME"] + "/aiflow_server.yaml"
    if not os.path.exists(aiflow_server_config):
        logging.info("{} does not exist, creating the default aiflow server config".format(aiflow_server_config))
        required_env = {'AIFLOW_HOME', 'AIFLOW_DB_CONN', 'AIFLOW_DB_TYPE'}
        for key in required_env:
            if key not in os.environ:
                raise Exception("Failed to create default aiflow server config, {} env variable not set.".format(key))
        aiflow_server_config = create_default_sever_config(os.environ["AIFLOW_HOME"], os.environ.copy())
    start_master(aiflow_server_config)
