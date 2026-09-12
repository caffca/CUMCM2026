# D 题问题二：六撤销里程碑

状态：`FULL_LEXICOGRAPHIC_PROVED`。第一层最少撤销数已由 CP-SAT 上下界闭合证明为 **6**；随后用独立 CNF + CaDiCaL 对各层相邻阈值做不可行性证明，精炼方案 B 的七层字典序已全部闭合。

## 模型与目标

对 150 个计划分别枚举 `keep / frequency-shift / time-shift / revoke`，所有候选均展开完整重复事件。频移满足 `|df|≤10`，时移满足 `|dt|≤5`，一次只能改变一个参数；资源域为 `[0,643)×[0,100)`，区间采用半开口径。4,582 个候选通过 52,939 条资源格团约束实现全局冲突消解。

采用精炼方案 B 的字典序：总撤销数 `R` → A 类撤销数 `R_A` → B 类撤销数 `R_B` → 参数调整数 `M` → A、B 类调整数 `M_A,M_B` → 归一化平移量 `|df|/10+|dt|/5`。只有更高层已经证明时，下一层的“最优”才成立。

## 当前正式方案

| 类别 | 保留 | 调整 | 撤销 |
|---|---:|---:|---:|
| A | 4 | 16 | 0 |
| B | 2 | 34 | 4 |
| C | 12 | 76 | 2 |
| 合计 | 18 | 126 | 6 |

撤销计划为 `B009、B018、B024、B028、C027、C054`。频移绝对值合计 595，时移绝对值合计 90，十倍归一化平移分数为 `595+2×90=775`。

## 上下界与诚实边界

| 目标层 | LB | UB | 结论 |
|---|---:|---:|---|
| `R` | 6 | 6 | 已证明最优 |
| `R_A | R=6` | 0 | 0 | 已证明最优 |
| `R_B | R=6,R_A=0` | 4 | 4 | 已证明最优 |
| `M | R=6,R_A=0,R_B=4` | 126 | 126 | 已证明最优 |
| `M_A`（上述前缀固定） | 16 | 16 | 已证明条件最优 |
| `M_B`（上述前缀及 `M_A=16` 固定） | 34 | 34 | 已证明条件最优 |
| `S10`（上述前缀固定） | 775 | 775 | 已证明最优 |

`revocation_bound.json` 保存 CP-SAT 的 `objective=6`、`best_objective_bound=6` 证书；`proof/sat_b_le_3.json` 证明 `B≤3` 不可行，`proof/sat_adjust_le_125.json` 证明 `M≤125` 不可行，另两份 SAT 证据闭合 `M_A=16` 与 `M_B=34`；`proof/sat_shift_le_774_full.json` 在完整 4,582 个候选全集上证明 `S10≤774` 不可行。外部工作簿提供具体动作见证，动作本身由独立验证复核；次级最优性来自阈值不可行性证据。

## 独立验证

`six_revocation_candidate.json` 是从外部工作簿规范化得到的动作表。两份验证重新读取原始附件并确认：144 个活动计划全部重复事件无越界；连续与离散两套检查均零冲突；15,816 个资源格无重复、最大占用为 1；调整均为单参数整数平移，宽度、时长、间隔和次数不变。

正式 `result2.xlsx` 由模板重建，只填写实际改变的参数列，撤销行写“是”，并通过工作簿复核。旧 19 撤销结果与探针保留作历史诊断，但已被 supersede，不再作为正文主结果或 Q3 输入。用户已批准当前工作簿作为 Q3 唯一接口；Q3 已从该工作簿反向解析并完成独立最优性核验。

## 正式资产

- `results.json`、`result2.xlsx`、`validation.json`、`workbook_validation.json`；
- `revocation_bound.json`、`priority_prefix_run.json`；
- `six_revocation_candidate.json`、`six_revocation_validation.json`；
- `q2_proof_matrix.csv`、`proof/SAT_EVIDENCE_INDEX.md`、`proof/sat_evidence_validation.json` 及 `proof/` 下的独立 SAT/CP-SAT 阈值证据；
- `figures/fig_q2_solution_tradeoff.{pdf,svg,png}` 及灰度 QA。
