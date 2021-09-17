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
from typing import List, Tuple

from sqlalchemy import Column, String, BigInteger, Text, Integer, Boolean
from sqlalchemy import func

from high_availability_utils.wal.db_init import Base
from high_availability_utils.wal.wal import TransactionMessage, WAL


class WALModel(Base):
    """
    Before import the WALLogModel class, the user should call
    the set_ha_db_base function(module: high_availability_utils.wal.db_init) to set the Base class.
    Example:
        from sqlalchemy.ext.declarative import declarative_base
        Base = declarative_base()
        set_ha_db_base(Base)
        from high_availability_utils.wal.db_wal import WALLogModel
    """
    __tablename__ = "wal"
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    server_id = Column(String(1024), nullable=False)
    message = Column(Text())
    finished = Column(Boolean)

    def __init__(self, server_id: str, message: str):
        self.server_id = server_id
        self.message = message
        self.finished = False

    def __repr__(self) -> str:
        return str(self.__dict__)


class DbWAL(WAL):
    def __init__(self, session) -> None:
        super().__init__()
        self.session = session

    def begin_transaction(self, transaction_message: TransactionMessage, server_id: str) -> int:
        message = TransactionMessage.to_json(transaction_message)
        wal_log_model = WALModel(server_id=server_id, message=message)
        self.session.add(wal_log_model)
        self.session.commit()
        return wal_log_model.id

    def end_transaction(self, transaction_id: int):
        wal_log_model = self.session.query(WALModel).filter(WALModel.id == transaction_id).first()
        if wal_log_model is None:
            raise Exception('Can not find transaction with transaction_id: {}'.format(transaction_id))
        else:
            wal_log_model.finished = True
            self.session.merge(wal_log_model)
            self.session.commit()

    def read_incomplete_transaction_messages(self, server_id: str) -> List[Tuple[str, bool]]:
        min_id = self.session.query(func.min(WALModel.id)).filter(
            WALModel.server_id == server_id,
            WALModel.finished == False).scalar()
        records = self.session.query(WALModel.message, WALModel.finished).filter(
            WALModel.server_id == server_id,
            WALModel.id >= min_id).order_by(WALModel.id).all()
        return records
