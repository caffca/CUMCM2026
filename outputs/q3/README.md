# Q3 结果索引

Q3 当前结果基于冻结的 `outputs/q2/Q2-T-incumbent-v1.json`，并采用 `H=643` 与 C 类模板
`(频宽,持续,间隔,次数)=(3,2,8,12)`。

| 文件 | 内容 |
|---|---|
| `result3.xlsx` | 附件 2 result3 模板格式的 138 个新增计划 |
| `solver_report.json` | 候选生成、过滤、资源单元模型求解状态、上下界和合并复验 |
| `pairwise_crosscheck.json` | 将同一候选集改写为逐候选冲突边后的独立 CP-SAT 复核 |
| `selected_Q2-T-incumbent-v1.json` | 新增计划的结构化清单 |
| `summary.md` | 机器生成的简要摘要 |

完整建模推导和论文措辞见 `D题/Q3_解题与验证阶段报告.md`。若 Q2 输入快照、时间域或 C
模板发生变化，必须重新运行 `scripts/solve_d_q3.py`，不能沿用本目录的 138 台结论。
