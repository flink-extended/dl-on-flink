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

from ai_flow.api.configuration import set_project_config_file, project_config
from ai_flow.common import path_util

DEFAULT_MYSQL_USERNAME = ''
DEFAULT_MYSQL_PASSWORD = ''
DEFAULT_MYSQL_HOST = ''
DEFAULT_MYSQL_PORT = 3306


def get_project_config_file():
    return os.path.dirname(os.path.abspath(__file__)) + "/project.yaml"


def get_master_config_file():
    return os.path.dirname(os.path.abspath(__file__)) + "/master.yaml"


def set_project_config(main_file):
    set_project_config_file(get_project_config_file())
    project_config()['entry_module_path'] = path_util.get_module_name(main_file)


def get_mysql_server_url():
    db_username = os.environ.get('MYSQL_TEST_USERNAME') if 'MYSQL_TEST_USERNAME' in os.environ \
        else DEFAULT_MYSQL_USERNAME
    db_password = os.environ.get('MYSQL_TEST_PASSWORD') if 'MYSQL_TEST_PASSWORD' in os.environ \
        else DEFAULT_MYSQL_PASSWORD
    db_host = str(os.environ['MYSQL_TEST_HOST']) if 'MYSQL_TEST_HOST' in os.environ \
        else DEFAULT_MYSQL_HOST
    db_port = int(os.environ['MYSQL_TEST_PORT']) if 'MYSQL_TEST_PORT' in os.environ \
        else DEFAULT_MYSQL_PORT
    if db_username is None or db_password is None:
        raise Exception(
            "Username and password for MySQL tests must be specified via the "
            "MYSQL_TEST_USERNAME and MYSQL_TEST_PASSWORD environment variables. "
            "environment variable. In posix shells, you rerun your test command "
            "with the environment variables set, e.g: MYSQL_TEST_USERNAME=your_username "
            "MYSQL_TEST_PASSWORD=your_password <your-test-command>. You may optionally "
            "specify MySQL host via MYSQL_TEST_HOST (default is 100.69.96.145) "
            "and specify MySQL port via MYSQL_TEST_PORT (default is 3306).")
    return 'mysql+pymysql://%s:%s@%s:%s' % (db_username, db_password, db_host, db_port)
