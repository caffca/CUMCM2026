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
| C | 6 | FIXED | 6.0 | 0.0 | 0.000 | None | None |
| M | 120 | FEASIBLE | 88.0 | 0.26666666666666666 | 300.359 | 0 | 0 |

## 分类统计

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 4 | 3 | 17 | 24 |
| 调整 | 15 | 32 | 73 | 120 |
| 撤销 | 1 | 5 | 0 | 6 |

## 复验

- canonical validation: plans=150, occurrences=1277, conflicts=0, ok=True
- fast selected-state conflict count: `0`

本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。
