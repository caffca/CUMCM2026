# Q2 当前结果记录（2026-09-11）

本文件是 Q2 的阶段性、可复查结果，不把限时 incumbent 写成完整的严格词典序最优。模型统一采用 `H=643`、频率域 `[0,100)`、整数半开区间、每个计划一个候选状态；资源单元团约束与 270,626 条状态冲突边等价，并由统一检测器复验。

## T：题面顺序主方案

- 总撤销层已严格确定：`C<=5` 在完整状态模型上 INFEASIBLE；`C=6` 零冲突排程存在，因此 `C*=6`。
- 当前 T 调整层 incumbent：`M=120`，CP-SAT 下界 `88`，`M<=119` 在 300 s 内为 `UNKNOWN`，所以不能称 `M*=120`。
- 在条件前缀 `C=6, M=120` 下的类别保护 incumbent：`P_A=15, C_A=1, P_B=38, C_B=5, P_C=73`；其余位移层未完成严格证明。
- 该 T incumbent 的原始位移为 `Σ|df|=619`、`Σ|dt|=114`，故 `S_sum=619+2×114=847`；最大单计划频移/时移分别为 10/5。
- 条件结果：`outputs/q2/selected_T_cells_tiebreak120_300.json`、`solver_T_cells_tiebreak120_300.json`、`result2_T_cells_tiebreak120_300.xlsx`。

## P：优先级优先对照

在完全相同的候选状态与可行域上先保护 A/B，再优化总撤销、调整和位移；8 个词典序层均为 `OPTIMAL`，统一复验冲突数为 0：

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 20 | 20 | 2 | 42 |
| 调整 | 0 | 17 | 13 | 30 |
| 撤销 | 0 | 3 | 75 | 78 |

目标向量为 `(P_A,C_A,P_B,C_B,C,M,S_sum,S_max)=(0,0,20,3,78,30,192,10)`。

P 的原始位移为 `Σ|df|=82`、`Σ|dt|=55`，满足 `S_sum=82+2×55=192`；最大单计划频移/时移为 10/5。

新增隐含强传播约束后重新复核，8 层仍全部 `OPTIMAL` 且指标完全一致；当前优先引用 `solver_P_cells_verified.json`、`selected_P_cells_verified.json`、`result2_P_cells_verified.xlsx`。

## E：有界情景

已探索 `C<=7, M<=121` 的 P 优先级情景，得到零冲突可行 incumbent `P_A=13`，但首层限时未证明最优；在 T 的完整词典序前缀尚未全部证明前，E 只作为敏感性记录，不进入正式主比较表。证据：`solver_E_dc1_dm1_probe.json`。

## 复验与限制

- Q1--Q2 回归测试：14/14 通过；所有保留结果经 `validate_schedule()` 复验，冲突数为 0。
- 3 组真实四计划子集的全组合穷举与 edge/cell/lazy 三种 CP-SAT 结果完全一致，记录于 `outputs/q2/subset_validation.json`；该证据验证实现链，不替代 150 计划全局证明。
- `C*=6` 是当前可写入论文的严格结论；T 的 `M=120`、`P_A=15` 是阶段性 incumbent/条件 incumbent，必须在正文中同时报告上下界与求解状态。
- 详细推导、常规/创新路线比较、时间线和下一步计划见 `D题/D题_建模分析全过程与决策记录.md` §6.2.6。

## 阶段性可视化

- `plot_data/q2_policy_tradeoff_stage.json` 固定了 T/P/E 的比较口径；`figures/fig_q2_policy_tradeoff_stage.pdf`（及 PNG 预览）展示总撤销/调整与 A/B/C 类行动构成。
- 图仅表达政策代价结构，不替代词典序证明；图下注明了 T/E 的限时 incumbent 和 P 的已证最优状态。
- 生成脚本：`scripts/figures/plot_q2_policy_tradeoff.py`。
