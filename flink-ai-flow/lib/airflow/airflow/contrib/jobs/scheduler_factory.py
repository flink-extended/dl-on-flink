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
import logging

from airflow.configuration import conf
from airflow.utils.module_loading import import_string

log = logging.getLogger(__name__)


class SchedulerFactory:

    DEFAULT_SCHEDULER = "SchedulerJob"
    EVENT_BASED_SCHEDULER = "EventBasedSchedulerJob"

    executors = {
        DEFAULT_SCHEDULER: 'airflow.jobs.scheduler_job.SchedulerJob',
        EVENT_BASED_SCHEDULER: 'airflow.contrib.jobs.event_based_scheduler_job.EventBasedSchedulerJob',
    }

    @classmethod
    def get_default_scheduler(cls):
        scheduler_name = cls.get_scheduler_name()
        log.debug("Loading core scheduler: %s", scheduler_name)
        if scheduler_name in cls.executors:
            return import_string(cls.executors[scheduler_name])
        else:
            return import_string(scheduler_name)

    @classmethod
    def get_scheduler_name(cls):
        return conf.get('core', 'scheduler', fallback=cls.DEFAULT_SCHEDULER)
