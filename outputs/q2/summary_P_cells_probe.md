# Q2 求解摘要

- policy: `P`
- mode: `full`
- proven_optimal: `True`
- plans: `150`
- candidate states: `4582`
- state conflict edges used: `270626`
- lazy cuts added: `0`
- solver iterations: `8`

## 目标向量

| 层 | 值 | 状态 | 下界 | gap | 秒 | CP 冲突 | 分支 |
|---|---:|---|---:|---:|---:|---:|---:|
| P_A | 0 | OPTIMAL | 0.0 | 0.0 | 0.244 | 0 | 0 |
| C_A | 0 | OPTIMAL | 0.0 | 0.0 | 0.208 | 0 | 0 |
| P_B | 20 | OPTIMAL | 20.0 | 0.0 | 0.244 | 0 | 0 |
| C_B | 3 | OPTIMAL | 3.0 | 0.0 | 0.304 | 119 | 564 |
| C | 78 | OPTIMAL | 78.0 | 0.0 | 0.783 | 50 | 2689 |
| M | 30 | OPTIMAL | 30.0 | 0.0 | 0.784 | 263 | 8919 |
| S_sum | 192 | OPTIMAL | 192.0 | 0.0 | 1.215 | 10 | 3395 |
| S_max | 10 | OPTIMAL | 10.0 | 0.0 | 1.388 | 66 | 4309 |

## 分类统计

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 20 | 20 | 2 | 42 |
| 调整 | 0 | 17 | 13 | 30 |
| 撤销 | 0 | 3 | 75 | 78 |

## 复验

- canonical validation: plans=150, occurrences=388, conflicts=0, ok=True
- fast selected-state conflict count: `0`

本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。
