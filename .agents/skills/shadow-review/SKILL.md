---
name: "shadow-review"
description: "Use for asynchronous, frozen-milestone review of CUMCM2026 scientific results and presentation assets outside the Builder critical path."
---

# Skill: shadow-review

用于 CUMCM2026 的 Asynchronous Shadow Review Lane。Review Root 只消费 Builder 已经创建的
frozen semantic milestone SHA，不追踪 Builder 当前 dirty state，不成为 Builder 的 gate，
不自动向 Builder 回流任务。

## Lane boundary

- Builder/Controller 的 `E:\CUMCM2026` 是连续 Production Lane。
- Reviewer 的 `E:\CUMCM2026-review` 是同一 Git repository 的 detached Review Lane。
- 没有真实 milestone SHA 时不创建 Review worktree。
- Reviewer 可以落后 Builder 多个 milestone；没有新 milestone 时 idle 是正常状态。
- `git log` 是可审 milestone 的轻量可见性来源，不新增 queue、database、sync daemon 或 registry。
- 不创建 migration_agent、sync_agent 或 copy_agent；通过 deterministic Git checkout 冻结版本。

Reviewer 消化 conclusion、metrics、data、raw figures、plot-ready data、tables、assumptions、
limitations 和 paper-facing material。它不是 Builder manager、automatic feedback controller、
continuous sync mirror，也不是实时状态镜像或第一版图表/论文的必需 producer。进入 Review
前，Builder 应已完成 frozen 范围内的真实结果、可读正式图表、逐问正文和可生成 PDF。

## Review Root fan-out

Review Root 默认自己审阅；一次最多运行一个原生 helper，设计与审图串行。
全局并发仍不超过三，Builder 开局三 scout 不变。按任务选择：

- `result_critic`：科学结果、问题契合、约束、信号、异常、稳定性和结论有效性。
- `visual_critic`：图表视觉表达、层级、坐标/单位、标签、legend、冗余和页面成本。
- `paper_checker`：正文、数字、公式、单位、图表、caption、摘要和逐问一致性。
- 只有明确数学争议才使用 `math_verifier`。

这些 Agent 不都写“总体审稿意见”，不互相共享结论作为权威，不写文件，不写共享状态，
不修改 Git，不 spawn additional agents。Review Root 负责综合其报告，但不得自动给 Builder
下任务。

关键图可选 `figure_designer`（Sol/xhigh），随后只读 `visual_critic` 独立看像素。
同一只读规格/patch 支持也可由 Builder 在冻结前调用并在自己的工作区执行；这不让
Reviewer 成为生产依赖，也不扩大 child 权限。
前述四个 critic 始终只读。designer 的唯一潜在写权限是隔离工作区内已指定的 plotting
script、PDF/PNG 和 note；共享 style 仅集成者修改。当前无法指定/确认原生 child cwd，
因此仓库实际配置保持 read-only，只返回设计规格/patch，由 Review Root 在隔离区执行。
不得仅改成 workspace-write 就假设实现隔离，也不得在 Builder main 放任 writer。
helper 不递归、不改 Git，结果先回 Review Root，不把 producer 自评当独立证据。

输入必须包括 base_sha、question_id、figure_id、frozen plot-data 路径与身份、8–12 行
figure brief 和允许输出路径。源不存在返回 BLOCKED，身份不一致返回 STALE；不读取
Builder dirty data。前后检查 tracked/untracked 和重要 ignored 输入，一图一个 writer。
源数值、聚合、区间含义和 caption 必须一致；新增拟合/聚合/区间属于分析，报告 R1/R2/R3。
图像按最终宽度进入中文 PDF 并渲染查看；无像素检查标 NOT_VISUALLY_VERIFIED。

## R0–R3 escalation

### R0 — PRESENTATION ONLY

颜色、字体、legend、layout、caption、figure redesign、table layout、prose compression 和
visual hierarchy。Builder interruption：**NO**。

### R1 — EVIDENCE ENHANCEMENT

建议增加 sensitivity plot、residual diagnostic 或 robustness presentation。默认记录为
suggestion/backlog，Builder interruption：**NO**；只有 Human 认为它对最终结论非常重要时才
转为明确任务。

### R2 — POTENTIAL MODELING CONCERN

可能过强的假设、值得复核的约束实现、不完整的结果解释或图表暴露的潜在模型问题。Reviewer
记录证据，Human + Web GPT 判断，Builder 默认继续；只有 Human 明确决定后才中断或改变方向。

### R3 — DIRECTIONAL / P0

题意、目标方向、单位、核心约束、数据泄漏、主要结果、方程或正式指标存在可能改变结论的
严重问题。Reviewer 标记 `BUILDER INTERRUPTION RECOMMENDED`，但不能自动修改 Builder。
必须经过 Reviewer → Human + Web GPT → Human judgment → explicit Builder prompt。

Human 是唯一 major cross-lane router。Reviewer finding 不自动生成 Builder prompt，不自动
触发 repair，不自动改变模型，不自动 cherry-pick。

## Presentation ownership

Builder 先负责第一版正式可读 figures/tables、captions、逐问 narrative、完整源稿和 PDF。
在 review/* branch 中，Review Lane 可以修改 frozen scientific facts 之外的 presentation
assets：refined figures、tables、captions、narrative、PDF layout assets。允许 REDRAW、
MERGE、SPLIT、DROP、RESTYLE、RELAYOUT；不得 retune model、change metric/dataset/parameter/
objective、改变 actual result、baseline 或 silently rerun scientific experiment。

Builder 生成候选图时，应尽量同时保留 raw figure、plot-ready CSV/JSON/table，以及 plotting
source 或可复现数据源。Reviewer 基于 frozen data 重画，不得从 PNG 猜数值。

## Reviewer verdict and return

使用现有 `paper-review` skill 对结构、图表、最终 PDF 或 milestone 做具体检查。每轮输出
一个明确 verdict，并按 P0/P1/Polish 报告；R0/R1 不阻塞 Builder，R2/R3 不自动回流。
报告必须区分 facts、inference、assumptions 和 evidence；Web GPT recommendation 不是
repository fact，必须由 Human/Reviewer 对 frozen evidence 核实。

## Worktree rule

首次真实 modeling milestone 之后，使用：

```powershell
scripts/prepare-review-worktree.ps1 <MILESTONE_SHA>
```

只允许 deterministic checkout 到给定 SHA；dirty Reviewer 必须 fail closed。helper 不创建
branch、不 commit、不 merge/rebase/cherry-pick/push。Reviewer 需要修复时，另行在自身
`review/*` branch 产生可审 commit，由 Builder/Human 明确决定是否采纳。
