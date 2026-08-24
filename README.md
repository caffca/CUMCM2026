# CUMCM2026

面向数学建模竞赛的 Agent-first 工作仓库。目标是让 Agent 尽快完成题意理解、
数据检查、建模、运行、验证、图表和论文，而不是维护一套繁重的审计手续。

## 比赛当天怎么开始

直接提供：

```text
我们正式选择 B 题。
这是完整题面和全部附件。

请先完成题意拆解、数据检查和整体建模路线，然后直接开始第一问。
```

Agent 会读取材料，检查数据依赖，建立第一问 baseline，实际运行并根据结果
继续改进。无需先准备 protocol、manifest、hash、run id 或其他模板记录。

## 工作模式

### explore

默认探索模式：EDA、清洗试验、baseline、候选模型、参数试验、临时图和失败方案。
探索可以放在 `tmp/` 或普通 working output，不需要 RUN ID、manifest、hash 或立即 commit。

### milestone

当某一问的方案、模型、结果或图表值得保留时，整理：

```text
outputs/qX/
  summary.md
  results.*
  figures/
```

`summary.md` 记录问题、模型、假设、输入、关键结果、选择理由、主要验证、代码、
图表和遗留问题。然后更新 `docs/CURRENT_PROGRESS.md`，做最低成本检查并创建 local
milestone commit。默认不 push。

## Optional Dual-Window Mode

```text
Builder:
E:\CUMCM2026
main

Reviewer:
E:\CUMCM2026-review
detached milestone → review/* when needed
```

一次性创建 Reviewer worktree：

```powershell
git worktree add --detach E:\CUMCM2026-review HEAD
```

Builder 可以继续推进 Q2，同时 Reviewer 审计已经提交的 Q1 milestone。Reviewer 只消费
frozen milestone，不跟踪 Builder 的实时脏工作树；被接受的修改由 Builder 显式 cherry-pick。

## 目录

| Path | 用途 |
|---|---|
| `src/` | 可复用源码 |
| `scripts/` | 数据处理、求解和绘图脚本 |
| `configs/` | 人工维护配置 |
| `data/raw/` | 原始题面附件和数据，默认只读 |
| `data/processed/` | 脚本生成的处理数据 |
| `outputs/qX/` | 各问题的 milestone 结果 |
| `outputs/figures/` | 正式图件 |
| `outputs/tables/` | 正式表格 |
| `paper/` | 论文源文件 |
| `references/` | 参考资料 |
| `tmp/` | 可丢弃的探索文件 |
| `docs/` | 当前状态、建模/数据指南、写作和视觉资产 |

## 论文与图表

论文按逐问闭环组织：建模思路 → 模型 → 求解 → 必要验证 → 结果 → 小结。
使用 `docs/PAPER_WRITING_GUIDE.md` 和 `docs/FIGURE_STYLE_GUIDE.md` 的内部约定。
图表应由脚本生成，采用稳定文件名，并在对应问题的 `summary.md` 中说明来源。

官方提交格式、AI 使用规定和支撑材料要求不在日常 active workflow 中预维护；
用户明确要求最终提交检查且提供当届材料后，再按实际要求处理。

## 结果保存规则

探索结果可以临时覆盖或丢弃，但不要把未运行、未解释或虚构的数字写进论文。
准备保留的结果应有：

```text
清晰路径 + 稳定文件名 + 生成脚本 + 关键参数 + 必要验证
```

重要决定写入 `docs/DECISIONS.md`；普通参数试验、颜色调整和函数重命名不写入。
需要在下一窗口恢复时，优先更新 `docs/CURRENT_PROGRESS.md` 和对应问题的 `summary.md`。

## 进入仓库后的最小操作

当前工作状态以 `docs/CURRENT_PROGRESS.md` 为准；路径和环境文档只有发生变化或
出现故障时再读取。仓库默认保持本地工作，任何远程同步都由用户明确决定。

```powershell
git status --short
Get-Content docs/CURRENT_PROGRESS.md
```

普通探索直接开始。milestone 前检查代码是否实际运行、关键输出是否存在、单位和
shape 是否合理，并运行：

```powershell
git diff --check
git status --short
```
