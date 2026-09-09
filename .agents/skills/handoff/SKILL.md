---
name: "handoff"
description: "Use only when the user explicitly requests cross-session, cross-machine, or cross-person handoff documentation for the CUMCM2026 repository."
---

# Skill: handoff

仅在用户明确要求跨会话、跨机器或跨人员交接时使用。

生成独立 handoff 时包含：

- canonical repo / branch / HEAD；
- worktree dirty state；
- current objective；
- confirmed modeling/data/submission rules；
- completed work；
- failed/mixed attempts；
- evidence/run paths；
- paper/figure status；
- blockers；
- exact next actions；
- authorization boundary。

受众必须明确区分：

- 网页分析窗口：默认无本机访问，包内必须包含必要题面摘要、公式、真实结果与小附件，
  不能只给本机路径；
- 本机 Builder：记录实际 repo/branch/HEAD/dirty、当前目标和最短可执行下一步；
- frozen Reviewer：记录真实 base_sha，只使用该提交中的 tracked 内容；缺少的 ignored/
  外置输入单列，不从 Builder dirty 工作区补读。

`docs/WINDOW_HANDOFF_GUIDE.md` 是稳定、自包含的唯一操作手册；动态
`WINDOW_PACKET.md` 是一次导出快照，不是第二个进度板。只导出当前范围和显式附件，
不复制完整聊天、全仓库、参考论文全文、环境目录、凭据或全局配置。
动态包从已有 `CURRENT_PROGRESS.md`、`DECISIONS.md` 和各问 `summary.md` 提取必要状态，
不要求用户同步另一套日志；给网页端的关键结果和图必须作为显式附件实际随包导出。
dirty status 包可用于恢复讨论，但不得冒充 frozen SHA 证据。冻结包的“来自该SHA”
与“科学结论正确”是两件事。用户明确要求交接时可运行
`scripts/export_window_handoff.py`；缺题面或附件时如实标 PARTIAL，不补造。
