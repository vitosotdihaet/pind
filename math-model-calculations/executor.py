"""
All executor-related calculations are present in here
"""

import btree


def search_LSI(
    data_cardinality_per_replicaset: int,
    btree_order: int,
    pk_per_fk_per_cardinality_per_replicaset: int,
    cpu_frequency: float,
    mem_frequency: float,
) -> float:
    return (
        btree.find_n_keys_by_fk_in_index_comparison_count(
            data_cardinality_per_replicaset, btree_order
        )
        / cpu_frequency
        + btree.find_n_keys_by_fk_in_index_memory_jumps_count(
            data_cardinality_per_replicaset,
            pk_per_fk_per_cardinality_per_replicaset,
            btree_order,
        )
        / mem_frequency
    )


def send_result_to_coordinator_time(
    pk_per_fk_per_cardinality_per_replicaset: int,
    row_size: int,
    cluster_net_speed: float,
) -> float:
    return pk_per_fk_per_cardinality_per_replicaset * row_size / cluster_net_speed


def load(intensity: float, processing_time: float) -> float:
    return intensity * processing_time
