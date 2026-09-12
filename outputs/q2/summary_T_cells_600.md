# Q2 求解摘要

- policy: `T`
- mode: `full`
- proven_optimal: `False`
- plans: `150`
- candidate states: `4582`
- state conflict edges used: `270626`
- lazy cuts added: `0`
- solver iterations: `1`

## 目标向量

| 层 | 值 | 状态 | 下界 | gap | 秒 |
|---|---:|---|---:|---:|---:|
| C | 10 | FEASIBLE | 5.0 | 0.5 | 601.002 |

## 分类统计

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 0 | 0 | 1 | 1 |
| 调整 | 18 | 32 | 89 | 139 |
| 撤销 | 2 | 8 | 0 | 10 |

## 复验

- canonical validation: plans=150, occurrences=1262, conflicts=0, ok=True
- fast selected-state conflict count: `0`

本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。
