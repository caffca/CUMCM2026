# AI Usage Log

Append-only。用于比赛期间保留实质性 AI 辅助记录，并在官方要求明确后生成最终声明/附件。

> 是否需要披露、披露格式和具体字段，以 `SUBMISSION_SPEC.md` 中核验的当届官方规则为准。

| Time | Tool / model | Stage | Purpose / prompt summary | Output adopted? | Human modification | Verification | Final artifact |
|---|---|---|---|---|---|---|---|
| 2026-08-24 | Codex current agent | Repository bootstrap | Initialized the independent repository from the supplied template; recorded verified local paths/tool facts; created governance documentation updates. | Yes, bootstrap documentation and directory placeholders | Scope restricted to repository bootstrap; no problem, data, model, metrics, paper, or submission rule was invented | Read-only path/tool checks, governance check, diff check; plotting smoke check recorded as failed because Matplotlib is absent | `E:\CUMCM2026` repository bootstrap; no modeling or publication artifact |

## Recording Guidance

优先记录会实质影响以下内容的 AI 使用：

- 问题拆解 / 建模候选；
- 代码生成 / 修改；
- 参数或实验设计；
- 数据分析；
- 图表设计；
- 论文结构和大段文字；
- reviewer-style 审计；
- 最终格式/支撑材料生成。

普通语法补全、无实质采用的尝试可按官方要求决定是否需要记录，不在模板中自行定义豁免。
