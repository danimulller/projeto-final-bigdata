from io import BytesIO
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scripts.utils.constants.constants import Parameters

def rename_json_columns(json_dict: dict, map_column: dict = Parameters.MAP_COLUMNS) -> dict:
    """ Renomeia as colunas de um JSON """

    try:
        if isinstance(json_dict, dict):
            # Renomeia as chaves do dicionário atual
            return {map_column.get(key, key): rename_json_columns(value, map_column) for key, value in json_dict.items()}
        elif isinstance(json_dict, list):
            # Aplica a renomeação em cada item da lista
            return [rename_json_columns(item, map_column) for item in json_dict]
        else:
            # Retorna o valor se não for um dicionário ou lista
            return json_dict
    except Exception as e:
        print(f"Erro ao renomear as colunas do JSON: {str(e)}")
        raise

def convert_json_to_parquet(json_data: dict):
    df = pd.DataFrame(json_data)

    table = pa.Table.from_pandas(df)

    # Armazenar o Parquet em memória
    parquet_buffer = BytesIO()
    pq.write_table(table, parquet_buffer)
    
    # Retornar o conteúdo do buffer em bytes
    return parquet_buffer.getvalue()

def transform_from_raw(json: dict):
    """ Realiza as transformações da RAW para TRUSTED de Posicao """

    try:
        transformed_json = rename_json_columns(json, Parameters.MAP_COLUMNS)

        print("JSON:")
        print(transformed_json)

        return transformed_json
    except Exception as e:
        print(f"Erro ao transformar o arquivo JSON: {str(e)}")
        raise