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
| C | 19 | FEASIBLE | 3.0 | 0.8421052631578947 | 45.835 |

## 分类统计

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 0 | 1 | 3 | 4 |
| 调整 | 18 | 23 | 86 | 127 |
| 撤销 | 2 | 16 | 1 | 19 |

## 复验

- canonical validation: plans=150, occurrences=1218, conflicts=0, ok=True
- fast selected-state conflict count: `0`

本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。
