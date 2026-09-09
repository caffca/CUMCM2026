# CUMCM2026 跨窗口交接与比赛使用手册

本文件是稳定、自包含的唯一操作手册。一次性的当前状态使用
`scripts/export_window_handoff.py` 生成 `WINDOW_PACKET.md`；不要再维护一套需要用户
手工同步的日志、队列或进度板。

2026 当届官方格式、页数、匿名、AI 使用声明、支撑材料和提交要求在官方文件到位前均为
`UNVERIFIED`。本手册只定义仓库内部生产、冻结、审阅和交接流程，不把往届经验升级为
官方要求。

## 1. 一页操作契约

### 固定路径与真实状态

- Builder / Production Lane：`E:\CUMCM2026`，通常为 `main`。
- Reviewer / Review Lane：首次真实 milestone 后才创建的同仓库独立 worktree，通常为
  `E:\CUMCM2026-review`。
- 当前事实先读：`docs/CURRENT_PROGRESS.md`。
- 跨问题长期决定：`docs/DECISIONS.md`。
- 每问可恢复状态：`outputs/qX/summary.md`。
- 临时和演练材料：`tmp/`；不能冒充正式赛题结果。

进入任何窗口先运行：

```powershell
Set-Location E:\CUMCM2026
git status --short
Get-Content docs\CURRENT_PROGRESS.md
```

不得把 dirty 工作区当作 frozen 证据，也不得为了“干净”而覆盖、重置或删除已有改动。

### 角色与责任

**Builder / Controller 是完整初稿的生产责任人。** 选题和关键约束确认后，Builder 在已有
授权内连续完成题意与数据检查、建模、真实求解、必要自检、一次有界修复、可读正式图表、
逐问正文、完整论文源稿和实际多页 PDF。只交代码、数值、配置、单页测试或粗略提纲不算
完成；正式图和主要写作不能默认留给 Review。

Builder 可以按实际能力请求只读 `figure_designer` 的规格或文本 patch，并由 Builder 在
自己的工作区核对输入、执行绘图和验收。实际模型/effort 以调用回执为准；这不扩大
子 Agent 权限，不增加角色，也不让 Review 成为生产依赖。

**Reviewer 和网页窗口是冻结后的独立验收与精修层。** 它们只消费明确的 milestone SHA
及随包材料，不读取 Builder 同名 dirty 文件，不自动修改主线，不自动 merge、rebase、
cherry-pick 或 push。Reviewer 可在自己的 `review/*` 分支做 presentation-only 精修；是否
采纳由 Human/Builder 明确决定。

**Human 是跨窗口裁决者和最终提交者。** 普通技术取舍不反复询问；只有关键歧义、P0、
缺少必须输入或资源授权、高成本/破坏性操作才升级。最终终审与官方提交始终手工完成。

### 正常结束条件

以下条件必须同时满足，不能用其中一项替代全局完成：

1. 题目要求的每问都有可追溯答案；
2. 核心约束、单位和可能改变结论的必要验证已检查；
3. 各问模型、求解、验证、结果和小结已写成完整正文；
4. 可读正式图表、caption、数字和正文彼此一致；
5. 完整论文源稿和实际多页 PDF 已生成；
6. PDF 已逐页渲染检查，关键图表页面完成像素审阅；
7. 失败、局限和待队员核验项明确。

主解、某问、某次 commit、Review 未开始、旧 PASS 或单页 PDF 均不是正常结束。只有真实
P0、关键歧义/输入、未授权资源、用户叫停或会话/服务错误可暂停受影响分支。

## 2. 比赛开始后的连续 Builder 流程

用户提供“选定题目 + 完整题面 + 全部可用附件”后：

1. 只读取当前题面和附件，不从旧聊天或历史论文猜事实。
2. 运行 `problem_scout`、`data_auditor`、`model_scout` 三个独立只读视角；Controller 综合。
3. 建立 minimum-sufficient baseline 和逐问依赖，先实际运行 Q1。
4. 检查约束、单位、边界和关键数字；只对可能改变结论的风险补验证。
5. 完成一问即整理 `outputs/qX/results.*`、`plot_data/`、`figure_briefs.md`、正式图和
   `summary.md`，同时写入论文对应章节。
6. Q1 可用后继续 Q2/Q3，不等待异步 Review；所有问题可用后转入全文整合。
7. 生成完整多页 PDF，逐页渲染并检查中文、公式、表格、图、caption、页码和裁切。
8. 满足第 1 节全部结束条件后才报告 Builder 完成；终审和提交仍交给用户。

长计算期间继续做不依赖结果的下一问分析、diagnostics、plot-ready data 或论文整理。
普通技术取舍由 Builder 处理；一次 targeted critique、一次正常修复、一次 targeted
validation 后作出 ACCEPT / CHANGE / STOP，禁止无限修复循环。

## 3. explore、milestone 与 Git

- `explore`：EDA、清洗试验、baseline、候选模型、临时图和失败路线；可放 `tmp/`，不建
  run registry、manifest 或 prompt commit。
- `milestone`：可保留的模型、结果、图表、逐问正文和验证已形成；更新该问 summary 与
  `CURRENT_PROGRESS.md`，完成轻量检查后创建语义 local commit。

milestone 前至少检查实际运行、关键输出、单位/shape、图文数字、PDF 页面，并运行：

```powershell
git diff --check
git status --short
```

显式 stage 相关路径，不使用 `git add .`。永不自动 push、merge、rebase 或 cherry-pick。
已有无法安全归因的 dirty 状态时，不自动提交主仓库。

## 4. 冻结 Reviewer

首次真实 milestone 后，以完整 40 位 SHA 创建或切换同仓库 worktree：

```powershell
scripts\prepare-review-worktree.ps1 <FULL_MILESTONE_SHA>
```

Reviewer 必须核对 `git rev-parse HEAD` 与目标 SHA 一致且自身工作树可控。它审查题意契合、
约束、公式、单位、结果、图表、逐问叙述和完整 PDF；Builder 可同时继续主线。Review
findings 按 P0 / P1 / Polish 和 R0–R3 报告，不自动回流。`visual_critic` 只读像素并只给
KEEP / REDRAW / MERGE / SPLIT / DROP 之一。

Reviewer 如保留 presentation-only 修改，只能在自己的 `review/*` 分支显式提交。主仓库
是否采纳由 Human/Builder 另行决定；无明确决定时不 merge/cherry-pick。

## 5. 动态 WINDOW_PACKET 导出

### 当前工作状态包

状态包从当前 `CURRENT_PROGRESS.md`、`DECISIONS.md`、全部已有 `outputs/q*/summary.md` 和
先验索引提取必要状态。网页端需要的关键结果和图必须用 `--attach` 实际随包复制：

```powershell
.\.venv\Scripts\python.exe scripts\export_window_handoff.py `
  --repo E:\CUMCM2026 `
  --mode status `
  --attach outputs\q1\results.json `
  --attach outputs\q1\figures\main.png `
  --out E:\CUMCM2026\tmp\handoff\WINDOW_PACKET.md
```

没有正式题目时省略不存在的 `--attach`，并保留 PARTIAL/无赛题说明。状态包会明确标记
`WORKING_COPY_NOT_FROZEN`，只用于恢复讨论。

### 冻结问题包

冻结包从给定 commit 读取 tracked 内容，不切换 Builder 工作树：

```powershell
.\.venv\Scripts\python.exe scripts\export_window_handoff.py `
  --repo E:\CUMCM2026 `
  --mode frozen `
  --base-sha <FULL_MILESTONE_SHA> `
  --question q1 `
  --attach outputs\q1\results.json `
  --attach outputs\q1\plot_data\main.json `
  --attach outputs\q1\figures\main.png `
  --attach paper\submission_draft.pdf `
  --out E:\CUMCM2026\tmp\handoff\Q1_<SHORT_SHA>.md
```

导出器自动尝试内嵌该 SHA 中的 progress、decisions、问题 summary/results/brief，并生成同名
附件目录。`--external-attach` 只用于明确声明不在 base SHA 内的工作副本文件；它会醒目标记，
不能冒充冻结证据。输出路径或附件目录已存在时 fail closed，请换一个新名称，不覆盖旧包。

禁止导出完整仓库、完整聊天、参考论文全文、`.git`、`.venv`、环境文件、凭据或私钥。
“来自 SHA”只证明版本身份，不证明科学结论正确。

### 给网页窗口的最短提示

```text
请只根据随附 WINDOW_PACKET 及附件审阅。先确认 base_sha、题目身份和证据边界；
核对关键结果、公式、图和逐问回答，按 P0/P1/Polish 报告。不要猜测本机文件，
不要把建议写成仓库事实，也不要要求 Builder 依赖本窗口才能生产完整初稿。
```

## 6. 绘图与 PDF 验收

Builder 为关键图准备 8–12 行 brief、冻结 plot-data、目标宽度、对象 ID、单位、区间语义和
禁止推断。只读 `figure_designer` 可提供 Sol/xhigh 规格/patch；调用它的 root 在自己的
授权工作区执行。随后检查：数据/图元正确性 → PNG/PDF 像素 → 嵌入中文 PDF 的实际页面。
没有查看实际像素时必须标 `NOT_VISUALLY_VERIFIED`。

内部合成演练可用：

```powershell
C:\Users\zyy17\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  paper\build_internal_rehearsal.py --source-root <FROZEN_SOURCE_ROOT> --out <OUTPUT_PDF>

C:\Users\zyy17\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  tests\paper\check_multi_page_pdf.py --pdf <OUTPUT_PDF> --render-dir <PAGE_DIR> --out <QA_JSON>
```

该演练只证明内部多页中文链路可运行，不证明 2026 官方格式合规。

## 7. 恢复与故障处理

- Builder dirty、Reviewer frozen：以 Reviewer SHA 为审阅证据，Builder dirty 只作当前工作状态。
- 子 Agent timeout/空响应：记录 PARTIAL；基础设施失败可同角色重试一次，普通主线继续。
- 结果或输入身份变化：标 STALE，重新冻结后再审；不得从 PNG 猜数值。
- 缺题面、附件或官方规则：标 `TBD`/`UNVERIFIED`，只请求最小缺失材料。
- PDF 机器检查通过但未看页面：仍为 `NOT_VISUALLY_VERIFIED`。
- P0：冻结受影响结论并升级 Human；不相关工作可继续。
- P1/Polish：进入有界 backlog，不让 Review 成为 Builder critical path。

## 8. 本轮已验证能力与未验证边界

截至 2026-09-09，独立 synthetic scratch 已实际跑通计算 → plot-data → 正式中文图 →
逐问正文 → 4 页 A4 中文 PDF → 全页渲染 → frozen worktree → 只读视觉审阅 → 有界交接包。
这不是正式赛题运行，不产生现实竞赛结论。语料数量、环境版本和最新 Git 状态始终以
动态包及 `docs/CURRENT_PROGRESS.md` 为准。

仍需用户按优先级提供：2026 官方竞赛通知、官方论文模板/格式、官方 AI 工具规定、官方
支撑材料/提交要求，以及开赛后的正式题目与全部附件。在材料到位前保持 `UNVERIFIED`。

## 9. Pre-contest freeze

设计先验库达到20篇完整设计阅读后，立即停止新增检索、下载、抽取和模式扩展；原50篇目标
仅作为赛后长期事项。本轮结束即进入 pre-contest freeze：除真实P0外不再扩充 Agent、Skill、
治理文档、目录或工作流架构；开赛直接按本手册运行 Builder、冻结 Review lane 与
WINDOW_PACKET。冻结策略已生效，但用户确认 snapshot 前仍不得自动 stage 或 commit。
