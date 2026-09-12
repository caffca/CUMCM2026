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
| C | 8 | FEASIBLE | 4.0 | 0.5 | 60.268 |

## 分类统计

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 1 | 0 | 0 | 1 |
| 调整 | 17 | 34 | 90 | 141 |
| 撤销 | 2 | 6 | 0 | 8 |

## 复验

- canonical validation: plans=150, occurrences=1270, conflicts=0, ok=True
- fast selected-state conflict count: `0`

本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。
