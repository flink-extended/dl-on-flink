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
from enum import Enum
from typing import Text, List

from ai_flow.graph.edge import Edge
from ai_flow.util.json_utils import Jsonable
from notification_service.base_notification import UNDEFINED_EVENT_TYPE, DEFAULT_NAMESPACE


class ConditionType(str, Enum):
    """
    MEET_ALL: The action will be triggered when and only all the EventConditions are met.
    MEET_ANY: The action will be triggered when any of the EventConditions is met.
    """
    MEET_ALL = "MEET_ALL"
    MEET_ANY = "MEET_ANY"


class JobAction(str, Enum):
    """
    START: Start the job.
    RESTART: If the job is running, stop it first and then start it. If the job is not running,just start it.
    STOP: Stop the job.
    NONE: Do nothing.
    """
    START = "START"
    RESTART = "RESTART"
    STOP = "STOP"
    NONE = "NONE"


class WorkflowAction(str, Enum):
    """
    START: Start a new workflow execution.
    STOP: Stop the workflow execution.
    NONE: Do nothing.
    """
    START = "START"
    STOP = "STOP"
    NONE = "NONE"


class EventLife(str, Enum):
    """
    ONCE: The event value will be used only once.
    REPEATED: The event value will be used repeated.
    """
    ONCE = "ONCE"
    REPEATED = "REPEATED"


class ValueCondition(str, Enum):
    """
    EQUALS: The condition that notification service updates a value which equals to the event value.
    UPDATED: The condition that notification service has a update operation on the event key which event
            value belongs.
    """
    EQUALS = "EQUALS"
    UPDATED = "UPDATE"


class EventMeetConfig(Jsonable):
    def __init__(self,
                 event_key: Text,
                 event_value: Text,
                 event_type: Text = UNDEFINED_EVENT_TYPE,
                 namespace: Text = DEFAULT_NAMESPACE,
                 sender: Text = None,
                 life: EventLife = EventLife.ONCE,
                 value_condition: ValueCondition = ValueCondition.EQUALS
                 ):
        """
        EventMeetConfig defines a set of criteria of the event we are interested in.

        :param event_key: The Key of the event(notification_service.base_notification.BaseEvent).
        :param event_value: The value of the event(notification_service.base_notification.BaseEvent).
        :param namespace: The namespace of the event(notification_service.base_notification.BaseEvent).
        :param event_type: (Optional) Type of the event(notification_service.base_notification.BaseEvent).
        :param sender: The sender of the event(notification_service.base_notification.BaseEvent).
        :param life: ai_flow.workflow.control_edge.EventLife
        :param value_condition: ai_flow.workflow.control_edge.MetValueCondition
        """
        self.event_type = event_type
        self.event_key = event_key
        self.event_value = event_value
        self.life = life
        self.value_condition = value_condition
        self.namespace = namespace
        self.sender = sender

    def __eq__(self, o: object) -> bool:
        if isinstance(o, EventMeetConfig):
            return self.__dict__ == o.__dict__
        else:
            return False

    def __repr__(self):
        return self.__dict__.__repr__()


class EventCondition(Jsonable):
    def __init__(self, events: List[EventMeetConfig], condition_type: ConditionType):
        """
        EventCondition combines a list of EventMeetConfig and a ConditionType to defines when the condition is met
        based on the events we see.

        :param events: A set of EventMeetConfig that the condition interested in.
        :param condition_type: condition_type defines when the condition is met.
        """
        self.events = events
        self.condition_type = condition_type

    def add_event(self,
                  event_key: Text,
                  event_value: Text,
                  event_type: Text = UNDEFINED_EVENT_TYPE,
                  namespace: Text = DEFAULT_NAMESPACE,
                  sender: Text = None,
                  life: EventLife = EventLife.ONCE,
                  value_condition: ValueCondition = ValueCondition.EQUALS):
        event_meet_config = EventMeetConfig(event_key, event_value, event_type,
                                            namespace, sender, life, value_condition)
        if event_meet_config in self.events:
            return self
        self.events.append(event_meet_config)
        return self

    def __eq__(self, o):
        if not isinstance(o, EventCondition):
            return False
        return self.events == o.events and self.condition_type == o.condition_type

    def __repr__(self):
        return self.__dict__.__str__()


class MeetAllEventCondition(EventCondition):
    """
    MeetAllEventCondition is met when all the events are met.
    """

    def __init__(self, events: List[EventMeetConfig] = None):
        if events is None:
            events = []
        super(MeetAllEventCondition, self).__init__(events, ConditionType.MEET_ALL)


class MeetAnyEventCondition(EventCondition):
    """
    MeetAnyEventCondition is met when any event is met.
    """

    def __init__(self, events: List[EventMeetConfig] = None):
        if events is None:
            events = []
        super(MeetAnyEventCondition, self).__init__(events, ConditionType.MEET_ANY)


class JobSchedulingRule(Jsonable):
    def __init__(self, event_condition: EventCondition, action: JobAction):
        """
        A SchedulingRule defines what JobAction to take when the condition is met.
        :param event_condition: A config that defines the condition.
        :param action: The action to take when condition is met.
        """
        self.event_condition = event_condition
        self.action = action

    def __eq__(self, o):
        if not isinstance(o, JobSchedulingRule):
            return False
        return self.event_condition == o.event_condition and self.action == o.action


class WorkflowSchedulingRule(Jsonable):
    def __init__(self, event_condition: EventCondition, action: WorkflowAction):
        """
        A SchedulingRule defines what WorkflowAction to take when the condition is met.
        :param event_condition: A config that defines the condition.
        :param action: The action to take when condition is met.
        """
        self.event_condition = event_condition
        self.action = action

    def __eq__(self, o):
        if not isinstance(o, WorkflowSchedulingRule):
            return False
        return self.event_condition == o.event_condition and self.action == o.action


class ControlEdge(Edge):
    """
    ControlEdge defines event-based dependencies between jobs(ai_flow.workflow.job.Job).
    """

    def __init__(self,
                 destination: Text,
                 scheduling_rule: JobSchedulingRule,
                 ) -> None:
        """
        :param destination: The name of the job which depends on the scheduling rule
        :param scheduling_rule: The scheduling rule of the job
        """
        super().__init__('*', destination)
        self.scheduling_rule = scheduling_rule

    def __eq__(self, o):
        if not isinstance(o, ControlEdge):
            return False
        return self.destination == o.destination and self.source == o.source \
               and self.scheduling_rule == o.scheduling_rule


class AIFlowInternalEventType(object):
    """Per-defined some event types which are generated by ai flow system."""
    JOB_STATUS_CHANGED = "JOB_STATUS_CHANGED"  # Indicates the job(ai_flow.workflow.job.Job) status changed event.
    PERIODIC_ACTION = "PERIODIC_ACTION"  # Indicates the type of event that a job or workflow runs periodically.
    DATASET_CHANGED = "DATASET_CHANGED"  # Indicates the type of dataset changed event.
