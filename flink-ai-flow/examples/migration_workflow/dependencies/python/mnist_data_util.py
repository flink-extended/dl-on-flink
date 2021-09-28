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
import os
from datetime import datetime, date, time as d_time, timedelta

import numpy as np
import time
import uuid
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic


class CSVBuffer(object):
    def __init__(self):
        self.buffer = []

    def write(self, v):
        self.buffer.append(v[:-1])

    def close(self):
        pass


class MNISTData(object):
    def __init__(self, mnist_data_file):
        self.mnist_data_file = mnist_data_file
        self.mnist_data = self._load_mnist_data()

    def _load_mnist_data(self):
        return np.load(self.mnist_data_file)

    def x_train(self):
        return self.mnist_data['x_train']

    def x_train_2d(self):
        return self.x_train().reshape(-1, 28 * 28)

    def y_train(self):
        return self.mnist_data['y_train']

    def x_test(self):
        return self.mnist_data['x_test']

    def x_test_2d(self):
        return self.x_test().reshape(-1, 28 * 28)

    def y_test(self):
        return self.mnist_data['y_test']

    def train_data(self):
        return np.c_[self.x_train_2d(), self.y_train()]

    def test_data(self):
        return np.c_[self.x_test_2d(), self.y_test()]


class KafkaUtil(object):
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)

    def create_topic(self, topic):
        self.admin_client.create_topics(
            new_topics=[NewTopic(name=topic, num_partitions=1, replication_factor=1)])

    def delete_topic(self, topic):
        self.admin_client.delete_topics(topics=[topic], timeout_ms=5000)
        print("{} is deleted.".format(topic))

    def list_topics(self):
        return self.admin_client.list_topics()

    def producer_loop(self, file_path, topic, interval=10, days=2):
        producer = KafkaProducer(bootstrap_servers=[self.bootstrap_servers])
        mnist_data = MNISTData(file_path)
        csv_buffer = CSVBuffer()
        np.savetxt(csv_buffer, mnist_data.test_data(), '%d')
        num = 0
        current_datetime = datetime.combine(date.today(), d_time())
        second = timedelta(seconds=1)
        expect_interval_ms = interval / 3600 * 1000
        for hour in range(days * 24):
            idx = np.random.choice(np.arange(len(csv_buffer.buffer)), 3600, replace=False)

            for i in idx:
                expect_time = time.time_ns() // 1000_000 + expect_interval_ms
                sample = '{},{}'.format(csv_buffer.buffer[i], current_datetime.isoformat(' '))
                producer.send(topic, key=bytes(str(uuid.uuid1()), encoding='utf8'),
                              value=bytes(sample, encoding='utf8'))
                current_datetime += second

                sleep_time = (expect_time - time.time_ns() // 1000_000) / 1000
                if sleep_time > 0:
                    time.sleep(sleep_time)
            print("current datetime {}".format(current_datetime))

    def clear_topic(self, topic):
        self.delete_topic(topic)
        time.sleep(3)
        self.create_topic(topic)

    def consumer_print(self, topic, max_num):
        consumer = KafkaConsumer(topic, bootstrap_servers=[self.bootstrap_servers], group_id=str(
            uuid.uuid1()), auto_offset_reset='earliest')
        num = 0
        for message in consumer:
            num += 1
            print(message.value)
            if num > max_num:
                break


if __name__ == '__main__':
    DATASET_URI = os.path.abspath(os.path.join(__file__, "../../../..")) + '/dataset_data/mnist_train.npz'

    k = KafkaUtil('localhost:9092')
    k.producer_loop(DATASET_URI, 'test')



