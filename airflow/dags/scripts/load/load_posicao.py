from io import BytesIO
import json

import pandas as pd
from scripts.utils.constants.constants import Parameters
from scripts.utils.api.boto_client import get_client

def load_file_to_bucket(data: dict, file_name: str, folder: str, bucket: str, file_type: str = 'json') -> bool:
    """ Envia um arquivo para uma pasta específica do bucket """

    try:
        # Configurações do cliente S3
        s3_client = get_client()
        
        # Caminho do objeto no bucket
        object_name = f"{folder}{file_name}"

        if file_type == 'json':
            # Convertendo o dicionário para uma string JSON
            json_data = json.dumps(data)
            content = json_data.encode('utf-8')
            content_type = 'application/json'

        elif file_type == 'parquet':
            # Converte o dicionário para DataFrame e salva como Parquet no buffer
            df = pd.DataFrame(json.loads(data))
            buffer = BytesIO()
            df.to_parquet(buffer, index=False)
            buffer.seek(0)
            content = buffer.getvalue()
            content_type = 'application/x-parquet'

        else:
            print(f"Tipo {file_type} não suportado!")
            raise

        # Envia o arquivo para o bucket
        s3_client.put_object(Bucket=bucket, Key=object_name, Body=content, ContentType=content_type)

        print(f"Arquivo {file_name} foi carregado em {folder} no bucket {bucket}!")

        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo {file_name} no bucket {bucket}: {str(e)}")
        raise
