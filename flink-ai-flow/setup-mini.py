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


def get_script():
    bin_dir = os.path.join(CURRENT_DIR, "bin")
    return [os.path.join("bin", filename) for filename in os.listdir(bin_dir)]


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

    packages = []
    for package in find_packages():
        if 'airflow' not in package and 'python_ai_flow' not in package and 'flink_ai_flow' not in package:
            packages.append(package)

    require_file = '{}/{}'.format(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    with open(require_file) as f:
        context = f.read()
        require_file_lines = context.strip().split('\n')
    required_packages = []
    for line in require_file_lines:
        if line.startswith("# Optional"):
            break
        if not len(line.strip()) == 0 and not line.startswith("#"):
            required_packages.append(line)

    setup(
        name='ai_flow',
        version='0.3.0',
        description='This is an ai flow of the setup',
        author='',
        author_email='',
        url='',
        packages=packages,
        install_requires=required_packages,
        include_package_data=True,
        scripts=get_script(),
    )
finally:
    if in_source:
        remove_if_exists(CURRENT_DIR + "/notification_service")
        remove_if_exists(CURRENT_DIR + "/airflow")
