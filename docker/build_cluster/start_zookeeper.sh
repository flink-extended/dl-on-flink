#!/usr/bin/env bash

echo "zookeeper starting..."
docker run -d -h minizk --name minizk zookeeper
echo "zookeeper started!"