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
| C | 6 | FEASIBLE | 5.0 | 0.16666666666666666 | 301.175 | 0 | 0 |

## 分类统计

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 1 | 0 | 2 | 3 |
| 调整 | 18 | 35 | 88 | 141 |
| 撤销 | 1 | 5 | 0 | 6 |

## 复验

- canonical validation: plans=150, occurrences=1277, conflicts=0, ok=True
- fast selected-state conflict count: `0`

本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。
