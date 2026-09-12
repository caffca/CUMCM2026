# Q2 求解摘要

- policy: `P`
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
| P_A | 13 | FEASIBLE | 6.0 | 0.5384615384615384 | 120.356 | 0 | 1136 |

## 分类统计

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 7 | 2 | 13 | 22 |
| 调整 | 12 | 32 | 77 | 121 |
| 撤销 | 1 | 6 | 0 | 7 |

## 复验

- canonical validation: plans=150, occurrences=1273, conflicts=0, ok=True
- fast selected-state conflict count: `0`

本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。
