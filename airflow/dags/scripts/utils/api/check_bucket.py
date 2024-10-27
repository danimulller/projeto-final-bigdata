from scripts.utils.api.boto_client import get_client


def is_bucket_empty(bucket_name: str) -> bool:
    """ Verifica se o bucket está vazio """

    client = get_client()
    response = client.list_objects(Bucket=bucket_name)

    if "Contents" not in response:
        print(f"The bucket '{bucket_name}' is empty.")
        return True
    else:
        print(f"The bucket '{bucket_name}' is not empty.")
        return False
    
def check_file_bucket(file_name: str, folder: str, bucket: str = 'raw') -> bool:
    """ Verifica se o arquivo com o mesmo nome já existe na pasta especificada no bucket """
    
    # Constrói o caminho completo com a pasta
    file_key = f"{folder}{file_name}"
    client = get_client()
    
    # Tenta buscar o arquivo no bucket, caso consiga, já existe
    try:
        client.head_object(Bucket=bucket, Key=file_key)

        # O arquivo existe
        return True
    except:
        # O arquivo não existe
        return False
