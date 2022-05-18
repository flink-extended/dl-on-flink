#!/usr/bin/env bash
#
# Copyright 2022 Deep Learning on Flink Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
echo "stop zookeeper!"
docker rm -f minizk

echo "stop hdfs!"
docker rm -f minidfs

echo "stop flink jm!"
docker rm -f flink-jm

for i in 0 1 2
do
    echo "stop tm-${i}"
    docker rm -f flink-tm-${i}
done