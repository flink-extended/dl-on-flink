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
import json
from abc import abstractmethod
from typing import List, Text, Union, Tuple


class TransactionMessage(object):
    def __init__(self, name: Union[Text, str] = None):
        self.name = name

    def transaction_name(self) -> Text:
        """Return transaction name"""
        return self.name

    @classmethod
    def to_json(cls, message: 'TransactionMessage') -> Text:
        return json.dumps(message.__dict__)

    @classmethod
    def from_json(cls, message: str) -> 'TransactionMessage':
        transaction_message = cls()
        transaction_message.__dict__ = json.loads(message)
        return transaction_message


class WAL(object):
    @abstractmethod
    def begin_transaction(self, transaction_message: TransactionMessage, server_id: str) -> int:
        """
        Start a transaction.
        :param transaction_message:
        :param server_id: The the server's id where the transaction is running.
        :return: transaction id
        """
        pass

    @abstractmethod
    def end_transaction(self, transaction_id: int):
        """
        Stop a transaction.
        :param transaction_id: The transaction id
        """
        pass

    @abstractmethod
    def read_incomplete_transaction_messages(self, server_id: str) -> List[Tuple[str, bool]]:
        """
        Read all records of outstanding transactions
        :param server_id: The the server's id where the transaction is running.
        :return: List[(The transaction message, is_finished)]
        """
        pass
