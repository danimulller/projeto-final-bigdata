from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import S3ListBucketsOperator
from airflow.utils.dates import days_ago

# Defina a DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

with DAG(
    dag_id='list_minio_buckets',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=['minio', 's3'],
) as dag:

    # Tarefa para listar os buckets no MinIO
    list_buckets = S3ListBucketsOperator(
        task_id='list_buckets',
        aws_conn_id='s3_minio',  # Nome da conexão S3 configurada no Airflow
    )

    list_buckets