import json
from scripts.utils.constants.constants import Parameters
from scripts.utils.api.boto_client import get_client

def load_file_to_bucket(data: dict, file_name: str, folder: str, bucket: str) -> bool:
    try:
        # Configurações do cliente S3
        s3_client = get_client()

        # Convertendo o dicionário para uma string JSON
        json_data = json.dumps(data)
        
        # Caminho do objeto no bucket
        object_name = f"{folder}{file_name}"

        # Envia o arquivo para o bucket
        s3_client.put_object(Bucket=bucket, Key=object_name, Body=json_data, ContentType='application/json')

        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo {file_name} no bucket {bucket}: {str(e)}")
        raise
