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
#

import os
import sys
import time
import uuid

import yaml
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic


class CensusKafkaUtil(object):
    def __init__(self):
        super().__init__()
        self._yaml_config = None
        with open(os.path.dirname(os.path.abspath(__file__)) + '/kafka_config.yaml', 'r') as yaml_file:
            self._yaml_config = yaml.load(yaml_file)
        self.bootstrap_servers = self._yaml_config.get('bootstrap_servers')
        self.census_input_preprocess_topic = self._yaml_config.get('census_input_preprocess_topic')
        self.census_train_input_topic = self._yaml_config.get('census_train_input_topic')
        self.census_predict_input_topic = self._yaml_config.get('census_predict_input_topic')
        self.census_predict_output_topic = self._yaml_config.get('census_predict_output_topic')
        self.admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)

    def _send_data_loop(self, count=None):
        raw_data = []
        with open(file=self._yaml_config.get('dataset_uri'), mode='r') as f:
            for line in f.readlines():
                raw_data.append(line[:-1])
        producer = KafkaProducer(bootstrap_servers=[self.bootstrap_servers])
        num = 0
        if count is None:
            count = sys.maxsize
        while num < count:
            for line in raw_data:
                num += 1
                producer.send(self.census_input_preprocess_topic,
                              key=bytes(str(uuid.uuid1()), encoding='utf8'),
                              value=bytes(line, encoding='utf8'))
                if num > count:
                    break
                if 0 == num % 1000:
                    print("send data {}".format(num))
                    time.sleep(self._yaml_config.get('time_interval') / 500)

    def _clean_create(self, new_topic, topics):
        if new_topic in topics:
            self.admin_client.delete_topics(topics=[new_topic], timeout_ms=5000)
            print("{} is deleted.".format(new_topic))
            time.sleep(5)
        self.admin_client.create_topics(
            new_topics=[NewTopic(name=new_topic, num_partitions=1, replication_factor=1)])

    def create_topic(self):
        topics = self.admin_client.list_topics()
        print(topics)
        self._clean_create(self.census_input_preprocess_topic, topics)
        self._clean_create(self.census_train_input_topic, topics)
        self._clean_create(self.census_predict_input_topic, topics)
        self._clean_create(self.census_predict_output_topic, topics)

        # self._send_data_loop(count)

    def read_input_data(self, count):
        self.read_data(self.census_train_input_topic, count)

    def read_output_data(self, count):
        self.read_data(self.census_predict_output_topic, count)

    def read_data(self, topic, count=None):
        consumer = KafkaConsumer(topic, bootstrap_servers=[self.bootstrap_servers], group_id=str(
            uuid.uuid1()), auto_offset_reset='earliest')
        num = 0
        if count is None:
            count = sys.maxsize
        for message in consumer:
            num += 1
            print(message.value)
            if num > count:
                break

    def read_data_into_file(self, topic, filepath, count=None):
        consumer = KafkaConsumer(topic, bootstrap_servers=[self.bootstrap_servers], group_id=str(
            uuid.uuid1()), auto_offset_reset='earliest')
        num = 0
        if count is None:
            count = sys.maxsize
        with open(filepath, "wb") as f:
            for message in consumer:
                num += 1
                f.write(message.value)
                if num >= count:
                    break

    def delete_topic(self):
        topics = self.admin_client.list_topics()
        print(topics)
        for topic in topics:
            if str(topic).startswith("census"):
                self.admin_client.delete_topics(topics=[topic], timeout_ms=5000)
                print("{} is deleted.".format(topic))
                time.sleep(5)
        topics = self.admin_client.list_topics()
        print(topics)


if __name__ == '__main__':
    kafka_util = CensusKafkaUtil()
    # Clear and init kafka topics
    # kafka_util.create_topic()
    topics = kafka_util.admin_client.list_topics()
    print(topics)
    # kafka_util.read_data_into_file(kafka_util.census_train_input_topic, '/tmp/tmpread', 200)
    # kafka_util.delete_topic()
    # Create continuous data stream
    kafka_util._send_data_loop(200000000)

    # kafka_util.read_data(100)
    # kafka_util.create_topic()
    # kafka_util._send_data_loop(20000)
    # kafka_util.read_input_data(100)
    # kafka_util.read_output_data(100)
