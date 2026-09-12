# q4_intermediate_m139

- 分支/HEAD：`main` / `c5d1b3baa55a72f211abfdf794acd415644aef21`（工作区 dirty=True）
- 时间域：`[0,643)`；动作集合：keep / frequency-shift / time-shift / revoke; C additionally gap-shift。
- 目标顺序：`R→R_A→R_B→M→M_A→M_B→S10^(4)`；目标向量：`[3, 0, 1, 139, 19, 37, 943]`。
- 求解状态：`SAT`；最优性标签：`FEASIBLE_WITNESS`。
- 冲突数/越界数：`0` / `0`；对应 Q3 容量：`None`。
- 结论：已验证的中间 SAT 见证；被 M=136 严格支配，保留用于审计链。
- 源文件：`outputs/q4/proof_R3_RA0_RB1_M139_witness.json`；验证：`outputs/q4/proof_R3_RA0_RB1_M139_validation.json`。
