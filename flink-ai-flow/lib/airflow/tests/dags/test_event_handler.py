import logging
from typing import Tuple

from airflow.executors.scheduling_action import SchedulingAction
from airflow.models.eventhandler import EventHandler
from airflow.utils.state import State
from notification_service.base_notification import BaseEvent


class TaskStatusChangedEventHandler(EventHandler):
    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        logging.info("Handler received event: {}".format(event))
        if event.value == State.RUNNING:
            return SchedulingAction.START, task_state
        else:
            return SchedulingAction.NONE, task_state
