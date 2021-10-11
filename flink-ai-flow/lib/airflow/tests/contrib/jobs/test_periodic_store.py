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
import datetime as dt
import pytz
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from airflow.models.periodic_task_model import PeriodicTaskModel
from airflow.contrib.jobs.periodic_store import PeriodicTaskSQLAlchemyJobStore
from airflow.utils.session import create_session
from tests.test_utils import db

run_num = 0


def func(a, b):
    global run_num
    print(a, b)
    run_num += 1


class TestPeriodicStore(unittest.TestCase):
    def setUp(self) -> None:
        db.clear_db_periodic_task_model()
        self.store = PeriodicTaskSQLAlchemyJobStore()
        self.jobstores = {
            'default': self.store
        }
        self.sc = BackgroundScheduler(jobstores=self.jobstores)
        self.sc.start()

    def tearDown(self) -> None:
        self.sc.shutdown()

    def test_add_job(self):
        self.sc.add_job(func=func, kwargs={'a': 'a', 'b': 'b'}, id='1',
                        trigger=DateTrigger(run_date=dt.datetime.utcnow() + dt.timedelta(seconds=2),
                                            timezone=pytz.timezone('UTC')))
        self.sc.add_job(func=func, kwargs={'a': 'a', 'b': 'b'}, id='2',
                        trigger=DateTrigger(run_date=dt.datetime.utcnow() + dt.timedelta(seconds=60),
                                            timezone=pytz.timezone('UTC')))
        with create_session() as session:
            task_models = session.query(PeriodicTaskModel).all()
            self.assertEqual(2, len(self.sc.get_jobs()))
            self.assertEqual(2, len(task_models))
            time.sleep(3)
            self.assertEqual(1, len(self.sc.get_jobs()))
            task_models = session.query(PeriodicTaskModel).all()
            self.assertEqual(1, len(task_models))

    def test_add_interval_job(self):
        self.sc.add_job(func=func, kwargs={'a': 'a', 'b': 'b'}, id='1',
                        trigger=IntervalTrigger(seconds=5))
        with create_session() as session:
            task_models = session.query(PeriodicTaskModel).all()
            self.assertEqual(1, len(self.sc.get_jobs()))
            self.assertEqual(1, len(task_models))
            time.sleep(6)
            self.assertEqual(1, len(self.sc.get_jobs()))
            task_models = session.query(PeriodicTaskModel).all()
            self.assertEqual(1, len(task_models))

    def test_operate_job(self):
        for i in range(1, 4):
            self.sc.add_job(func=func, kwargs={'a': 'a', 'b': 'b'}, id=str(i),
                            trigger=DateTrigger(run_date=dt.datetime.utcnow() + dt.timedelta(seconds=30*i),
                                                timezone=pytz.timezone('UTC')))

        with create_session() as session:
            self.assertEqual(3, len(self.sc.get_jobs()))
            task_models = session.query(PeriodicTaskModel).all()
            self.assertEqual(3, len(task_models))
            self.assertEqual('1', self.sc.get_job(job_id='1').id)
            self.sc.remove_job('1')
            self.assertEqual(2, len(self.sc.get_jobs()))
            task_models = session.query(PeriodicTaskModel).all()
            self.assertEqual(2, len(task_models))
            self.sc.remove_all_jobs()
            self.assertEqual(0, len(self.sc.get_jobs()))
            task_models = session.query(PeriodicTaskModel).all()
            self.assertEqual(0, len(task_models))

    def test_query_none_job(self):
        job = self.sc.get_job('1')
        self.assertIsNone(job)

    def test_query_job_from_store(self):
        for i in range(1, 4):
            self.sc.add_job(func=func, kwargs={'a': 'a', 'b': 'b'}, id=str(i),
                            trigger=DateTrigger(run_date=dt.datetime.utcnow() + dt.timedelta(seconds=5*i),
                                                timezone=pytz.timezone('UTC')))

        self.assertEqual(3, len(self.store.get_all_jobs()))
        time.sleep(6)
        self.assertEqual(2, len(self.store.get_all_jobs()))
        self.store.remove_job('2')
        self.assertEqual(1, len(self.store.get_all_jobs()))
        self.store.remove_all_jobs()
        self.assertEqual(0, len(self.store.get_all_jobs()))

    def test_restart_scheduler_job(self):
        global run_num
        for i in range(0, 2):
            self.sc.add_job(func=func, kwargs={'a': 'a', 'b': 'b'}, id=str(i),
                            trigger=DateTrigger(run_date=dt.datetime.utcnow() + dt.timedelta(seconds=5*i+2),
                                                timezone=pytz.timezone('UTC')))
        self.assertEqual(2, len(self.sc.get_jobs()))
        time.sleep(2)
        self.assertEqual(1, len(self.sc.get_jobs()))
        self.sc.shutdown()
        self.assertEqual(1, run_num)
        self.sc = BackgroundScheduler(jobstores=self.jobstores)
        self.sc.start()
        self.assertEqual(1, len(self.sc.get_jobs()))
        time.sleep(7)
        self.assertEqual(0, len(self.sc.get_jobs()))
        self.assertEqual(2, run_num)


if __name__ == '__main__':
    unittest.main()
