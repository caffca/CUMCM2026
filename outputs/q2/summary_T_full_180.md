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
| C | 11 | FEASIBLE | 5.0 | 0.5454545454545454 | 180.369 |

## 分类统计

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 0 | 0 | 0 | 0 |
| 调整 | 18 | 31 | 90 | 139 |
| 撤销 | 2 | 9 | 0 | 11 |

## 复验

- canonical validation: plans=150, occurrences=1258, conflicts=0, ok=True
- fast selected-state conflict count: `0`

本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。
