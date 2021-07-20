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

current_dir=$(cd "$(dirname "$0")";pwd)
root_dir=${current_dir}/../..
echo $root_dir

git clone https://github.com/grpc-ecosystem/grpc-gateway.git
cd grpc-gateway
git checkout v1
cd ..
sudo go get \
    github.com/grpc-ecosystem/grpc-gateway/protoc-gen-grpc-gateway \
    github.com/golang/protobuf/protoc-gen-go
sudo rm -rf $GOPATH/src/github.com/grpc-ecosystem/grpc-gateway
sudo cp -r grpc-gateway $GOPATH/src/github.com/grpc-ecosystem/
sudo rm -rf grpc-gateway
sudo go get github.com/ghodss/yaml
sudo go get github.com/golang/glog
sudo go get github.com/golang/protobuf/proto
sudo go get github.com/golang/protobuf/jsonpb
sudo go get github.com/golang/protobuf/protoc-gen-go
sudo go get google.golang.org/genproto/googleapis/api/annotations
sudo go install \
    github.com/grpc-ecosystem/grpc-gateway/protoc-gen-grpc-gateway \
    github.com/grpc-ecosystem/grpc-gateway/protoc-gen-swagger \
    github.com/golang/protobuf/protoc-gen-go
sudo cp -r $GOPATH/src/google.golang.org/genproto/googleapis/api/* $GOPATH/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis/google/api/