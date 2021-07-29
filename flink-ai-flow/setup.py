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
import os
import subprocess
from shutil import copytree, rmtree
from setuptools import setup, find_packages

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
in_source = os.path.isfile(CURRENT_DIR + "/run_tests.sh")


def remove_if_exists(file_path):
    if os.path.exists(file_path):
        if os.path.islink(file_path) or os.path.isfile(file_path):
            os.remove(file_path)
        else:
            assert os.path.isdir(file_path)
            rmtree(file_path)


def remove_installed_airflow():
    from distutils.sysconfig import get_python_lib

    local_site_package = get_python_lib()
    installed_airflow_path = os.path.join(local_site_package, "airflow")
    for file in os.listdir(installed_airflow_path):
        abs_path = os.path.join(installed_airflow_path, file)
        if os.path.isdir(abs_path) and file == 'providers':
            print("Airflow providers are not being removed.")
        else:
            remove_if_exists(abs_path)


def compile_assets():  # noqa
    # """Run a command to compile and build airflow assets."""
    subprocess.check_call('./lib/airflow/airflow/www/compile_assets.sh')


try:
    if in_source:
        compile_assets()
        AIRFLOW_DIR = CURRENT_DIR + "/lib/airflow"
        try:
            os.symlink(AIRFLOW_DIR + "/airflow", CURRENT_DIR + "/airflow")
        except BaseException:  # pylint: disable=broad-except
            copytree(AIRFLOW_DIR + "/airflow", CURRENT_DIR + "/airflow")
    else:
        remove_installed_airflow()

    require_file = '{}/{}'.format(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    with open(require_file) as f:
        context = f.read()
        require_file_lines = context.strip().split('\n')
    require_packages = []
    for line in require_file_lines:
        if not len(line.strip()) == 0 and not line.startswith("#"):
            require_packages.append(line)

    packages = find_packages()
    setup(
        name='ai_flow',
        version='0.1.0',
        description='An open source framework that bridges big data and AI.',
        author='',
        author_email='flink.aiflow@gmail.com',
        url='https://github.com/alibaba/flink-ai-extended',
        packages=find_packages(),
        install_requires=require_packages,
        python_requires='>=3.7, <3.8',
        include_package_data=True,
        scripts=['bin/start-aiflow.sh',
                 'bin/stop-aiflow.sh',
                 'bin/start_aiflow.py',
                 'bin/start_notification_service.py'],
        package_data={
            '': ['airflow/alembic.ini', "airflow/git_version", "*.ipynb",
                 "airflow/providers/cncf/kubernetes/example_dags/*.yaml"],
            'airflow.serialization': ["*.json"],
        }
    )
finally:
    if in_source:
        remove_if_exists(CURRENT_DIR + "/airflow")
