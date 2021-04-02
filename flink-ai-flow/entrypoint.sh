#!/usr/bin/env bash

mysql_conn=$1

# start ai_flow server and Apache Airflow
start-aiflow.sh $mysql_conn
sleep 3


exec "/bin/bash"