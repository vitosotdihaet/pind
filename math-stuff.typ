
// define variable names
#let iter_i = $i = overline(1..N)$

// math model parameters
#let replicaset_count = $N$
#let data_cardinality = $D$
#let search_data_cardinality = $S$
#let row_size = $r$
#let fk_cardinality = $K$
#let pk_per_fk_cardinality_per_replicaset = $s$
// fk_copy_count_per_replicaset = search_data_cardinality / replicaset_count
#let data_cardinality_per_replicaset = $d$

#let cpu_frequency = $f_"cpu"$
#let mem_frequency = $f_"mem"$
#let wal_time = $T_"WAL"$
#let timeout = $T_"timeout"$

#let user_time_k = $k_"user"$
#let user_time_theta = $theta_"user"$
#let user_net_speed = $v_"user"$

#let cluster_time_k = $k_"cluster"$
#let cluster_time_theta = $theta_"cluster"$
#let cluster_net_speed = $v_"cluster"$


#let btree_order = $m$
#let btree_max_keys = $2#btree_order - 1$
#let btree_min_keys = $2/3 (#btree_max_keys)$
#let btree_full_node_probability = $P_"full"$
#let btree_full_node_probability_value = $0.81$


// COMMON
#let user_request_time = $t_"user"^"request"$
#let user_response_time = $t_"user"^"response"$
#let cluster_request_time_ith = $t_"replicaset"^("request", i)$
#let cluster_response_time_ith = $t_"replicaset"^("response", i)$

#let time_user = $T^"user"$
#let service_time_coordinate = $W^"coordinate"$

#let result_size = $R$
#let request_size = $Q$
#let exec_plan_size = $P$

#let intensity_search = $lambda_"search"$
#let intensity_update = $lambda_"update"$

// LSI SEARCH
#let subintensity_search = intensity_search

#let load_executor_search_LSI = $rho^"executor"_"search,LSI"$

#let search_btree_node_jumps = $log_#btree_order #data_cardinality_per_replicaset$
#let search_btree_leaf_jumps = $(#pk_per_fk_cardinality_per_replicaset - 1) / #btree_min_keys$
#let search_btree_jumps_total = $#search_btree_node_jumps + 3 dot (#pk_per_fk_cardinality_per_replicaset - 1) / (4m - 2) + 1$
#let search_btree_search_ops_node = $log_2 (2#btree_order - 1)$
#let search_btree_search_ops_total = $#search_btree_node_jumps dot #search_btree_search_ops_node$

#let time_user_search_LSI = $T^"user"_"search,LSI"$
#let time_coordinate_search_LSI = $T^"coordinate"_"search,LSI"$
#let time_coordinate_search_LSI_ith = $T^"coordinate"_("search,LSI", i)$
#let time_execute_search_LSI = $T^"execute"_"search,LSI"$

#let service_time_coordinate_search_LSI = $W^"coordinate"_"search,LSI"$
#let service_time_execute_search_LSI = $W^"execute"_"search,LSI"$
#let queue_time_execute_search_LSI = $W^"execute"_"search,q,LSI"$

#let queue_length_execute_search_LSI = $L^"execute"_"search,LSI"$

#let time_coordinate_search_LSI_ith_right_side = $#cluster_request_time_ith + #exec_plan_size / #cluster_net_speed + #service_time_execute_search_LSI + #cluster_response_time_ith + (#pk_per_fk_cardinality_per_replicaset #row_size) / #cluster_net_speed$

#let random_part_of_tcsi = $Y$
#let deterministic_part_of_tcsi = $C^"coordinate"$

#let random_part_of_tss = $V$

#let random_part_of_tcs = $Z$

// LSI UPDATE
#let time_execute_update = $T^" execute"_"update"$
#let time_service_update = $T^" service"_"update"$
#let load_update = $rho_"update"$

#let update_btree_node_jumps = search_btree_node_jumps
#let update_btree_node_search_ops = search_btree_search_ops_total
#let update_btree_node_split_probability_value = $0.19$
#let update_btree_free_space_before_overflow_long = $(#btree_max_keys)#update_btree_node_split_probability_value$
#let update_btree_free_space_before_overflow_inv = $5.26 / #btree_max_keys$


// GSI SEARCH

// GSI UPDATE
#let time_user_update_GSI = $T^"user"_"update,GSI"$


// Theorem helpers
#import "@preview/lemmify:0.1.8": *

#let (
  theorem,
  lemma,
  corollary,
  remark,
  proposition,
  example,
  proof,
  rules: thm-rules,
) = default-theorems("all", lang: "ru")
#show: thm-rules
