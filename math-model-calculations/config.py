import random

import yaml
from pydantic import (
    BaseModel,
    NonNegativeFloat,
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
    fk_cardinality: PositiveInt

    # float (ops/second)
    cpu_frequency: NonNegativeFloat
    mem_frequency: NonNegativeFloat

    # in seconds
    wal_time: NonNegativeFloat
    timeout: PositiveFloat

    # btree
    btree_order: PositiveInt

    @staticmethod
    def random() -> "MathModelInput":
        replicaset_count = random.randint(3, 512)

        cluster_time_k = random.uniform(1.5, 3.0)
        cluster_time_theta = random.uniform(0.001, 0.01)

        user_time_k = random.uniform(2.0, 5.0)
        user_time_theta = random.uniform(0.005, 0.42)

        cluster_net_speed = random.uniform(0.250, 2500) * 10**6
        user_net_speed = random.uniform(0.125, 125) * 10**6

        total_load = random.uniform(5000, 100000)
        read_ratio = random.uniform(0.7, 0.95)

        intensity_search = total_load * read_ratio
        intensity_update = total_load * (1 - read_ratio)

        row_size = random.randint(128, 2048)
        data_cardinality = random.randint(10**3, 10**7)

        fk_cardinality = random.randint(10**2, data_cardinality // 10)

        cpu_frequency = random.uniform(1e7, 5e8)
        mem_frequency = cpu_frequency * random.uniform(1.0, 2.0)

        wal_time = random.uniform(0.0001, 0.01)
        timeout = 5.0

        btree_order = random.choice([64, 128, 256, 512])

        return MathModelInput(
            intensity_search_LSI=intensity_search,
            intensity_update_LSI=intensity_update,
            intensity_search_GSI=intensity_search,
            intensity_update_GSI=intensity_update,
            replicaset_count=replicaset_count,
            cluster_time_k=cluster_time_k,
            cluster_time_theta=cluster_time_theta,
            cluster_net_speed=cluster_net_speed,
            user_time_k=user_time_k,
            user_time_theta=user_time_theta,
            user_net_speed=user_net_speed,
            row_size=row_size,
            data_cardinality=data_cardinality,
            fk_cardinality=fk_cardinality,
            cpu_frequency=cpu_frequency,
            mem_frequency=mem_frequency,
            wal_time=wal_time,
            timeout=timeout,
            btree_order=btree_order,
        )


def load_config(path: str = "config.yaml") -> MathModelInput:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return MathModelInput(**data)
