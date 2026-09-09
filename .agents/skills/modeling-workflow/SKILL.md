---
name: "modeling-workflow"
description: "Use for the CUMCM2026 explore and milestone workflow: minimum-sufficient modeling, bounded computation, validation, and question-level artifacts."
---

# Skill: modeling-workflow

用于比赛期间快速推进建模。只保留 `explore` 和 `milestone` 两种模式。

## explore

目标：快速判断当前路线是否值得继续。

```text
理解当前问题
→ 检查必要数据
→ 建 baseline / candidate
→ 实际运行
→ 查看结果
→ 诊断主要问题
→ 继续或换路线
```

适用于 EDA、数据清洗试验、候选模型、参数试验、临时图、残差查看和失败方案。
不创建 RUN ID、manifest、hash、journal 或 evidence matrix。可以使用 `tmp/`，
不要求单独 commit。

## milestone

当结果准备保留、模型准备沿用、图表准备进入论文、重要决策已确定或一问基本完成时：

1. 确认当前方案和关键假设。
2. 只做会改变结论的必要验证。
3. 实际运行求解，完成会改变结论的必要自检和一次有界修复。
4. 整理正式脚本、结果、plot-ready data 和可读的论文图表。
5. 创建 `outputs/qX/summary.md`，并把该问的模型、求解、验证、结果和小结写入论文源稿。
6. 更新 `docs/CURRENT_PROGRESS.md`。
7. 运行最低成本检查并创建 local milestone commit。

`summary.md` 至少说明：问题、模型、假设、关键输入、关键结果、选择理由、主要验证、
对应代码、对应图表和仍存在的问题。不复制完整终端日志，不计算 hash，不建立大型 manifest。

Builder 是完整初稿生产责任人。各问完成后继续全文整合，直到主要图表、caption、逐问
正文、完整源稿和实际多页 PDF 都存在并完成逐页渲染检查。不得用代码、数值、单页测试
或粗略提纲替代完整交付，也不得把正式图和主要写作默认留给 Reviewer。

## 共同原则

- 先用简单充分模型，再根据证据升级。
- baseline 是比较基准，不是必须堆叠的算法清单。
- 验证针对真正可能改变结论的风险。
- 负结果和 mixed result 如实保留。
- 不把缺失数据或未运行方案写成结果。
- 普通技术取舍直接推进；只有关键歧义、P0 或未授权资源才升级。
