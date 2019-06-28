#!/usr/bin/env bash
basePath=$(cd `dirname $0`; pwd)
projectPath=${basePath}/../../

# start jm
echo "flink job master starting..."
docker run -d --ulimit core=10000000000 -h flink-jm --name flink-jm --link minizk --link minidfs -v ${projectPath}:/opt/work_home/ -p 8081:8081 flink-ml/flink jobmanager
echo "flink job master started!"

# start tm
for i in 0 1 2
do
    echo "starting tm-${i} ..."
    docker run -d --ulimit core=10000000000 -h flink-tm-${i} --name flink-tm-${i} -e TASK_MANAGER_NUMBER_OF_TASK_SLOTS=2 -e JOB_MANAGER_RPC_ADDRESS=flink-jm --link minizk --link minidfs --link flink-jm flink-ml/flink taskmanager
    echo "tm-${i} started!"
done
