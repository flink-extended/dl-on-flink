#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

set -e

python -m grpc_tools.protoc --version

DIR=$(dirname "${BASH_SOURCE-$0}")
DIR=$(cd "$DIR"; pwd)

PYTHON_ROOT_DIR="${DIR}"
PROTO_DIR=$(cd "$DIR/../src/proto"; pwd)
PROTO_OUT_DIR="${PYTHON_ROOT_DIR}"/dl_on_flink_framework

echo "Generating protobuf from proto file in ${PROTO_DIR} to ${PROTO_OUT_DIR}"

python -m grpc_tools.protoc \
  -I="${PROTO_DIR}" \
  --python_out="${PROTO_OUT_DIR}" \
  "${PROTO_DIR}"/node.proto

python -m grpc_tools.protoc \
  -I="${PROTO_DIR}" \
  --python_out="${PROTO_OUT_DIR}" \
  --grpc_python_out="${PROTO_OUT_DIR}" \
  "${PROTO_DIR}"/node_service.proto

sed -i -E 's/^import node_pb2 as node__pb2/from \. import node_pb2 as node__pb2/' "${PROTO_OUT_DIR}"/*pb2*.py
rm -rf "${PROTO_OUT_DIR}"/*.py-E