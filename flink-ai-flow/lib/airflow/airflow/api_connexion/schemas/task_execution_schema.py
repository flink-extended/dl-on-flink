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

from typing import List, NamedTuple, Optional, Tuple

from marshmallow import Schema, fields
from marshmallow.utils import get_value

from airflow.api_connexion.parameters import validate_istimezone
from airflow.api_connexion.schemas.enum_schemas import TaskInstanceStateField
from airflow.api_connexion.schemas.sla_miss_schema import SlaMissSchema
from airflow.models import SlaMiss
from airflow.models.taskexecution import TaskExecution


class TaskExecutionSchema(Schema):
    """Task execution schema"""

    task_id = fields.Str()
    dag_id = fields.Str()
    execution_date = fields.DateTime(validate=validate_istimezone)
    seq_num = fields.Int()
    start_date = fields.DateTime(validate=validate_istimezone)
    end_date = fields.DateTime(validate=validate_istimezone)
    duration = fields.Float()
    state = TaskInstanceStateField()
    hostname = fields.Str()
    unixname = fields.Str()
    pool = fields.Str()
    pool_slots = fields.Int()
    queue = fields.Str()
    priority_weight = fields.Int()
    operator = fields.Str()
    queued_dttm = fields.DateTime(data_key="queued_when")
    pid = fields.Int()
    executor_config = fields.Str()
    sla_miss = fields.Nested(SlaMissSchema, default=None)

    def get_attribute(self, obj, attr, default):
        if attr == "sla_miss":
            # Object is a tuple of task_instance and slamiss
            # and the get_value expects a dict with key, value
            # corresponding to the attr.
            slamiss_instance = {"sla_miss": obj[1]}
            return get_value(slamiss_instance, attr, default)
        return get_value(obj[0], attr, default)


class TaskExecutionCollection(NamedTuple):
    """List of task executions with metadata"""

    task_executions: List[Tuple[TaskExecution, Optional[SlaMiss]]]
    total_entries: int


class TaskExecutionCollectionSchema(Schema):
    """Task execution collection schema"""

    task_executions = fields.List(fields.Nested(TaskExecutionSchema))
    total_entries = fields.Int()


task_execution_schema = TaskExecutionSchema()
task_execution_collection_schema = TaskExecutionCollectionSchema()
