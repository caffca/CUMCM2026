# VALIDATION PLAN（人读版，与 JSON 逐条同判据）

冻结时间：2026-09-12T11:55:20+08:00（早于任何生产运行）· 依据 FMS v4 + QUESTION_CONTRACT capabilities

| id | 问 | 判据（机器） | 级别 | 反宣称 |
|---|---|---|---|---|
| V-Q1-01 | Q1 | `equals(results:symdiff_vs_evaluator,0)` | must | 三实现共享同一隐蔽 bug（要求 checker 为不 import 主实现的第二代码路径） |
| V-Q1-02 | Q1 | `equals(results:three_way_max_symdiff,0)` | must | — |
| V-Q1-03 | Q1 | `equals(results:boundary_cases_failed,0)` | must | — |
| V-Q1-04 | Q1 | `equals(results:result1_edge_symdiff,0)` | must | — |
| V-Q1-05 | Q1 | `equals(results:classpair_sum_minus_total,0)` | must | — |
| V-Q1-06 | Q1 | `threshold_gte(results:stress_min_recall,0.99)` | recommended | — |
| V-Q2-01 | Q2 | `equals(results:residual_pairs_second_impl,0)` | must | checker 与被检实现同源（要求：checker 不得 import 求解代码，独立区间算术） |
| V-Q2-02 | Q2 | `equals(results:compliance_violations,0)` | must | — |
| V-Q2-03 | Q2 | `threshold_gte(results:ladder_proven_revoke_lb,1)` | must | — |
| V-Q2-04 | Q2 | `threshold_gte(results:degeneracy_ratio,0.05)` | must | — |
| V-Q2-05 | Q2 | `equals(results:tuple_matches_second_impl,1)` | must | — |
| V-Q2-06 | Q2 | `absolute_improvement_gte(results:revoke,results:grasp_revoke_median)` | recommended | — |
| V-Q2-07 | Q2 | `equals(results:table_closure_diff,0)` | must | — |
| V-Q2-08 | Q2 | `equals(results:gap_revoke,0)` | recommended | — |
| V-Q3-01 | Q3 | `equals(results:conflict_total_second_impl,0)` | must | — |
| V-Q3-02 | Q3 | `equals(results:cand_count_second_impl_minus_solver,0)` | must | — |
| V-Q3-03 | Q3 | `threshold_gte(results:ub_min_minus_lb,0)` | must | — |
| V-Q3-04 | Q3 | `equals(results:gap_certified,0)` | recommended | — |
| V-Q3-05 | Q3 | `equals(results:result3_rows_minus_phi,0)` | must | — |
| V-Q3-06 | Q3 | `equals(results:base_is_production_q2,1)` | must | — |
| V-Q3-07 | Q3 | `threshold_gte(results:alt2B_ran,1)` | optional | — |
| V-Q4-01 | Q4 | `equals(results:violations_second_impl,0)` | must | — |
| V-Q4-02 | Q4 | `equals(results:planted_q2_feasible,1)` | must | — |
| V-Q4-03 | Q4 | `absolute_improvement_gte(results:scalar,results:scalar_q2_ref)` | must | 『不劣于』只是域包含的构造性必然 ⇒ 必须另报严格改善量（见 V-Q4-04），不得把构造必然包装成发现 |
| V-Q4-04 | Q4 | `threshold_gte(results:revoke_gain_vs_q2,1)` | recommended | — |
| V-Q4-05 | Q4 | `equals(results:tuple_matches_second_impl,1)` | must | — |
| V-Q4-06 | Q4 | `equals(results:table_closure_diff,0)` | must | — |

判定纪律：must FAIL/UNKNOWN → result_review BLOCK 并按预注册 failure_class 回退；recommended FAIL → 降级表述登记；optional 跳过记 SKIPPED。