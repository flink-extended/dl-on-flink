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
import os
import textwrap
import ai_flow
from airflow.logging_config import configure_logging


def create_default_sever_config(root_dir_path):
    content = textwrap.dedent(f"""\
        # Config of master server

        # endpoint of master
        master_ip: localhost
        master_port: 50051
        # uri of database backend in master
        db_uri: sqlite:///{root_dir_path}/aiflow.db
        # type of database backend in master
        db_type: sql_lite
        # the default notification service is no need to started
        # when using the airflow scheduler 
        start_default_notification: False
        # uri of the notification service
        notification_uri: localhost:50052
    """)
    master_yaml_path = root_dir_path + "/master.yaml"
    with open(master_yaml_path, "w") as f:
        f.write(content)
    return master_yaml_path


def start_master(master_yaml_path):
    configure_logging()
    master = ai_flow.AIFlowMaster(config_file=master_yaml_path)
    master.start(is_block=True)
    return master


if __name__ == '__main__':
    if "AIRFLOW_HOME" in os.environ:
        root_dir = os.environ["AIRFLOW_HOME"]
    else:
        root_dir = os.environ["HOME"] + "/airflow"
    master_yaml = root_dir + "/master.yaml"
    if not os.path.exists(master_yaml):
        master_yaml = create_default_sever_config(root_dir)
    start_master(master_yaml)
