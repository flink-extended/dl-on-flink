#  Copyright 2022 Deep Learning on Flink Authors
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import sys
from datetime import datetime

from setuptools import setup, find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))
version_file = os.path.join(this_directory, 'dl_on_flink_pytorch/version.py')

try:
    exec(open(version_file).read())
except IOError:
    print("Failed to load dl_on_flink_framework version file for packaging. " +
          "'%s' not found!" % version_file,
          file=sys.stderr)
    sys.exit(-1)
VERSION = __version__  # noqa
PACKAGE_NAME = "dl-on-flink-pytorch"
DL_ON_FLINK_FRAMEWORK_PACKAGE_NAME = "dl-on-flink-framework"

if os.getenv("NIGHTLY_WHEEL") == "true":
    if 'dev' not in VERSION:
        raise RuntimeError("Nightly wheel is not supported for non dev version")
    VERSION = VERSION[:str.find(VERSION, 'dev') + 3] + \
              datetime.now().strftime('%Y%m%d')

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    python_requires=">=3.6",
    packages=find_packages(where=this_directory,
                           include=['dl_on_flink_pytorch',
                                    'dl_on_flink_pytorch.*']),
    install_requires=['torch>=1.10',
                      'apache-flink>=1.14.0, <1.15.0',
                      'pandas>=1.0',
                      f'{DL_ON_FLINK_FRAMEWORK_PACKAGE_NAME}=={VERSION}'],
    url='https://github.com/flink-extended/dl-on-flink',
    license='https://www.apache.org/licenses/LICENSE-2.0'
)
