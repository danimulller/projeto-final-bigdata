import json
from scripts.utils.api.check_bucket import is_bucket_empty
from scripts.utils.constants.constants import Parameters
from scripts.utils.api.boto_client import get_client
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def move_full_data():

    client = get_client()
    paginator = client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(
        Bucket=Parameters.BUCKET_ORIGIN, Prefix=Parameters.PREFIX
    )

    for page in page_iterator:
        if "Contents" in page:
            for obj in page["Contents"]:
                key = obj["Key"]

                if key.endswith("/"):
                    continue

                copy_source = {"Bucket": Parameters.BUCKET_ORIGIN, "Key": key}
                print(f"Copying {key} to {Parameters.BUCKET_DESTINATION}/{key}")
                client.copy_object(
                    CopySource=copy_source,
                    Bucket=Parameters.BUCKET_DESTINATION,
                    Key=key,
                )

def extract_data_from_raw():
    is_empty = is_bucket_empty(bucket_name=Parameters.BUCKET_DESTINATION)

    if is_empty:
        move_full_data()
    else:
        extract_last_json()

def extract_last_json(bucket = 'raw', root_folder = 'posicao/'):
    """ Consulta o último arquivo JSON inserido no bucket """

    s3 = S3Hook(aws_conn_id="s3_minio")
    s3_client = get_client()

    # Lista as pastas de primeiro nível (anos)
    lista_pasta_ano = s3.list_prefixes(
        bucket_name=bucket, prefix=root_folder, delimiter="/"
    )
    lista_ano = [folder.split("/")[-2] for folder in lista_pasta_ano]
    maior_ano = max(lista_ano)

    # Lista as pastas de segundo nível (meses) no maior ano
    lista_pasta_mes = s3.list_prefixes(
        bucket_name=bucket, prefix=f"{root_folder}{maior_ano}/", delimiter="/"
    )
    lista_mes = [folder.split("/")[-2] for folder in lista_pasta_mes]
    maior_mes = max(lista_mes)

    # Lista as pastas de terceiro nível (dias) no maior ano e mês
    lista_pasta_dia = s3.list_prefixes(
        bucket_name=bucket,
        prefix=f"{root_folder}{maior_ano}/{maior_mes}/",
        delimiter="/",
    )
    lista_dia = [folder.split("/")[-2] for folder in lista_pasta_dia]
    maior_dia = max(lista_dia)

    # Lista as pastas de quarto nível (horas) no maior ano, mês e menor dia
    lista_pasta_hora = s3.list_prefixes(
        bucket_name=bucket,
        prefix=f"{root_folder}{maior_ano}/{maior_mes}/{maior_dia}/",
        delimiter="/",
    )
    lista_hora = [folder.split("/")[-2] for folder in lista_pasta_hora]
    maior_hora = max(lista_hora)

    ultima_pasta = f"{root_folder}{maior_ano}/{maior_mes}/{maior_dia}/{maior_hora}/"

    # Lista os arquivos JSON na última pasta
    lista_arquivos = s3.list_keys(
        bucket_name=bucket, prefix=ultima_pasta, delimiter="/"
    )

    # Filtra apenas arquivos JSON
    lista_arquivos_json = [
        arquivo for arquivo in lista_arquivos if arquivo.endswith(".json")
    ]

    # Inicializa variáveis para o arquivo mais recente
    ultimo_arquivo_json = None
    ultima_data_modificacao = None

    # Percorre os arquivos JSON para determinar qual é o mais recente
    for arquivo in lista_arquivos_json:
        # Obtemos os metadados do arquivo usando o cliente boto3
        response = s3_client.head_object(Bucket=bucket, Key=arquivo)

        # A data de modificação do arquivo é acessível por response['LastModified']
        data_modificacao = response["LastModified"]

        # Verifica se este arquivo é o mais recente
        if ultimo_arquivo_json is None or data_modificacao > ultima_data_modificacao:
            ultimo_arquivo_json = arquivo
            ultima_data_modificacao = data_modificacao

    # Usa get_object para baixar o arquivo
    response = s3_client.get_object(Bucket=bucket, Key=ultimo_arquivo_json)

    # Nome original do arquivo no bucket raw
    nome_original = response['ResponseMetadata']['HTTPHeaders']['content-disposition']

    # Lê o conteúdo do arquivo
    conteudo_json = response['Body'].read().decode('utf-8')

    # Converte o conteúdo JSON para um dicionário
    dict_conteudo = json.loads(conteudo_json)

    return {
        "name": nome_original,
        "type": 'json',
        "folder": ultima_pasta,
        "content": dict_conteudo
    }
