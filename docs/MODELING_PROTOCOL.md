# Modeling Guide

这是一份比赛期间的轻量建模指南，不预设尚未提供的题目、假设、目标函数或参数。

## Core principles

- 先诊断问题，再选能回答问题的最简单充分模型。
- baseline 是判断复杂模型是否必要的参照。
- 复杂度必须解决已诊断的明确不足，并带来可重复收益或结构价值。
- 黑盒模型进入主结论时，说明 baseline、评估方式和至少一种合适解释。
- 精确优化可行时优先 LP / MILP / convex / DP / graph algorithm；启发式方法说明必要性。
- negative / mixed result 如实保留；不把 correlation 写成 causality。
- 不把题目或附件没有提供的证据写成实验结果。

## Baseline → stronger model

每一问先建立可解释 baseline 或 exact reference。只有当 baseline 的不足被实际结果、
残差、约束冲突或问题结构诊断出来，才升级模型，并说明：

1. 不足是什么；
2. 哪个证据暴露了不足；
3. 新模型解决什么；
4. 收益或结构价值是否足够支持复杂度。

## Validation by risk

只做会改变结论的验证：

- 预测题：泛化误差、合理的数据划分和必要的残差检查；
- 优化题：约束满足、解质量和必要的小规模对照；
- 评价题：权重、参数或情景敏感性；
- 机制题：核心假设和关键关系是否成立。

不要求每一问机械完成 baseline、CV、ablation、sensitivity、robustness、oracle、
error decomposition 全套检查。

## Result discipline

正式指标由代码生成，不手工修改。论文、摘要、图表和结果使用同一口径。证据不足时
明确写 `not evaluated`、`insufficient evidence`、`mixed result` 或 `requires further validation`。
