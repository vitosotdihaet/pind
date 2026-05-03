import yaml
from pydantic import (
    BaseModel,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
)


class MathModelInput(BaseModel):
    # intensities (requests/second)
    intensity_search_LSI: PositiveFloat
    intensity_update_LSI: PositiveFloat
    intensity_search_GSI: PositiveFloat
    intensity_update_GSI: PositiveFloat

    # replicaset configuration
    replicaset_count: PositiveInt

    # node to node latency
    cluster_time_k: PositiveFloat
    cluster_time_theta: PositiveFloat

    # bytes/s
    cluster_net_speed: PositiveFloat

    # user to node latency
    user_time_k: PositiveFloat
    user_time_theta: PositiveFloat

    # bytes/s
    user_net_speed: PositiveFloat

    # bytes
    row_size: PositiveInt

    # cardinality
    data_cardinality: PositiveInt
    fk_cardinality: NonNegativeInt

    # float (ops/second)
    cpu_frequency: NonNegativeFloat
    mem_frequency: NonNegativeFloat

    # in seconds
    wal_time: NonNegativeFloat
    timeout: PositiveFloat

    # btree
    btree_order: PositiveInt


def load_config(path: str = "config.yaml") -> MathModelInput:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return MathModelInput(**data)
