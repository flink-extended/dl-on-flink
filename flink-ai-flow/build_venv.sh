#!/usr/bin/env bash
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
set -e
CURRENT_DIR=$(pwd)
SOURCE_ROOT=$(cd "$(dirname "$0")";pwd)
cd "${SOURCE_ROOT}"
trap "rm -f miniconda.sh;cd ${CURRENT_DIR}" EXIT

# download miniconda.sh
if [[ `uname -s` == "Darwin" ]]; then
    wget "https://repo.anaconda.com/miniconda/Miniconda3-py37_4.9.2-MacOSX-x86_64.sh" -O "miniconda.sh"
else
    wget "https://repo.anaconda.com/miniconda/Miniconda3-py37_4.9.2-Linux-x86_64.sh" -O "miniconda.sh"
fi
# add the execution permission
chmod +x miniconda.sh

# create python virtual environment
./miniconda.sh -b -p venv

# activate the conda python virtual environment
source venv/bin/activate ""

python -m pip install -r requirements.txt

cat>venv/lib/python3.7/site-packages/ai_flow_lib.pth<<EOF
${SOURCE_ROOT}
${SOURCE_ROOT}/lib/airflow
${SOURCE_ROOT}/lib/notification_service
EOF
awk "{gsub(\"#\!/usr/bin/env python\", \"#\!${SOURCE_ROOT}/venv/bin/python\"); print \$0}" lib/airflow/airflow/bin/airflow > venv/bin/airflow
cp bin/start-all-aiflow-services.sh venv/bin/
cp bin/stop-all-aiflow-services.sh venv/bin/
awk "{gsub(\"#\!/usr/bin/env python\", \"#\!${SOURCE_ROOT}/venv/bin/python\"); print \$0}" bin/start_aiflow.py > venv/bin/start_aiflow.py
awk "{gsub(\"#\!/usr/bin/env python\", \"#\!${SOURCE_ROOT}/venv/bin/python\"); print \$0}" bin/start_notification_service.py > venv/bin/start_notification_service.py
chmod +x venv/bin/airflow
chmod +x venv/bin/start-all-aiflow-services.sh
chmod +x venv/bin/stop-all-aiflow-services.sh
chmod +x venv/bin/start_aiflow.py
chmod +x venv/bin/start_notification_service.py

# remove the cached packages
rm -rf venv/pkgs
