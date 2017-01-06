from airflow import DAG
from datetime import datetime, timedelta
from operators.emr_spark_operator import EMRSparkOperator
from utils.constants import DS_WEEKLY

default_args = {
        'owner': 'amiyaguchi@mozilla.com',
        'depends_on_past': False,
        'email': ['telemetry-alerts@mozilla.com', 'amiyaguchi@mozilla.com'],
        'email_on_failure': True,
        'email_on_retry': True,
        'retries': 2,
        'retry_delay': timedelta(minutes=30),
        }

dag = DAG('topline_perf', default_args=default_args, schedule_interval=None)

instance_counts = [1]
samples = [3]

for instance_count in instance_counts:
    for sample in samples:
        EMRSparkOperator(
                task_id = (
                    "topline_perf_instances={}_sample={}"
                    .format(instance_count, sample)
                    ),
                job_name = (
                    "Topline performance, instances={}, count={}"
                    .format(instance_count, sample)
                    ),
                execution_timeout = timedelta(hours=8),
                release_label = "emr-5.0.0",
                instance_count = instance_count,
                env = {
                    "report_date": "20161101",
                    "mode": "monthly",
                    "sample": sample
                    },
                uri = (
                    "https://raw.githubusercontent.com/acmiyaguchi/"
                    "telemetry-batch-view/topline-report/"
                    "jobs/topline.sh"
                    ),
                output_visibility = "public",
                dag = dag)
