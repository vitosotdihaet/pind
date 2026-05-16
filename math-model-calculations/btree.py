from math import ceil, floor, log


def min_key_count_in_leaf(tree_order: int) -> int:
    return floor(2 / 3 * max_key_count_in_node(tree_order))


def max_key_count_in_node(tree_order: int) -> int:
    return 2 * tree_order - 1


def full_node_probbility() -> float:
    return 0.81


def find_keys_by_fk_in_index_comparison_count(
    number_of_keys: int, tree_order: int
) -> int:
    return ceil(log(number_of_keys, tree_order)) * ceil(
        log(max_key_count_in_node(tree_order), 2)
    )


def find_keys_by_fk_in_index_memory_jumps_count(
    number_of_keys: int, tree_order: int, pk_per_fk_per_cardinality_per_replicaset: int
) -> int:
    return (
        ceil(log(number_of_keys, tree_order))
        + ceil(
            (pk_per_fk_per_cardinality_per_replicaset - 1)
            / min_key_count_in_leaf(tree_order)
        )
        + 1
    )
