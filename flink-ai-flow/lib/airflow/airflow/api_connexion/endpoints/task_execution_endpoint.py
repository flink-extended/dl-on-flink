# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from sqlalchemy import and_

from airflow.api_connexion import security
from airflow.api_connexion.exceptions import NotFound
from airflow.api_connexion.schemas.task_execution_schema import (
    TaskExecutionCollection,
    task_execution_collection_schema
)
from airflow.models import SlaMiss
from airflow.models.dagrun import DagRun as DR
from airflow.models.taskexecution import TaskExecution as TE
from airflow.security import permissions
from airflow.utils.session import provide_session


@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG_RUN),
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_TASK_EXECUTION),
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_TASK_INSTANCE),
    ]
)
@provide_session
def list_task_executions(dag_id: str, dag_run_id: str, session=None):
    """List task executions"""
    query = (
        session.query(TE)
        .filter(TE.dag_id == dag_id)
        .join(DR, and_(TE.dag_id == DR.dag_id, TE.execution_date == DR.execution_date))
        .filter(DR.run_id == dag_run_id)
        .outerjoin(
            SlaMiss,
            and_(
                SlaMiss.dag_id == TE.dag_id,
                SlaMiss.execution_date == TE.execution_date,
                SlaMiss.task_id == TE.task_id,
            ),
        )
        .add_entity(SlaMiss)
    )
    task_executions = query.all()
    if task_executions is None:
        raise NotFound("Task executions are not found for dag id({}) and dag run id({}).".format(dag_id, dag_run_id))
    total_count = len(task_executions)

    return task_execution_collection_schema.dump(
        TaskExecutionCollection(task_executions=task_executions, total_entries=total_count)
    )


@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG_RUN),
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_TASK_EXECUTION),
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_TASK_INSTANCE),
    ]
)
@provide_session
def list_task_executions_by_task_id(dag_id: str, dag_run_id: str, task_id: str, session=None):
    """List task executions"""
    query = (
        session.query(TE)
        .filter(TE.dag_id == dag_id)
        .join(DR, and_(TE.dag_id == DR.dag_id, TE.execution_date == DR.execution_date))
        .filter(DR.run_id == dag_run_id)
        .filter(TE.task_id == task_id)
        .outerjoin(
            SlaMiss,
            and_(
                SlaMiss.dag_id == TE.dag_id,
                SlaMiss.execution_date == TE.execution_date,
                SlaMiss.task_id == TE.task_id,
            ),
        )
        .add_entity(SlaMiss)
    )
    task_executions = query.all()
    if task_executions is None:
        raise NotFound("Task executions are not found for dag id({}), dag run id({}) and task id({}) ."
                       .format(dag_id, dag_run_id, task_id))
    total_count = len(task_executions)

    return task_execution_collection_schema.dump(
        TaskExecutionCollection(task_executions=task_executions, total_entries=total_count)
    )
