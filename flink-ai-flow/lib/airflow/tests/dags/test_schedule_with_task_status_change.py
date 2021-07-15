from datetime import datetime

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from tests.dags.test_event_handler import TaskStatusChangedEventHandler

default_args = {
    'schedule_interval': '@once',
    'start_date': datetime.utcnow()
}

dag = DAG(dag_id='schedule_on_state', default_args=default_args)

op_0 = BashOperator(task_id='task_1', dag=dag, bash_command="echo hello")

op_1 = BashOperator(task_id='task_2', dag=dag, bash_command="echo hello")
op_1.subscribe_event('schedule_on_state.task_1', 'TASK_STATUS_CHANGED', 'schedule_on_state', 'task_1')
op_1.set_events_handler(TaskStatusChangedEventHandler())
