from math import ceil


def data_cardinality_per_replicaset(
    data_cardinality: int, replicaset_count: int
) -> int:
    return ceil(data_cardinality / replicaset_count)


def pk_per_fk_per_cardinality_per_replicaset(
    data_cardinality_per_replicaset: int, fk_cardinality: int
) -> int:
    return ceil(data_cardinality_per_replicaset / fk_cardinality)
