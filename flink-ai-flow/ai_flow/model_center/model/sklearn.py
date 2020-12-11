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
"""
The ``aiflow.sklearn`` module provides an API for loading scikit-learn models.
"""

from __future__ import absolute_import

import pickle


def _load_model_from_local_file(path):
    """Load a scikit-learn model saved as an aiflow artifact on the local file system."""
    with open(path, "rb") as f:
        return pickle.load(f)


def load_model(model_uri):
    """
    Load a scikit-learn model from a local file.

    :param model_uri: The location, in URI format, of the aiflow model, for example:

                      - ``/Users/aiflow/path/to/local/model``
                      - ``relative/path/to/local/model``
                      - ``s3://my_bucket/path/to/model``
                      - ``models:/<model_name>/<model_version>``
                      - ``models:/<model_name>/<stage>``

    :return: A scikit-learn model.
    """
    return _load_model_from_local_file(path=model_uri)
