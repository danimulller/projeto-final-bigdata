from dataclasses import dataclass


@dataclass(frozen=True)
class Parameters:
    BUCKET_ORIGIN = "raw"
    BUCKET_DESTINATION = "trusted"
    PREFIX = "posicao"
