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
from airflow.utils.mailbox import Mailbox
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from airflow.events.scheduler_events import PeriodicEvent


def trigger_periodic_task(mailbox, run_id, task_id):
    mailbox.send_message(PeriodicEvent(run_id, task_id).to_event())


class PeriodicManager(object):
    def __init__(self, mailbox: Mailbox):
        self.mailbox = mailbox
        self.sc = BackgroundScheduler()

    def start(self):
        self.sc.start()

    def shutdown(self):
        self.sc.shutdown()

    def _generate_job_id(self, run_id, task_id):
        return '{}:{}'.format(run_id, task_id)

    def add_task(self, run_id, task_id, cron_config):
        self.sc.add_job(id=self._generate_job_id(run_id, task_id),
                        func=trigger_periodic_task, args=(self.mailbox, run_id, task_id),
                        trigger=CronTrigger.from_crontab(cron_config))

    def remove_task(self, run_id, task_id):
        self.sc.remove_job(job_id=self._generate_job_id(run_id, task_id))
