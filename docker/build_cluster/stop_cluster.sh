#!/usr/bin/env bash

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