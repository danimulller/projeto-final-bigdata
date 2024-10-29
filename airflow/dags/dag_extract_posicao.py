from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.utils.constants.constants import Parameters
from scripts.extract.extract_posicao import extract_last_json
from scripts.utils.api import check_bucket
from scripts.transform.transform_posicao import transform_from_raw
from scripts.load.load_posicao import load_file_to_bucket

def verificar_json_trusted(**kwargs) -> bool:
    ti = kwargs['ti']
    dict_json_raw = ti.xcom_pull(task_ids='consultar_ultimo_arquivo')

    return check_bucket.check_file_bucket(
        dict_json_raw['name'] + '.' + dict_json_raw['type'],
        dict_json_raw['folder'],
        Parameters.BUCKET_DESTINATION
    )

def transformar_json(**kwargs) -> dict:
    ti = kwargs['ti']
    dict_json_raw = ti.xcom_pull(task_ids='consultar_ultimo_arquivo')

    # Caso o arquivo já exista, retorna
    if ti.xcom_pull(task_ids='verificar_arquivo_trusted'):
        print(f"File {dict_json_raw['name']}.{dict_json_raw['type']} already exists in {dict_json_raw['folder']}! Returning...")
        return True

    return transform_from_raw(dict_json_raw['content'])

def enviar_trusted(**kwargs) -> bool:
    ti = kwargs['ti']
    dict_json_raw = ti.xcom_pull(task_ids='consultar_ultimo_arquivo')

    if ti.xcom_pull(task_ids='verificar_arquivo_trusted'):
        print(f"File {dict_json_raw['name']}.{dict_json_raw['type']} already exists in {dict_json_raw['folder']}! Returning...")
        return True

    transformed_json = ti.xcom_pull(task_ids='transformar_arquivo')

    dict_json_raw['content'] = transformed_json
    dict_json_raw['type'] = 'parquet'

    print(dict_json_raw)

    return load_file_to_bucket(
        data=dict_json_raw['content'],
        file_name=dict_json_raw['name'] + '.' + dict_json_raw['type'],
        folder=dict_json_raw['folder'],
        file_type=dict_json_raw['type'],
        bucket='trusted'
    )

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 1, 1),
    "retries": 0,
}

# Definição da DAG
with DAG(
    "dag_extract_posicao",
    default_args=default_args,
    # schedule_interval='* * * * *',  # Executa a cada 1 minuto
    schedule_interval=None, # Execução manual
    catchup=False,
) as dag:

    consultar_ultimo_arquivo = PythonOperator(
        task_id='consultar_ultimo_arquivo',
        python_callable=extract_last_json,
        op_args=[Parameters.BUCKET_ORIGIN, Parameters.PREFIX + '/'],
        provide_context=True
    )

    verificar_arquivo_trusted = PythonOperator(
        task_id='verificar_arquivo_trusted',
        python_callable=verificar_json_trusted,
        provide_context=True
    )

    transformar_arquivo = PythonOperator(
        task_id='transformar_arquivo',
        python_callable=transformar_json,
        provide_context=True
    )

    enviar_arquivo_trusted = PythonOperator(
        task_id='enviar_arquivo_trusted',
        python_callable=enviar_trusted,
    )

    consultar_ultimo_arquivo >> verificar_arquivo_trusted >> transformar_arquivo >> enviar_arquivo_trusted