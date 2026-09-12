# Q2 求解摘要

- policy: `T`
- mode: `lazy`
- proven_optimal: `False`
- plans: `150`
- candidate states: `4582`
- state conflict edges used: `1498`
- lazy cuts added: `1498`
- solver iterations: `5`

## 目标向量

| 层 | 值 | 状态 | 下界 | gap | 秒 |
|---|---:|---|---:|---:|---:|

## 分类统计

| 指标 | A | B | C | 总计 |
|---|---:|---:|---:|---:|
| 保留 | 0 | 0 | 0 | 0 |
| 调整 | 20 | 40 | 90 | 150 |
| 撤销 | 0 | 0 | 0 | 0 |

## 复验

- canonical validation: plans=150, occurrences=1300, conflicts=301, ok=False
- fast selected-state conflict count: `301`

本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。
