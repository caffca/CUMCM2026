# Q2 Figure Brief

- status: `STALE_PENDING_FINAL_REDRAW`（现有图仍含旧证明状态，论文暂不引用）
- figure_id: `fig_q2_solution_tradeoff`
- question: D 题问题 2
- purpose: 展示六撤销正式方案的类别构成，以及精炼方案 B 字典序前缀的上下界状态
- supported_claim: 总撤销 6、A 类撤销 0、B 类撤销 4、调整数 126、A/B 类调整数 16/34 已按条件字典序逐层证明；末级 S10=775 仅为可行上界
- source: `outputs/q2/results.json`、`outputs/q2/revocation_bound.json`、`outputs/q2/priority_prefix_run.json`、`outputs/q2/validation.json`
- unit_and_population: 150 个原始计划；计划数量单位为条
- aggregation: 每个计划按保留、调整或撤销恰计一次；右图逐层列出 LB、UB 与证明状态
- uncertainty: 末级平移量 S10 尚未完成全局阈值证明；其余六层前缀均已闭合
- required_comparison: `bound:lexicographic_prefix`、`solution:six_revocation_incumbent`
- final_width_mm: 155
- language: zh-CN
- forbidden_inference: 不把 S10=775 写成全局最优；不把旧 19 撤销方案混入当前结果
- visual_qa: 彩色与灰度 PNG 已实际检查，图例、数值标注和底部图例无遮挡；SVG 保留文本元素
- delivery: `figures/fig_q2_solution_tradeoff.pdf`、`figures/fig_q2_solution_tradeoff.svg`、`figures/fig_q2_solution_tradeoff.png`
