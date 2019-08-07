#!/usr/bin/env bash
basePath=$(cd `dirname $0`; pwd)
set -e
dockerContainerName=venv-build
projectPath=${basePath}/../../
docker run -d --ulimit core=10000000000 -h ${dockerContainerName} --name ${dockerContainerName} -v ${projectPath}:/opt/work_home/ flink-ml/flink jobmanager
docker exec ${dockerContainerName} bash /opt/work_home/docker/flink/create_venv.sh
docker rm -f ${dockerContainerName}


