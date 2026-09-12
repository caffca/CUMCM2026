# D 题问题三：固定六撤销 Q2 后的新增结果

问题三固定经用户批准的 `outputs/q2/result2.xlsx` 中的 144 个活动计划。工作簿先被反向解析为动作表并通过 Q2 独立验证，再只在剩余 `[0,643)×[0,100)` 资源中新增完整 C 类模板；不反向改变 Q2。

C 类模板宽 3、单次时长 2、间隔 8、使用 12 次，相邻起点步长为 10，每个计划占用 72 个资源格。整数起点共有 52,136 个，筛除与 Q2 冲突者后剩 2,334 个候选。0-1 集合装填模型选中 **141 台**，HiGHS 返回 `OPTIMAL`，上界同为 141，`mip_gap=0`。独立的候选两两冲突模型仍得到 141，并证明“至少 142 台”不可行。

固定 Q2 占用 15,816 个资源格；新增计划占用 10,152 个资源格；合并后 285 个活动计划共占 25,968 个不同资源格。独立验证重新检查全部重复事件、边界、Q2—Q3 冲突、Q3 内部冲突及工作簿逐行一致性，结果为 `PASS`。

141 小于旧 19 撤销 Q2 背景下的 203，是因为新 Q2 只撤销 6 个计划，保留背景更多、剩余容量更少。旧 203 已被 supersede，不能与新 `result2.xlsx` 配套使用。

正式资产：`q2_input_from_result2.json`（由批准的 `result2.xlsx` 解析）、`results.json`、`q3_optimality_audit.json`、`q3_optimization_audit.md`、`result3.xlsx`、`validation.json`、`figures/fig_q3_addition_layout.{pdf,svg,png}` 及 `plot_data/`。
