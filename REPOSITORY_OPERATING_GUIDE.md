# Repository Operating Guide

本手册解释仓库结构和常用工作流。强制规则以适用的 `AGENTS.md`、`AGENTS.override.md`、官方 `SUBMISSION_SPEC` 和显式调用的 skill 为准。

## 1. Repository Layers

```text
Governance
  AGENTS.md

Current state
  docs/CURRENT_PROGRESS.md
  docs/CODEX_EXECUTION_JOURNAL.md

Modeling contract
  docs/MODELING_PROTOCOL.md
  docs/DATA_PROTOCOL.md
  docs/DECISIONS.md

Evidence
  outputs/runs/
  outputs/reports/
  docs/RESULTS_EVIDENCE_MATRIX.md

Publication
  docs/SUBMISSION_SPEC.md
  docs/PAPER_WRITING_GUIDE.md
  docs/FIGURE_STYLE_GUIDE.md
  docs/FIGURE_TABLE_INDEX.md
  paper/

Compliance
  docs/AI_USAGE_LOG.md
  scripts/governance_check.py
```

## 2. Governance File Directory

| File | Owns | Update when |
|---|---|---|
| `AGENTS.md` | 长期规则、权限、closure、Git policy | 稳定治理规则变化 |
| `docs/CURRENT_PROGRESS.md` | 当前有效状态 | 当前事实、阻塞、下一步、里程碑变化 |
| `docs/CODEX_EXECUTION_JOURNAL.md` | Prompt 执行与恢复历史 | 每个 substantive task 结束前 append |
| `docs/REPOSITORY_MAP.md` | 本地/远程路径、数据和输出位置 | 路径或同步事实确认/变化 |
| `docs/ENVIRONMENT.md` | 环境、依赖、solver、运行命令 | 环境事实变化 |
| `docs/MODELING_PROTOCOL.md` | 建模原则和冻结口径 | 目标/约束/评价/选择规则变化 |
| `docs/DATA_PROTOCOL.md` | 数据、清洗、单位、派生变量 | 数据处理事实变化 |
| `docs/DECISIONS.md` | 长期决策 | durable decision 做出/废弃 |
| `docs/RESULTS_EVIDENCE_MATRIX.md` | 结论—证据关系 | 结论支持状态变化 |
| `docs/FIGURE_STYLE_GUIDE.md` | 图表视觉语法 | 统一风格规则变化 |
| `docs/FIGURE_TABLE_INDEX.md` | 图表 provenance | 图表源或输出变化 |
| `docs/PAPER_WRITING_GUIDE.md` | 内部论文写作合同 | 写作生产规范变化 |
| `docs/SUBMISSION_SPEC.md` | 官方硬格式和提交要求 | 官方文件核验后变化 |
| `docs/AI_USAGE_LOG.md` | AI 使用留痕 | 有实质性 AI 辅助时 append |
| `docs/REFERENCE_PAPER_ANALYSIS.md` | 参考论文经验 | 新增高质量参考样文或复盘 |

## 3. Normal Session

1. 进入仓库并读取 `AGENTS.md`。
2. 读取 current state、repo map、modeling protocol 和相关 decision。
3. 检查 Git 状态并识别预先存在的 dirty files。
4. 报告计划和验证方式。
5. 做最小、可验证修改。
6. 完成文档/发布影响审计。
7. 验证、journal、local commit。

## 4. Formal Modeling Run

使用 `$modeling-run-integrity`。

每个正式 run 使用独立目录：

```text
outputs/runs/RUN-YYYYMMDD-NNN_<short-name>/
```

至少保存：

```text
manifest.yaml
summary.md
metrics.json      # 如适用
figures/          # 如适用
```

大型中间文件、缓存和原始数据不应为了 Git 历史而复制。

## 5. Paper Workflow

论文默认采用竞赛式逐问闭环：

```text
摘要
问题重述
问题分析
假设与符号
数据处理
逐问：建模思路 → 数学模型 → 求解 → 验证 → 结果 → 小结
模型评价与推广
参考文献
附录 / 支撑材料
```

正式论文修改时同时维护：

- `RESULTS_EVIDENCE_MATRIX`
- `FIGURE_TABLE_INDEX`
- `AI_USAGE_LOG`（如适用）
- `SUBMISSION_SPEC`（仅官方规则变化时）

## 6. Reference Papers

参考获奖论文用于学习竞赛阅读语法和有效图表，不是官方格式来源。

当前两篇参考论文的提炼见 `docs/REFERENCE_PAPER_ANALYSIS.md`。

## 7. Final Submission Gate

```text
P0 Structure Complete
P1 Numerical Provenance Passed
P2 Modeling Consistency Passed
P3 Figure/Table QA Passed
P4 Official Format Compliance Passed
P5 Independent Reviewer Audit Passed
P6 Final PDF Visual Inspection Passed
```

P0–P5 不能替代最终 PDF 逐页检查。
