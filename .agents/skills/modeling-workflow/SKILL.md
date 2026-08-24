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
3. 整理正式脚本、结果和图表。
4. 创建 `outputs/qX/summary.md`。
5. 更新 `docs/CURRENT_PROGRESS.md`。
6. 运行最低成本检查并创建 local milestone commit。

`summary.md` 至少说明：问题、模型、假设、关键输入、关键结果、选择理由、主要验证、
对应代码、对应图表和仍存在的问题。不复制完整终端日志，不计算 hash，不建立大型 manifest。

## 共同原则

- 先用简单充分模型，再根据证据升级。
- baseline 是比较基准，不是必须堆叠的算法清单。
- 验证针对真正可能改变结论的风险。
- 负结果和 mixed result 如实保留。
- 不把缺失数据或未运行方案写成结果。
