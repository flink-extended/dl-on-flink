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
from datetime import datetime
from typing import Dict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from airflow.contrib.jobs.periodic_store import PeriodicTaskSQLAlchemyJobStore
from airflow.events.scheduler_events import PeriodicEvent
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.mailbox import Mailbox

_mailbox: Mailbox = None


def set_global_mailbox(mailbox):
    global _mailbox
    _mailbox = mailbox


def trigger_periodic_task(dag_id, execution_date, task_id):
    global _mailbox
    _mailbox.send_message(PeriodicEvent(dag_id, execution_date, task_id).to_event())


class PeriodicManager(LoggingMixin):
    """
    Support cron and interval config
    cron: second minute hour day month day_of_week option(year)
    interval: weeks,days,hours,minutes,seconds
    """

    def __init__(self, mailbox: Mailbox):
        super().__init__()
        self.mailbox = mailbox
        set_global_mailbox(mailbox)
        self.store = PeriodicTaskSQLAlchemyJobStore()
        jobstores = {
            'default': self.store
        }
        self.sc = BackgroundScheduler(jobstores=jobstores)

    def start(self):
        self.sc.start()

    def shutdown(self):
        self.sc.shutdown()

    def _generate_job_id(self, dag_id, execution_date, task_id):
        return '{}:{}:{}'.format(dag_id, execution_date, task_id)

    def add_task(self,
                 dag_id: str,
                 execution_date: datetime,
                 task_id: str,
                 periodic_config: Dict):
        if 'cron' in periodic_config:
            def build_cron_trigger(expr, time_zone) -> CronTrigger:
                cron_items = expr.split()
                if len(cron_items) == 7:
                    return CronTrigger(second=cron_items[0],
                                       minute=cron_items[1],
                                       hour=cron_items[2],
                                       day=cron_items[3],
                                       month=cron_items[4],
                                       day_of_week=cron_items[5],
                                       year=cron_items[6],
                                       timezone=time_zone)
                elif len(cron_items) == 6:
                    return CronTrigger(second=cron_items[0],
                                       minute=cron_items[1],
                                       hour=cron_items[2],
                                       day=cron_items[3],
                                       month=cron_items[4],
                                       day_of_week=cron_items[5],
                                       timezone=time_zone)
                else:
                    raise ValueError('The cron expression {} is incorrect format, follow the pattern: '
                                     'second minute hour day month day_of_week optional(year).'.format(expr))

            self.sc.add_job(id=self._generate_job_id(dag_id, execution_date, task_id),
                            func=trigger_periodic_task, args=(dag_id, execution_date, task_id),
                            trigger=build_cron_trigger(periodic_config['cron'], periodic_config[
                                'timezone'] if 'timezone' in periodic_config else None))
        elif 'interval' in periodic_config:
            interval_expr: str = periodic_config['interval']
            interval_items = interval_expr.split(',')
            if len(interval_items) != 5:
                raise ValueError('The interval expression {} is incorrect format, follow the pattern: '
                                 'weeks,days,hours,minutes,seconds.'.format(interval_expr))
            temp_list = []
            is_zero = True
            for item in interval_items:
                if item is None or '' == item.strip():
                    v = 0
                else:
                    v = int(item.strip())
                if v < 0:
                    raise Exception('The item of interval expression must be greater than or equal to 0.')
                if v > 0:
                    is_zero = False
                temp_list.append(v)
            if is_zero:
                raise Exception('The interval config must be greater than 0.')

            self.sc.add_job(id=self._generate_job_id(dag_id, execution_date, task_id),
                            func=trigger_periodic_task, args=(dag_id, execution_date, task_id),
                            trigger=IntervalTrigger(seconds=temp_list[4],
                                                    minutes=temp_list[3],
                                                    hours=temp_list[2],
                                                    days=temp_list[1],
                                                    weeks=temp_list[0]))
        else:
            self.log.error('Periodic support type cron or interval. current periodic config {}'.format(periodic_config))

    def remove_task(self,
                    dag_id: str,
                    execution_date: datetime,
                    task_id: str):
        job_id = self._generate_job_id(dag_id, execution_date, task_id)
        job = self.sc.get_job(job_id)
        if job is not None:
            self.sc.remove_job(job_id=job_id)
