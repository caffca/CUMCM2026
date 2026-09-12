# Q4：固定最小撤销层后的次级相邻阈值证明矩阵

更新时间：2026-09-12。本文档是计算过程审计入口，不把 `UNKNOWN`、限时或旧候选升级为最优性证明。

统一口径为 `H=643`、资源域 `[0,643)×[0,100)`、150 条原计划、每条计划从有限合法动作中恰选一项；Q4 允许 C 类改变间隔，其余动作规则与 Q2 一致。Q4 主层已由 `R≤3` 可行和 `R≤2` 六个类别分支全 `UNSAT` 闭合，因此以下均固定 `R=3`。

**当前正式接口已统一为 M=136。** M=136 的 SAT 见证及独立验证严格优于 M=139、M=140 和旧 M=142；因此 `outputs/q4/result4.xlsx`、`result4_selected.json` 和 `result4_workbook_validation.json` 均指向 M=136。M=139/M=140 仍保留为审计材料，不能再标为当前最好方案。

## 证明规则

对最小化目标 (z)，必须同时具备：

1. 一个通过独立重建的可行见证 (zle u)；
2. 在相同更高层前缀下，对相邻阈值 (zle u-1) 返回 `UNSAT` 的有限模型证据。

`SAT` 只降低上界，`UNKNOWN`/`TIMELIMIT` 不提供下界；只有上下界相等时才登记为 `PROVED_OPTIMAL`。

## 当前矩阵

| 层级 | 固定前缀 | 相邻阈值 | 当前证据 | 状态 | 结论 |
|---|---|---|---|---|---|
| 撤销总数 (R) | 无 | (Rle2) | 六个类别配额 SAT 分支全 `UNSAT`；`R=3` 见证验证 PASS | 已闭合 | (R^*=3) |
| A 类撤销 (R_A) | (R=3) | (R_Ale-1) | 自然下界 0，且已有 (R_A=0) 见证 | 已闭合 | (R_A^*=0) |
| B 类撤销 (R_B) | (R=3,R_A=0) | (R_Ble0)（即 A/B 不撤销、C 撤销 3 台） | MapleChrono 独立 SAT 模型返回 `UNSAT`；前序 CP-SAT、CSP、Glucose3/4、SCIP 结果仅作旁证 | 已闭合 | (R_B^*=1) |
| 调整数 (M) | (R=3,R_A=0,R_B=1) | (Mle141) | SAT；独立验证 PASS，实际 (M=140) | 反驳旧上界 | 旧 (M=142) 已失效 |
| 调整数 (M) | 同上 | (Mle139) | SAT；独立验证 PASS，实际 (M=139) | 反驳旧上界 | 当前可行上界至少降至 139 |
| 调整数 (M) | 同上 | (Mle138) | SAT；feature-aware 安全支配约简，独立验证 PASS，实际 (M=138) | 反驳旧上界 | 当前可行上界至少降至 138 |
| 调整数 (M) | 同上 | (Mle137) | MapleChrono feature-aware SAT：`SAT`，独立验证 PASS，实际 (M=136) | 反驳旧上界 | 当前可行上界至少降至 136 |
| 调整数 (M) | 同上 | (Mle136) | 同一独立见证重算得到 (M=136)，验证 PASS；显式紧阈值重跑未及时返回 | 可行上界 | 尚非最优证明 |
| 调整数 (M) | 同上 | (Mle135) | MapleChrono（feature-aware、adjustment-aware）与 CaDiCaL195 均 `UNKNOWN`；CP-SAT warm-start 亦 `UNKNOWN` | 未闭合 | 不能暂定 (M^*=136) |
| A 类调整 (M_A) | 需先固定 (M^*) | (M_Ale M_A^*-1) | 尚未运行 | 未闭合 | — |
| B 类调整 (M_B) | 需先固定 (M^*,M_A^*) | (M_Ble M_B^*-1) | 尚未运行 | 未闭合 | — |
| 末级 (S_{10}^{(4)}) | 需先固定上述前缀 | (S_{10}^{(4)}le S_{10}^{(4)*}-1) | 已加入计划成本指示器编码，待前层固定后运行 | 未闭合 | — |

## 已验证的新见证

`proof_R3_RA0_RB0_infeasible.json` 是固定 `R=3,R_A=0,R_B=0,R_C=3` 的独立 SAT 不可行性证据，返回 `UNSAT`。因此相邻阈值 `R_Ble0` 已排除，结合 `R_B=1` 可行，得到 `R_B^*=1`。

`proof_R3_RA0_RB1_M140_witness.json` 是 `M≤141` SAT 返回的方案，独立回读为 `PASS`，统计为 A `0/20/0`、B `0/39/1`、C `7/81/2`，实际 (M=140)。

`proof_R3_RA0_RB1_M139_witness.json` 是 `M≤139` SAT 返回的方案，独立回读为 `PASS`，统计为 A `1/19/0`、B `2/37/1`、C `5/83/2`，实际 (M=139)。两份见证均使用完整的 Q4 合法动作语义；它们是可行上界，不是相邻阈值不可行证明。

`proof_R3_RA0_RB1_M138_witness.json` 是 `M≤138` SAT 返回的方案，独立回读为 `PASS`，统计为 A `0/20/0`、B `2/37/1`、C `7/81/2`，实际 (M=138)。该次安全支配约简保持类别、调整标志和不增的末级平移代价，故只用于缩小等价搜索域；它仍然只给出可行上界，`Mle137` 尚未闭合。

`proof_R3_RA0_RB1_M136_witness.json` 由 `M≤137` 的 SAT 见证复制归档，但对其 150 条选择重新计数得到 A `19`、B `36`、C `81`，即实际 `M=136`；独立重建验证为 `PASS`。因此它是 (Mle136) 的可行见证，不是 (M) 的下界证明。

对 `M≤135` 已完成三条独立计算路径：feature-aware MapleChrono、adjustment-aware MapleChrono、adjustment-aware CaDiCaL195，以及带 `M=136` warm-start 的 CP-SAT；它们均未在预算内返回 `UNSAT` 或新的更小见证，统一登记为 `UNKNOWN`，不构成不可行性结论。

## 计算入口

- Q4 主模型：[solve_q4_cp_sat.py](../../scripts/solve_q4_cp_sat.py)
- 独立 SAT 阈值模型：[prove_q4_active_sat.py](../../scripts/prove_q4_active_sat.py)
- 独立重建验证：[validate_q4.py](../../scripts/validate_q4.py)
- 新见证及验证：`proof_R3_RA0_RB1_M140_*`、`proof_R3_RA0_RB1_M139_*`
- Q4 主层覆盖证明：[r2_global_proof_status.md](r2_global_proof_status.md)

在本矩阵中，任何 `UNKNOWN`、`TIMELIMIT` 或“运行中”条目都不会进入论文的“最优”措辞；只有完成相邻阈值 `UNSAT` 后，才更新 `summary.md`、`q4_optimization_audit.md`、工作簿和论文正文。
