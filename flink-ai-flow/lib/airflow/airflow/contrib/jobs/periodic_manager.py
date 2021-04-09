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
from apscheduler.triggers.interval import IntervalTrigger
from airflow.events.scheduler_events import PeriodicEvent
from airflow.utils.log.logging_mixin import LoggingMixin


def trigger_periodic_task(mailbox, run_id, task_id):
    mailbox.send_message(PeriodicEvent(run_id, task_id).to_event())


class PeriodicManager(LoggingMixin):
    def __init__(self, mailbox: Mailbox):
        super().__init__()
        self.mailbox = mailbox
        self.sc = BackgroundScheduler()

    def start(self):
        self.sc.start()

    def shutdown(self):
        self.sc.shutdown()

    def _generate_job_id(self, run_id, task_id):
        return '{}:{}'.format(run_id, task_id)

    def add_task(self, run_id, task_id, periodic_config):
        if 'cron' in periodic_config:
            self.sc.add_job(id=self._generate_job_id(run_id, task_id),
                            func=trigger_periodic_task, args=(self.mailbox, run_id, task_id),
                            trigger=CronTrigger.from_crontab(periodic_config['cron']))
        elif 'interval' in periodic_config:
            interval_config: dict = periodic_config['interval']
            if 'seconds' in interval_config:
                seconds = interval_config['seconds']
            else:
                seconds = 0
            
            if 'minutes' in interval_config:
                minutes = interval_config['minutes']
            else:
                minutes = 0
            
            if 'hours' in interval_config:
                hours = interval_config['hours']
            else:
                hours = 0
                
            if 'days' in interval_config:
                days = interval_config['days']
            else:
                days = 0
            
            if 'weeks' in interval_config:
                weeks = interval_config['weeks']
            else:
                weeks = 0
            
            if seconds < 10 and 0 >= minutes and 0 >= hours and 0 >= days and 0 >= weeks:
                self.log.error('Interval mast greater than 20 seconds')
                return 
            self.sc.add_job(id=self._generate_job_id(run_id, task_id),
                            func=trigger_periodic_task, args=(self.mailbox, run_id, task_id),
                            trigger=IntervalTrigger(seconds=seconds, 
                                                    minutes=minutes, 
                                                    hours=hours, 
                                                    days=days, 
                                                    weeks=weeks))
        else:
            self.log.error('Periodic support type cron or interval. current periodic config {}'.format(periodic_config))

    def remove_task(self, run_id, task_id):
        self.sc.remove_job(job_id=self._generate_job_id(run_id, task_id))
