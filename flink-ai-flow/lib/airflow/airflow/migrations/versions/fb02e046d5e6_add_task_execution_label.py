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

"""Add task execution label

Revision ID: fb02e046d5e6
Revises: d47076ca1426
Create Date: 2021-09-02 11:45:12.937665

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'fb02e046d5e6'
down_revision = 'd47076ca1426'
branch_labels = None
depends_on = None


def upgrade():
    """Apply Add task execution label"""
    op.add_column('task_execution', sa.Column('execution_label', sa.Text, nullable=True))


def downgrade():
    """Unapply Add task execution label"""
    op.drop_column('task_execution', 'execution_label')
