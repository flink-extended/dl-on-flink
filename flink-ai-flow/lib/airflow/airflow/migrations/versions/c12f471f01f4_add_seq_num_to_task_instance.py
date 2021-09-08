#
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

"""add seq_num to task_instance

Revision ID: c12f471f01f4
Revises: d47076ca1426
Create Date: 2021-09-08 14:36:44.693163

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
from sqlalchemy.engine.reflection import Inspector
# revision identifiers, used by Alembic.
revision = 'c12f471f01f4'
down_revision = 'd47076ca1426'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()  # pylint: disable=no-member
    is_sqlite = bool(conn.dialect.name == "sqlite")

    if is_sqlite:
        op.execute("PRAGMA foreign_keys=off")

    with op.batch_alter_table('task_instance', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('seq_num', sa.Integer(), nullable=True))

    with op.batch_alter_table('task_execution', schema=None) as batch_op:
        batch_op.add_column(sa.Column('try_number', sa.Integer(), nullable=True))


def downgrade():
    """Unapply add seq_num to task_instance"""
    with op.batch_alter_table('task_instance', schema=None) as batch_op:
        batch_op.drop_column('is_active')
        batch_op.drop_column('seq_num')

    """Unapply add try_number to task_execution"""
    with op.batch_alter_table('task_execution', schema=None) as batch_op:
        batch_op.drop_column('try_number')
