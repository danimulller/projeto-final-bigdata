import json
from aiohttp import ClientError
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime
import boto3

BUCKET_RAW = 'raw'
BUCKET_TRUSTED = 'trusted'
PASTA_RAIZ = 'posicao/'

# Cria uma sessão do boto3
session = boto3.session.Session()
s3_client = session.client(
    service_name='s3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='datalake',
    aws_secret_access_key='datalake'
)

def consultar_ultimo_json():
    """ Consulta o último JSON inserido no bucket raw """

    # Inicializa o hook S3 para o MinIO
    s3 = S3Hook(aws_conn_id='s3_minio')
    
    # Lista as pastas de primeiro nível (anos)
    lista_pasta_ano = s3.list_prefixes(bucket_name=BUCKET_RAW, prefix=PASTA_RAIZ, delimiter='/')
    lista_ano = [folder.split('/')[-2].replace('ano=', '') for folder in lista_pasta_ano]

    maior_ano = max(lista_ano)

    # Lista as pastas de segundo nível (meses) no maior ano
    lista_pasta_mes = s3.list_prefixes(bucket_name=BUCKET_RAW, prefix=f'{PASTA_RAIZ}ano={maior_ano}/', delimiter='/')
    lista_mes = [folder.split('/')[-2].replace('mes=', '') for folder in lista_pasta_mes]

    maior_mes = max(lista_mes)

    # Lista as pastas de terceiro nível (dias) no maior ano e mês
    lista_pasta_dia = s3.list_prefixes(bucket_name=BUCKET_RAW, prefix=f'{PASTA_RAIZ}ano={maior_ano}/mes={maior_mes}/', delimiter='/')
    lista_dia = [folder.split('/')[-2].replace('dia=', '') for folder in lista_pasta_dia]
    maior_dia = max(lista_dia)

    # Lista as pastas de quarto nível (horas) no maior ano, mês e menor dia
    lista_pasta_hora = s3.list_prefixes(bucket_name=BUCKET_RAW, prefix=f'{PASTA_RAIZ}ano={maior_ano}/mes={maior_mes}/dia={maior_dia}/', delimiter='/')
    lista_hora = [folder.split('/')[-2].replace('hora=', '') for folder in lista_pasta_hora]
    maior_hora = max(lista_hora)

    ultima_pasta = f'{PASTA_RAIZ}ano={maior_ano}/mes={maior_mes}/dia={maior_dia}/hora={maior_hora}/'

    # Lista os arquivos JSON na última pasta
    lista_arquivos = s3.list_keys(bucket_name=BUCKET_RAW, prefix=ultima_pasta, delimiter='/')

    # Filtra apenas arquivos JSON
    lista_arquivos_json = [arquivo for arquivo in lista_arquivos if arquivo.endswith('.json')]

    # Inicializa variáveis para o arquivo mais recente
    ultimo_arquivo_json = None
    ultima_data_modificacao = None

    # Percorre os arquivos JSON para determinar qual é o mais recente
    for arquivo in lista_arquivos_json:
        # Obtemos os metadados do arquivo usando o cliente boto3
        response = s3_client.head_object(Bucket=BUCKET_RAW, Key=arquivo)

        # A data de modificação do arquivo é acessível por response['LastModified']
        data_modificacao = response['LastModified']

        # Verifica se este arquivo é o mais recente
        if ultimo_arquivo_json is None or data_modificacao > ultima_data_modificacao:
            ultimo_arquivo_json = arquivo
            ultima_data_modificacao = data_modificacao

    # Usa get_object para baixar o arquivo
    response = s3_client.get_object(Bucket=BUCKET_RAW, Key=ultimo_arquivo_json)

    # Nome original do arquivo no bucket raw
    nome_original = response['ResponseMetadata']['HTTPHeaders']['content-disposition']

    # Nome do arquivo na Trusted
    novo_nome_arquivo = f"{maior_ano}_{maior_mes}_{maior_dia}_{maior_hora}_{nome_original}"

    # Lê o conteúdo do arquivo
    conteudo_json = response['Body'].read().decode('utf-8')

    # Converte o conteúdo JSON para um dicionário
    dict_conteudo = json.loads(conteudo_json)

    return { "nome": novo_nome_arquivo, "conteudo": dict_conteudo }

def verificar_json_trusted(**kwargs):
    """ Verifica se o arquivo com o mesmo nome já existe no bucket trusted """

    ti = kwargs['ti']
    dict_retorno_raw = ti.xcom_pull(task_ids='consultar_ultimo_arquivo')

    print(dict_retorno_raw)

    # Tenta buscar o arquivo na trusted, caso consiga, já existe
    try:
        s3_client.head_object(Bucket=BUCKET_TRUSTED, Key=dict_retorno_raw['nome'])

        # O arquivo existe
        return True
    except:
        # O arquivo não existe
        return False

def transformar_json(**kwargs):
    """ Realiza transformações no JSON vindo da war """

    ti = kwargs['ti']

    arquivo_existe_trusted = ti.xcom_pull(task_ids='verificar_arquivo_trusted')

    # Caso o arquivo já exista, retorna
    if arquivo_existe_trusted: return True

    dict_retorno_raw = ti.xcom_pull(task_ids='consultar_ultimo_arquivo')

    print(dict_retorno_raw)

    return

def enviar_trusted(arquivo):
    return True

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

    consultar_ultimo_arquivo = PythonOperator(
        task_id='consultar_ultimo_arquivo',
        python_callable=consultar_ultimo_json,
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

    consultar_ultimo_arquivo >> verificar_arquivo_trusted >> transformar_arquivo # >> enviar_arquivo_trusted
