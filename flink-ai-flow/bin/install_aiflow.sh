#!/usr/bin/env bash
##
## Licensed to the Apache Software Foundation (ASF) under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  The ASF licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##   http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing,
## software distributed under the License is distributed on an
## "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
## KIND, either express or implied.  See the License for the
## specific language governing permissions and limitations
## under the License.
##

set -e

bin=$(dirname "${BASH_SOURCE[0]}")
bin=$(cd "$bin"; pwd)
workdir=$bin/..

# In case of existed typing cause version conflict, uninstall it and then install AI Flow from source
pip uninstall -y typing

# Compile Web UI assets of airflow (yarn is required)
bash "$workdir"/lib/airflow/airflow/www/compile_assets.sh
pip install "$workdir"/lib/notification_service
pip install "$workdir"/lib/airflow
pip install "$workdir"