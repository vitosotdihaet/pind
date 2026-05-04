// define variable names
#let iter_i = $i = overline(1..N)$
#let iter_i_to_k = $i = overline(1..k)$

// math model parameters
#let replicaset_count = $N$
#let data_cardinality = $D$
#let row_size = $r$
#let fk_cardinality = $K$
#let pk_per_fk_cardinality_per_replicaset = $s$
#let pk_per_fk_cardinality_per_replicaset_ith = $s_i$
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
#let user_request_time = $t^"user"_"request"$
#let user_response_time = $t^"user"_"response"$
#let cluster_request_time_ith = $t^"replicaset"_("request", i)$
#let cluster_response_time_ith = $t^"replicaset"_("response", i)$

#let time_user = $T^"user"$
#let service_time_coordinate = $W^"coordinate"$

#let result_size = $R$
#let query_size = $Q$
#let exec_plan_size = $P$
#let exec_plan_size_ith = $P_i$

#let intensity_search = $lambda_"search"$
#let intensity_update = $lambda_"update"$

// LSI SEARCH
// SMO
#let intensity_search_LSI = $lambda_"search,LSI"$
#let subintensity_search_LSI = $lambda_"search,LSI"$

#let load_executor_search_LSI = $rho^"executor"_"search,LSI"$
#let max_subintensity_search_LSI = $lambda_"search,LSI"^"max"$
#let queue_time_total_LSI = $W^"total"_"search,q,LSI"$

#let btree_node_jumps_search_LSI = $log_#btree_order #data_cardinality_per_replicaset$
#let btree_leaf_jumps_search_LSI = $(#pk_per_fk_cardinality_per_replicaset - 1) / #btree_min_keys$
#let btree_jumps_total_search_LSI = $#btree_node_jumps_search_LSI + 3 dot (#pk_per_fk_cardinality_per_replicaset - 1) / (4m - 2) + 1$
#let btree_search_ops_node_search_LSI = $log_2 (2#btree_order - 1)$
#let btree_search_ops_total_search_LSI = $#btree_node_jumps_search_LSI dot #btree_search_ops_node_search_LSI$

#let time_user_search_LSI = $T^"user"_"search,LSI"$
#let time_coordinate_search_LSI = $T^"coordinate"_"search,LSI"$
#let time_coordinate_search_LSI_ith = $T^"coordinate"_("search,LSI", i)$
#let time_execute_search_LSI = $T^"execute"_"search,LSI"$

#let service_time_coordinate_search_LSI = $W^"coordinate"_"search,LSI"$
#let service_time_execute_search_LSI = $W^"execute"_"search,LSI"$
#let queue_time_execute_search_LSI = $W^"execute"_"search,q,LSI"$

#let queue_length_execute_search_LSI = $L^"execute"_"search,LSI"$

#let time_coordinate_search_LSI_ith_right_side = $#cluster_request_time_ith + #exec_plan_size / #cluster_net_speed + #service_time_execute_search_LSI + #cluster_response_time_ith + (#pk_per_fk_cardinality_per_replicaset #row_size) / #cluster_net_speed$

#let random_part_of_tcsi_LSI = $Y$
#let deterministic_part_of_tcsi_LSI = $C^"coordinate"$
#let random_part_of_tss_LSI = $V$
#let random_part_of_tcs_LSI = $Z$
#let deterministic_part_of_tus_LSI = $C^"user"$

// some calculations
#let net_reqs_search_LSI_name = $"NR"^"LSI"_"search"$

// LSI UPDATE
#let time_execute_update_LSI = $T^" execute"_"update,LSI"$
#let time_service_update_LSI = $T^" service"_"update,LSI"$
#let load_update_LSI = $rho_"update,LSI"$

#let btree_node_jumps_update_LSI = btree_node_jumps_search_LSI
#let btree_node_search_ops_update_LSI = btree_search_ops_total_search_LSI
#let btree_node_split_probability_value_update_LSI = $0.19$
#let btree_free_space_before_overflow_long_update_LSI = $(#btree_max_keys)#btree_node_split_probability_value_update_LSI$
#let btree_free_space_before_overflow_inv_update_LSI = $5.26 / #btree_max_keys$


// GSI SEARCH
#let fk_execute_request_time = $t^"FK-execute"_"request"$
#let fk_execute_response_time = $t^"FK-execute"_"response"$

#let intensity_search_GSI = $lambda_"search,GSI"$
#let subintensity_search_GSI = $lambda^"sub"_"search,GSI"$
#let max_subintensity_search_GSI = $lambda_"search,GSI"^"sub,max"$
#let max_intensity_search_GSI = $lambda_"search,GSI"^"max"$

#let load_executor_search_GSI = $rho^"executor"_"search,GSI"$
#let queue_time_total_GSI = $W^"total"_"search,q,GSI"$

#let btree_node_jumps_search_GSI = $log_#btree_order #data_cardinality_per_replicaset$
#let btree_leaf_jumps_search_GSI = $(#pk_per_fk_cardinality_per_replicaset - 1) / #btree_min_keys$
#let btree_jumps_total_search_GSI = $#btree_node_jumps_search_GSI + 3 dot (#pk_per_fk_cardinality_per_replicaset - 1) / (4m - 2) + 1$
#let btree_search_ops_node_search_GSI = $log_2 (2#btree_order - 1)$
#let btree_search_ops_total_search_GSI = $#btree_node_jumps_search_GSI #btree_search_ops_node_search_GSI$

#let time_user_search_GSI = $T^"user"_"search,GSI"$
#let time_coordinate_search_GSI = $T^"coordinate"_"search,GSI"$
#let time_fk_execute_search_GSI = $T^"FK-execute"_"search,GSI"$
#let time_fk_execute_search_GSI_ith = $T^"FK-execute"_("search,GSI", i)$
#let time_execute_search_GSI = $T^"execute"_"search,GSI"$

#let service_time_coordinate_search_GSI = $W^"coordinate"_"search,GSI"$
#let service_time_execute_search_GSI = $W^"execute"_"search,GSI"$
#let service_time_fk_execute_search_GSI = $W^"FK-execute"_"search,GSI"$
#let queue_time_execute_search_GSI = $W^"execute"_"search,q,GSI"$

#let queue_length_execute_search_GSI = $L^"execute"_"search,GSI"$

#let time_fk_execute_search_GSI_ith_right_side = $#cluster_request_time_ith + #exec_plan_size_ith / #cluster_net_speed + #service_time_execute_search_GSI + #cluster_response_time_ith + (#pk_per_fk_cardinality_per_replicaset_ith #row_size) / #cluster_net_speed$

#let time_fk_execute_search_GSI_ith_right_side_bs = $#cluster_request_time_ith + #exec_plan_size / #cluster_net_speed + #service_time_execute_search_GSI + #cluster_response_time_ith + (#pk_per_fk_cardinality_per_replicaset #row_size) / #cluster_net_speed$

#let random_part_of_tfei_GSI = $U$
#let deterministic_part_of_tfei_GSI = $C^"FK-execute"$
#let random_part_of_tfe_GSI = $V$
#let deterministic_part_of_tfe_GSI = $C^"FK-execute"_"full"$
#let random_part_of_tce_GSI = $W$
#let deterministic_part_of_tce_GSI = $C^"coordinate"$
#let random_part_of_tus_GSI = $X$
#let deterministic_part_of_tus_GSI = $C^"user"$

#let exec_plan_size_avg = $P_"avg"$

// calc
#let net_reqs_search_GSI_name = $"NR"^"GSI"_"search"$

// GSI UPDATE
#let time_user_update_GSI = $T^"user"_"update,GSI"$
