# Q2 SAT/CaDiCaL 证据索引

更新时间：2026-09-12  
用途：给队友复核 Q2 字典序前缀；本索引只整理已存在的 CNF 证书，不会把临时日志或导入可行解误标为最优证明。

## 结论先看

五个阈值测试均返回 `UNSAT`，因此对应阈值“无解”已经闭合。每个阈值的上一层可行方案已在同一候选全集中给出，所以可以得到完整的七层字典序结论：

`R_B=4`、`M=126`、`M_A=16`、`M_B=34`、`S10=775`（均是在更高字典序层固定后的条件最优）。

末级平移量 `S10=Σ(|df|+2|dt|)=775` 已由 `S10≤774` 的全候选 `UNSAT` 证书闭合；对应的归一化量为 `S_n=77.5`。

## 证书清单

| probe | 被检验的阈值（假设可行） | 实际状态 | 证书结论 | 正式文件 |
|---|---|---|---|---|
| `b_le_3` | `R=6, R_A=0, R_B≤3` | `UNSAT` | `R_B≥4`；结合 incumbent `R_B=4`，得到 `R_B=4` | [`sat_b_le_3.json`](sat_b_le_3.json) |
| `adjust_le_125` | `R=6, R_A=0, R_B=4, M≤125` | `UNSAT` | `M≥126`；结合 incumbent `M=126`，得到 `M=126` | [`sat_adjust_le_125.json`](sat_adjust_le_125.json) |
| `adjust_a_le_15` | `R=6, R_A=0, R_B=4, M=126, M_A≤15` | `UNSAT` | `M_A≥16`；结合 incumbent `M_A=16`，得到 `M_A=16` | [`sat_adjust_a_le_15.json`](sat_adjust_a_le_15.json) |
| `adjust_b_le_33` | `R=6, R_A=0, R_B=4, M=126, M_A=16, M_B≤33` | `UNSAT` | `M_B≥34`；结合 incumbent `M_B=34`，得到 `M_B=34` | [`sat_adjust_b_le_33.json`](sat_adjust_b_le_33.json) |
| `shift_le_774` | `R=6, R_A=0, R_B=4, M=126, M_A=16, M_B=34, S10≤774` | `UNSAT` | `S10≥775`；结合可行方案 `S10=775`，得到 `S10=775` | [`sat_shift_le_774_full.json`](sat_shift_le_774_full.json)、[`sat_shift_le_774.json`](sat_shift_le_774.json) |

前四份证书的共同模型元数据为 `H=643`、`4582` 个候选动作、`150` 个原计划、`52939` 条资源格团约束；末级阈值的全候选证书 `sat_shift_le_774_full.json` 使用相同的 `4582` 个候选和 `52939` 条资源格约束，求解器为 CaDiCaL `cadical195`。`sat_shift_le_774.json` 是同一阈值的当前层指示器编码复核，使用保真支配缩减后的 `4514` 个候选。机器可读的交叉核对结果见 [`sat_evidence_validation.json`](sat_evidence_validation.json)。

## 如何解释 SAT 状态

- `UNSAT`：在证书中写明的全部条件下不存在解，可作为该阈值的下界证据。
- `SAT`：只说明找到了一个满足条件的见证解，不能单独推出最优。
- `UNKNOWN`、超时或中断：不能当作上下界闭合。
- `PASS`：表示验证器的数据/约束复核通过，不等于求解器证明最优。

因此 `outputs/q2/six_revocation_candidate.json` 中的 `IMPORTED_FEASIBLE_CANDIDATE` 是导入来源标签，不能替代本索引中的 `UNSAT` 证书；该文件已增加 `canonical_status` 和 `canonical_proof_reference` 以消除歧义。

## 与 Q2 正式结果的关系

- 正式总目标：`R=6`（CP-SAT 的 LB=UB 已闭合）。
- 精炼方案 B 前缀：`R → R_A → R_B → M → M_A → M_B` 已闭合，正式状态标签为 `FULL_LEXICOGRAPHIC_PROVED`。
- 末级 `S10=775` 由六撤销可行方案给出上界，并由 `sat_shift_le_774_full.json` 的全候选 `UNSAT` 证书给出下界，状态为 `PROVED_OPTIMAL`。
- [`outputs/q2/results.json`](../results.json) 的 `proof_chain` 已改为引用本目录下的正式证书；`tmp/q2_proof_sat_*.json` 只保留为本机生成日志，不能作为队友包的唯一证据。

## 复核边界

本索引没有修改 `data/raw/`。若队友改变候选生成规则、半开区间语义、资源域或动作约束，必须重新生成五个阈值证书；当前证书只对 `outputs/q2/results.json` 所使用的 `4582` 候选全集有效。

## 证据元数据补充（2026-09-12）

五个阈值文件现在都包含结构化的 `evidence_metadata`：固定前缀、阈值、求解器版本、构造/求解时间、变量/约束/子句计数、生成脚本、可复现命令、原始输入哈希和对应可行见证。历史实际命令未记录的字段标记为`historical_command_verified=false`，不能将重现命令冒充历史日志。

Q2 的 CP-SAT 撤销下界 `outputs/q2/revocation_bound.json` 和前缀汇总
`outputs/q2/priority_prefix_run.json` 也保存同一复现契约；前缀汇总额外列出七个阶段的固定前缀、
相邻阈值、状态和对应证据文件。
