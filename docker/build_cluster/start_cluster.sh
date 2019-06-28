#!/usr/bin/env bash
basePath=$(cd `dirname $0`; pwd)
projectPath=${basePath}/../../

set -e

sh ${basePath}/start_hdfs.sh
sh ${basePath}/start_zookeeper.sh
sh ${basePath}/start_flink.sh
