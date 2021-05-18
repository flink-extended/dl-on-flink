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

#generate python file
python3 -m grpc.tools.protoc -I. \
  -I/usr/local/include \
  -I$GOPATH/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis \
  --python_out=. \
  --grpc_python_out=. \
  notification_service.proto

#generate java file
protoc -I/usr/local/include -I. \
  -I$GOPATH/src -I$GOPATH/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis \
  --java_out=../../java/src/main/java \
  --proto_path=. \
  notification_service.proto

protoc -I/usr/local/include -I. \
  -I$GOPATH/src -I$GOPATH/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis \
  --plugin=protoc-gen-grpc-java \
  --grpc-java_out=../../java/src/main/java \
  --proto_path=. \
  notification_service.proto

#generate go file
protoc -I/usr/local/include -I. \
  -I$GOPATH/src \
  -I$GOPATH/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis \
  --go_out=Mgoogle/api/annotations.proto=github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis/google/api,plugins=grpc:../go \
  notification_service.proto

protoc -I/usr/local/include -I. \
  -I$GOPATH/src -I$GOPATH/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis \
  --grpc-gateway_out=logtostderr=true:../go \
  notification_service.proto

sed -i -E 's/^import notification_service_pb2 as notification__service__pb2/from \. import notification_service_pb2 as notification__service__pb2/' *pb2*.py
rm -rf *.py-E

cd ..

sed -i -E 's/^package notification_service/package service/' go/notification_service/*.go
sed -i '' 's/\_ "github.com\/grpc-ecosystem\/grpc-gateway\/third_party\/googleapis\/google\/api"/\/\/\_ "github.com\/grpc-ecosystem\/grpc-gateway\/third_party\/googleapis\/google\/api"/g' go/notification_service/notification_service.pb.go
rm -rf go/*.go-E
