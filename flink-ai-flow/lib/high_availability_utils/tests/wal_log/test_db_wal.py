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
#
import unittest

from high_availability_utils.wal.db_init import set_ha_db_base
from tests.wal_log.db_util import create_session, set_sql_alchemy_conn, prepare_db, get_engine, Base, provide_session

set_ha_db_base(Base)
from high_availability_utils.wal import TransactionMessage
from high_availability_utils.wal.db_wal import DbWAL, WALModel


def create_table(db_conn=None):
    if db_conn is not None:
        set_sql_alchemy_conn(db_conn)
    prepare_db()
    if not get_engine().dialect.has_table(get_engine(), WALModel.__tablename__):
        Base.metadata.create_all(get_engine())


@provide_session
def cleanup(session=None):
    session.query(WALModel).delete()
    session.commit()


class MyTransactionMessage(TransactionMessage):

    def __init__(self, name=None, message=None):
        super().__init__(name)
        self.message = message


class DbWALTest(unittest.TestCase):

    def setUp(self) -> None:
        create_table()

    def tearDown(self) -> None:
        cleanup()

    def test_begin_end_transaction(self):
        with create_session() as session:
            wal_log = DbWAL(session=session)
            transaction_id = wal_log.begin_transaction(transaction_message=
                                                       MyTransactionMessage(name='a', message='b'), server_id='1')
            wal_log_records = session.query(WALModel).all()
            self.assertEqual(1, len(wal_log_records))
            self.assertEqual(False, wal_log_records[0].finished)
            wal_log.end_transaction(transaction_id=transaction_id)
            self.assertEqual(True, wal_log_records[0].finished)

    def test_read_incomplete_transaction_messages_1(self):
        with create_session() as session:
            wal_log = DbWAL(session=session)
            transaction_id = wal_log.begin_transaction(transaction_message=
                                                       MyTransactionMessage(name='a', message='a1'), server_id='1')
            wal_log.end_transaction(transaction_id)
            transaction_id = wal_log.begin_transaction(transaction_message=
                                                       MyTransactionMessage(name='b', message='b1'), server_id='1')
            transaction_id = wal_log.begin_transaction(transaction_message=
                                                       MyTransactionMessage(name='c', message='c1'), server_id='1')
            logs = wal_log.read_incomplete_transaction_messages(server_id='1')
            self.assertEqual(2, len(logs))

            message_1 = MyTransactionMessage.from_json(logs[0][0])
            self.assertEqual('b', message_1.name)
            self.assertEqual('b1', message_1.message)
            self.assertFalse(logs[0][1])

            message_2 = MyTransactionMessage.from_json(logs[1][0])
            self.assertEqual('c', message_2.name)
            self.assertEqual('c1', message_2.message)
            self.assertFalse(logs[1][1])

    def test_read_incomplete_transaction_messages_2(self):
        with create_session() as session:
            wal_log = DbWAL(session=session)
            transaction_id = wal_log.begin_transaction(transaction_message=
                                                       MyTransactionMessage(name='a', message='a1'), server_id='1')
            transaction_id = wal_log.begin_transaction(transaction_message=
                                                       MyTransactionMessage(name='b', message='b1'), server_id='1')
            wal_log.end_transaction(transaction_id)
            transaction_id = wal_log.begin_transaction(transaction_message=
                                                       MyTransactionMessage(name='c', message='c1'), server_id='1')
            logs = wal_log.read_incomplete_transaction_messages(server_id='1')
            self.assertEqual(3, len(logs))

            message_1 = MyTransactionMessage.from_json(logs[0][0])
            self.assertEqual('a', message_1.name)
            self.assertEqual('a1', message_1.message)
            self.assertFalse(logs[0][1])

            message_2 = MyTransactionMessage.from_json(logs[1][0])
            self.assertEqual('b', message_2.name)
            self.assertEqual('b1', message_2.message)
            self.assertTrue(logs[1][1])

            message_3 = MyTransactionMessage.from_json(logs[2][0])
            self.assertEqual('c', message_3.name)
            self.assertEqual('c1', message_3.message)
            self.assertFalse(logs[2][1])


if __name__ == '__main__':
    unittest.main()
