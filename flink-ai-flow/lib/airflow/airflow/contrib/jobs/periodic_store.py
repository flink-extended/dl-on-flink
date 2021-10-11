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


from apscheduler.jobstores.base import BaseJobStore, JobLookupError, ConflictingIdError
from apscheduler.util import datetime_to_utc_timestamp, utc_timestamp_to_datetime
from apscheduler.job import Job
from airflow.models.periodic_task_model import PeriodicTaskModel
from airflow.utils.session import create_session

try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle

try:
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.sql.expression import null
except ImportError:  # pragma: nocover
    raise ImportError('SQLAlchemyJobStore requires SQLAlchemy installed')


class PeriodicTaskSQLAlchemyJobStore(BaseJobStore):
    """ The class saves the periodic scheduling information of periodic tasks to database. """
    def __init__(self, pickle_protocol=pickle.HIGHEST_PROTOCOL):
        super(PeriodicTaskSQLAlchemyJobStore, self).__init__()
        self.pickle_protocol = pickle_protocol
        self.session = None

    def set_session(self, session):
        """
        If you set an external session, after calling the interfaces(add_job, update_job, remove_job, remove_all_jobs),
        you need to call session.commit() to update to the database.
        """
        self.session = session

    def unset_session(self):
        self.session = None

    def lookup_job(self, job_id):
        def _internal_lookup_job(job_id, session):
            job_state = session.query(PeriodicTaskModel.job_state).filter(PeriodicTaskModel.id == job_id).scalar()
            return self._reconstitute_job(job_state) if job_state else None

        if self.session is None:
            with create_session() as session:
                return _internal_lookup_job(job_id, session)
        else:
            return _internal_lookup_job(job_id, self.session)

    def get_due_jobs(self, now):
        timestamp = datetime_to_utc_timestamp(now)
        return self._get_jobs(PeriodicTaskModel.next_run_time <= timestamp)

    def get_next_run_time(self):
        def _internal_get_next_run_time(session):
            next_run_time = session.query(PeriodicTaskModel.next_run_time).filter(
                PeriodicTaskModel.next_run_time != null()).order_by(PeriodicTaskModel.next_run_time).limit(1).scalar()
            return utc_timestamp_to_datetime(next_run_time)
        if self.session is None:
            with create_session() as session:
                return _internal_get_next_run_time(session)
        else:
            return _internal_get_next_run_time(self.session)

    def get_all_jobs(self):
        jobs = self._get_jobs()
        self._fix_paused_jobs_sorting(jobs)
        return jobs

    def add_job(self, job):
        r = PeriodicTaskModel()
        r.id = job.id
        r.next_run_time = datetime_to_utc_timestamp(job.next_run_time)
        r.job_state = pickle.dumps(job.__getstate__(), self.pickle_protocol)
        if self.session is None:
            with create_session() as session:
                try:
                    session.add(r)
                    session.commit()
                except IntegrityError:
                    raise ConflictingIdError(job.id)
        else:
            self.session.add(r)

    def update_job(self, job):
        def _internal_update_job(session):
            periodic_task_model = session.query(PeriodicTaskModel).filter(PeriodicTaskModel.id == job.id).first()
            if periodic_task_model is None:
                raise JobLookupError(job.id)
            else:
                periodic_task_model.next_run_time = datetime_to_utc_timestamp(job.next_run_time)
                periodic_task_model.job_state = pickle.dumps(job.__getstate__(), self.pickle_protocol)
                session.merge(periodic_task_model)
        if self.session is None:
            with create_session() as session:
                _internal_update_job(session)
        else:
            _internal_update_job(self.session)

    def remove_job(self, job_id):
        if self.session is None:
            with create_session() as session:
                session.query(PeriodicTaskModel).filter(PeriodicTaskModel.id == job_id).delete()
        else:
            self.session.query(PeriodicTaskModel).filter(PeriodicTaskModel.id == job_id).delete()

    def remove_all_jobs(self):
        if self.session is None:
            with create_session() as session:
                session.query(PeriodicTaskModel).delete()
        else:
            self.session.query(PeriodicTaskModel).delete()

    def _reconstitute_job(self, job_state):
        job_state = pickle.loads(job_state)
        job_state['jobstore'] = self
        job = Job.__new__(Job)
        job.__setstate__(job_state)
        job._scheduler = self._scheduler
        job._jobstore_alias = self._alias
        return job

    def _get_jobs(self, *conditions):
        if self.session is None:
            with create_session() as session:
                return self._internal_get_jobs(conditions, session)
        else:
            return self._internal_get_jobs(conditions, self.session)

    def _internal_get_jobs(self, conditions, session):
        jobs = []
        query = session.query(PeriodicTaskModel) \
            .order_by(PeriodicTaskModel.next_run_time)
        query = query.filter(*conditions) if conditions else query
        selectable_jobs = query.all()
        failed_job_ids = set()
        for job in selectable_jobs:
            try:
                jobs.append(self._reconstitute_job(job.job_state))
            except BaseException as e:
                self._logger.exception('Unable to restore job "%s exception [%s]" -- removing it', job.id, str(e))
                failed_job_ids.add(job.id)
        # Remove all the jobs we failed to restore
        if failed_job_ids:
            session.query(PeriodicTaskModel).filter(PeriodicTaskModel.id.in_(failed_job_ids)).delete()
            session.commit()
        return jobs
