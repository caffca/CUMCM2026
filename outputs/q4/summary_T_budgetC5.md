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
| C | None |
| M | None |
| P_A | None |
| C_A | None |
| P_B | None |
| C_B | None |
| S_sum | None |
| S_max | None |

## 求解层状态

| 层 | 状态 | 值 | 下界 | gap | 秒 |
|---|---|---:|---:|---:|---:|
| C | UNKNOWN | None | None | None | 189.091 |

## 分类统计

| 类别 | 保留 | 调整 | 撤销 |
|---|---:|---:|---:|
| A | 20 | 0 | 0 |
| B | 40 | 0 | 0 |
| C | 90 | 0 | 0 |

## 统一复验

- 本预算下没有返回可复验的完整排程；不能生成正式 result4。
- solver status: `NO_FEASIBLE_SELECTION`

Q4 的 gap 状态仅允许 C 类使用，且与频移、时间平移和撤销互斥；结果不得与 Q2 的排程行混合解释。
若某层状态为 UNKNOWN 或 FEASIBLE，目标值只能作为 incumbent/边界报告，不能写成严格词典序最优。
