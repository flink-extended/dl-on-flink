
from datetime import timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.utils import timezone
from airflow.utils.dates import days_ago
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
DEFAULT_DATE = timezone.datetime(2020, 1, 1)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': DEFAULT_DATE,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}
dag = DAG(
    dag_id='test_event_based_dag',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
)

t1 = BashOperator(
    task_id='sleep_1000_secs',
    bash_command='sleep 1000',
    dag=dag,
)

t2 = BashOperator(
    task_id='sleep',
    depends_on_past=False,
    bash_command='sleep 5000',
    retries=3,
    dag=dag,
)
dag.doc_md = __doc__


t1 >> [t2]
