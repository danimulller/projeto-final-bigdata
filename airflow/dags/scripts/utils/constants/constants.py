from dataclasses import dataclass


@dataclass(frozen=True)
class Parameters:
    BUCKET_ORIGIN = "raw"
    BUCKET_DESTINATION = "trusted"
    PREFIX = "posicao"

    MAP_COLUMNS = {
        "hr": "hora",
        "l": "linhas",
        "c": "letreiro",
        "cl": "codigo_linha",
        "sl": "sentido_operacao",
        "lt0": "letreiro_destino",
        "lt1": "letreiro_origem",
        "qv": "quantidade_veiculos",
        "vs": "veiculos",
        "p": "prefixo",
        "a": "acessivel",
        "ta": "horario",
        "py": "latitude",
        "px": "longitude"
    }
