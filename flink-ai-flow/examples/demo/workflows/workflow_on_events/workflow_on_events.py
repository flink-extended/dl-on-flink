from typing import Text, Set

import cloudpickle
from notification_service.base_notification import BaseEvent

from ai_flow.api.context_extractor import ContextExtractor, EventContext

import ai_flow as af
from ai_flow_plugins.job_plugins.bash import BashProcessor


class TestContext(EventContext):
    """
    This class indicates that the event should be broadcast.
    """

    def is_broadcast(self) -> bool:
        return True

    def get_contexts(self) -> Set[Text]:
        s = set()
        s.add('hello')
        return s


class TestContextExtractor(ContextExtractor):
    """
    BroadcastAllContextExtractor is the default ContextExtractor to used. It marks all events as broadcast events.
    """

    def extract_context(self, event: BaseEvent) -> EventContext:
        return TestContext()


def main():
    af.init_ai_flow_context()
    with af.job_config('task_1'):
        af.user_define_operation(processor=BashProcessor("echo hello"))
    with af.job_config('task_2'):
        af.user_define_operation(processor=BashProcessor("echo hello"))

    af.action_on_job_status('task_2', 'task_1')

    workflow_name = af.current_workflow_config().workflow_name
    stop_workflow_executions(workflow_name)
    af.set_context_extractor(TestContextExtractor())
    af.workflow_operation.submit_workflow(workflow_name)
    af.workflow_operation.start_new_workflow_execution(workflow_name)

    t = af.get_ai_flow_client().get_workflow_by_name('demo', workflow_name)
    cc = cloudpickle.loads(t.context_extractor_in_bytes)
    print(cc.extract_context(BaseEvent(key='1', value='1')).get_contexts())


def stop_workflow_executions(workflow_name):
    workflow_executions = af.workflow_operation.list_workflow_executions(workflow_name)
    for workflow_execution in workflow_executions:
        af.workflow_operation.stop_workflow_execution(workflow_execution.workflow_execution_id)


if __name__ == '__main__':
    main()
