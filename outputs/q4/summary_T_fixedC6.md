# Q4 求解摘要

Q4 从原始 Q1 计划重新建模；C 类增加间隔调整候选，不复用某个 Q2 结果作为约束。

- horizon: `[0,643)`
- policy: `T`
- candidate states: `6103`
- state conflict edges (audit): `444561`
- cell cliques (solve): `53679`

## 目标向量

| 指标 | 值 |
|---|---:|
| C | 6 |
| M | 115 |
| P_A | 16 |
| C_A | 1 |
| P_B | 37 |
| C_B | 5 |
| S_sum | 819 |
| S_max | 10 |

## 求解层状态

| 层 | 状态 | 值 | 下界 | gap | 秒 |
|---|---|---:|---:|---:|---:|
| C | FIXED | 6 | 6.0 | 0.0 | 0.000 |
| M | FEASIBLE | 115 | 81.0 | 0.2956521739130435 | 120.348 |

## 分类统计

| 类别 | 保留 | 调整 | 撤销 |
|---|---:|---:|---:|
| A | 4 | 15 | 1 |
| B | 3 | 32 | 5 |
| C | 22 | 68 | 0 |

## 统一复验

- plans: `150`
- occurrences: `1277`
- conflicts: `0`
- boundary violations: `0`
- fast selected-state conflicts: `0`
- canonical ok: `True`

Q4 的 gap 状态仅允许 C 类使用，且与频移、时间平移和撤销互斥；结果不得与 Q2 的排程行混合解释。
若某层状态为 UNKNOWN 或 FEASIBLE，目标值只能作为 incumbent/边界报告，不能写成严格词典序最优。
