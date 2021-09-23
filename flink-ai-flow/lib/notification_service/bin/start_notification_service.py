#!/usr/bin/env python
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
import argparse

from notification_service.high_availability import DbHighAvailabilityStorage, SimpleNotificationServerHaManager
from notification_service.master import NotificationMaster
from notification_service.service import NotificationService, HighAvailableNotificationService
from notification_service.event_storage import DbEventStorage


def start_notification_service(port: int = 50052,
                               db_conn: str = None,
                               enable_ha: bool = False,
                               server_uri: str = None,
                               create_table_if_not_exists: bool = True):
    if db_conn:
        storage = DbEventStorage(db_conn, create_table_if_not_exists)
    else:
        raise Exception('Failed to start notification service without database connection info.')

    if enable_ha:
        if not server_uri:
            raise Exception("When HA enabled, server-uri must be set.")
        port = server_uri.split(':')[1]
        ha_storage = DbHighAvailabilityStorage(db_conn=db_conn)
        ha_manager = SimpleNotificationServerHaManager()
        service = HighAvailableNotificationService(
            storage,
            ha_manager,
            server_uri,
            ha_storage,
            5000)
        master = NotificationMaster(service=service,
                                    port=int(port))
    else:
        master = NotificationMaster(service=NotificationService(storage),
                                    port=port)

    master.run(is_block=True)


def _prepare_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=50052,
                        help='The port on which to run notification service，default is 50052. '
                             'It would be ignored when server-uri is set in HA mode.')
    parser.add_argument('--database-conn', type=str, default=None,
                        help='Database connection info')
    parser.add_argument('--enable-ha', type=bool, default=False,
                        help='Whether to start a notification service with HA enabled, default is False')
    parser.add_argument('--server-uri', type=str, default=None,
                        help='Need to be set when HA is enabled. '
                             'It should be the URI of local notification server that can be reached from others')
    return parser.parse_args()


if __name__ == '__main__':

    args = _prepare_args()
    ns_port = args.port
    database_conn = args.database_conn
    enable_ha = args.enable_ha
    server_uri = args.server_uri

    start_notification_service(port=ns_port,
                               db_conn=database_conn,
                               enable_ha=enable_ha,
                               server_uri=server_uri)
