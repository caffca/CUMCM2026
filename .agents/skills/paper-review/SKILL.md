# Skill: paper-review

## Purpose

对数学建模竞赛论文执行结构、证据、图表、格式和最终 PDF 审查。

## Modes

- `structure`：摘要、章节比例、逐问闭环、重复内容和模型选择。
- `figure`：图表类型、视觉统一、caption、页面成本和可读性。
- `final`：数字、公式、答案、图表和最终 PDF 的整体检查。
- `milestone`：基于 frozen milestone commit 对单个问题做轻量独立审查。

按任务读取 `docs/PAPER_WRITING_GUIDE.md`、`docs/FIGURE_STYLE_GUIDE.md`、论文源文件
或最终 PDF；不强制读取 submission、evidence 或全局 provenance 文件。

## Milestone mode

输入必须是一个明确的 milestone commit SHA 和一个问题编号 `QX`。Reviewer 在独立
worktree 中审查该 frozen SHA，不跟踪 Builder 的 dirty worktree，也不直接修改 main。

### A. Question fit

- 是否真正回答该问题；
- 是否遗漏题面硬约束；
- 上一问输入是否正确传递；
- 是否把额外假设写成题面事实。

若存在 `docs/PROBLEM_BRIEF.md`，以其中对应问题为快速核对入口。

### B. Model audit

只找最关键风险：模型匹配性、是否有更简单充分方法、单位/边界/目标函数、算法条件、
参数或数据使用。不要机械执行完整 checklist，优先给出 1–3 个真正重要问题。

### C. Result audit

确认核心程序有实际输出、关键数字与保存结果一致、主要约束满足，并指出值得 Builder
停下来检查的异常。只有可能改变结论时才要求补实验。

### D. Paper / figure polish

检查应保留的公式、冗余文字、图表选型和风格、caption、表图重复以及是否有更有信息
价值的主图。Reviewer 可以在自己的 worktree 修改 plotting script、正式图或局部论文。

### Verdict

每轮最后只给一个 verdict：

```text
ACCEPT
ACCEPT WITH MINOR FIX
REVISE
BLOCK
```

随后只报告：

```text
P0 — 必须立即处理，否则该问可能错误
P1 — 建议进入最终论文前处理
Polish — 可选视觉/语言改善
```

如需交给外部网页 GPT，可在 `tmp/` 生成未跟踪的
`review_packet_<QX>_<shortsha>.md`，只包含问题要求、模型概述、关键假设/公式、结果、
正式图表、核心风险和 2–4 个外部审查问题，不复制整个仓库或完整日志。

## Structure Audit

检查：

- 问题重述是否只是重述；
- 问题分析是否解释模型选择；
- 每问能否快速定位模型、求解、验证、答案；
- 是否存在算法堆砌；
- 是否存在过长背景和重复结论；
- 摘要是否给定量结果。

## Result and consistency check

- 摘要、正文、图、表数字一致；
- 重要结果能回到 `outputs/qX/` 和对应脚本；
- negative / mixed result 未被包装；
- 结论没有超出当前证据边界。

## Figure Audit

- 每图目的明确；
- chart type 与数据职责匹配；
- style 一致；
- 图内 title 不重复 caption；
- table+figure 非机械重复；
- 3D / rainbow / radar 等是否真的必要；
- 最终 PDF 100% 缩放可读。

## Final mode

检查：

- 各问答案是否明确；
- 公式、符号、单位和数字是否一致；
- 图表是否可读且服务于结论；
- 摘要是否覆盖全部问题；
- 最终 PDF 是否存在溢出、裁切、乱码或不可读内容。

当用户明确提供当届官方规则并要求格式审查时，再按实际材料补充检查；没有材料时
不猜测官方要求。
