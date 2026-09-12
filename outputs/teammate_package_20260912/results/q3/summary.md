# Q3 求解摘要

- Q2 input: `C:\Users\l\Desktop\CUMCM2026\outputs\q2\Q2-T-incumbent-v1.json`
- horizon: `[0,643)`
- C template: `{'width': 3, 'duration': 2, 'gap': 8, 'count': 12}`

## 候选与求解

- raw candidates: `52136`
- rejected by frozen Q2: `49684`
- compatible candidates: `2452`
- resource-cell cliques: `13988`
- solver status: `OPTIMAL`
- selected new C plans: `138`
- best bound: `138.0`
- gap: `0.0`
- seconds: `0.197`

## 统一复验

- plans after merge: `288`
- occurrence count: `2933`
- conflict count: `0`
- boundary violations: `0`
- ok: `True`

Q3 的最大值只针对报告所列 Q2 排程、时间域和 C 类模板成立；若 Q2 排程发生变化，应重新求解。
若 solver status 不是 OPTIMAL，selected new C plans 只能称为已验证可行值，不能称为全局最大值。
