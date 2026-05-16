from math import ceil

QUERY_METADATA_SIZE: int = 160
PLAN_METADATA_SIZE: int = 148


def data_cardinality_per_replicaset(
    data_cardinality: int, replicaset_count: int
) -> int:
    return ceil(data_cardinality / replicaset_count)


def pk_per_fk_cardinality_per_replicaset(
    data_cardinality_per_replicaset: int, fk_cardinality: int
) -> int:
    return ceil(data_cardinality_per_replicaset / fk_cardinality)


def exec_plan_size(row_size: int) -> int:
    return PLAN_METADATA_SIZE + row_size


def query_size(row_size: int) -> int:
    return QUERY_METADATA_SIZE + row_size
