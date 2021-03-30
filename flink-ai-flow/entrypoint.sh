#!/usr/bin/env bash

mysql_conn=$1

# start ai_flow server and Apache Airflow
start-aiflow.sh $mysql_conn
sleep 3

# create a default Admin user
airflow users create \
    --username admin \
    --password admin \
    --firstname admin \
    --lastname admin \
    --role Admin \
    --email admin@example.org

exec "/bin/bash"