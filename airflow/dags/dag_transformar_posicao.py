from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime

BUCKET = 'raw'
PASTA_RAIZ = 'posicao/'

def consultar_ultimo_json():
    # Inicializa o hook S3 para o MinIO
    s3 = S3Hook(aws_conn_id='s3_minio')
    
    # Lista as pastas de primeiro nível (anos)
    lista_pasta_ano = s3.list_prefixes(bucket_name=BUCKET, prefix=PASTA_RAIZ, delimiter='/')
    lista_ano = [folder.split('/')[-2] for folder in lista_pasta_ano]
    maior_ano = max(lista_ano)

    # Lista as pastas de segundo nível (meses) no maior ano
    lista_pasta_mes = s3.list_prefixes(bucket_name=BUCKET, prefix=f'{PASTA_RAIZ}{maior_ano}/', delimiter='/')
    lista_mes = [folder.split('/')[-2] for folder in lista_pasta_mes]
    maior_mes = max(lista_mes)

    # Lista as pastas de terceiro nível (dias) no maior ano e mês
    lista_pasta_dia = s3.list_prefixes(bucket_name=BUCKET, prefix=f'{PASTA_RAIZ}{maior_ano}/{maior_mes}/', delimiter='/')
    lista_dia = [folder.split('/')[-2] for folder in lista_pasta_dia]
    maior_dia = max(lista_dia)

    # Lista as pastas de quarto nível (horas) no maior ano, mês e menor dia
    lista_pasta_hora = s3.list_prefixes(bucket_name=BUCKET, prefix=f'{PASTA_RAIZ}{maior_ano}/{maior_mes}/{maior_dia}/', delimiter='/')
    lista_hora = [folder.split('/')[-2] for folder in lista_pasta_hora]
    maior_hora = max(lista_hora)

    ultima_pasta = f'{PASTA_RAIZ}{maior_ano}/{maior_mes}/{maior_dia}/{maior_hora}/'

    print(ultima_pasta)

    # Lista os arquivos JSON na última pasta
    lista_arquivos = s3.list_keys(bucket_name=BUCKET, prefix=ultima_pasta, delimiter='/')

    print(lista_arquivos)
    
    return ultima_pasta

# Configurações da DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 0
}

# Definição da DAG
with DAG(
    'dag_transformar_posicao',
    default_args=default_args,
    schedule_interval=None,  # Executa manualmente
    catchup=False,
) as dag:

    fetch_json = PythonOperator(
        task_id='consultar_ultimo_json',
        python_callable=consultar_ultimo_json,
    )

    fetch_json
