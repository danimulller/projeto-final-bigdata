import json
from scripts.utils.constants.constants import Parameters
from scripts.utils.api.boto_client import get_client

def load_file_to_bucket(data: dict, file_name: str, folder: str, bucket: str, type: str = 'json') -> bool:
    try:
        # Configurações do cliente S3
        s3_client = get_client()
        
        # Caminho do objeto no bucket
        object_name = f"{folder}{file_name}"

        if type == 'json':
            # Convertendo o dicionário para uma string JSON
            json_data = json.dumps(data)
            content_type = 'application/json'
        elif type == 'parquet':
            content_type = 'application/x-parquet'
        else:
            print(f"Tipo {type} não suportado!")
            raise

        # Envia o arquivo para o bucket
        s3_client.put_object(Bucket=bucket, Key=object_name, Body=json_data, ContentType=content_type)

        print(f"Arquivo {file_name}.{type} foi carregado em {folder} no bucket {bucket}!")

        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo {file_name} no bucket {bucket}: {str(e)}")
        raise
