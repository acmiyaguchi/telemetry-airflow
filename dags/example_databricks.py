import airflow
from airflow import DAG
from airflow.contrib.operators.databricks_operator import DatabricksSubmitRunOperator

default_args = {
    'owner': 'amiyaguchi@mozilla.com',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(2),
    'email': ['amiyaguchi@mozilla.com'],
}

dag = DAG('example_databricks', default_args=default_args, schedule_interval='@daily')

new_cluster = {
    "spark_version": "3.3.x-scala2.11",
    "node_type_id": "c3.2xlarge",
    "aws_attributes": {
        "availability": "ON_DEMAND",
        "instance_profile_arn": "arn:aws:iam::144996185633:instance-profile/databricks-ec2"
    },
    "num_workers": 1
}


# NOTE: The template '{{ task.__class__.private_output_bucket }}' is mapped to
# the environment variable PRIVATE_OUTPUT_BUCKET. `os.environ` can be used to
# access this.
PRIVATE_OUTPUT_BUCKET = "mozilla-databricks-telemetry-test"

mozetl_task = DatabricksSubmitRunOperator(
    task_id='mozetl_task',
    dag=dag,
    json={
        "run_name": "mozetl task",
        "new_cluster": new_cluster,
        "libraries": [{
            "pypi": {
                "package": "git+https://github.com/acmiyaguchi/python_mozetl.git@databricks-poc"
            }
        }],
        "timeout_seconds": 3600,
        "spark_python_task": {
            "python_file": "s3://net-mozaws-prod-us-west-2-pipeline-analysis/amiyaguchi/databricks-poc/mozetl_runner.py",
            "parameters": [
                "example_python",
                "--date", "{{ ds_nodash }}",
                "--sample-id", "42",
                "--bucket", PRIVATE_OUTPUT_BUCKET
            ]
        }
    }
)

tbv_task = DatabricksSubmitRunOperator(
    task_id='tbv_task',
    dag=dag,
    new_cluster=new_cluster,
    spark_jar_task={
        'main_class_name': 'com.mozilla.telemetry.views.ExampleView',
        'parameters': [
            '--date', '{{ ds_nodash }}',
            '--sample_id', '57',
            '--bucket', PRIVATE_OUTPUT_BUCKET
        ]
    },
    libraries=[{
        'jar': 's3://net-mozaws-prod-us-west-2-pipeline-analysis/amiyaguchi/databricks-poc/telemetry-batch-view-1.1.jar'
    }]
)
