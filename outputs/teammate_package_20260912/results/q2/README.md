# Q2 结果索引

本目录同时保留探索、证书和阶段性输出；文件名中的 `T/P/E` 表示政策，`cells/edges` 表示约束表达。

问题级模型、路线比较和论文措辞见 [`D题/Q2_解题与验证阶段报告.md`](../../D题/Q2_解题与验证阶段报告.md)；模型质量、少量设备验证边界和 R² 说明见 [`D题/Q2_模型质量与验证方案.md`](../../D题/Q2_模型质量与验证方案.md)。本地与队友分支的目标协议和证据接入规则见 [`D题/本地与队友D分支对比审计_待核验.md`](../../D题/本地与队友D分支对比审计_待核验.md)。

| 文件 | 作用 | 是否可称严格最优 |
|---|---|---|
| `summary.md` | 当前阶段性结论、限制和证据入口 | 仅 C 层与 P 对照按文件内说明 |
| `edge_equivalence_audit.json` | 全状态边、资源团与统一检测器的一致性审计 | — |
| `subset_validation.json` | 3 组真实四计划子集的全组合穷举，对照 edge/cell/lazy 求解器 | 实现正确性证据，不是全实例证明 |
| `solver_T_cells_budget5.json` | `C<=5` 不可行证书 | 是（不可行性） |
| `selected_T_cells_lexfixed.json` | T 在 `C=6` 面上的零冲突可行 incumbent | 否（M 未证） |
| `Q2-T-incumbent-v1.json` / `.md` | 冻结给 Q3 使用的 T 排程快照与使用边界 | `C*=6` 严格；`M=120` 为 incumbent |
| `solver_T_cells_budgetM119.json` | `C=6,M<=119` 的限时边界检查 | UNKNOWN，不是不可行证书 |
| `selected_T_cells_tiebreak120_300.json` | 条件前缀 `C=6,M=120` 的保护层 incumbent | 否 |
| `solver_P_cells_verified.json` | 优先级优先 P 的完整词典序报告 | 是，8 层均 OPTIMAL |
| `selected_P_cells_verified.json` / `result2_P_cells_verified.xlsx` | P 的设备变更清单与模板输出 | 与报告一致 |
| `solver_E_dc1_dm1_probe.json` | `C<=7,M<=121` 的 E 探索情景 | 否，首层限时 |
| `policy_comparison.csv` / `displacement_audit.csv` | T/P/E 指标和原始位移拆分 | 阶段性，T 前缀明确标注 |
| `plot_data/q2_policy_tradeoff_stage.json` / `figure_briefs.md` | 阶段性政策比较图的冻结输入和 brief | 图表输入；不升级未证结果 |
| `figures/fig_q2_policy_tradeoff_stage.pdf` / `.png` | T/P/E 撤销-调整及类别构成可视化 | 阶段性展示 |

所有 `selected_*.json` 与对应 `result2_*.xlsx` 均由同一候选状态索引生成，并经过 `validate_schedule()`；详细推导和时间线见 `D题/D题_建模分析全过程与决策记录.md` §6.2.6。
