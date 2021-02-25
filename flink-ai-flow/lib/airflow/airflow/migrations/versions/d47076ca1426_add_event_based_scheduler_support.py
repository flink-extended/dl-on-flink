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

"""Add event_based_scheduler tables

Revision ID: d47076ca1426
Revises: 98271e7606e2
Create Date: 2020-12-29 16:00:00.

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd47076ca1426'
down_revision = '98271e7606e2'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()  # pylint: disable=no-member
    is_mysql = bool(conn.dialect.name == "mysql")
    is_sqlite = bool(conn.dialect.name == "sqlite")
    datetime = sa.DATETIME() if not is_mysql else mysql.DATETIME(fsp=6)

    if is_sqlite:
        op.execute("PRAGMA foreign_keys=off")

    """Apply Add event_relationships Column to dag table"""
    with op.batch_alter_table('serialized_dag', schema=None) as batch_op:
        batch_op.add_column(sa.Column('event_relationships', sa.String(10240), nullable=True))

    """Apply Add scheduling_job_id,event_ack_id Column to dag_run table"""
    with op.batch_alter_table('dag_run', schema=None) as batch_op:
        batch_op.add_column(sa.Column('scheduling_job_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('event_ack_id', sa.BigInteger(), nullable=True))

    """Add task_state table"""
    op.create_table(
        'task_state',
        sa.Column('task_id', sa.String(length=250), nullable=False),
        sa.Column('dag_id', sa.String(length=250), nullable=False),
        sa.Column('execution_date', datetime, nullable=False),
        sa.Column('state', sa.PickleType(), nullable=True),
        sa.PrimaryKeyConstraint('task_id', 'dag_id', 'execution_date')
    )

    """Add task_execution table"""
    op.create_table(
        'task_execution',
        sa.Column('task_id', sa.String(length=250), nullable=False),
        sa.Column('dag_id', sa.String(length=250), nullable=False),
        sa.Column('execution_date', datetime, nullable=False),
        sa.Column('seq_num', sa.Integer(), nullable=False),
        sa.Column('start_date', datetime, nullable=True),
        sa.Column('end_date', datetime, nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('state', sa.String(length=20), nullable=True),
        sa.Column('hostname', sa.String(length=1000), nullable=True),
        sa.Column('unixname', sa.String(length=1000), nullable=True),
        sa.Column('job_id', sa.Integer(), nullable=True),
        sa.Column('pool', sa.String(length=50), nullable=True),
        sa.Column('pool_slots', sa.Integer(), default=1),
        sa.Column('queue', sa.String(length=256), nullable=True),
        sa.Column('priority_weight', sa.Integer(), nullable=True),
        sa.Column('operator', sa.String(length=1000), nullable=True),
        sa.Column('queued_dttm', datetime, nullable=True),
        sa.Column('queued_by_job_id', sa.Integer(), nullable=True),
        sa.Column('pid', sa.Integer(), nullable=True),
        sa.Column('executor_config', sa.PickleType(), nullable=True),
        sa.PrimaryKeyConstraint('task_id', 'dag_id', 'execution_date', 'seq_num')
    )


def downgrade():
    conn = op.get_bind()  # pylint: disable=no-member
    is_sqlite = bool(conn.dialect.name == "sqlite")

    if is_sqlite:
        op.execute("PRAGMA foreign_keys=off")

    with op.batch_alter_table('serialized_dag', schema=None) as batch_op:
        batch_op.drop_column('event_relationships')

    with op.batch_alter_table('dag_run', schema=None) as batch_op:
        batch_op.drop_column('scheduling_job_id')
        batch_op.drop_column('event_ack_id')

    op.drop_table('task_state')
    op.drop_table('task_execution')
