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

| 层 | 值 | 状态 | 下界 | gap | 秒 | CP 冲突 | 分支 |
|---|---:|---|---:|---:|---:|---:|---:|
| C | 7 | FEASIBLE | 3.0 | 0.5714285714285714 | 60.364 | 0 | 0 |

## 分类统计

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 0 | 0 | 0 | 0 |
| 调整 | 18 | 35 | 90 | 143 |
| 撤销 | 2 | 5 | 0 | 7 |

## 复验

- canonical validation: plans=150, occurrences=1274, conflicts=0, ok=True
- fast selected-state conflict count: `0`

本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。
