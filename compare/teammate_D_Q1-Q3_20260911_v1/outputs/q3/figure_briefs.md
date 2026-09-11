# Q3 Figure Brief

- figure_id: `fig_q3_addition_layout`
- question: D 题问题 3
- purpose: 展示固定 Q2 计划形成的可行 C 类候选起点，以及集合装填模型选中的新增计划和其时间分布
- supported_claim: 当前六撤销 Q2 方案和 `[0,643)×[0,100)` 资源域下，52,136 个完整候选中 2,334 个与 Q2 不冲突，最多选中 141 个新增 C 类计划
- source: `outputs/q3/q2_input_from_result2.json`（由批准的 `outputs/q2/result2.xlsx` 解析）、`outputs/q3/results.json`、`outputs/q3/validation.json`、`outputs/q3/plot_data/feasible_candidate_starts.csv`、`outputs/q3/plot_data/selected_start_positions.csv`
- unit_and_population: C 类完整模板；频段宽度 3、单次时长 2、空闲间隔 8、使用 12 次；起点按离散时间/频段刻度；数量单位为台
- aggregation: 左图逐点展示可行候选与选中起点；右图按首次时间起点区间计数
- uncertainty: 基准场景求解器已返回最优状态；结论以当前冻结的具体 Q2 方案为条件
- required_comparison: `candidate:feasible_under_fixed_q2`、`solution:selected_q3_templates`
- final_width_mm: 155
- language: zh-CN
- forbidden_inference: 不把 141 台推广为任意 Q2 方案或任意时间域下的结论；不把右图分布当作优化目标；不以空闲面积除以 72 代替完整模板可行性
- visual_qa: 彩色与灰度 PNG 已实际检查；图例、坐标轴、条末数量和左右图标题无遮挡；SVG 无嵌入栅格且保留文本元素
- delivery: `figures/fig_q3_addition_layout.pdf`、`figures/fig_q3_addition_layout.svg`、`figures/fig_q3_addition_layout.png`
