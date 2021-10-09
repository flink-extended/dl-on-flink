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

"""add_periodic_task_model

Revision ID: cf3cb8473f3c
Revises: c12f471f01f4
Create Date: 2021-10-08 16:05:00.262365

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'cf3cb8473f3c'
down_revision = 'c12f471f01f4'
branch_labels = None
depends_on = None


def upgrade():
    """Apply add_periodic_task_model"""

    op.create_table(
        'periodic_task_model',
        sa.Column('id', sa.String(length=750), nullable=False),
        sa.Column('next_run_time', sa.Float(25), nullable=False),
        sa.Column('job_state', sa.LargeBinary, nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Unapply add_periodic_task_model"""
    op.drop_table('periodic_task_model')

