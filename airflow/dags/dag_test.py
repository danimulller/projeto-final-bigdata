from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.python import PythonOperator

# Função para listar os buckets usando boto3 através do S3Hook
def list_buckets_minio(**kwargs):
    s3_hook = S3Hook(aws_conn_id='s3_minio')
    # Acessar o cliente boto3
    s3_client = s3_hook.get_conn()
    # Listar os buckets
    buckets = s3_client.list_buckets()
    bucket_names = [bucket['Name'] for bucket in buckets['Buckets']]
    print(f"Buckets disponíveis: {bucket_names}")
    return bucket_names

# Configuração básica da DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 0
}

with DAG(
    dag_id='list_minio_buckets',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    # Operador Python para listar os buckets
    list_buckets_task = PythonOperator(
        task_id='list_buckets',
        python_callable=list_buckets_minio,
    )

    list_buckets_task