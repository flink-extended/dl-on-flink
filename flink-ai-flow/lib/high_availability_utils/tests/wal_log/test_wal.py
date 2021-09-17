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

from high_availability_utils.wal.wal import TransactionMessage


class MyTransactionMessage(TransactionMessage):

    def __init__(self, name=None, message=None):
        super().__init__(name)
        self.message = message


class WALTest(unittest.TestCase):

    def test_transaction_message_to_json(self):
        json_str = TransactionMessage.to_json(MyTransactionMessage(name='a', message='b'))
        result = MyTransactionMessage.from_json(json_str)
        self.assertEqual('a', result.name)
        self.assertEqual('b', result.message)


if __name__ == '__main__':
    unittest.main()
