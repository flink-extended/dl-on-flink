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
import pika


def connect(uri):
    connection = pika.BlockingConnection(pika.ConnectionParameters(uri))
    return connection


def create_channel(conn: pika.BaseConnection, channel_num=None):
    return conn.channel(channel_number=channel_num)


def declare(channel, queue):
    channel.queue_declare(queue=queue)


def close(connection):
    connection.close()


def send_message(channel, routing_key,  message):
    channel.basic_publish(exchange='',
                          routing_key=routing_key,
                          body=message)


def receive_message(channel, queue)->bytes:
    c = channel.basic_get(queue=queue)
    channel.basic_ack(delivery_tag=c[0].delivery_tag)
    return c[2]
