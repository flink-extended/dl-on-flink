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

from setuptools import setup, find_packages

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


def get_script():
    bin_dir = os.path.join(CURRENT_DIR, "bin")
    return [os.path.join("bin", filename) for filename in os.listdir(bin_dir)]


setup(
    name='notification_service',
    version='0.1.0',
    description='A Python package which provides stable notification service.',
    author='',
    author_email='flink.aiflow@gmail.com',
    url='https://github.com/alibaba/flink-ai-extended',
    packages=find_packages(exclude=['tests*']),
    scripts=get_script(),
    install_requires=["protobuf==3.15.6", "grpcio==1.34.0", "sqlalchemy>=1.3.18, <2"]
)
