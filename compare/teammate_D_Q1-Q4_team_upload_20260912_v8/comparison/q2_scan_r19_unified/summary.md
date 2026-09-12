# q2_scan_r19_unified

- 分支/HEAD：`main` / `c5d1b3baa55a72f211abfdf794acd415644aef21`（工作区 dirty=True）
- 时间域：`[0,643)`；动作集合：keep / frequency-shift / time-shift / revoke; complete repeated events。
- 目标顺序：`R→R_A→R_B→M→M_A→M_B→S10`；目标向量：`[19, 0, 0, 114, 17, 36, 733]`。
- 求解状态：`FEASIBLE_INCUMBENT`；最优性标签：`NOT_PROVED`。
- 冲突数/越界数：`0` / `0`；对应 Q3 容量：`106`。
- 结论：同为 R=19 但保护顺序和占用集合不同；用于说明不能只按撤销数预测 Q3。
- 源文件：`outputs/q2_q3_pareto/R19/q2/results.json`；验证：`outputs/q2_q3_pareto/R19/q2/validation.json`。
