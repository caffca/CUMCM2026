# AGENTS.md

本文件只保留比赛期间长期有效、能帮助 Agent 快速推进建模的规则。

## 1. 普通开始

新窗口通常只需：

1. 确认 repo root。
2. 运行 `git status --short`。
3. 读取 `docs/CURRENT_PROGRESS.md`。
4. 根据任务需要读取相关代码、数据、论文或环境文档。
5. 直接开始工作。

`REPOSITORY_MAP.md`、`ENVIRONMENT.md`、`DATA_PROTOCOL.md`、`DECISIONS.md`、
论文文档和其他治理文件均按需读取，不要求每轮全部打开。普通任务不需要
先输出完整的 confirmed facts / unknowns / authorization / validation 报告；
复杂任务用几句说明路线即可。

## 2. Contest Start Fast Path

当用户提供：

```text
选定题目 + 完整题面 + 全部附件
```

即视为正式进入比赛。Agent 可以直接：

- 读取和解析全部题面、附件与数据；
- 做数据清洗、EDA、baseline、数学建模和普通求解；
- 进行参数实验、统计分析、必要的敏感性/稳健性分析和绘图；
- 修改源码、创建结果文件、整理 `outputs/qX/`；
- 修改论文源文件并推进下一问；
- 安装普通轻量 Python 科学计算依赖。

不需要为上述每一步重新申请。只有以下情况需要再次确认：

- 删除或覆盖重要原始数据、正式结果或论文；
- destructive Git 操作；
- 大规模 GPU 训练或显著高成本 sweep；
- 付费 API；
- 大范围、可能破坏环境的 CUDA / PyTorch / 核心依赖修改；
- 明显改变用户已确认的题意或整体建模方向。

## 2A. Continuous Builder + Asynchronous Shadow Review

需要两个 Codex 窗口时，主仓库 `C:\Users\ysw\Desktop\CUMCM2026` 的 `main` 是 Continuous Builder /
Controller 的 Production Lane；`C:\Users\ysw\Desktop\CUMCM2026-review` 是 Asynchronous Shadow
Review Lane。Reviewer 消费已经冻结的 milestone SHA，不跟踪 Builder 当前 dirty
state，也不属于 Builder 的 critical path。

Builder 持续推进题意、数据、主模型、Q1→Q2→Q3、验证、正式可读图表、逐问正文、
完整论文源稿与 PDF、
`CURRENT_PROGRESS.md`、`DECISIONS.md` 和 semantic milestone commits，不等待：

- Reviewer；
- Web GPT；
- Human 的逐步确认；
- Review Lane 的增值 presentation / figure / caption 精修；
- P1 review finding；
- ordinary review completion。

选题和关键约束确认后，Builder 是完整初稿的生产责任人：应在现有授权内连续完成建模、
真实求解、必要自检、一次有界修复、可读正式图表、逐问闭环正文、完整论文源稿和实际
多页 PDF。只交代码、数值或粗略提纲不构成 Builder 完成；正式图和主要写作不得默认留给
Reviewer。Builder 可按实际能力调用只读 `figure_designer` 获取规格或文本 patch，并在
自己的工作区核对输入后执行；这不扩大子 Agent 权限，也不使 Review 成为生产依赖。
普通技术取舍由 Builder 连续处理，只有关键歧义、P0 或资源授权阻塞才升级。

Reviewer 必须使用同一 Git repository 的独立 worktree，并且只审明确的 frozen
milestone SHA。Reviewer 可以落后 Builder 多个 milestone；这属于设计目标，不是同步
失败。没有新的 milestone 时 Reviewer idle 是正常状态。

Reviewer 可以检查题意契合、假设、公式、单位、边界、关键结果、复杂度、图表和论文
呈现。需要修改时，只在自己的 `review/*` 分支/worktree 中创建独立 commit；不直接写
main，不维护 Builder 的 `CURRENT_PROGRESS.md` / `DECISIONS.md`，不静默更换主模型，
不重构 Builder 正在推进的下一问，不自动 merge/rebase/cherry-pick/push。

首次真实 modeling milestone 之前，不创建 `C:\Users\ysw\Desktop\CUMCM2026-review`。创建或切换 review
worktree 必须使用 `scripts/prepare-review-worktree.ps1 <MILESTONE_SHA>` 的 deterministic
Git checkout 逻辑；禁止 migration agent、sync agent、copy agent 或让 LLM 决定复制哪些文件。

### 2B. Competition Autonomous Continuation Mode

一旦用户明确进入正式比赛模式，并给出总目标和允许的计算范围，Builder 是连续的
modeling/evidence production engine。Builder 每完成一个阶段，都选择当前最有价值的
下一步并继续，不因以下事件自动停止：

- 一个 subagent 完成；
- 一个问题的 baseline 或 primary solution 完成；
- 一个 milestone commit 完成；
- Reviewer 尚未开始或尚未完成；
- Human 暂时离开；
- Web GPT 尚未审计；
- presentation、figure 或 caption 尚未 polish。

优先级为：未回答的核心问题 → 核心结果正确性 → 可能改变结论的必要验证 →
敏感性/鲁棒性 → diagnostics → 可读正式图表和逐问正文 → 完整初稿与 PDF →
Reviewer 可消费的 frozen artifacts → 低价值增值 polish。若 Q1 已有 defensible primary
solution 而 Q2 尚未解决，优先推进 Q2，同时不得在最终整合时遗漏该问正文和图表。
长计算运行时，可以分析下一问、准备候选模型、做上一问 diagnostics 或整理 plot-ready
data；Builder 是 opportunistic scheduler。

各问都有 defensible primary solution 或必要 validation 完成后，转入全文整合，
不能把其中任一项单独当成正常结束。正常完成必须同时满足：

1. 本题要求的每问都有可追溯答案；
2. 核心约束、单位和必要 validation 已检查；
3. 包含逐问完整叙述而非提纲的论文源稿存在；
4. 表图、数字和正文相互对应；
5. 实际多页 PDF 已生成、逐页渲染检查，并看过关键图表页面；
6. 失败、局限和待队员核验项清楚。

只有真实 P0、必须由用户裁决的关键歧义或输入、未授权的资源/高成本操作、
用户明确叫停，或会话/服务错误，才暂停受影响主线。只继续不依赖阻塞结果的工作。
工作流完成不等于参赛提交完成；最终终审和提交始终由用户手工执行。

正式比赛 autonomous mode 中，Builder 被预授权为 coherent semantic milestone 创建 local
commit，不需要每问完成或每次 commit 再向用户申请 gate。仍然禁止 prompt commit、push、
merge、rebase、force operation、destructive Git 和自动 cherry-pick Review 修改。

## 3. 两种工作模式

### explore

默认模式，服务于快速判断路线是否值得继续。包括 EDA、清洗试验、baseline、
候选模型、参数试验、临时图和失败尝试。

基本流程：

```text
理解问题 → 检查必要数据 → 建 baseline/candidate → 实际运行
→ 看结果 → 诊断主要问题 → 继续或换路线
```

探索不创建 RUN ID、manifest、文件 hash、evidence matrix 或 execution journal。
可以使用 `tmp/` 或普通 working output；无价值试验可以被后续试验替代。

### milestone

当某一问得到基本满意、某个模型成为当前主模型、结果准备进入论文、正式图表
准备保留、重要建模决策确定，或一问基本完成时，升级为 milestone。

轻量归档放在：

```text
outputs/q1/
outputs/q2/
...
```

每个问题按实际需要创建目录。`summary.md` 只记录问题、采用模型、核心假设、
关键输入、关键结果、选择理由、主要验证、对应代码/图表和仍存在的问题。
不复制完整终端日志，不为普通结果计算 hash，不建立庞大 manifest。

## 4. 建模原则

- Minimum sufficient modeling：先用能回答问题的最简单充分模型。
- Complexity must be earned by evidence：复杂度必须解决已诊断的明确不足。
- 先建立可解释 baseline；只有证据支持时才升级模型。
- 黑盒模型进入主结论时，说明 baseline、数据评估方式和至少一种合适解释。
- 优先使用与结构匹配的精确优化方法；启发式方法说明必要性和解质量。
- negative / mixed result 如实保留，不为叙事删除失败方案。
- 不把 correlation 写成 causality，不补造题目或附件没有提供的证据。

验证只针对可能改变结论的风险：预测题重泛化误差，优化题重约束和解质量，
评价题重权重/参数敏感性，机制题重核心假设。不机械完成固定的全套检查表。

## 4A. 时间纪律

比赛前期允许快速探索；各问已有可用闭环后，优先补关键验证、正式图表和论文，
不为了“可能更高级”无限增加模型。如果当前方法已充分回答题目，不因复杂算法存在
而自动替换。milestone 后只有重大错误、明显性能不足或题目要求未满足，才重新打开
核心模型。比赛后半程新增模型必须解决明确的 P0/P1 问题。最终优先保证每问有答案、
数字和单位正确、图表可读、摘要覆盖全部问题、PDF 完整。

## 5. 数据与结果

- `data/raw/` 默认只读，不手工覆盖原始附件。
- `data/processed/` 由脚本生成，关键单位转换和清洗操作要能解释。
- 重要结果应有清晰路径、稳定文件名、生成脚本和关键参数。
- 论文重要数字应能回到 `outputs/qX/` 的正式结果和对应脚本。
- 不创建假 run、假 metrics、虚构数据或无法解释的占位结论。

## 6. 论文与图表

论文按逐问闭环推进：建模思路 → 模型 → 求解 → 必要验证 → 结果 → 小结。
遵守 `docs/PAPER_WRITING_GUIDE.md` 和 `docs/FIGURE_STYLE_GUIDE.md` 的内部约定。
正式图表优先使用稳定文件名和可重复脚本；图必须服务于明确结论。
Builder 负责第一版可提交形态的图表、caption、逐问正文、完整源稿和 PDF；Reviewer/Web
窗口只在 frozen 版本后独立验收与精修，不能作为这些资产出现的前置条件。

当届官方格式、页数、匿名、AI 使用和支撑材料要求未由用户提供前，不预设
任何官方 MUST。最终提交检查在用户明确要求且材料到位后再进行。

## 7. 重要决定

`docs/DECISIONS.md` 只记录会影响后续多问或整篇论文的 durable decision，例如：
最终选择题目、统一评价指标、核心假设、主模型切换、放弃重要路线或统一单位。
不要记录调一个参数、换颜色、改函数名等局部操作。

## 8. 安全边界

默认允许读取、搜索、比较文件，修改本任务范围内的源码/文档/结果，并做小型
静态检查和 smoke check。不得写入密码、token、私钥或个人敏感凭据。

删除、覆盖或移动用户数据、题目附件、正式结果和论文前必须再次确认。禁止
`reset --hard`、`clean -fd`、强制 checkout、rebase、force push；永不自动 push。

## 9. Git

Git 采用 milestone commit，而不是 prompt commit：

1. 普通探索不要求立即提交。
2. milestone 时更新 `CURRENT_PROGRESS.md`，整理 `outputs/qX/summary.md` 和正式资产。
3. 运行相关代码检查、关键输出检查、`git diff --check` 和 `git status --short`。
4. 只显式 stage 本次 milestone 的相关路径，不使用 `git add .`。
5. 创建一个语义清楚的 local commit；不自动 push。

不要为了把新 commit SHA 写回文档而再创建 documentation-only commit。Git history
就是 commit source of truth，文档不人工维护 HEAD SHA。若本轮开始已有无法安全
区分的用户改动，不自动提交。

## 10. 常用文件地图

- `docs/CURRENT_PROGRESS.md`：当前状态板，只在实际进展变化时更新。
- `docs/MODELING_PROTOCOL.md`：轻量建模指南。
- `docs/DATA_PROTOCOL.md`：轻量数据处理约定。
- `docs/DECISIONS.md`：重要长期决定。
- `docs/REPOSITORY_MAP.md`、`docs/ENVIRONMENT.md`：路径和环境的 dormant reference，只有变化或故障时读取。
- `docs/PAPER_WRITING_GUIDE.md`、`docs/FIGURE_STYLE_GUIDE.md`：论文与图表长期资产。
- `outputs/qX/`：问题级 milestone 结果、摘要和正式图表。
- `paper/`：论文源文件；`references/`：参考资料；`tmp/`：可丢弃探索文件。

## 11. Skill routing

- `.agents/skills/modeling-workflow/SKILL.md`：正式比赛中的 `explore` / `milestone` 工作流。
- `.agents/skills/paper-review/SKILL.md`：按 `structure`、`figure`、`final`、`milestone` 模式审查论文。
- `.agents/skills/handoff/SKILL.md`：仅在用户明确要求跨会话、跨机器或跨人员交接时使用。
- `.agents/skills/contest-orchestrator/SKILL.md`：V1 原生子 Agent 的 L0–L3 路由、并发、权限和回传协议。
- `.agents/skills/shadow-review/SKILL.md`：frozen milestone 的异步旁路审查、R0–R3 分级和 presentation ownership。
- `.agents/skills/design-priors/SKILL.md`：赛前历史设计库建设，以及题面解释后的按需模式检索。

Skill 用于减少重复劳动，不把比赛流程变成额外审计流程。

## 12. Native Multi-Agent Orchestration (V1)

### 12.1 Controller boundary

The Controller is the root model the user actually selected for the Builder session.
It may be Astra, Sol, or another available model; repository prose and role names never
switch the real session model. Report actual model overrides when known, and continue
within the user-authorized scope without treating a non-Sol root as a workflow failure.

The Controller is the sole orchestrator, synthesis layer, modeling judge, default
main-line writer, and writer of shared durable state. Native subagents are narrow,
read-only, evidence-oriented readers that report back to the Controller, except the
narrow isolated presentation producer described below (currently read-only fallback).

Native subagents must not write `docs/CURRENT_PROGRESS.md`, `docs/DECISIONS.md`,
milestone summaries, durable paper state, formal `outputs/qX/` results, source/data
files (except assigned plotting scripts under the isolated producer exception),
the Git index, or the `main` branch. They must not run `git add`, `git commit`,
`git push`, merge, rebase, or cherry-pick, and must not spawn additional agents.

The detached Reviewer remains an independent frozen-milestone audit in its own
worktree. Native subagents are Builder-internal cognition and do not replace it.

### 12.2 Complexity router and budgets

- **L0:** trivial or mechanical work; spawn 0.
- **L1:** bounded implementation or local issue; spawn 0–1 narrow verifier.
- **L2:** ambiguous modeling/data/model interpretation; spawn 2–3 orthogonal roles.
- **L3:** core derivation, milestone, or key integrated conclusion; use targeted native review and optionally the frozen Reviewer.

Do not spawn all six agents by default or spawn merely to demonstrate multi-agent
capability. Normal concurrent native subagents are `<= 3`. One Controller turn has a
total spawn budget of `<= 5`, including retries and follow-up verification. A retry is
allowed only for infrastructure failure or an empty response, at most once for the
same narrow role. Do not retry substantive disagreement, an inconvenient conclusion,
or a negative result. There is no recursive delegation (`agent -> agent -> agent`).

### 12.3 Contest Start Fast Path

When a selected problem, complete statement, and available attachments are identified,
the Controller starts exactly these three independent agents in parallel:

1. `problem_scout` — questions, objectives, inputs, outputs, constraints, units, dependencies, ambiguities, and scoring risks.
2. `data_auditor` — attachment inventory, schemas, units, missingness, duplicates, anomalies, temporal/spatial structure, variables, roles, and quality risks.
3. `model_scout` — minimum-sufficient baseline, justified stronger candidate, and useful genuinely different alternate, each with object, assumptions, I/O, objective/equations/constraints, strengths, failure modes, implementation/validation cost, and evidence required for an upgrade.

They work independently, do not read sibling reports as authority, separate facts from
inference, and return directly to the Controller. The Controller waits for all three
unless timeout/failure occurs, then synthesizes the dependency graph, data facts,
candidate models, minimum-sufficient modeling spine, and executable Q1 plan. Only the
Controller can freeze the modeling spine. A fourth agent is sequential and targeted
only after the first three finish and only for a demonstrated L3 gap.

### 12.4 Post-run review and repair

`result_critic` is callable only after a real artifact exists. It reviews question fit,
hard constraints, expected versus observed signal, anomalies, baseline sufficiency,
earned complexity, instability, overfit, invalidity, and recommends `ACCEPT`, `REPAIR`,
`CHANGE`, or `STOP`.

`math_verifier` is used only for mathematical risk: derivation, objective, constraints,
units, dimensions, probability, boundaries, or cross-question variable propagation.
The two roles must remain orthogonal rather than both reviewing the whole task. A core
L3 disagreement is escalated to the Controller directly; no permanent Sol verifier
subagent is created.

The repair flow is one targeted critique, one normal repair, targeted validation, then
Controller decision. If a core assumption fails, the Controller may reopen the model
decision once. P1/Polish items go to a backlog and do not block the next question.

### 12.5 Compact return contract

Every native report uses this shape and normally returns only 5–8 key findings:

```text
ROLE:
TASK:
STATUS: COMPLETE | PARTIAL | TIMEOUT | BLOCKED
FACTS:
- ...
INFERENCE:
- ...
ASSUMPTIONS:
- ...
RISKS:
- P0 / P1 / Polish: ...
RECOMMENDATION:
- ...
BLOCKER:
- none / ...
EVIDENCE:
- relative path / section / table / output
CONFIDENCE: HIGH | MEDIUM | LOW
```

No report may invent data, runs, metrics, official rules, or evidence. A substantive
disagreement is resolved by source inspection and, if needed, one targeted escalation;
the Controller does not use majority vote as proof.

### 12.6 Existing workflow and official-rule boundaries

Keep Fast Path, `explore`/`milestone`, minimum-sufficient modeling, evidence-gated
complexity, risk-based validation, honest negative/mixed results, question-level
`outputs/qX/`, `CURRENT_PROGRESS.md`, `DECISIONS.md`, and light paper review. Do not
add journals, run registries, whole-repository hashes, manifests, agent databases, voting systems,
automatic decision engines, general-purpose writer subagents, automatic paper-claim promotion, merge,
or push.

Until official 2026 material is provided, format, page count, anonymity, AI-use
declaration, support materials, and submission requirements remain `TBD`/`UNVERIFIED`.

## 13. Shadow Review Escalation and Ownership

Review Lane is an asynchronous side channel. A Reviewer finding does not automatically
create a Builder prompt, trigger a repair, change a model, or enter the Builder critical
path. The only major cross-lane router is Human judgment, optionally informed by Web GPT
and the Reviewer’s frozen evidence:

```text
Reviewer / Web GPT finding
        -> Human review and judgment
        -> explicit Builder prompt only when necessary
```

Use these lightweight escalation levels:

- **R0 — PRESENTATION ONLY:** color, font, legend, layout, caption, figure redesign,
  table layout, prose compression, or visual hierarchy. Builder interruption: **NO**.
- **R1 — EVIDENCE ENHANCEMENT:** sensitivity plot, residual diagnostic, or robustness
  presentation suggestion. Record as backlog; interruption: **NO**, unless Human promotes it.
- **R2 — POTENTIAL MODELING CONCERN:** strong assumption, constraint implementation,
  incomplete explanation, or a figure exposing a possible model problem. Record evidence;
  Builder continues until Human explicitly decides otherwise.
- **R3 — DIRECTIONAL / P0:** wrong problem interpretation/objective/unit, missing core
  constraint, leakage, invalid equation, serious data/result contradiction, or metric
  mismatch that can change the conclusion. Mark `BUILDER INTERRUPTION RECOMMENDED`, but
  do not interrupt or repair automatically; require Human judgment and an explicit prompt.

`visual_critic` is a read-only Review Lane agent for frozen figures and tables. Its only
primary recommendations are `KEEP`, `REDRAW`, `MERGE`, `SPLIT`, or `DROP`. It may assess
presentation assets but cannot change scientific facts, data, metrics, parameters,
objectives, models, baselines, or actual results. Review Root defaults to self-review;
at most one native helper runs at a time, including figure_designer. Design and critique
are sequential; the global concurrent limit remains three. No recursive spawn.

Builder owns modeling code, computation, configs, formal result evidence, raw outputs,
plot-ready data, readable formal figures/tables, captions, question-level prose, the
complete first-draft manuscript, and the generated PDF. Review Lane consumes that frozen
complete artifact for independent acceptance and optional refinement; only in its own
`review/*` branch may it modify presentation assets such as polished figures/tables,
captions, narrative, and PDF layout. Reviewer must use frozen data, must not read values
back from PNGs, and is never a required producer for Builder completion. Existing
`paper-review` remains the source of truth for paper review modes.

### 13A. Frozen figure production and design priors

`figure_designer` targets Sol/xhigh for key figures. Builder or Review Root may request its
bounded support. Its only potential write exception is an assigned pure plotting script,
figure PDF/PNG and note in an explicitly isolated review or scratch workspace. It cannot
modify shared style, configuration, scientific inputs, results or claims. Workspace-write
is not a file whitelist or automatic worktree isolation. If actual child cwd/permissions
cannot be established, keep the configured read-only specification/patch fallback and let
the invoking root execute it in that root's own authorized workspace. Current configuration
uses that fallback. Check tracked, untracked and important ignored inputs before/after execution.
One figure has one writer. Frozen source identity must match; missing input is BLOCKED,
changed input is STALE. No automatic merge, rebase or cherry-pick.

Builder produces and exports `outputs/qX/plot_data/`, important `figure_briefs.md`, plotting
scripts, readable formal figures and the paper-facing version. Review Lane owns only its
optional `review/*` refinements; it does not own first production. Keep source, use,
version/base_sha and necessary checks in the existing question summary.
Only corpus deduplication, frozen plotting-input identity and submission packaging use
necessary hashes; ordinary experiments still have no run registry or execution journal.

After interpreting the current statement/attachments, consult the design-priors skill
on demand: INDEX plus at most 3–5 relevant cards. Historical papers cannot supply current
data, weights, thresholds or conclusions. User-confirmed seeds and independently verified
additions have distinct provenance. Reviewed official_showcase_design cards may also inform
design without implying verified prize status; evidence-backed singletons remain provisional
but callable. No contest AI-policy review is part of this upgrade;
ordinary authorized analysis, plotting and tests need no repeated approval. Human remains
the cross-window router for accepting patches and substantive scientific changes.

## 14. Pre-contest freeze

The pre-contest design-prior cap is 20 complete design readings. Complete means the body
mainline plus abstract, framework, core model, result, validation/limitation, model-choice,
claim-evidence, figure-role, transferable and non-transferable extraction; download-only or
abstract-only items do not count. Once the inventory reports 20, stop corpus search,
download, extraction and pattern expansion. The former 50-paper target is post-contest work.

The pre-contest freeze becomes active when this finalization turn ends: do not expand agents,
skills, governance, directory structure or workflow architecture. During the contest use the
existing Builder, frozen Review lane, handoff guide and WINDOW_PACKET path directly. Only a
real P0 that blocks competition use may justify an architectural change, and it still requires
an explicit, bounded repair. The freeze policy is active even though a snapshot/freeze commit
must not be created until the user separately confirms it.
