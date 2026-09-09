---
name: "contest-orchestrator"
description: "Use for bounded repository-native Codex multi-agent orchestration in CUMCM2026: L0-L3 routing, Contest Start fan-out, read-only role contracts, wait/fallback policy, and bounded review repair."
metadata:
  short-description: "CUMCM2026 bounded native multi-agent orchestration"
---

# Skill: contest-orchestrator

用于 CUMCM2026 的受控原生 Codex multi-agent。该 skill 默认协调窄范围、只读、
证据导向的子 Agent；用户实际选择的 Builder 根模型担任 Controller，负责综合、
裁决和共享状态写入。

## Scope and non-goals

保留现有 `explore` / `milestone`、Fast Path、minimum-sufficient modeling、风险导向
验证、诚实保留 negative/mixed result、`outputs/qX/`、`CURRENT_PROGRESS.md`、
`DECISIONS.md` 和 detached Reviewer 双窗口。不要把仓库变成科研框架；不新增 journal、
run registry、hash/manifest、agent result database、投票系统、自动决策、自动 writer、
自动 paper claim promotion、自动 merge 或 push。Builder 负责第一版正式图表和完整初稿；
当前 figure_designer 配置为可由 Builder 或 Review Root 调用的只读设计/patch 回退。
语料去重和冻结绘图输入允许必要身份校验。

缺失的 2026 官方格式、页数、匿名、AI 使用声明、支撑材料和提交要求保持
`TBD`/`UNVERIFIED`，不得用往届论文或经验代替。

## Controller boundary

Builder/Controller 是用户在当前会话实际选择的根模型，可以是 Astra、Sol 或其他
可用模型；“Act as Sol”和仓库配置都不能改变真实 session model。已知模型覆盖须按
真实回执报告，非Sol根模型不是失败。Controller 是 sole orchestrator、sole synthesis
layer、sole modeling judge、default main-line writer 和 shared durable state 的 sole writer。
它也是从已确认任务到真实求解、可读图表、逐问正文、完整源稿和多页 PDF 的生产责任人。

Native agents 默认只读分配的范围并 report back；隔离绘图例外按 AGENTS 13A。不得写 `docs/CURRENT_PROGRESS.md`、
`docs/DECISIONS.md`、milestone summary、durable paper state、formal `outputs/qX/`、
source/data、Git index 或 `main`；不得执行 `git add`、`commit`、`push`、merge、rebase、
cherry-pick；不得 spawn additional agents。当前 detached Reviewer 仍是 frozen SHA 的
独立审查层，不审 Builder dirty state。Reviewer 默认自己审阅；一次最多一个原生 helper，
designer 与 critic 串行，不递归 delegation；全局并发仍不超过三。

## Complexity router

| Level | Condition | Spawn policy |
|---|---|---|
| L0 | trivial / mechanical | 0 |
| L1 | bounded implementation / local issue | 0–1 narrow verifier |
| L2 | ambiguous modeling / data or model interpretation | 2–3 orthogonal roles |
| L3 | core derivation / milestone / key integrated conclusion | targeted native review; optional frozen Reviewer |

禁止所有任务默认启动六 Agent，也禁止为了展示 multi-agent 而 spawn。正常并发 native
agents `<= 3`。单个 Controller turn 总 spawn budget `<= 5`，包括 retry 和 follow-up
verification。retry 仅限 infrastructure failure 或 empty response，同一窄角色最多一次；
不因 substantive disagreement、不方便的结论或 negative result retry。第四视角不提高全局
并发，前三个完成后才由 Controller sequentially spawn targeted verifier。

## Contest Start Fast Path

只有在 selected problem、complete statement、available attachments 都已识别时执行。
Controller 并行且只启动：

1. `problem_scout`：题目分解、逐问目标、输入、输出、硬约束、单位、依赖、歧义、评分风险。
2. `data_auditor`：附件清单、schema、单位、missing、duplicates、anomalies、时空结构、变量、数据角色和质量风险。
3. `model_scout`：A minimum-sufficient baseline、B justified stronger candidate、C genuinely different alternate（仅在有用时），并说明 mathematical object、assumptions、input/output、objective/equations/constraints、strengths、failure modes、implementation/validation cost 和 complexity upgrade evidence。

三者执行前不得获得 sibling report，不得把 sibling report 当 authority，必须独立工作、
区分事实与推断、直接回传 Controller。Controller WAIT all，除非 timeout/failure；然后
才综合 problem dependency graph、data facts、candidate models，形成 minimum-sufficient
modeling spine 和 Q1 executable plan。只有 Controller 可以 freeze Modeling Spine。

## Post-run review

`result_critic` 只有在真实 artifact 存在后调用，检查是否真正回答问题、hard constraints、
expected/observed signal、异常、baseline sufficiency、complexity 是否 earned、
instability/overfit/invalidity，并只给 `ACCEPT`、`REPAIR`、`CHANGE` 或 `STOP` 建议。

`math_verifier` 仅在存在 derivation、objective、constraint、unit、dimension、probability、
boundary 或 variable-propagation 风险时调用。两者必须 orthogonal，不得都做“全面审核”。
L3 核心数学争议由 math verifier 报告升级需求，再由 Controller 直接裁决；不创建永久
Sol verifier subagent。

## Normal completion

一问主解或必要验证完成都只触发下一问或全文整合，不单独结束。正常完成要求同时具有：
每问可追溯答案；核心约束/单位/必要验证已查；逐问完整叙述和完整源稿；可读正式图表；
表图数字与正文相符；实际多页 PDF 逐页渲染检查；失败、局限和人工待核项明确。代码、
数值、粗略提纲、配置存在、单页测试或旧 PASS 均不能替代本轮完整运行。只有 P0、关键
歧义/外部输入、未授权资源、用户叫停或会话/服务错误可暂停受影响分支。普通技术取舍
不反复询问。最终参赛提交仍由用户手工完成。

## Bounded repair

```text
artifact
  -> targeted critique
  -> one normal repair
  -> targeted validation
  -> Controller: ACCEPT | CHANGE MODEL | STOP
```

核心假设失败时 Controller 只能重新打开 modeling decision 一次。P1/Polish 进入 backlog，
不阻塞下一问。禁止无限 `critic -> repair -> critic -> repair`，也不因超时或失败 helper
把可以诚实推进的任务变成永久 blocker。

## Read scope and context minimization

- `problem_scout`：题面和相关附件索引。
- `data_auditor`：附件、metadata、数据协议；不读 sibling conclusion。
- `model_scout`：题面、附件索引/schema、建模协议和已批准 artifacts。
- `math_verifier`：指定公式、假设、单位、约束、相关实现和结果。
- `result_critic`：实际 run/output、图表、目标、baseline 和相关配置。
- `paper_checker`：逐问摘要、paper section、图表、公式、caption 和 `outputs/qX/`。

不要把同一批大型文件无差别复制给所有 Agent。子 Agent 默认只读；不要运行正式训练、
正式求解、大规模分析、真实竞赛题任务或下载比赛数据作为 orchestration 验证。

## Return contract

默认只返回 5–8 条关键 findings：

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

没有证据的内容必须标为 inference、assumption、blocker 或 `UNVERIFIED`。事实冲突由
Controller 检查源文件；推断冲突才在确有结论影响时追加一次 targeted escalation；不使用
majority vote 代替验证。

## Review and implementation boundary

Contest Start fan-out 是 Builder 内部 cognition layer，不替代 Builder 生产。Builder 在
冻结前独立完成该阶段的求解、检查、正式图表和论文内容；milestone 后继续下一问。
Reviewer 在 detached worktree 消费 frozen SHA，负责独立验收和可选精修，而非必需的
生产依赖。需要修复时只在 `review/*` 分支创建具体 commit，由 Builder/Human 决定是否
cherry-pick。禁止 Reviewer 直接写 main 的 progress/decisions，禁止自动 merge/rebase/push。

本 skill 与 `.agents/skills/modeling-workflow/SKILL.md`、`.agents/skills/paper-review/SKILL.md`
配合使用，不替代它们。

## On-demand design prior routing

先解释当前题面/附件并形成任务口径和候选路线，再按需调用
`.agents/skills/design-priors/SKILL.md`：只读 INDEX 和最多 3–5 张匹配卡。
不扩展 Contest Start 三 scout。历史设计不能覆盖题面或代入旧数值；绘图模式必须匹配
当前 brief。Builder 可在自身工作区复用 figure_designer（Sol/xhigh）的只读规格/patch，
并自行执行和验收；frozen 后 Review Root 可再次独立调用 designer 与只读 visual_critic。
