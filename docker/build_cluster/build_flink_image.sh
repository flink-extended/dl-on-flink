#!/usr/bin/env bash
basePath=$(cd `dirname $0`; pwd)

cd ${basePath}/../flink/ && docker build -t flink-ml/flink:latest .