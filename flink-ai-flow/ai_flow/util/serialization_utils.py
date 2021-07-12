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
import pickle

_BYTES_ENCODE = "ISO-8859-1"


def serialize(o: object) -> bytes:
    return pickle.dumps(o)


def deserialize(s: bytes) -> object:
    return pickle.loads(s)


def read_object_from_serialized_file(file_path):
    with open(file_path, 'rb') as f:
        serialized_bytes = f.read()
    return deserialize(serialized_bytes)