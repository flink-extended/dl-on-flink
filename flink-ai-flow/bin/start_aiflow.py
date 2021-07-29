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
import argparse
import os
import textwrap
import ai_flow
from airflow.logging_config import configure_logging


def create_default_sever_config(root_dir_path, db_uri, airflow_deploy_path):
    """
    Generate default server config which use Apache Airflow as scheduler.
    """
    from ai_flow.store.db.db_util import extract_db_engine_from_uri

    db_type = extract_db_engine_from_uri(db_uri)
    content = textwrap.dedent(f"""\
        # Config of master server

        # endpoint of AI Flow Server
        server_ip: localhost
        server_port: 50051

        # uri of database backend of AIFlow server
        db_uri: {db_uri}

        # type of database backend in master
        db_type: {db_type}

        # whether to start the scheduler service
        start_scheduler_service: True

        # Whether to start default notification service, if not a custom URI should be set
        start_default_notification: False
        notification_uri: localhost:50052

        # scheduler config
        scheduler:
          scheduler_class: ai_flow_plugins.scheduler_plugins.airflow.airflow_scheduler.AirFlowScheduler
          scheduler_config:
            airflow_deploy_path: {airflow_deploy_path}
            notification_service_uri: localhost:50052
    """)
    master_yaml_path = root_dir_path + "/master.yaml"
    with open(master_yaml_path, "w") as f:
        f.write(content)
    return master_yaml_path


def start_master(master_yaml_path):
    configure_logging()
    server_runner = ai_flow.AIFlowServerRunner(config_file=master_yaml_path)
    server_runner.start(is_block=True)
    return server_runner


def _prepare_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database-conn', type=str, default=None,
                        help='Database connection info')
    parser.add_argument('--airflow-deploy-path', type=str, default=None,
                        help='The directory which airflow read dags')
    return parser.parse_args()


if __name__ == '__main__':
    args = _prepare_args()
    database_conn = args.database_conn
    airflow_deploy_path = args.airflow_deploy_path
    if "AIRFLOW_HOME" in os.environ:
        root_dir = os.environ["AIRFLOW_HOME"]
    else:
        root_dir = os.environ["HOME"] + "/airflow"
    master_yaml = root_dir + "/master.yaml"
    if not os.path.exists(master_yaml):
        master_yaml = create_default_sever_config(root_dir, database_conn, airflow_deploy_path)
    start_master(master_yaml)
