# Q4 当前里程碑摘要

## 题目与模型

问题四从问题一的 150 条原始用频计划重新建模，不读取问题二或问题三的结果作为约束。统一资源域为 `[0,643)×[0,100)`，重复事件按“单次占用时长 + 空闲间隔”递推，区间采用半开口径。

每条计划从保持、频段平移、首次时间平移、撤销中择一；C 类额外允许间隔变化 `δg∈{-8,…,-1,1,…,10}`。所有动作在候选生成阶段展开完整重复事件，再用资源格至多占用一条约束求解。字典序按 `R→R_A→R_B→M→M_A→M_B→S10^(4)` 记录，但只有上下界闭合的层才称为已证明最优。

## 最少撤销层

`R≤3` 有独立验证的可行见证；`R≤2` 的六个类别分拆
`(R_A,R_B,R_C)` 全部返回 `UNSAT`，并由全局覆盖核验确认无遗漏。因此在当前有限动作集合和 `H=643` 下：

\[
R_{Q4}^*=3.
\]

六个分支及覆盖证明见 `proof_R_le_2_active_sat_r2_*.json`、`proof_R_le_2_global_coverage_validation.json` 和 `r2_global_proof_status.md`。

## 当前正式可行方案（统一为 M=136）

仓库中已验证的 M=136 见证严格优于 M=139、M=140 和旧的 M=142，因此按照“更好的已验证可行解立即更新上界”规则，当前 `result4.xlsx` 与 `result4_selected.json` 统一采用 M=136。M=139、M=140 文件仍作为可追溯的审计见证保留，不再作为当前最好方案。

| 类别 | 保留 | 调整 | 撤销 |
|---|---:|---:|---:|
| A | 1 | 19 | 0 |
| B | 3 | 36 | 1 |
| C | 7 | 81 | 2 |
| 合计 | 11 | 136 | 3 |

当前正式目标向量为
`(R,R_A,R_B,M,M_A,M_B,S10^(4))=(3,0,1,136,19,36,924)`。
这是固定 `R=3,R_A=0,R_B=1` 前缀下的当前最好可行上界；M 的相邻阈值、后续类别调整层和末级平移量尚未全部作出不可行证明，不能写成完整次级字典序最优。

## 工作簿一致性

- `result4.xlsx` 由 `result4_selected.json` 的 M=136 动作重建，显式动作行 139，11 台计划按模板语义隐式保持不变。
- `result4_workbook_validation.json` 记录 Artifact Tool 导出检查、工作簿回读、动作集合一致性及独立验证路径。
- `result4_M136_workbook_validation_independent.json`：147 个活动计划，连续/离散冲突均为 0，越界为 0，不同占用格 16,356，最大格占用 1，重算目标与报告目标一致。
- 旧 M=142 工作簿保留为 `result4_legacy_20260912.xlsx`；此前生成的 M=139 工作簿保留为 `result4_M139_legacy_20260912.xlsx`。

## 证据边界

`proof_R3_RA0_RB1_M136_witness.json`、`proof_R3_RA0_RB1_M139_witness.json` 和 `proof_R3_RA0_RB1_M140_witness.json` 都是 SAT 可行见证；独立验证文件证明动作合法且无冲突，但 SAT 可行本身不是 M 的下界。只有在同一固定前缀下补齐 `M≤m-1` 的 UNSAT 证据后，才可把某个 M 写成条件最优。

## 复现入口

- 主层覆盖：[r2_global_proof_status.md](r2_global_proof_status.md)
- 次级证据矩阵：[q4_secondary_proof_matrix.md](q4_secondary_proof_matrix.md)
- SAT 求解器：[prove_q4_active_sat.py](../../scripts/prove_q4_active_sat.py)
- 独立核验：[validate_q4.py](../../scripts/validate_q4.py)
- 当前动作接口：[result4_selected.json](result4_selected.json)
- 当前工作簿：[result4.xlsx](result4.xlsx)
