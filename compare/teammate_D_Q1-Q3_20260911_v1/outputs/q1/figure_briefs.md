# Q1 Figure Brief

- figure_id: `fig_q1_conflict_structure`
- question: D 题问题 1
- purpose: 展示冲突装备对的类别结构，并为 Q2 的耦合消解提供定位依据
- supported_claim: 297 对冲突中 B-C 占 181 对，且按 3,600 个可能 B-C 配对归一化后的冲突率 5.03% 仍为最高
- source: `outputs/q1/conflict_pairs.csv`、`outputs/q1/plot_data/conflict_counts_by_category.csv`、`outputs/q1/plot_data/degree_by_plan.csv`
- unit_and_population: 150 个原始装备计划；左图为二元邻接关系，右图为各类别组合的冲突装备对占该组合全部可能配对的百分比
- aggregation: 每个无序装备对只计一次；条末为“冲突对数/可配对数”
- uncertainty: none，结果来自确定性完整枚举
- required_comparison: A-A、A-B、A-C、B-B、B-C、C-C 六类组合
- final_width_mm: 155
- language: zh-CN
- forbidden_inference: 不据此直接决定 Q2 平移对象，不把装备对数 297 与事件重叠次数 431 混同
- visual_qa: 彩色、灰度和 155 mm 画布均已检查；SVG 保留文本元素；标注无遮挡
- delivery: `figures/fig_q1_conflict_structure.pdf`、`figures/fig_q1_conflict_structure.svg`、`figures/fig_q1_conflict_structure.png`
