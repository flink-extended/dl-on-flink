set -e

python -m grpc_tools.protoc --version

DIR=$(dirname "${BASH_SOURCE-$0}")
DIR=$(cd "$DIR"; pwd)

PYTHON_ROOT_DIR="${DIR}"
PROTO_DIR=$(cd "$DIR/../src/proto"; pwd)
PROTO_OUT_DIR="${PYTHON_ROOT_DIR}"/flink_ml_framework

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