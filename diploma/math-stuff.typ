// an equation without numbering
#let nonum_eq(eq) = math.equation(block: true, numbering: none, eq)

// math model parameters
#let replicaset_count = $N$
#let data_cardinality = $D$
#let row_size = $r$
#let replicaset_count_with_fk = $H$
#let fk_cardinality = $K$
#let fk_cardinality_per_replicaset = $k$
#let pk_per_fk_cardinality_per_replicaset = $s$
#let pk_per_fk_cardinality_per_replicaset_ith = $s_i$
// fk_copy_count_per_replicaset = search_data_cardinality / replicaset_count
#let data_cardinality_per_replicaset = $d$

// define variable names
#let iter_i = $i = overline(1..#replicaset_count)$
#let iter_i_to_k = $i = overline(1..#replicaset_count_with_fk)$

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
#let btree_node_avg_fullness = $0.81$


// COMMON
#let user_request_time = $t^"user"_"request"$
#let user_response_time = $t^"user"_"response"$
#let cluster_request_time_ith = $t^"replicaset"_("request", i)$
#let cluster_response_time_ith = $t^"replicaset"_("response", i)$
#let cluster_request_time = $t^"replicaset"_"request"$
#let cluster_response_time = $t^"replicaset"_"response"$

#let time_user = $T^"user"$
#let service_time_coordinate = $W^"coordinate"$

#let result_size = $R$
#let query_size = $Q$
#let exec_plan_size = $P$
#let exec_plan_size_ith = $P_i$

#let intensity_search = $lambda_"search"$
#let intensity_update = $lambda_"update"$
#let max_intensity = $lambda^"max"$
#let queue_time_total = $W^"total,q"$

// LSI SEARCH
#let intensity_search_LSI = $lambda_"search,LSI"$
#let subintensity_search_LSI = $lambda_"search,LSI"^"sub"$
#let max_intensity_search_LSI = $lambda_"search,LSI"^"max"$
#let max_subintensity_search_LSI = $lambda_"search,LSI"^"sub,max"$

#let load_executor_search_LSI = $rho^"executor"_"search,LSI"$
#let queue_time_total_search_LSI = $W^"total,q"_"search,LSI"$

#let btree_node_jumps_search_LSI = $log_#btree_order #data_cardinality_per_replicaset$
#let btree_leaf_jumps_search_LSI = $(#pk_per_fk_cardinality_per_replicaset - 1) / #btree_min_keys$
#let btree_jumps_total_search_LSI = $#btree_node_jumps_search_LSI + 3 dot (#pk_per_fk_cardinality_per_replicaset - 1) / (4#btree_order - 2) + 1$
#let btree_search_ops_node_search_LSI = $log_2 (2#btree_order - 1)$
#let btree_search_ops_total_search_LSI = $#btree_node_jumps_search_LSI #btree_search_ops_node_search_LSI$

#let time_user_search_LSI = $T^"user"_"search,LSI"$
#let time_coordinate_search_LSI = $T^"coordinate"_"search,LSI"$
#let time_coordinate_search_LSI_ith = $T^"coordinate"_("search,LSI", i)$
#let time_execute_search_LSI = $T^"execute"_"search,LSI"$

#let service_time_coordinate_search_LSI = $W^"coordinate"_"search,LSI"$
#let service_time_execute_search_LSI = $W^"execute"_"search,LSI"$
#let queue_time_execute_search_LSI = $W^"execute,q"_"search,LSI"$
#let queue_length_execute_search_LSI = $L^"execute"_"search,LSI"$

#let time_coordinate_search_LSI_ith_right_side = $#cluster_request_time_ith + #exec_plan_size / #cluster_net_speed + #service_time_execute_search_LSI + #cluster_response_time_ith + (#pk_per_fk_cardinality_per_replicaset #row_size) / #cluster_net_speed$

#let random_part_of_tcsi_search_LSI = $UU^"c"_i$
#let deterministic_part_of_tcsi_search_LSI = $CC^"c"$
#let random_part_of_tcs_search_LSI = $UU^"c"$

#let random_part_of_tss_search_LSI = $UU^"u"$
#let deterministic_part_of_tus_search_LSI = $CC^"u"$

#let net_reqs_search_LSI_name = $"NR"^"LSI"_"search"$

// LSI UPDATE
#let intensity_update_LSI = $lambda_"update,LSI"$
#let subintensity_update_LSI = $lambda^"sub"_"update,LSI"$
#let max_intensity_update_LSI = $lambda_"update,LSI"^"max"$
#let max_subintensity_update_LSI = $lambda_"update,LSI"^"sub,max"$

#let time_user_update_LSI = $T^"user"_"update,LSI"$
#let time_coordinate_update_LSI = $T^"coordinate"_"update,LSI"$
#let time_execute_update_LSI = $T^"execute"_"update,LSI"$

#let service_time_coordinate_update_LSI = $W^"coordinate"_"update,LSI"$
#let service_time_execute_update_LSI = $W^"execute"_"update,LSI"$
#let queue_time_execute_update_LSI = $W^"execute,q"_"update,LSI"$

#let queue_length_execute_update_LSI = $L^"execute"_"update,LSI"$

#let load_executor_update_LSI = $rho^"executor"_"update,LSI"$
#let queue_time_total_update_LSI = $W^"total,q"_"update,LSI"$
#let time_service_update_LSI = $T^" service"_"update,LSI"$
#let load_update_LSI = $rho_"update,LSI"$

#let btree_node_jumps_update_LSI = btree_node_jumps_search_LSI
#let btree_node_search_ops_update_LSI = btree_search_ops_total_search_LSI
#let btree_node_split_probability_value_update_LSI = $0.19$
#let btree_free_space_before_overflow_long_update_LSI = $#btree_node_split_probability_value_update_LSI (#btree_max_keys)$
#let btree_free_space_before_overflow_inv_update_LSI = $5.26 / #btree_max_keys$

#let time_coordinate_update_LSI_ith_right_side = $#cluster_request_time + #exec_plan_size / #cluster_net_speed + #service_time_execute_update_LSI + #cluster_response_time$

#let random_part_of_tcs_update_LSI = $UU^"c"$
#let deterministic_part_of_tcs_update_LSI = $CC^"c"$
#let random_part_of_tus_update_LSI = $UU^"u"$
#let deterministic_part_of_tus_update_LSI = $CC^"u"$

#let net_reqs_update_LSI_name = $"NR"^"LSI"_"update"$
#let rps_update_LSI_name = $"RPS"^"LSI"_"update"$

// GSI SEARCH
#let fk_execute_request_time = $t^"FK-execute"_"request"$
#let fk_execute_response_time = $t^"FK-execute"_"response"$

#let intensity_search_GSI = $lambda_"search,GSI"$
#let subintensity_search_GSI = $lambda^"sub"_"search,GSI"$
#let max_subintensity_search_GSI = $lambda_"search,GSI"^"sub,max"$
#let max_intensity_search_GSI = $lambda_"search,GSI"^"max"$

#let load_executor_search_GSI = $rho^"executor"_"search,GSI"$
#let queue_time_total_search_GSI = $W^"total,q"_"search,GSI"$

#let btree_node_jumps_search_GSI = $log_#btree_order #data_cardinality_per_replicaset$
#let btree_search_ops_node_search_GSI = $log_2 (2#btree_order - 1)$
#let btree_search_ops_total_search_GSI = $#btree_node_jumps_search_GSI #btree_search_ops_node_search_GSI$

#let btree_node_jumps_search_GSI_fk = $log_#btree_order #data_cardinality_per_replicaset$
#let btree_jumps_total_search_GSI_fk = $#btree_node_jumps_search_GSI_fk + 3 dot (#pk_per_fk_cardinality_per_replicaset - 1) / (4#btree_order - 2) + 1$
#let btree_search_ops_node_search_GSI_fk = $log_2 (2#btree_order - 1)$
#let btree_search_ops_total_search_GSI_fk = $#btree_node_jumps_search_GSI #btree_search_ops_node_search_GSI_fk$

#let time_user_search_GSI = $T^"user"_"search,GSI"$
#let time_coordinate_search_GSI = $T^"coordinate"_"search,GSI"$
#let time_execute_fk_search_GSI = $T^"FK-execute"_"search,GSI"$
#let time_execute_fk_subsearch_GSI = $T^"FK-execute"_"subsearch,GSI"$
#let time_execute_fk_subsearch_GSI_ith = $T^"FK-execute"_("subsearch,GSI", i)$
#let time_execute_search_GSI = $T^"execute"_"search,GSI"$

#let service_time_coordinate_search_GSI = $W^"coordinate"_"search,GSI"$
#let service_time_execute_search_GSI = $W^"execute"_"search,GSI"$
#let service_time_fk_execute_search_GSI = $W^"FK-execute"_"search,GSI"$
#let queue_time_execute_search_GSI = $W^"execute,q"_"search,GSI"$

#let queue_length_execute_search_GSI = $L^"execute"_"search,GSI"$

#let time_fk_execute_search_GSI_ith_right_side = $#cluster_request_time_ith + #exec_plan_size_ith / #cluster_net_speed + #service_time_execute_search_GSI + #cluster_response_time_ith + (#pk_per_fk_cardinality_per_replicaset_ith #row_size) / #cluster_net_speed$

#let time_fk_execute_search_GSI_ith_right_side_bs = $#cluster_request_time_ith + #exec_plan_size / #cluster_net_speed + #service_time_execute_search_GSI + #cluster_response_time_ith + (#pk_per_fk_cardinality_per_replicaset #row_size) / #cluster_net_speed$

#let random_part_of_tfei_GSI = $UU^"FK"_i$
#let deterministic_part_of_tfei_GSI = $CC^"FK"_i$
#let random_part_of_tfe_GSI = $UU^"FK"$
#let deterministic_part_of_tfe_GSI = $CC^"FK"$
#let random_part_of_tce_GSI = $UU^"c"$
#let deterministic_part_of_tce_GSI = $CC^"c"$
#let random_part_of_tus_GSI = $UU^"u"$
#let deterministic_part_of_tus_GSI = $CC^"u"$

#let random_part_of_tu_and_c_GSI = $UU^"uc"$

#let net_reqs_search_GSI_name = $"NR"^"GSI"_"search"$

// GSI UPDATE
#let cluster_request_time_sk = $t^"SK-replicaset"_"request"$
#let cluster_response_time_sk = $t^"SK-replicaset"_"response"$
#let cluster_request_time_fk = $t^"FK-replicaset"_"request"$
#let cluster_response_time_fk = $t^"FK-replicaset"_"response"$

#let intensity_update_GSI = $lambda_"update,GSI"$
#let subintensity_update_GSI = $lambda^"sub"_"update,GSI"$
#let max_intensity_update_GSI = $lambda_"update,GSI"^"max"$
#let max_subintensity_update_GSI = $lambda_"update,GSI"^"sub,max"$

#let time_user_update_GSI = $T^"user"_"update,GSI"$
#let time_coordinate_sk_update_GSI = $T^"SK-coordinate"_"update,GSI"$
#let time_coordinate_fk_update_GSI = $T^"FK-coordinate"_"update,GSI"$
#let time_execute_sk_update_GSI = $T^"SK-execute"_"update,GSI"$
#let time_execute_fk_update_GSI = $T^"FK-execute"_"update,GSI"$

#let service_time_coordinate_update_GSI = $W^"coordinate"_"update,GSI"$
#let service_time_execute_sk_update_GSI = $W^"execute"_"SK-update,GSI"$
#let service_time_execute_fk_update_GSI = $W^"execute"_"FK-update,GSI"$
#let queue_time_execute_update_GSI = $W^"execute,q"_"update,GSI"$

#let queue_length_execute_update_GSI = $L^"execute"_"update,GSI"$

#let load_executor_update_GSI = $rho^"executor"_"update,GSI"$
#let queue_time_total_update_GSI = $W^"total,q"_"update,GSI"$
#let time_service_update_GSI = $T^" service"_"update,GSI"$
#let load_update_GSI = $rho_"update,GSI"$

#let btree_node_jumps_update_GSI = btree_node_jumps_search_GSI
#let btree_node_search_ops_update_GSI = btree_search_ops_total_search_GSI
#let btree_node_split_probability_value_update_GSI = $0.19$
#let btree_free_space_before_overflow_long_update_GSI = $#btree_node_split_probability_value_update_GSI (#btree_max_keys)$
#let btree_free_space_before_overflow_inv_update_GSI = $5.26 / #btree_max_keys$

#let time_execute_sk_update_GSI_right_side = $#cluster_request_time_sk + #exec_plan_size / #cluster_net_speed + #service_time_execute_sk_update_GSI + #cluster_response_time_sk$
#let time_execute_fk_update_GSI_right_side = $#cluster_request_time_fk + #exec_plan_size / #cluster_net_speed + #service_time_execute_fk_update_GSI + #cluster_response_time_fk$

#let random_part_of_tcs_update_GSI = $UU^"c"$
#let deterministic_part_of_tcs_update_GSI = $CC^"c"$
#let random_part_of_tus_update_GSI = $UU^"u"$
#let deterministic_part_of_tus_update_GSI = $CC^"u"$

#let net_reqs_update_GSI_name = $"NR"^"GSI"_"update"$
#let rps_update_GSI_name = $"RPS"^"GSI"_"update"$


// math model accuracy stuff
#let MAPE_rps = $"MAPE"_"RPS"$
#let MAPE_timeout = $"MAPE"_"timeout"$
#let MAPE_T_user = $"MAPE"_T$
#let MAPE_queue = $"MAPE"_"queue"$
