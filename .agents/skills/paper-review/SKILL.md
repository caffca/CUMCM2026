# Skill: paper-review

## Purpose

对数学建模竞赛论文执行结构、证据、图表、格式和最终 PDF 审查。

## Modes

- `structure`：摘要、章节比例、逐问闭环、重复内容。
- `evidence`：所有数字、结论、表格和图是否可追溯。
- `figure`：图表类型、视觉统一、caption、页面成本和可读性。
- `format`：对照 `SUBMISSION_SPEC.md` 审查官方硬规则。
- `final`：P0–P6 完整最终审查。

## Required Reads

- `docs/SUBMISSION_SPEC.md`
- `docs/PAPER_WRITING_GUIDE.md`
- `docs/FIGURE_STYLE_GUIDE.md`
- `docs/RESULTS_EVIDENCE_MATRIX.md`
- `docs/FIGURE_TABLE_INDEX.md`
- 论文源文件 / 最终 PDF

## Structure Audit

检查：

- 问题重述是否只是重述；
- 问题分析是否解释模型选择；
- 每问能否快速定位模型、求解、验证、答案；
- 是否存在算法堆砌；
- 是否存在过长背景和重复结论；
- 摘要是否给定量结果。

## Evidence Audit

- 摘要、正文、图、表数字一致；
- claim 对应 evidence matrix；
- negative / mixed result 未被包装；
- 未出现手工无法追溯数字；
- 结论没有超出当前证据边界。

## Figure Audit

- 每图目的明确；
- chart type 与数据职责匹配；
- style 一致；
- 图内 title 不重复 caption；
- table+figure 非机械重复；
- 3D / rainbow / radar 等是否真的必要；
- 最终 PDF 100% 缩放可读。

## Format Audit

只依据 `SUBMISSION_SPEC.md` 中已核验官方规则。

遇到 `UNVERIFIED` 规则必须报告，不能猜。

## Final Gate

```text
P0 Structure Complete
P1 Numerical Provenance Passed
P2 Modeling Consistency Passed
P3 Figure/Table QA Passed
P4 Official Format Compliance Passed
P5 Independent Reviewer Audit Passed
P6 Final PDF Visual Inspection Passed
```

必须明确给出每个 gate 的 PASS / FAIL / BLOCKED 和原因。
