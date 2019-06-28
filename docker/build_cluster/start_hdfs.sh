#!/usr/bin/env bash
set -e
docker run -d -h minidfs --name minidfs sequenceiq/hadoop-docker /etc/bootstrap.sh -d
echo "sleep 10s wait for hdfs starting..."
sleep 10s
docker exec minidfs /usr/local/hadoop/bin/hdfs dfsadmin -safemode wait
echo "hdfs started!"