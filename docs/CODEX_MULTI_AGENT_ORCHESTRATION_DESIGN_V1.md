# Codex Multi-Agent Orchestration Design V1

**Status:** HISTORICAL / DESIGN ONLY — not a description of current runtime state.
Current entry points: `AGENTS.md`, `.codex/config.toml`, `.codex/agents/` and the routed skills.

**Repository:** `E:\CUMCM2026`

**Audit date:** 2026-09-04

**Scope:** repository-native Codex multi-agent orchestration design for the 2026 CUMCM workflow. This document does not activate any agent configuration, create a `.codex/` tree, run competition work, modify the paper, or create a Git commit.

## 1. Executive Summary

The current repository is suitable for a controlled native multi-agent layer. Its existing operating principles already provide the most important safety boundary: a Builder/Controller owns the main line, durable state has a single writer, exploration is separated from milestones, and the independent Reviewer works from a frozen state.

The recommended V1 is deliberately narrow:

- One GPT-5.6 Sol Builder/Controller is the only orchestrator, synthesizer, model decision-maker, and default writer on the main line.
- Luna subagents provide cheap, orthogonal, read-only cognition: problem decomposition, data audit, model scouting, result criticism, and paper checking.
- A math verifier is available for high-risk mathematics; ordinary checks may use Luna at high or xhigh reasoning, while core or disputed mathematics can be upgraded to Sol.
- Contest Start uses exactly three native agents: `problem_scout`, `data_auditor`, and `model_scout`. A fourth agent is normally premature.
- Post-run review uses `result_critic` and `math_verifier` only when the artifact or conclusion risk justifies the overhead.
- The existing detached Reviewer window remains. Native subagents are Builder-internal assistants, not replacements for an independent frozen-state review.

The local Codex installation verifies a stable `multi_agent` feature flag, model/reasoning/sandbox CLI controls, and the current global configuration. It does not verify a repository-local custom-agent file schema or the exact native spawn contract. Those fields remain `TO VERIFY` until verified against the local Codex version and official product documentation.

## 2. Current Repository Audit

### 2.1 Repository state observed

At the beginning of this design-only task:

- Absolute repository path: `E:\CUMCM2026`.
- Git branch: `main`.
- HEAD observed: `db7f9c0 chore: finalize competition environment`.
- Worktree was clean before this design document was created.
- No repository-local `.codex/` directory or custom-agent definitions were present.
- No competition problem, attachment set, formal run, result set, or paper body was assumed.

The final worktree for this task is intentionally expected to contain only this new untracked design document. No commit is authorized in this round.

### 2.2 Existing governance that this design preserves

The repository already contains the following relevant controls:

- Fast Path for time-critical contest work.
- Explore/Milestone separation.
- Minimum-sufficient modeling and evidence-based complexity escalation.
- Validation by risk rather than by a fixed checklist performed blindly.
- Honest handling of negative, mixed, or inconclusive results.
- Builder main-line continuity without waiting for the Reviewer.
- Detached Reviewer worktree review from a frozen milestone state.
- `outputs/qX/` as the natural question-level artifact boundary.
- `CURRENT_PROGRESS.md` as a dashboard, not a full laboratory notebook.
- `DECISIONS.md` as the durable decision record.
- Light paper review rather than a heavy journal, hash, manifest, or registry system.
- No automatic push.

### 2.3 Relevant current files and skills

The audit found the existing governance and workflow documents requested by the repository bootstrap instructions, including:

- `AGENTS.md`
- `README_START_HERE.md`
- `REPOSITORY_OPERATING_GUIDE.md`
- `PROJECT_BOOTSTRAP_CHECKLIST.md`
- `docs/CURRENT_PROGRESS.md`
- `docs/REPOSITORY_MAP.md`
- `docs/ENVIRONMENT.md`
- `docs/MODELING_PROTOCOL.md`
- `docs/DATA_PROTOCOL.md`
- `docs/SUBMISSION_SPEC.md`
- `.agents/skills/handoff/SKILL.md`
- `.agents/skills/modeling-workflow/SKILL.md`
- `.agents/skills/paper-review/SKILL.md`

The current repository does not yet contain actual `q1`, `q2`, or later problem artifacts. Therefore, this design defines how future artifacts are reviewed without pretending that any result exists now.

### 2.4 Local Codex and CLI facts observed

The local Codex CLI was available at the time of audit. The following were directly observable:

- `codex exec --help` exposes `--model`, `--profile`, `--sandbox`, `--cd`, `--add-dir`, and related execution controls.
- Recognized sandbox values include `read-only`, `workspace-write`, and `danger-full-access`.
- `codex agents --help` describes browsing agent sessions on the local app-server; it does not document custom repository agent definitions.
- `codex features list` reports `multi_agent` as stable and enabled.
- `multi_agent_v2` is present but disabled and not treated as a V1 dependency.
- The current global configuration contains `model = "gpt-5.6-luna"`, `model_reasoning_effort = "xhigh"`, and `sandbox_mode = "workspace-write"`.
- No local command output inspected during this audit established the schema for `.codex/agents/*.toml` or a repository-local orchestration file.

The desired Controller model is GPT-5.6 Sol, but binding that role through a repository-local custom-agent mechanism is `TO VERIFY`; the current global default must not be mistaken for an active project Controller policy.

### 2.5 Suitability assessment

| Area | Assessment | Consequence |
|---|---|---|
| Main-line ownership | Ready | Keep Builder/Controller as sole integrator and default writer. |
| Artifact boundaries | Ready | Use statement, attachments, `outputs/qX/`, paper sections, and milestones as scopes. |
| Durable state | Ready | Keep `CURRENT_PROGRESS.md` and `DECISIONS.md` Controller-owned. |
| Independent review | Ready | Keep the frozen detached Reviewer window. |
| Native role definitions | Not active | Design now; verify schema before implementation. |
| Native spawn/wait semantics | Partially observed | Use a bounded controller policy; do not rely on undocumented fields. |
| Contest facts | Not available | Leave problem, official rules, format, AI declaration, and submission requirements `TBD`/`UNVERIFIED`. |

## 3. Why Multi-Agent Helps / Does Not Help Here

### 3.1 Where it helps

1. Independent first-pass cognition reduces the chance that one Controller interpretation of a statement, unit, attachment, or constraint becomes an unchallenged premise.
2. Orthogonal scouts reduce Sol context load while preserving a central decision-maker who can compare assumptions and evidence.
3. Targeted adversarial review catches mathematical, dimensional, objective, boundary-condition, and result-integrity errors before they become paper claims.
4. A bounded paper checker can compare question answers, formulas, figures, captions, and reported outputs without turning every modeling step into a full review.

### 3.2 Where it does not help

Multi-agent orchestration is not useful for trivial file edits, deterministic formatting, a single obvious calculation, or repeated rereading of the same large file. It also cannot replace the Controller’s responsibility for choosing a model, interpreting conflicting evidence, deciding whether a complexity increase is justified, or making an official-submission decision.

The overhead is real: prompt construction, context transfer, waiting, disagreement resolution, and increased opportunities for stale or overconfident advice. The router below therefore treats spawning as a risk/cost decision, not as a default quality badge.

## 4. Proposed Architecture

```text
Human
  |
  v
GPT-5.6 Sol Builder / Controller
  |  sole orchestration, synthesis, judgment, default writing
  |-- L0/L1: direct work or one narrow check
  |-- L2: bounded orthogonal native fan-out
  |       |-- problem_scout      (Luna)
  |       |-- data_auditor       (Luna)
  |       |-- model_scout        (Luna)
  |       |-- result_critic      (Luna)
  |       |-- math_verifier      (Luna or Sol upgrade)
  |       `-- paper_checker      (Luna)
  |
  |  compact returns, source inspection, synthesis, decision
  v
Main-line implementation and durable artifacts
  |
  `-- frozen milestone -> independent Reviewer worktree
```

The control flow is:

1. The Controller classifies the task and defines non-overlapping scopes.
2. Native subagents read the assigned material independently and return compact, evidence-linked reports.
3. The Controller waits according to the router, checks direct evidence when reports disagree, and makes the decision.
4. Only the Controller writes shared durable state on the Builder main line.
5. An independent Reviewer is invoked only at a meaningful frozen milestone or when the risk justifies a second worktree.

Native subagents must not recursively spawn agents in V1. There is no automatic majority vote, automatic model selection, automatic merge, or automatic push.

## 5. Controller Responsibilities

The Builder/Controller must:

- Confirm the task scope, available files, and current milestone before spawning anything.
- Classify work as L0, L1, L2, or L3.
- Select only orthogonal roles whose outputs can change a decision or reduce a material risk.
- Give each role a narrow read scope and explicitly state that other reports are unavailable.
- Set a deadline, maximum concurrency, retry limit, and fallback before fan-out.
- Keep problem facts, assumptions, inferences, and decisions separate.
- Synthesize reports instead of copying a report into `CURRENT_PROGRESS.md` or `DECISIONS.md`.
- Decide whether to implement, repair, change, stop, or defer.
- Preserve the minimum-sufficient baseline and require evidence for complexity escalation.
- Continue the next question when a non-critical review is pending.
- Freeze a milestone before invoking the detached Reviewer.
- Keep all official-rule, format, page, anonymity, AI-disclosure, support-material, and submission claims `UNVERIFIED` until official sources arrive.
- Never allow a native subagent to write shared governance state, stage files, alter the main branch, or push.

## 6. Agent Role Matrix

The names below are proposed stable role names. They are not active custom-agent files in this round.

| Role | Default model intent | Trigger | Required output | Explicit limit |
|---|---|---|---|---|
| `problem_scout` | GPT-5.6 Luna, high | Contest Start or materially ambiguous statement | Independent decomposition, dependencies, ambiguities, candidate deliverables, open questions | No final model, no status writes, no conclusions from other agents |
| `data_auditor` | GPT-5.6 Luna, high | Attachments or external data are present | File inventory, schema, units, missingness, duplicates, outliers, data role, quality risks | No final model, no fabricated data, no result/status writes |
| `model_scout` | GPT-5.6 Luna, xhigh for L2; high for bounded work | Multiple plausible formulations or model selection risk | Baseline, stronger candidate, alternate; objective, assumptions, I/O, constraints, costs, failure modes, validation, upgrade conditions | No “advanced” method for its own sake; no implementation or model freeze |
| `math_verifier` | Luna xhigh by default; Sol high/xhigh for L3 core disputes | Mathematical, unit, dimension, probability, boundary, or inter-question propagation risk | Adversarial check with exact claims, counterexamples, severity, repair | Does not choose the final model; may escalate a core dispute to Sol |
| `result_critic` | GPT-5.6 Luna, high | A real output or experiment artifact exists | Question fit, constraints, signal, anomalies, baseline sufficiency, complexity value, overfit/instability/invalidity, next action | Never invents metrics or criticizes absent outputs |
| `paper_checker` | GPT-5.6 Luna, high | A question summary, figure/table, or draft section exists | Per-question answer coverage, output consistency, formulas/units, figures/captions, abstract, stacking, redundancy, mixed/negative integrity, page cost | Does not infer official requirements; works with existing paper-review guidance |

The Controller remains the final judge. A stronger model is an escalation path, not a default reward for every role.

## 7. Task Complexity Router

| Level | Typical work | Native fan-out | Default concurrency | Decision rule |
|---|---|---:|---:|---|
| L0 | Mechanical edit, known command, simple lookup, deterministic formatting | None | 0 | Controller acts directly. |
| L1 | Bounded engineering, one narrow ambiguity, one local sanity check | Optional one verifier | 0–1 | Spawn only if the check can alter the next action. |
| L2 | Ambiguous modeling, competing formulations, nontrivial attachment interpretation | Orthogonal scouts/verifiers | 2–3 | Fan out when independent evidence is cheaper than a wrong path. |
| L3 | High-risk mathematics, milestone, key conclusion, integrated paper claim | Targeted native review plus optional detached Reviewer | Up to 3 native; 4 only by explicit Controller exception | Require adversarial coverage and a bounded decision gate. |

### 7.1 When to spawn

Spawn when at least one of the following is true:

- Two or more materially different interpretations or formulations are plausible.
- An attachment or data issue could invalidate a model or conclusion.
- A result will be promoted into a paper claim or milestone.
- A mathematical, dimensional, boundary, probability, or propagation error could survive ordinary inspection.
- The cost of an independent check is lower than the expected cost of rework.

### 7.2 When not to spawn

Do not spawn for a show-of-work pattern, a direct edit, a missing artifact, a single obvious route, a task already bounded by a trusted test, or a time-critical action where orchestration overhead exceeds the remaining decision window. Do not ask `result_critic` to review an experiment that has not produced an actual output.

### 7.3 Upgrade Luna to Sol

Upgrade the math verifier or request direct Sol analysis when a disputed issue affects the objective, a hard constraint, a core derivation, a key probability/statistical claim, an inter-question dependency, or a final conclusion. Do not upgrade merely because a method sounds sophisticated or because a Luna report is inconvenient.

## 8. Contest Start Fan-Out

This Fast Path applies only when a problem has been selected and the complete statement plus all available attachments have been identified.

### 8.1 Exact initial fan-out

The Controller starts exactly these three independent native roles:

1. `problem_scout`: read the statement and identify structure, dependencies, ambiguities, and deliverables.
2. `data_auditor`: inspect the attachments and data structure, units, quality, and intended role.
3. `model_scout`: read the statement and attachment index independently and propose baseline/stronger/alternate formulations with validation conditions.

They receive no conclusions from one another. Each receives only the source paths and its task contract. They do not write shared state.

### 8.2 Controller synthesis

After the bounded wait, the Controller:

- labels each report as complete, partial, timed out, or failed;
- checks important claims against the source files;
- builds the initial dependency graph;
- selects a minimum-sufficient modeling spine;
- defines the baseline and its validation plan;
- writes an executable Question 1 plan only after synthesis;
- records unresolved assumptions as unresolved rather than silently resolving them.

`math_verifier` is normally not the fourth Contest Start agent because no model or derivation exists yet. `result_critic` is premature because no output exists. `paper_checker` is premature because no answer or figure exists. A fourth role is justified only by a demonstrated L3 risk, such as a mathematically ambiguous statement that can change the whole problem structure.

## 9. Modeling / Implementation Review Flow

The normal modeling loop is:

```text
Controller chooses baseline
        |
        v
Builder implements / runs bounded experiment
        |
        v
Actual artifact exists? ---- no ---> continue implementation or stop
        |
       yes
        v
Targeted result_critic + math_verifier, if risk warrants
        |
        v
Controller Judge: ACCEPT / REPAIR / CHANGE / STOP
```

The Controller must preserve a runnable baseline while exploring a stronger candidate. A scout recommendation is not a result, and a plausible model is not a validated conclusion. The Controller decides whether the stronger candidate earns its complexity through evidence, interpretability, stability, and question fit.

For a normal L1 task, the Controller may inspect directly. For L2 work, `result_critic` and `math_verifier` should receive different scopes and should not be asked to produce duplicate general reviews. For L3 work, a stronger-model math verification or a frozen Reviewer may be added.

## 10. Milestone Review Flow

The existing dual-window workflow remains the milestone boundary:

1. Builder completes a coherent milestone: code, outputs, question summary, validation notes, and required paper-facing artifacts.
2. Builder creates a local milestone commit and records the SHA according to existing repository rules.
3. Builder continues the next question or next bounded task without waiting for the Reviewer.
4. Reviewer opens a detached worktree at the frozen milestone SHA.
5. Reviewer performs an independent integrated review; it may create a review branch/commit if a concrete repair is needed.
6. Builder/Controller evaluates the review and cherry-picks only an accepted, attributable repair.
7. No automatic merge, rebase, or push occurs.

Milestone review is not required for every exploratory run. It is valuable when a model, result, figure, or narrative is about to become a durable cross-question dependency or a major paper claim.

## 11. Builder Native Agents vs Reviewer Worktree

| Concern | Builder-native subagent | Detached Reviewer |
|---|---|---|
| State | Current Builder working state | Frozen milestone SHA |
| Purpose | Fast, narrow, local cognition and triage | Independent integrated audit |
| Timing | During exploration or immediately after an artifact exists | At milestone or high-risk integrated claim |
| Scope | One role and one bounded question | Cross-file, cross-question, paper-facing consistency |
| Writes | Read-only by default; no main-line writes | Own detached worktree/review branch only |
| Integration | Report returns to Controller | Controller reviews and cherry-picks accepted repair |
| Replacement relationship | Not a replacement for independent review | Not a reason to spawn native agents for every task |

### 11.1 Overlap and distinction

Native `result_critic` catches a local issue quickly: an anomaly, a weak baseline comparison, a constraint violation, an unstable output, or an obvious question-fit problem. The Reviewer checks whether the complete milestone remains coherent across code, outputs, figures, tables, question answers, and paper narrative.

Native `math_verifier` can stop a bad derivation before the Builder spends time on it. The Reviewer verifies the integrated artifact after the assumptions, implementation, outputs, and prose have been connected.

### 11.2 Reviews that are native-only by default

- Early exploration triage.
- Whether a small experiment is worth continuing.
- Local shape, unit, and input-output sanity checks.
- Whether a baseline is sufficient to unblock the next question.
- Immediate anomaly classification where no durable claim exists.

### 11.3 Reviews that should reach the detached Reviewer

- A major model or assumption being frozen as a milestone.
- A result that will drive multiple later questions.
- A final or near-final figure/table and its surrounding narrative.
- A critical paper claim whose correctness depends on multiple files.
- A cross-question consistency issue that cannot be checked from one local artifact.

The Builder does not block the next question for Reviewer polish. A P0 integrity issue can pause promotion of the affected claim, but unrelated work may continue.

### 11.4 Reviewer helper policy

The Reviewer may use one narrow read-only helper for a clearly orthogonal issue during an L3 review, such as a unit check or figure-caption check. The helper must not spawn another helper, must not write the review branch, and must return to the Reviewer rather than directly to main. The Reviewer remains responsible for the integrated review result.

## 12. Read/Write Permission Matrix

| Actor | Read repository | Write source/code | Write `outputs/qX/` | Write progress/decisions | Git index/main | Own branch/worktree |
|---|---:|---:|---:|---:|---:|---:|
| Builder/Controller | Yes | Yes, when implementing | Yes | Yes, after judgment | Yes, when authorized by existing rules | N/A |
| Native subagent | Assigned scope only | No | No | No | No | No |
| Detached Reviewer | Frozen repository/worktree | Yes for an accepted review repair | Yes for review artifacts | No direct main-line governance writes | No main-line staging | Yes, review branch only |
| Reviewer helper | Narrow assigned scope | No | No | No | No | No |
| Human | As available | By explicit action | By explicit action | By explicit action | By explicit action | By explicit action |

“Sole writer” means one Controller owns shared durable state on the Builder main line. It does not prevent the human or a separately authorized Reviewer from making a deliberate, attributable change in its own context. A future writer agent, if ever added, must have an explicit artifact ownership boundary and its own worktree; it is not part of V1.

## 13. Subagent Return Contract

Every native report should be compact enough for synthesis and should distinguish direct evidence from inference:

```text
ROLE: <role name>
TASK: <one-sentence scope>
STATUS: COMPLETE | PARTIAL | TIMEOUT | BLOCKED
CONFIRMED FACTS:
- <fact with file/path evidence when available>
INFERENCE:
- <interpretation, clearly labeled>
ASSUMPTIONS:
- <assumption or unresolved ambiguity>
TOP RISKS:
- P0/P1/Polish: <risk and why it matters>
RECOMMENDATION:
- <next action, or “no action”>
BLOCKER:
- <only if a decision cannot safely proceed>
EVIDENCE:
- <relative path, section, line, table, or command output>
CONFIDENCE: HIGH | MEDIUM | LOW
```

Reports must not pretend that an absent file, absent metric, or unverified rule exists. They should prefer a short evidence list over a long essay. The Controller may request a follow-up only for a specific unresolved issue, not for open-ended elaboration.

## 14. Concurrency / Token / Latency Policy

### 14.1 Budgets

- L0: zero native subagents.
- L1: at most one narrow verifier.
- L2: normally two or three orthogonal native roles.
- L3: at most three native roles by default; a fourth requires an explicit Controller reason and must be genuinely orthogonal.
- Contest Start: exactly three native roles unless the Controller records an L3 exception.
- Detached Reviewer helper: at most one, with no recursion.

The default normal maximum is three concurrent native agents. Four is an exceptional ceiling, not a target.

### 14.2 Context minimization

The Controller should pass a compact task brief and paths, not duplicate every large file into every prompt:

- `problem_scout`: statement and relevant attachment index.
- `data_auditor`: attachments and any source metadata; no model conclusions.
- `model_scout`: statement and attachment index; it may inspect required inputs independently.
- `result_critic`: actual run/output paths, configuration, and question objective.
- `math_verifier`: formulas, assumptions, units, constraints, and relevant code/output paths.
- `paper_checker`: question summary, paper section, figure/table paths, and reported values.

### 14.3 Waiting, retry, and fallback

- Contest Start waits for all three roles up to a Controller-defined deadline because the synthesis depends on their orthogonal coverage.
- Other tasks wait only for the selected roles and do not make unrelated Builder work wait.
- A transport failure or empty response may be retried once with the same narrow scope.
- A substantive disagreement is not solved by blind retry or majority vote; the Controller inspects source evidence or requests one targeted escalation.
- A timeout becomes a recorded partial input, not a permanent blocker. The Controller proceeds with an explicit gap or falls back to direct Sol analysis.

The exact native timeout and token-budget field names are `TO VERIFY` in the local Codex configuration schema.

## 15. Failure / Timeout / Disagreement Handling

### 15.1 Failure states

Each role returns `COMPLETE`, `PARTIAL`, `TIMEOUT`, or `BLOCKED`. A missing report is not silently converted into agreement.

### 15.2 Fact disagreement

When two reports disagree about a fact, the Controller reads the source file or command output directly. If the fact remains unavailable, it stays `UNVERIFIED` and cannot be used as a hard premise.

### 15.3 Inference disagreement

When reports agree on facts but disagree on interpretation, the Controller records the alternatives, preserves the baseline, and requests a targeted verifier only if the choice can materially affect the outcome.

### 15.4 Stale or contaminated context

Reports tied to a changed working state, a different milestone, or a file modified after the assigned snapshot are stale. The Controller discards or re-runs them rather than merging them into the current decision.

### 15.5 Overconfident low-evidence advice

An answer without evidence, a result claim without an actual output, or an official-rule claim without an official source is treated as an inference or blocker, never as a confirmed fact.

## 16. Bounded Repair Policy

The repair loop is deliberately finite:

1. Run the baseline or candidate and collect actual artifacts.
2. Request targeted `result_critic` and/or `math_verifier` review.
3. Apply at most one normal repair attempt for the identified issue cluster.
4. Re-run only the targeted smoke check and the affected validation.
5. The Controller decides `ACCEPT`, `CHANGE`, or `STOP`.

If a P0 issue persists or the core assumption is invalid, the Controller may reopen the modeling decision once: compare the preserved baseline with one justified alternative, then choose a change or stop. P1 and Polish items become a bounded backlog and do not block unrelated questions.

There is no indefinite “critic → repair → critic” loop. Stop when the repair does not improve evidence, when complexity cost exceeds value, when time risk dominates, or when the available evidence cannot support a stronger claim. Mixed or negative results remain valid outcomes when honestly reported.

## 17. Proposed Repository File Layout

### 17.1 Current active layout to preserve

```text
AGENTS.md
README_START_HERE.md
REPOSITORY_OPERATING_GUIDE.md
PROJECT_BOOTSTRAP_CHECKLIST.md
docs/
  CURRENT_PROGRESS.md
  REPOSITORY_MAP.md
  ENVIRONMENT.md
  MODELING_PROTOCOL.md
  DATA_PROTOCOL.md
  SUBMISSION_SPEC.md
.agents/skills/
  handoff/SKILL.md
  modeling-workflow/SKILL.md
  paper-review/SKILL.md
data/
outputs/
paper/
references/
scripts/
tests/
```

### 17.2 Future layout, not created in V1 design-only mode

```text
.agents/skills/contest-orchestrator/SKILL.md
.codex/config.toml
.codex/agents/
  problem-scout.toml
  data-auditor.toml
  model-scout.toml
  math-verifier.toml
  result-critic.toml
  paper-checker.toml
```

The future `.codex/` names and file shapes are proposals only. No future tree is created by this document.

## 18. Exact Changes Needed in `AGENTS.md`, `.agents/skills/`, and Future `.codex/`

These are implementation requirements for a later, separately authorized round:

### 18.1 `AGENTS.md`

Add a short “Native Multi-Agent Orchestration” section that:

- defines the Sol Controller as the sole orchestrator and shared-state writer;
- defines L0–L3 routing and the default concurrency ceiling;
- defines the Contest Start three-role fan-out;
- requires independent prompts and compact fact/inference returns;
- forbids native recursive spawn, main-line writes by subagents, automatic merge, and push;
- explains that native subagents complement but do not replace the detached Reviewer;
- preserves Fast Path, Builder continuity, minimum sufficiency, risk-based validation, `CURRENT_PROGRESS.md`, and `DECISIONS.md`.

Do not rewrite the existing Builder/Reviewer rules into an agent framework.

### 18.2 `.agents/skills/`

Add a future `.agents/skills/contest-orchestrator/SKILL.md` containing the router, role contracts, wait/fallback rules, permission boundaries, and bounded repair policy. It should route to the existing `modeling-workflow` and `paper-review` skills rather than replace them.

The existing `paper-review/SKILL.md` should receive only a small integration note in a later implementation if needed: native `paper_checker` is a pre-review assistant, while the existing paper-review workflow remains the source of truth for paper checks.

### 18.3 Future `.codex/`

Only after local schema verification should a future implementation add `.codex/config.toml` and `.codex/agents/*.toml`. The implementation must use only fields verified for the installed Codex version. It must not copy global authentication, account, plugin, or unrelated machine configuration into the repository.

## 19. Proposed Custom-Agent Files and Model/Reasoning/Sandbox Intent

The following definitions describe intended behavior, not a validated TOML schema.

### 19.1 `problem-scout.toml`

- **Purpose:** independent problem structure and dependency scan.
- **Trigger:** Contest Start or a material statement ambiguity.
- **Non-trigger:** trivial interpretation, already settled local question, or no source statement.
- **Model/reasoning:** GPT-5.6 Luna, high; upgrade only for a demonstrated L3 ambiguity.
- **Sandbox intent:** read-only, exact repository source scope.
- **Allowed reads:** problem statement, assigned reference rules if provided, attachment index.
- **Forbidden writes:** all source, data, outputs, progress, decisions, Git state, and paper files.
- **Return:** compact contract in Section 13.
- **Ignore/escalate:** ignore unsupported “final model” advice; escalate a structural ambiguity that changes the dependency graph.

### 19.2 `data-auditor.toml`

- **Purpose:** audit attachment/data structure and quality.
- **Trigger:** attachments or external data are present.
- **Non-trigger:** no data artifact, or a deterministic one-file lookup.
- **Model/reasoning:** GPT-5.6 Luna, high.
- **Sandbox intent:** read-only; no data mutation.
- **Allowed reads:** assigned files, metadata, and data protocol.
- **Forbidden writes:** raw/processed/external data, scripts, outputs, status, decisions, and Git state.
- **Return:** file-level facts, units, missingness, duplicates, outliers, role, and risks.
- **Ignore/escalate:** ignore speculative cleaning; escalate a possible data leakage, unit, or target-definition problem.

### 19.3 `model-scout.toml`

- **Purpose:** compare a minimum-sufficient baseline, a justified stronger candidate, and an alternate formulation.
- **Trigger:** L2 ambiguity or competing model formulations.
- **Non-trigger:** model already selected and only implementation remains.
- **Model/reasoning:** GPT-5.6 Luna, xhigh for L2; Sol only through explicit Controller escalation.
- **Sandbox intent:** read-only; no execution unless a later policy explicitly permits a bounded dry run.
- **Allowed reads:** statement, attachment index/data schema, modeling protocol, existing approved artifacts.
- **Forbidden writes:** model freeze, code, configs, outputs, progress, decisions, paper, and Git state.
- **Return:** object, assumptions, I/O, objectives/constraints, pros, failure modes, cost, validation, and upgrade conditions.
- **Ignore/escalate:** ignore complexity without evidence; escalate incompatible objectives or constraints.

### 19.4 `math-verifier.toml`

- **Purpose:** adversarial verification of math and model semantics.
- **Trigger:** core derivation, units/dimensions, objective/constraint, probability, boundary condition, or cross-question propagation risk.
- **Non-trigger:** no formula, no model artifact, or a low-risk mechanical calculation.
- **Model/reasoning:** Luna xhigh by default; upgrade to GPT-5.6 Sol high/xhigh for L3 or disputed core mathematics.
- **Sandbox intent:** read-only; inspect exact formulas, code, configurations, and outputs.
- **Allowed reads:** assigned derivations, assumptions, units, constraints, relevant implementation and result paths.
- **Forbidden writes:** code, outputs, paper, progress, decisions, Git state, and final model selection.
- **Return:** exact check, counterexample or supporting evidence, severity, repair, and escalation need.
- **Ignore/escalate:** ignore stylistic disagreements; escalate a P0 validity threat.

### 19.5 `result-critic.toml`

- **Purpose:** criticize actual experiment or run outputs.
- **Trigger:** a real output, figure, table, metric, or result artifact exists.
- **Non-trigger:** before a run, with only a model proposal, or when there are no inspectable artifacts.
- **Model/reasoning:** GPT-5.6 Luna, high; Sol remains the judge.
- **Sandbox intent:** read-only.
- **Allowed reads:** run metadata, `outputs/qX/`, figures/tables, objective, baseline comparison, and relevant code/config.
- **Forbidden writes:** reruns, data mutation, output replacement, progress, decisions, paper, and Git state.
- **Return:** question fit, constraints, signal, anomalies, baseline sufficiency, complexity value, failure severity, and next action.
- **Ignore/escalate:** ignore unsupported metric invention; escalate unstable, invalid, or conclusion-changing evidence.

### 19.6 `paper-checker.toml`

- **Purpose:** question-level paper and artifact consistency pre-check.
- **Trigger:** a question summary, figure/table, or draft section exists.
- **Non-trigger:** no answer artifact or a purely exploratory note.
- **Model/reasoning:** GPT-5.6 Luna, high.
- **Sandbox intent:** read-only.
- **Allowed reads:** paper section, `outputs/qX/`, figures, tables, formulas, captions, and existing paper-review instructions.
- **Forbidden writes:** paper, figures, tables, progress, decisions, and Git state.
- **Return:** coverage, consistency, units, caption, abstract relevance, algorithm stacking, redundancy, mixed/negative integrity, and page cost.
- **Ignore/escalate:** ignore official-format assumptions; escalate a claim/output mismatch or an unverified submission requirement.

## 20. Codex Config Fields: Verified Locally vs `TO VERIFY`

### 20.1 Verified locally during this audit

| Capability/field | Local evidence | Status |
|---|---|---|
| Model selection | `codex exec --help` exposes `--model`; global config has `model` | Verified as a CLI/config concept |
| Reasoning selection | `codex exec --help` and global config expose reasoning control; current value is `xhigh` | Verified as a CLI/config concept |
| Sandbox selection | `codex exec --help` exposes `--sandbox` with read-only/workspace-write/danger-full-access | Verified as a CLI concept |
| Working directory | `--cd` is exposed and repository path is known | Verified as a CLI concept |
| Multi-agent feature | `codex features list` reports stable `multi_agent` enabled | Verified as a feature flag |
| Multi-agent V2 | Present but disabled | Not used by V1 |
| Repository custom-agent files | No `.codex/` tree found in this repository | Verified absent at audit time |

### 20.2 Still `TO VERIFY`

- Whether the installed Codex build supports repository-local `.codex/config.toml` overrides.
- Whether the supported custom-agent file is `.codex/agents/*.toml`, another format, or an app-server resource.
- Exact keys for agent name, prompt/developer instructions, model, reasoning, sandbox, approval, allowed paths, timeout, token budget, and output contract.
- Exact native spawn, parallel wait, cancellation, retry, and timeout APIs.
- Whether an agent can be explicitly prevented from spawning another agent.
- Whether native agents receive isolated worktrees or share the Builder working directory.
- Whether per-agent read-only semantics are enforceable independently of the parent session.
- Whether the visible host model identifiers can be bound in custom-agent definitions.
- Whether feature flags beyond stable `multi_agent` are required for repository-native role definitions.
- Precedence between global config, project config, profile config, and command-line overrides.

No undocumented field should be written into a future repository config merely because its name appears plausible.

## 21. Risks / Failure Modes

| Risk | Failure mode | Mitigation |
|---|---|---|
| Correlated reasoning | Several agents repeat the same first interpretation | Independent prompts, orthogonal scopes, no report sharing before synthesis |
| Orchestration overhead | More waiting and context transfer than the decision is worth | L0–L3 router and spawn budget |
| Scout overconfidence | Inference is presented as fact | Section 13 contract and source inspection |
| Stale state | Report describes files before a later edit | Scope/snapshot labels and Controller rejection of stale reports |
| Split-brain writing | Multiple agents mutate shared status or outputs | Controller-only main-line writes |
| Config drift | Future TOML is unsupported or silently ignored | Verify local schema before implementation; keep `TO VERIFY` explicit |
| Reviewer duplication | Native and detached reviews repeat each other | Local triage vs frozen integrated audit distinction |
| Complexity inflation | Stronger methods are adopted because they sound advanced | Baseline preservation and evidence-gated escalation |
| Context overload | Every role rereads every large input | Role-specific path scopes and compact returns |
| Infinite repair | Critic/retry loops consume contest time | One normal repair plus one bounded model reopen |
| Official-rule hallucination | Historical advice becomes current requirement | Keep all unavailable official facts `UNVERIFIED` |
| Premature paper claims | A promising output becomes prose before validation | Result critic and Controller promotion gate |

## 22. Minimal V1 Recommendation

The minimal useful V1 is:

- Define six read-only role contracts, but activate only the roles justified by the router.
- Use exactly three native agents at Contest Start: `problem_scout`, `data_auditor`, `model_scout`.
- Use at most three native agents concurrently by default and four only for an explicit L3 exception.
- Use `result_critic` and `math_verifier` after actual outputs exist and only when risk warrants them.
- Keep the detached Reviewer for frozen milestone and integrated paper-facing review.
- Keep Sol as the sole Controller, synthesizer, judge, and main-line writer.
- Do not create a future agent that writes shared durable state.
- Verify the installed Codex custom-agent schema before adding any `.codex/` file.

This is enough to obtain independent cognition where it has real value without turning the repository into a general research-agent framework.

## 23. Future V2 Possibilities

Only after V1 has been used and its overhead is observable should the project consider:

- Role activation based on measured failure patterns rather than blanket fan-out.
- A small library of contest-start and post-run prompt templates.
- A Reviewer helper for one additional orthogonal artifact check at L3.
- Better source-path and milestone labels in reports.
- A lightweight summary of recurring review defects, if it remains compatible with the existing governance philosophy.

V2 should not introduce a general workflow engine, automatic model registry, hash/manifest bureaucracy, or a requirement to record every internal thought.

## 24. Explicit List of Things Not to Automate

The following remain human/Controller decisions or explicitly authorized actions:

- Arbitrary or recursive agent spawning.
- Automatic selection or freezing of the final model.
- Automatic promotion of a result into a paper claim.
- Writing `CURRENT_PROGRESS.md` or `DECISIONS.md` from a subagent report without Controller synthesis.
- Direct native-subagent writes to source, data, outputs, paper, or Git state.
- Automatic merge, cherry-pick, rebase, or push.
- Deleting or overwriting files whose purpose is uncertain.
- Downloading data, installing dependencies, or upgrading core environments.
- Guessing 2026 official format, page limits, anonymity, AI declaration, support materials, or submission requirements.
- Copying past award papers into the project as current templates or official rules.
- Fabricating data, runs, metrics, figures, tables, citations, or validation.
- Running training, formal solving, large-scale analysis, or high-cost computation during bootstrap.
- Creating fake runs or placeholder metrics to satisfy a checklist.
- Building a heavy journal, hash, manifest, model registry, evidence matrix, or research-framework layer.
- Treating a majority vote among agents as proof of correctness.
- Allowing a timeout or failed helper to become a permanent blocker when the Controller can proceed honestly with a documented gap.

## Final Implementation Decision Record for This Design Round

- Current repository suitable for native multi-agent orchestration: **Yes, with a bounded V1**.
- Actual native multi-agent configuration created: **No**.
- Existing governance files modified: **No**.
- Competition task started: **No**.
- Formal model, run, metric, figure, table, or paper body created: **No**.
- Git commit created: **No, by explicit instruction for this design-only round**.
- Git push executed: **No**.
- Remaining unknowns: all custom-agent schema, native spawn/wait semantics, and official 2026 competition materials remain `TO VERIFY`/`UNVERIFIED` as applicable.

## Startup Prompt Examples

### Builder window

```text
Act as the GPT-5.6 Sol Builder/Controller for E:\CUMCM2026.
Classify the task L0–L3 before spawning anything.
Use native subagents only for orthogonal, read-only evidence gathering.
At Contest Start, spawn problem_scout, data_auditor, and model_scout only.
Keep facts, inference, assumptions, and decisions separate.
You are the sole orchestrator, judge, and shared-state writer.
Preserve the baseline, existing Fast Path, and Builder continuity.
Do not infer official 2026 rules; mark missing material UNVERIFIED.
Do not push or start formal competition computation without explicit scope.
```

### Reviewer window

```text
Review the frozen milestone SHA in your detached E:\CUMCM2026 worktree.
Audit code, outputs/qX, figures, tables, question answers, and paper consistency.
Remain independent from the Builder’s current working state.
Use at most one narrow read-only helper only for a demonstrated L3 issue.
Report facts separately from inference and classify P0/P1/Polish.
Create a review-branch repair only when it is concrete and attributable.
Do not write main-line progress or decisions.
Do not merge, rebase, or push.
Return ACCEPT, REPAIR, CHANGE, or STOP with evidence.
```
