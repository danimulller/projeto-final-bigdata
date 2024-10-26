from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.utils.constants.constants import Parameters
from scripts.extract.extract_posicao import extract_data_from_raw, extract_last_json
from scripts.utils.api import check_bucket
from scripts.transform.transform_posicao import transform_from_raw


def verificar_json_trusted(**kwargs):
    ti = kwargs['ti']
    dict_retorno_raw = ti.xcom_pull(task_ids='consultar_ultimo_arquivo')

    return check_bucket.check_file_bucket(
        dict_retorno_raw['name'],
        dict_retorno_raw['folder'],
        Parameters.BUCKET_DESTINATION
    )

def transformar_json(**kwargs):
    """ Realiza transformações no JSON vindo da war """

    ti = kwargs['ti']
    exists_in_trusted = ti.xcom_pull(task_ids='verificar_arquivo_trusted')

    dict_json_raw = ti.xcom_pull(task_ids='consultar_ultimo_arquivo')

    # Caso o arquivo já exista, retorna
    if exists_in_trusted:
        print(f"File {dict_json_raw['name']} already exists in {dict_json_raw['folder']}! Returning...")
        return True

    return transform_from_raw(dict_json_raw['content'])

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
    schedule_interval=None,  # Executa manualmente
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

    # enviar_arquivo_trusted = PythonOperator(
    #     task_id='enviar_arquivo_trusted',
    #     python_callable=enviar_trusted,
    # )

    consultar_ultimo_arquivo >> verificar_arquivo_trusted >> transformar_arquivo # >> enviar_arquivo_trusted