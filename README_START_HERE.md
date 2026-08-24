# Start Here — 数学建模竞赛 Agent 仓库

这是一个面向高教杯/数学建模竞赛的 Agent-first 仓库模板。

它不是“算法大全”，目标是让 72 小时竞赛中的题目理解、建模、求解、验证、图表、论文和提交证据保持可追溯、可恢复、可审计。

## 第一次进入

1. 阅读 `AGENTS.md`。
2. 完成 `PROJECT_BOOTSTRAP_CHECKLIST.md`。
3. 只填写已经确认的仓库、环境、数据和官方格式事实；未知项保留 `TBD/UNVERIFIED`。
4. 把当年官方论文模板、竞赛通知和 AI 使用规定核验后写入 `docs/SUBMISSION_SPEC.md`。
5. 正式建模前冻结第一版 `docs/MODELING_PROTOCOL.md` 和 `docs/DATA_PROTOCOL.md`。

## 日常入口

- 当前状态：`docs/CURRENT_PROGRESS.md`
- 建模规范：`docs/MODELING_PROTOCOL.md`
- 图表规范：`docs/FIGURE_STYLE_GUIDE.md`
- 论文规范：`docs/PAPER_WRITING_GUIDE.md`
- 官方格式：`docs/SUBMISSION_SPEC.md`
- 证据矩阵：`docs/RESULTS_EVIDENCE_MATRIX.md`
- 图表索引：`docs/FIGURE_TABLE_INDEX.md`

## Git

模板默认采用：

- substantive task 成功后自动 local commit；
- 不自动 push；
- 不使用 `git add .`；
- 已有 dirty changes 与本轮修改重叠时不自动提交。
