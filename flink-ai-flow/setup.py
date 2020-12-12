# coding:utf-8
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
from shutil import copytree, rmtree
from setuptools import setup, find_packages
import os

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
in_source = os.path.isfile(CURRENT_DIR + "/run_tests.sh")


def remove_if_exists(file_path):
    if os.path.exists(file_path):
        if os.path.islink(file_path) or os.path.isfile(file_path):
            os.remove(file_path)
        else:
            assert os.path.isdir(file_path)
            rmtree(file_path)


try:
    if in_source:
        AIRFLOW_DIR = CURRENT_DIR + "/lib/airflow"
        NOTIFICATION_SERVICE_DIR = CURRENT_DIR + "/lib/notification_service"
        try:
            os.symlink(AIRFLOW_DIR + "/airflow", CURRENT_DIR + "/airflow")
            support_symlinks = True
        except BaseException:  # pylint: disable=broad-except
            support_symlinks = False

        if support_symlinks:
            os.symlink(NOTIFICATION_SERVICE_DIR + "/notification_service",
                       CURRENT_DIR + "/notification_service")
        else:
            copytree(AIRFLOW_DIR + "/airflow", CURRENT_DIR + "/airflow")
            copytree(NOTIFICATION_SERVICE_DIR + "/notification_service",
                     CURRENT_DIR + "/notification_service")

    require_file = '{}/{}'.format(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    with open(require_file) as f:
        context = f.read()
        require_file_lines = context.strip().split('\n')
    require_packages = []
    for line in require_file_lines:
        if not len(line.strip()) == 0 and not line.startswith("#"):
            require_packages.append(line)

    packages = find_packages()

    version = "1.0-SNAPSHOT"
    jar_name = "flink_ai_flow-{}.jar".format(version)
    main_class = "com.apache.flink.ai.flow.FlinkJobMain"

    setup(
        name='ai_flow',
        version='0.1',
        description='This is an ai flow of the setup',
        author='',
        author_email='',
        url='',
        packages=find_packages(),
        install_requires=require_packages,
        include_package_data=True,
        scripts=['airflow/bin/airflow',
                 'ai_flow/bin/start-aiflow.sh',
                 'ai_flow/bin/stop-aiflow.sh',
                 'ai_flow/bin/start_aiflow.py'],
        package_data={
            '': ['airflow/alembic.ini', "airflow/git_version", "*.ipynb",
                 "airflow/providers/cncf/kubernetes/example_dags/*.yaml"],
            'airflow.serialization': ["*.json"],
        }
    )
finally:
    if in_source:
        remove_if_exists(CURRENT_DIR + "/notification_service")
        remove_if_exists(CURRENT_DIR + "/airflow")
