import yaml
from pydantic import (
    BaseModel,
    PositiveFloat,
    PositiveInt,
)


class LoadTestingConfig(BaseModel):
    # requests/second
    intensity_search_LSI: PositiveFloat
    intensity_insert_LSI: PositiveFloat
    intensity_search_GSI: PositiveFloat
    intensity_insert_GSI: PositiveFloat
    # bytes
    row_size: PositiveInt
    # cardinality
    data_cardinality: PositiveInt
    fk_cardinality: PositiveInt
    # timeout in secs
    timeout: PositiveFloat

    @staticmethod
    def default() -> "LoadTestingConfig":
        return LoadTestingConfig(
            intensity_search_LSI=1,
            intensity_insert_LSI=1,
            intensity_search_GSI=1,
            intensity_insert_GSI=1,
            row_size=1,
            data_cardinality=1,
            fk_cardinality=1,
            timeout=1,
        )


def load_config(path: str = "config.yaml") -> LoadTestingConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return LoadTestingConfig(**data)
