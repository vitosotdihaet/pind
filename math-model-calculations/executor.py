"""
All executor-related calculations are present in here
"""

import btree


def time_execute_search_LSI(
    data_cardinality_per_replicaset: int,
    btree_order: int,
    pk_per_fk_cardinality_per_replicaset: int,
    cpu_frequency: float,
    mem_frequency: float,
) -> float:
    return (
        btree.find_keys_by_fk_in_index_comparison_count(
            data_cardinality_per_replicaset, btree_order
        )
        / cpu_frequency
        + btree.find_keys_by_fk_in_index_memory_jumps_count(
            data_cardinality_per_replicaset,
            btree_order,
            pk_per_fk_cardinality_per_replicaset,
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


def pollaczek_khinchin_deterministic_queue_length(
    intensity: float, processing_time: float
) -> float:
    rho: float = load(intensity, processing_time)
    return rho + (rho * rho) / (2 * (1 - rho))


def littles_law_deterministic(queue_length: float, intensity: float) -> float:
    return queue_length / intensity


def queue_time_deterministic(service_time: float, processing_time: float) -> float:
    return service_time - processing_time
