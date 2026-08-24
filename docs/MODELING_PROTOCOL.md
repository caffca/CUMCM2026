# Modeling Protocol

Protocol version: v0.1
Status: draft
Freeze status: not frozen

## 1. Modeling Philosophy

核心原则：

> Problem diagnosis → minimal adequate model → stronger alternative only if justified → validation → sensitivity / robustness → decision.

不追求算法数量，不追求“看起来高级”。复杂度必须由问题结构和证据支持。

## 2. Problem Definition

- Official problem: TBD
- Primary decision / prediction / explanation target: TBD
- Required outputs: TBD
- Hard constraints from statement: TBD
- Units and coordinate/time conventions: TBD

## 3. Assumptions

仅记录真正影响模型成立条件的假设。

| ID | Assumption | Why needed | Risk if violated | Status |
|---|---|---|---|---|
| A-001 | TBD |  |  | proposed |

## 4. Model Selection Rules

### Baseline

每个非平凡问题优先建立可解释 baseline 或 exact reference。

### Escalation

更复杂模型必须说明：

1. 简单模型的明确不足是什么；
2. 该不足的诊断证据是什么；
3. 新模型解决什么；
4. 新模型相对 baseline 是否有可重复收益或结构价值。

### Black-box models

XGBoost / LightGBM / RF / NN 等若用于主结论，至少需要：

- 与简单 baseline 对比；
- 合理的数据划分 / CV；
- error / residual analysis；
- feature importance / SHAP / PDP / sensitivity 中至少一种合适解释。

### Optimization

优先使用问题结构匹配的精确或可证明方法：LP / MILP / convex / DP / graph algorithm。

启发式 / metaheuristic 只有在非凸、组合规模或时间预算确实需要时使用；可行时用小规模 exact solution 比较 optimality gap。

## 5. Validation Contract

按问题选择必要项目，不机械全做：

- baseline comparison
- train/validation/test or grouped CV
- residual analysis
- sensitivity analysis
- robustness / perturbation
- constraint satisfaction
- exact small-scale oracle
- scenario analysis
- error decomposition

每项验证必须对应一个明确风险。

## 6. Evidence Boundaries

禁止：

- 手工修改正式指标；
- 为了故事删除失败结果；
- 把 negative/mixed result 写成 stable improvement；
- 题目未提供数据却编造“实验结果”；
- 把 correlation 写成 causality；
- 结果与正文、摘要、图表使用不同口径。

证据不足时使用：

```text
not evaluated
insufficient evidence
mixed result
requires further validation
```

## 7. Final Model Selection Rule

TBD — 在正式比较前冻结；不得看完最终结果后再倒推修改。

## 8. Sensitivity / Robustness Rule

TBD — 根据题型冻结关键参数、权重或情景的扰动范围。

## 9. Change Log

| Version | Date | Change | Decision |
|---|---|---|---|
| v0.1 | bootstrap | Initial protocol skeleton | none |
