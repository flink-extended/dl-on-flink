# -*- coding: utf-8 -*-
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

from builtins import range
from collections import OrderedDict
import copy
# To avoid circular imports
import airflow.utils.dag_processing
from airflow.configuration import conf
from notification_service.client import NotificationClient
from airflow.settings import Stats
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.state import State
from airflow.models.event import TaskStatusEvent, TaskInstanceHelper


PARALLELISM = conf.getint('core', 'PARALLELISM')


class BaseExecutor(LoggingMixin):

    def __init__(self, parallelism=PARALLELISM):
        """
        Class to derive in order to interface with executor-type systems
        like Celery, Mesos, Yarn and the likes.

        :param parallelism: how many jobs should run at one time. Set to
            ``0`` for infinity
        :type parallelism: int
        """
        self.parallelism = parallelism
        self.queued_tasks = OrderedDict()
        self.running = {}
        self.event_buffer = {}
        self.use_nf = False
        self.nf_host = conf.get('scheduler', 'notification_host', fallback='localhost')
        self.nf_port = conf.getint('scheduler', 'notification_port', fallback=50051)
        self.client: NotificationClient = None

    def set_use_nf(self, use_nf):
        self.use_nf = use_nf

    def start(self):  # pragma: no cover
        """
        Executors may need to get things started. For example LocalExecutor
        starts N workers.
        """

    def queue_command(self, simple_task_instance, command, priority=1, queue=None):
        key = simple_task_instance.key
        if key not in self.queued_tasks and key not in self.running:
            self.log.info("Adding to queue: %s", command)
            self.queued_tasks[key] = (command, priority, queue, simple_task_instance)
        else:
            self.log.info("could not queue task %s", key)

    def queue_task_instance(
            self,
            task_instance,
            mark_success=False,
            pickle_id=None,
            ignore_all_deps=False,
            ignore_depends_on_past=False,
            ignore_task_deps=False,
            ignore_ti_state=False,
            pool=None,
            cfg_path=None):
        pool = pool or task_instance.pool

        # TODO (edgarRd): AIRFLOW-1985:
        # cfg_path is needed to propagate the config values if using impersonation
        # (run_as_user), given that there are different code paths running tasks.
        # For a long term solution we need to address AIRFLOW-1986
        command = task_instance.command_as_list(
            local=True,
            mark_success=mark_success,
            ignore_all_deps=ignore_all_deps,
            ignore_depends_on_past=ignore_depends_on_past,
            ignore_task_deps=ignore_task_deps,
            ignore_ti_state=ignore_ti_state,
            pool=pool,
            pickle_id=pickle_id,
            cfg_path=cfg_path)
        self.queue_command(
            airflow.utils.dag_processing.SimpleTaskInstance(task_instance),
            command,
            priority=task_instance.task.priority_weight_total,
            queue=task_instance.task.queue)

    def has_task(self, task_instance):
        """
        Checks if a task is either queued or running in this executor

        :param task_instance: TaskInstance
        :return: True if the task is known to this executor
        """
        if task_instance.key in self.queued_tasks or task_instance.key in self.running:
            return True

    def stop_task(self, task_instance):
        """
        Stop task if a task is either queued or running in this executor

        :param task_instance: TaskInstance
        :return: True if the task is known to this executor
        """
        if task_instance.key in self.queued_tasks:
            self.queued_tasks.pop(task_instance.key())
            self.log.debug("remove task {0} from queue.".format(task_instance.key()))
            return True

        if task_instance.key in self.running:
            self.running.pop(task_instance.key())
            self.log.debug("remove task {0} from running task.".format(task_instance.key()))
            return True

    def sync(self):
        """
        Sync will get called periodically by the heartbeat method.
        Executors should override this to perform gather statuses.
        """

    def heartbeat(self):
        # Triggering new jobs
        if not self.parallelism:
            open_slots = len(self.queued_tasks)
        else:
            open_slots = self.parallelism - len(self.running)

        num_running_tasks = len(self.running)
        num_queued_tasks = len(self.queued_tasks)

        self.log.debug("%s running task instances", num_running_tasks)
        self.log.debug("%s in queue", num_queued_tasks)
        self.log.debug("%s open slots", open_slots)

        Stats.gauge('executor.open_slots', open_slots)
        Stats.gauge('executor.queued_tasks', num_queued_tasks)
        Stats.gauge('executor.running_tasks', num_running_tasks)

        self.trigger_tasks(open_slots)

        # Calling child class sync method
        self.log.debug("Calling the %s sync method", self.__class__)
        self.sync()

    def trigger_tasks(self, open_slots):
        """
        Trigger tasks

        :param open_slots: Number of open slots
        :return:
        """
        sorted_queue = sorted(
            [(k, v) for k, v in self.queued_tasks.items()],
            key=lambda x: x[1][1],
            reverse=True)
        for i in range(min((open_slots, len(self.queued_tasks)))):
            key, (command, _, queue, simple_ti) = sorted_queue.pop(0)
            self.queued_tasks.pop(key)
            self.running[key] = command
            self.execute_async(key=key,
                               command=command,
                               queue=queue,
                               executor_config=simple_ti.executor_config)

    def change_state(self, key, state):
        self.log.debug("Changing state: %s %s", key, state)
        self.running.pop(key, None)
        if self.use_nf:
            if self.client is None:
                self.client: NotificationClient = NotificationClient(
                    server_uri="{0}:{1}".format(self.nf_host,
                                                self.nf_port))
            dag_id, task_id, execution_date, try_number = key
            self.client.send_event(TaskStatusEvent(
                task_instance_key=TaskInstanceHelper.to_task_key(dag_id, task_id, execution_date),
                status=TaskInstanceHelper.to_event_value(state, try_number)))
        else:
            self.event_buffer[key] = state

    def fail(self, key):
        self.change_state(key, State.FAILED)

    def success(self, key):
        self.change_state(key, State.SUCCESS)

    def stop_task(self, ti):
        """
        stop the task, call task on_kill function to do custom action.
        :param ti: TaskInstance
        :return: None
        """
        key = ti.key
        if key in self.queued_tasks:
            self.queued_tasks.pop(key)

        if key in self.running:
            task = ti.task
            task_copy = copy.copy(task)
            task_copy.on_kill()
            self.running.pop(key, None)

    def shutdown(self, ti):
        """
        shutdown the task
        :param ti: the taskinstance
        :return:
        """
        self.stop_task(ti)
        self.change_state(ti.key, State.SHUTDOWN)

    def restart(self, ti, full_filepath, pickle_id=None):
        """
        restart the task
        :param ti: the task instance
        :param full_filepath: the dag full_filepath
        :param pickle_id: the dag pickle_id
        :return:
        """
        self.stop_task(ti)

        from airflow.models.taskinstance import TaskInstance as TI
        simple_task_instance = airflow.utils.dag_processing.SimpleTaskInstance(ti)
        command = TI.generate_command(
            simple_task_instance.dag_id,
            simple_task_instance.task_id,
            simple_task_instance.execution_date,
            local=True,
            mark_success=False,
            ignore_all_deps=False,
            ignore_depends_on_past=False,
            ignore_task_deps=False,
            ignore_ti_state=False,
            pool=simple_task_instance.pool,
            file_path=full_filepath,
            pickle_id=pickle_id)

        priority = simple_task_instance.priority_weight
        queue = simple_task_instance.queue
        self.log.info(
            "Sending %s to executor with priority %s and queue %s",
            simple_task_instance.key, priority, queue
        )
        self.queue_command(
            simple_task_instance,
            command,
            priority=priority,
            queue=queue)

        self.change_state(ti.key, State.SCHEDULED)

    def get_event_buffer(self, dag_ids=None):
        """
        Returns and flush the event buffer. In case dag_ids is specified
        it will only return and flush events for the given dag_ids. Otherwise
        it returns and flushes all

        :param dag_ids: to dag_ids to return events for, if None returns all
        :return: a dict of events
        """
        cleared_events = dict()
        if dag_ids is None:
            cleared_events = self.event_buffer
            self.event_buffer = dict()
        else:
            for key in list(self.event_buffer.keys()):
                dag_id, _, _, _ = key
                if dag_id in dag_ids:
                    cleared_events[key] = self.event_buffer.pop(key)

        return cleared_events

    def execute_async(self,
                      key,
                      command,
                      queue=None,
                      executor_config=None):  # pragma: no cover
        """
        This method will execute the command asynchronously.
        """
        raise NotImplementedError()

    def end(self):  # pragma: no cover
        """
        This method is called when the caller is done submitting job and is
        wants to wait synchronously for the job submitted previously to be
        all done.
        """
        raise NotImplementedError()

    def terminate(self):
        """
        This method is called when the daemon receives a SIGTERM
        """
        raise NotImplementedError()
