# WINDOW_PACKET - working status

- 生成时间：2026-09-12T14:22:56+08:00
- 受众：网页分析 / 本机Builder接续
- 仓库：`C:\Users\ysw\Desktop\CUMCM2026`
- 分支 / HEAD：`main` / `c5d1b3baa55a72f211abfdf794acd415644aef21`
- dirty：yes
- 包类型：WORKING_STATUS（不是冻结证据）
- base_sha：not_applicable
- 当前赛题：D题《时频冲突检测与消解》；题面与附件由随包附件提供，结论以附件和问题摘要为准。
- 访问边界：接收者若无本机权限，只能使用本包正文和随包附件。

## Git时间点证据

```text
 M .gitignore
 M VISUAL_STYLE_PROFILE.toml
 M docs/CURRENT_PROGRESS.md
 M docs/DECISIONS.md
 M outputs/q1/figures/fig_q1_conflict_structure.pdf
 M outputs/q1/figures/fig_q1_conflict_structure.png
 M outputs/q1/figures/fig_q1_conflict_structure.svg
 M outputs/q1/figures/fig_q1_conflict_structure_grayscale.png
 M outputs/q1/results.json
 M outputs/q1/validation.json
 M outputs/q2/figures/fig_q2_solution_tradeoff.pdf
 M outputs/q2/figures/fig_q2_solution_tradeoff.png
 M outputs/q2/figures/fig_q2_solution_tradeoff.svg
 M outputs/q2/figures/fig_q2_solution_tradeoff_grayscale.png
 M outputs/q2/plot_data/objective_bounds.csv
 M outputs/q2/proof/sat_adjust_a_le_15.json
 M outputs/q2/proof/sat_adjust_b_le_33.json
 M outputs/q2/proof/sat_adjust_le_125.json
 M outputs/q2/proof/sat_b_le_3.json
 M outputs/q2/q2_optimization_audit.md
 M outputs/q2/q2_proof_matrix.csv
 M outputs/q2/results.json
 M outputs/q2/signal_and_upgrade.md
 M outputs/q2/six_revocation_candidate.json
 M outputs/q2/six_revocation_validation.json
 M outputs/q2/summary.md
 M outputs/q2/validation.json
 M outputs/q3/figures/fig_q3_addition_layout.pdf
 M outputs/q3/figures/fig_q3_addition_layout.png
 M outputs/q3/figures/fig_q3_addition_layout.svg
 M outputs/q3/figures/fig_q3_addition_layout_grayscale.png
 M outputs/q3/q2_input_from_result2.json
 M outputs/q3/q3_optimality_audit.json
 M outputs/q3/q3_optimization_audit.md
 M outputs/q3/results.json
 M outputs/q3/validation.json
 M outputs/q4/q4_optimization_audit.md
 M outputs/q4/r2_global_proof_status.md
 M outputs/q4/summary.md
 M paper/draft_sections/model_optimization.md
 M paper/draft_sections/q2.md
 M paper/draft_sections/q3.md
 M scripts/plot_q1_conflicts.py
 M scripts/plot_q2_tradeoff.py
 M scripts/plot_q3_additions.py
 M scripts/prove_q2_thresholds.py
 M scripts/prove_q4_active_milp.py
 M scripts/prove_q4_active_sat.py
 M scripts/search_q4_csp_bitset.py
 M scripts/solve_q2_cp_sat.py
 M scripts/validate_q2.py
 M src/visualization/style.py
 M work/q2/MODEL_CARD.md
 M work/q3/MODEL_CARD.md
 M work/q4/Q4_DIRECTION_MODEL_CARD.md
?? docs/D_EVIDENCE_CHAIN_AUDIT_20260912.md
?? docs/JUDGE_REVIEW_RESPONSE_20260912.md
?? docs/Q1_Q3_TEAM_HANDOFF_20260912.md
?? docs/Q4_PAPER_COMPLETION_PACKET_20260912.md
?? docs/Q4_R3_PROOF_AUDIT_HANDOFF_20260912.md
?? docs/Q4_RAW_FORMULA_GAP_20260912.md
?? docs/SCIENTIFIC_FIGURE_STYLE_RESEARCH.md
?? docs/team_handoff_20260912/
?? node_modules/
?? outputs/flowchart/
?? outputs/q2/evidence_audit_validation_20260912.json
?? outputs/q2/proof/SAT_EVIDENCE_INDEX.md
?? outputs/q2/proof/sat_evidence_validation.json
?? outputs/q2/proof/sat_shift_le_774.json
?? outputs/q2/proof/sat_shift_le_774_full.json
?? outputs/q2_q3_global_frontier/
?? outputs/q2_q3_joint_cp/
?? outputs/q2_q3_pareto/
?? outputs/q4/conditional_R3_RB1_validation_final.json
?? outputs/q4/proof_R3_RA0_RB1_M138_validation.json
?? outputs/q4/proof_R3_RA0_RB1_M138_witness.json
?? outputs/q4/proof_R3_RA0_RB1_M139_validation.json
?? outputs/q4/proof_R3_RA0_RB1_M139_witness.json
?? outputs/q4/proof_R3_RA0_RB1_M140_validation.json
?? outputs/q4/proof_R3_RA0_RB1_M140_witness.json
?? outputs/q4/proof_R_le_2_active_sat_glucose3.json
?? outputs/q4/proof_R_le_2_active_sat_r2_A2B0C0.json
?? outputs/q4/proof_R_le_2_dominance_validation.json
?? outputs/q4/proof_R_le_2_threshold_cutgen.json
?? outputs/q4/proof_R_le_2_threshold_cutgen_resume.json
?? outputs/q4/proof_R_le_2_threshold_cutgen_resume300.json
?? outputs/q4/proof_R_le_2_threshold_cutgen_resume300_correct.json
?? outputs/q4/proof_R_le_2_threshold_edge_cutgen.json
?? outputs/q4/proof_R_le_2_threshold_edge_cutgen_resume.json
?? outputs/q4/proof_R_le_2_threshold_edge_cutgen_resume2.json
?? outputs/q4/proof_R_le_2_threshold_edge_cutgen_resume3.json
?? outputs/q4/proof_R_le_3_validation_final.json
?? outputs/q4/q4_secondary_proof_matrix.md
?? outputs/q4/result4.xlsx.inspect.ndjson
?? outputs/q4/revocation_run.json
?? outputs/q4/revocation_validation.json
?? outputs/q4/sensitivity_H638_R_le_3_validation_final.json
?? outputs/q4/sensitivity_H648_R_le_3_validation_final.json
?? outputs/q4/smoke_R2_RA0_quick_restart.json
?? outputs/q4/smoke_max_active_q4.json
?? paper/figures/
?? paper/rebuild/
?? paper/tex/
?? scripts/assemble_q2_q3_pareto_report.py
?? scripts/build_q123_team_package.ps1
?? scripts/build_q4_proof_audit_package.ps1
?? scripts/build_submission_support_package.ps1
?? scripts/construct_joint_lower_bound_witnesses.py
?? scripts/greedy_joint_revocation_search.py
?? scripts/maximize_q4_active.py
?? scripts/prove_q2_q3_joint_sat.py
?? scripts/prove_q2_q3_joint_sat_occupancy.py
?? scripts/prove_q2_q3_joint_sat_occupancy_clique.py
?? scripts/prove_q2_q3_joint_sat_pairwise.py
?? scripts/prove_q2_q3_joint_sat_stream.py
?? scripts/prove_q2_shift_milp.py
?? scripts/prove_q2_shift_sat.py
?? scripts/q3_lp_dual.py
?? scripts/recheck_historical_19_q3.py
?? scripts/repair_q123_status.py
?? scripts/search_q4_r2_hamming.py
?? scripts/solve_q2_q3_joint.py
?? scripts/solve_q2_q3_joint_compact_cp.py
?? scripts/solve_q2_q3_joint_compact_threshold.py
?? scripts/solve_q2_q3_joint_cp_sat.py
?? scripts/solve_q2_q3_joint_cp_sat_strong.py
?? scripts/solve_q2_q3_joint_highs.py
?? scripts/solve_q2_q3_joint_interval_cp.py
?? scripts/solve_q2_q3_joint_scip.py
?? scripts/solve_q2_q3_pareto.py
?? scripts/solve_q4_scip.py
?? scripts/verify_q4_dominance_certificate.py
?? work/evidence/
```

### Worktrees

```text
worktree C:/Users/ysw/Desktop/CUMCM2026
HEAD c5d1b3baa55a72f211abfdf794acd415644aef21
branch refs/heads/main
```

## 当前进度原文
来源：`docs/CURRENT_PROGRESS.md`（dirty工作区时间点快照）

```markdown
# Current Progress

## Selected Problem

D 题：时频冲突检测与消解

## Current Goal

完成 Q1--Q4 论文重建、Q4 最小撤销层闭合、正式引用、AI 声明、用户指定版式复核和支撑包，保留未闭合次级指标的证据边界。

## Modeling Spine

计划行 → 重复使用事件展开 → 半开区间冲突检测 → 约束消解/新增计划优化 → Q4 间隔扩展 → 结果模板与论文统计。
当前已完成 intake；Q2 主目标与优先级前缀已完成证明，Q3 已从批准的 `result2.xlsx` 重新导入并完成最优装填和独立验证。

## Problem Status

| Problem | Status | Current method | Key result | Next |
|---|---|---|---|---|
| D / intake | complete | PDF + 5 个 XLSX + 用户 Markdown 对照；频率/时间/二维占用分析 | 已纠正重复事件语义：相邻起点步长=单次时长+空闲间隔；经验时间包络为 `[0,643)`；C 类步长为 10 | 作为 Q1–Q4 的统一输入口径 |
| D / Q1 | milestone complete | 正确重复递推 + 半开区间精确枚举；离散时频单元独立复核 | 150 个计划、1,300 个事件；297 对冲突，431 次事件级重叠；结果表已生成 | 将 297 条冲突边作为 Q2 硬约束输入 |
| D / Q2 | milestone complete / interface approved | CP-SAT 候选动作 + 资源格团约束 + 独立 CNF/CaDiCaL 阈值证明 + 双重独立复核 | `R*=6`、`R_A*=0`、`R_B*=4`、`M*=126`、`M_A*=16`、`M_B*=34`、`S10*=775` 已按条件字典序逐层证明；`S10≤774` 在完整候选全集上 `UNSAT` | Q3 已读取批准的 `result2.xlsx`；若改变 Q2 候选语义需重跑 |
| D / Q3 | milestone complete / optimum independently audited | 从批准 `result2.xlsx` 导入固定六撤销 Q2 + 完整 C 类候选枚举 + 资源格/成对冲突两种 0-1 编码 | 两种编码均闭合到 141；`sum(y)≥142` 不可行；独立可行性验证 PASS | Q2 方案变化时必须同步重算 |
| D / Q4 | milestone complete / minimum-revocation layer closed | 原始 150 条计划 + C 类间隔有限动作扩展；支配消元 + 六分支 SAT 全局证明；独立重建与工作簿回读 | `R≤3` 可行且 `R≤2` 六分支均 `UNSAT`，故统一口径下 `R*=3`；H=638/643/648 均有 `R≤3` 候选 | 固定 `R=3` 后继续闭合次级字典序层；不把当前工作簿写成完整次级最优 |

## Current Best Results

Q1 正式结果：在 11,175 个候选装备对中检出 297 对冲突装备（2.66%），其中 B-C 为 181 对，类别内冲突率 5.03%；148 个装备构成一个大连通分量，C007、C060 为孤立装备。连续区间算法与独立离散时频单元算法完全一致。正式资产见 `outputs/q1/`。

Q2 当前正式方案：150 个计划枚举为 4,582 个候选动作，CP-SAT 使用 52,939 条资源格团约束。总撤销目标的 LB=UB=6，固定 `R=6` 后 A 类撤销为 0；独立 CaDiCaL 证明 `B≤3`、`M≤125`、`M_A≤15`、`M_B≤33` 和 `S10≤774` 均不可行，因此七层条件字典序结果为 `(R,R_A,R_B,M,M_A,M_B,S10)=(6,0,4,126,16,34,775)`。正式方案为 A 类 4/16/0、B 类 2/34/4、C 类 12/76/2，144 个活动计划占用 15,816 个资源格，连续/离散检查均零冲突。末级证书使用完整候选全集，另有层指示器编码复核。

Q3 当前结果：从批准的 `result2.xlsx` 反向解析出 144 个活动计划和 15,816 个已占用单元，在 52,136 个完整 C 类候选起点中筛得 2,334 个与 Q2 不冲突的候选；资源格集合装填与 66,472 条成对冲突约束两种编码均得到 141，且“至少 142 台”阈值模型不可行。因此 Q3 题面主目标的 LB=UB=141；合并后 285 个活动计划占用 25,968 个不同单元，独立验证通过。旧 203 对应旧 19 撤销背景，已 supersede。

Q4 当前结果：在 H=643 下枚举 6103 个合法动作、建立 53679 条资源格约束；`R≤5`、`R≤4`、`R≤3` 均得到可行并通过独立重建验证。随后将 5953 个活动候选按外部冲突集合支配关系等价缩减为 5533 个，穷尽 `R=2` 的六个类别分支，六个 SAT 分支均返回 `UNSAT`，独立覆盖核验 `PASS`，因此统一口径下 `R*=3` 已闭合。旧工作簿候选 `R=3,R_A=0,R_B=1,M=142` 已被同一前缀下的独立验证 SAT 见证改进为 `M=140` 和 `M=139`；`R_B=0` 与 `M≤138` 的相邻阈值仍在证明中，不能把任何一个当前见证写成完整次级最优。边界 H=638、648 也均找到并验证 `R≤3` 候选。详细记录见 `outputs/q4/summary.md`、`outputs/q4/q4_optimization_audit.md`、`outputs/q4/q4_secondary_proof_matrix.md` 和 `outputs/q4/r2_global_proof_status.md`。

## Paper Status

摘要已按“问题—模型—算法—关键结果—证明边界”统一改写，第一页直接暴露 Q1 精确枚举、Q2 CP-SAT 与独立 SAT 阈值证明、Q3 HiGHS 集合装填、Q4 支配消元与六分支 SAT 证明，同时保留未闭合次级目标的范围说明。

已完成问题一至问题四逐问闭环的独立 XeLaTeX 重建稿 `paper/rebuild/`。正文包含摘要、问题重述、问题分析、合并式模型假设与符号说明、两列表符号表、独立数据预处理一级标题、Q1--Q4、模型检验、模型评价、AI 声明、引用和附录；流程图暂从正文撤出，图 3、图 6 的证据由三线表承载，Q1--Q3 图表统一使用 B 配色。PDF 页面检查和 20 页 A4 渲染检查均通过；本版结构按用户提供的参赛论文范例重排，不再把分离式模板检查器作为结构目标。问题四的完成入口为 `docs/Q4_PAPER_COMPLETION_PACKET_20260912.md`；正文只将 `R_{Q4}^*=3` 写成当前有限模型下已证明的最小撤销层，将 142 个调整等标为条件候选。最新评委视角复核见 `docs/JUDGE_REVIEW_RESPONSE_20260912.md`，当前主要待修是 AI 详情文件名、支撑包输入路径、Q2 边界见证封装和 Q4 两组可行见证的追溯说明。旧版 `paper/tex/` 保留不动。

## Important Decisions

D 题已进入当前工作线。用户正式确认 Q2–Q4 统一采用数据驱动时间包络 `[0,643)`，所有调整后事件不得越界；Q3 固定 Q2 结果并新增继承附件结构的 C 类设备。边界敏感性取 `H∈{638,643,648}`。Q2 已采用精炼方案 B；Q4 已批准继承同一字典序前缀，并仅为 C 类增加间隔动作。Q2 和 Q3 保持单向接口，Q3 剩余容量不回写 Q2；Q4 从 Q1 原始计划重新起算，不读取 Q3 新增设备。

Q2 采用精炼方案 B `R→R_A→R_B→M→M_A→M_B→S_n` 和 CP-SAT 资源格团约束；未证明的字典序层不得固定后继续形成正式最优结论。H<643 的完整重复包络边界规则继续有效。Q3 采用完整 C 类模板集合装填并固定 Q2，不反向影响 Q2。正式图提供 PDF/SVG/PNG 与灰度预览。

## Q2–Q3 Joint Pareto Audit — 2026-09-12

已完成联合接口的正式定义和证据分级稿 outputs/q2_q3_pareto/global_joint_pareto_proof.md。结论分为三层：Q2 第一目标 R*=6 已由可行解与 R≤5 不可行闭合；当前批准六撤销工作簿下 Q3=141 已闭合；把 Q2 布局和 Q3 同时优化的全体 F_r=max N3 尚未闭合。联合 CP-SAT 仅作为诊断，已找到 R=6 下 N3≥162（固定 Q2 已证前缀）和 N3≥187（不固定次级前缀）的可行下界，不得写成全局最优。R=6,8,10,12,15,19 及历史 R=19 的逐背景 Q3 条件最优表已生成，且历史 R=19 的 203 与统一链 R=19 的 106 说明完整 Q2 占用布局决定 Q3 容量。论文草稿 paper/draft_sections/model_optimization.md、q2.md、q3.md 与阶段 LaTeX 已加入该联合分析；正式题面接口仍保持 Q2 先求解、Q3 再固定背景。

## Immediate Next Actions

1. 人工核对匿名信息、当届官方提交通知以及 AI 使用记录；这些内容不由自动检查器替代。
2. Q2 七层证明已闭合；继续推进 Q4 时必须单独闭合 `R=3` 内的 `R_B、M、M_A、M_B、S_{10}^{(4)}` 相邻阈值，不得把 Q2 证据移作 Q4 证明。
3. 保持 Q1--Q4 支撑包与源稿版本一致，不把条件候选或敏感性上界改写为全局最优。

## Pre-contest Infrastructure — 2026-09-09

2026 D 题 modeling task has started; the official D statement and available attachments are present. Official submission format, page count, anonymity, AI declaration and support-material requirements remain TBD/UNVERIFIED.

Pre-contest design-prior cap reached: 24 deduplicated candidates, 20 verified local fulltexts and
20 complete design readings. Coverage is A/B/C = 3/5/5 and D/E = 3/4, including 7 vocational papers.
One user-confirmed and one independently verified national-first paper remain the only prize-eligible
count; the other 18 are official-showcase design readings with award status UNVERIFIED. Corpus search,
download, extraction and pattern expansion are now stopped. The former 50-paper target is post-contest
only. Exact pages and boundaries: `references/design_priors/INDEX.md`.

The Builder-first synthetic scratch completed, without Review help during production: task breakdown,
real integer enumeration, dependency-aware Q2, assertions, one bounded correction cycle, frozen plot
data, a readable formal figure, question-level prose and a complete 4-page A4 Chinese PDF. A real
`gpt-5.6-sol/xhigh` read-only figure specification was consumed by the Builder/root; the root executed
and integrated the figure. No additional human prompt was needed after the rehearsal task was stated.

Frozen review was then exercised at SHA `3c1e04882f7d5e38a94287fe85f89a93085d1232` in an independent
worktree. Deliberately changing the Builder result from 56 to 999 afterward did not change the Review
copy or frozen WINDOW_PACKET. A read-only `gpt-5.6-terra/high` visual review returned KEEP with no P0/P1
and one optional P2 spacing note; it did not modify Builder output. Review commit
`f2140263f77871b3b9bbcda5b10e7a2e8ff33c1a` remains isolated and was not merged or cherry-picked.

The final internal PDF is `output/pdf/CUMCM2026_synthetic_rehearsal.pdf`. Poppler rendered all four
pages; required Chinese/text/formula/table/figure/reference/appendix markers passed, and every page was
actually inspected. This validates only the synthetic repository publication chain. CTeX still lacks
`ctexart.cls`; the verified path uses bundled Python, ReportLab/pypdf, SimHei and Poppler. 2026 format,
page count, anonymity, AI declaration, support-material and submission requirements remain UNVERIFIED.

The self-contained guide is `docs/WINDOW_HANDOFF_GUIDE.md`; dynamic status and frozen packet export use
`scripts/export_window_handoff.py` and include explicit result/figure/PDF attachments. On 2026-09-09,
the user authorized one local main-repository pre-contest snapshot covering the previously approved
workflow sources, configuration, skills, guides, exporter and design-prior index/cards. Generated
scratch/review outputs, private fulltexts, credentials and environments are excluded; unrelated dirty
must be preserved. Git history and the newly exported status WINDOW_PACKET are the sources of truth
for the snapshot identity, not a manually maintained HEAD in this document. No push, merge, rebase,
cherry-pick or formal Review Lane creation is authorized. The workflow/design-prior freeze policy
remains active: do not expand repository architecture or governance; continue the official D modeling
line with the existing Builder, frozen Review lane and WINDOW_PACKET path. Only a real P0 blocker can
justify a bounded architecture repair.
```

## 已有决定原文
来源：`docs/DECISIONS.md`（dirty工作区时间点快照）

```markdown
# Decisions

只记录会长期影响后续建模、数据、论文结构、工具链或治理的 durable decisions。

旧 decision 不删除，使用 `superseded / deprecated / rejected`。

## Template

### DEC-YYYYMMDD-NNN — Short title

- Status: proposed / accepted / rejected / superseded
- Date:
- Context:
- Decision:
- Alternatives considered:
- Evidence / rationale:
- Consequences:
- Affected files:
- Supersedes:
- Superseded by:

### DEC-20260910-001 — 重复使用事件采用“时长加空闲间隔”步长

- Status: accepted
- Date: 2026-09-10
- Context: 初始脚本曾把附件中的“间隔时长”误作相邻两次使用的起点间距。
- Decision: 若首次区间长度为 `l`、空闲间隔为 `g`，第 `k` 次事件按 `k(l+g)` 平移。
- Alternatives considered: 按 `kg` 平移；该解释被 PDF 第 2 页 A001 示例否定。
- Evidence / rationale: A001 首次区间 `[35,40)`、间隔 60，PDF 明示第二次区间 `[40+60,45+60)=[100,105)`；C083 第 12 次据此为 `[641,643)`。
- Consequences: Q1–Q4 的事件展开、冲突检测、时间包络、分布图和优化约束统一采用新步长；旧的 `[0,621)` 及基于它的探索统计全部失效。
- Affected files: `scripts/solve_q1.py`、`scripts/analyze_plan_distribution.py`、`work/intake/`
- Supersedes: 初始 intake 草案中的 `kg` 递推解释
- Superseded by:

### DEC-20260910-002 — Q2–Q4 采用统一经验时间包络，Q3 固定 Q2 结果

- Status: accepted
- Date: 2026-09-10
- Context: 题面要求“不增加时频资源”，但没有给出全局时间终点；Q3 又要求基于 Q2 无冲突计划新增 C 类设备。
- Decision: 使用正确递推得到的原始事件包络 `[0,643)` 作为 Q2–Q4 一致的固定时间域；Q3 固定 Q2 最终计划，不联合重优化原计划。边界敏感性采用 `H∈{638,643,648}`，其偏移量 5 与 Q2 最大时间平移幅度一致。
- Alternatives considered: 以 Q2 解的最晚结束时刻动态定义时间域；该方案会使资源总量依赖 Q2 解。允许 Q3 重优化原计划；`result3.xlsx` 无法完整记录这种变化。
- Evidence / rationale: Q3 措辞为“基于问题 2 求解得到的无冲突用频计划”；result3 只记录新增序号、频段区间和时间区间。643 来自附件数据，不是题面给定值。
- Consequences: Q2 和 Q4 调整后的全部重复事件均需留在 `[0,643)`；Q3 只在剩余资源中选择新增 C 类有限重复计划。敏感性场景只改变时间终点并重新执行受影响的 Q2/Q3 流程，论文必须区分题面事实和建模边界。
- Affected files: `work/intake/PROBLEM_MAP.md`、`work/intake/PROBLEM_FRAMEWORK.md`、`work/intake/DISTRIBUTION_ANALYSIS.md`
- Supersedes:
- Superseded by:

### DEC-20260911-001 — Q2 采用候选动作全局模型并保留目标敏感性

- Status: superseded
- Date: 2026-09-11
- Context: Q1 冲突边总体稀疏但集中在 B-C，且一个频移/时移会同步改变一个计划的多条重复事件冲突关系；题面没有提供“尽可能/尽量”的数值权重。
- Decision: Q2 以每个计划的 keep/frequency-shift/time-shift/revoke 候选动作建立全局 0-1 冲突模型。主解释按撤销数、调整数、A/B 类修改数、总绝对平移量的字典序尝试；另保留 A 类优先探测作为目标敏感性。所有候选完整重复事件必须位于 `[0,643)×[0,100)`。
- Alternatives considered: 逐冲突边贪心修复；只检查首次事件；以未声明的加权和替代字典序；这些方案无法稳定表达全局耦合或题面目标层级。
- Evidence / rationale: 候选模型规模为 4,582 个动作、270,626 条候选冲突约束。当前 H=643 内已找到 19 撤销、113 调整的无冲突 incumbent；独立连续半开区间和离散时频单元复核均通过。第一层 solver 在限时内未证明全局最优，因此结果只标 incumbent。
- Consequences: `outputs/q2/results.json` 是当前主可行候选而非全局最优证明；`outputs/q2/priority_A_19_probe.json` 用于检查高优先级保持的代价。后续先加强下界/求解时间，再固定最终 Q2 方案进入 Q3。
- Affected files: `scripts/solve_q2.py`、`scripts/solve_q2_incumbent.py`、`scripts/solve_q2_stage.py`、`scripts/validate_q2.py`、`outputs/q2/`、`paper/draft_sections/q2.md`
- Supersedes:
- Superseded by: DEC-20260911-005

### DEC-20260911-002 — 修正 H<643 的候选边界筛选

- Status: accepted
- Date: 2026-09-11
- Context: H=638 敏感性试验暴露出原候选生成器允许完整重复时间包络超过 H 的频移动作/保持动作。
- Decision: 若原计划在不改变时间的动作下的完整重复终点超过 H，则 keep 和 frequency-shift 候选均删除；只有满足 H 的 time-shift 候选可以保留，随后仍由独立验证器检查。
- Alternatives considered: 仅在结果输出后检查边界；该方案可能让越界动作参与求解并污染 incumbent，拒绝。
- Evidence / rationale: 修正前 H=638 结果含 C083 `[641,643)`、C088 `[638,640)` 越界事件；修正后重算的 H=638 incumbent 通过独立验证。
- Consequences: Q2 的 H 敏感性必须使用修正后的候选生成器；旧 H=638 越界结果不进入正式结论或审计包。
- Affected files: `scripts/solve_q2.py`、`outputs/q2/summary.md`、`paper/draft_sections/q2.md`
- Supersedes: 修正前 H=638 探索结果
- Superseded by:

### DEC-20260911-003 — 保持 Q2/Q3 单向接口并采用统一科研图表主题

- Status: superseded
- Date: 2026-09-11
- Context: 当前 Q2 主 incumbent 的 C 类撤销数为 0，且旧图同时用颜色、斜线和异量纲柱形表达多层比较，容易误读为 C 类禁止撤销或把 Q3 目标提前混入 Q2。
- Decision: 保留 Q2 主方案 `19 撤销/113 调整`，另以固定总撤销数 19、至少 1 个 C 类撤销的独立 MILP 作为诊断，不用该诊断替换主方案；Q3 只能读取最终选定的 Q2 活动计划和剩余资源，不反向参与 Q2 选择。论文图统一使用 `VISUAL_STYLE_PROFILE.toml`，输出 PDF、保留文本元素的 SVG 和 400 dpi PNG 预览，并保留灰度 QA。
- Alternatives considered: 为了 Q3 容量而直接改选 Q2；把 C 类撤销 0 当作硬约束；直接复制外部 SEM 模拟数据/模板；继续使用旧版多重图例和斜线编码；均拒绝。
- Evidence / rationale: C 类撤销探针得到 A `3/15/2`、B `0/24/16`、C `11/78/1`，调整数 117，独立验证 PASS；主方案调整数 113，故仍保留。两份外部材料的模板与 SkillPack 均声明模拟数据不能作为实际结论，且其可迁移价值主要是风格、路由和 QA 机制。
- Consequences: `outputs/q2/c_revocation_probe_19.json` 只作语义诊断；`outputs/q2/figures/` 下的 Q1/Q2 图使用统一主题和 SVG 交付；后续 Q3 不得根据“看起来更适合新增 C 类”的指标回写 Q2。
- Affected files: `VISUAL_STYLE_PROFILE.toml`、`src/visualization/style.py`、`.agents/skills/scientific-figure-system/SKILL.md`、`scripts/diagnose_q2_c_revocation.py`、`scripts/plot_q1_conflicts.py`、`scripts/plot_q2_tradeoff.py`、`outputs/q1/`、`outputs/q2/`、`paper/draft_sections/q2.md`
- Supersedes:
- Superseded by: DEC-20260911-005（Q2 数值与主图部分；单向接口和图表主题继续有效）

### DEC-20260911-004 — Q3 固定 Q2 后采用完整 C 类模板集合装填

- Status: superseded
- Date: 2026-09-11
- Context: 问题三要求基于问题二无冲突计划，在不增加时频资源的前提下最多新增 C 类装备；C 类计划具有固定的 12 次重复结构。
- Decision: 固定当前 Q2 主方案的 131 个活动计划和占用矩阵，在 `[0,643)×[0,100)` 内枚举全部整数起点的完整 C 类模板，先筛除与 Q2 冲突的候选，再用 0-1 集合装填最大化新增计划数。Q3 不使用问题二的 ±10/±5 平移限制，也不反向改变 Q2。
- Alternatives considered: 用剩余面积除以 72；只安排首次事件；将 Q3 目标回写 Q2；这些方案无法表达 C 类完整重复结构或违反两问的单向接口。
- Evidence / rationale: 共枚举 52,136 个完整候选，3,555 个与 Q2 不冲突；HiGHS 返回 `OPTIMAL`，选中值和上界均为 203，独立连续/离散冲突复核及结果表核对均通过。
- Consequences: 当前 Q2 主方案和基准域下的 Q3 正式结论为最多新增 203 台；若 Q2 方案或 H 场景变化，必须重建占用矩阵并重新求解 Q3。Q3 结果不参与 Q2 目标选择。
- Affected files: `scripts/solve_q3.py`、`scripts/validate_q3.py`、`scripts/build_result3.mjs`、`outputs/q3/`、`paper/draft_sections/q3.md`
- Supersedes:
- Superseded by: DEC-20260911-005（固定背景和数值更新；模型形式继续有效）

### DEC-20260911-005 — Q2 采用精炼方案 B、CP-SAT 上下界 gate 与六撤销主结果

- Status: accepted
- Date: 2026-09-11
- Context: 旧 Q2 正式结果为 19 撤销的未证 incumbent，且更好的已验证可行解没有及时更新 UB；外部工作簿给出六撤销方案，仓库内 CP-SAT 运行又形成了 `LB=UB=6` 的独立证书。
- Decision: 保留候选动作、完整重复事件和双重验证基础，将主求解器强化为 CP-SAT 资源格团约束；Q2 采用精炼方案 B `R→R_A→R_B→M→M_A→M_B→S_n`，其中 `S_n=Σ(|df|/10+|dt|/5)`。每层记录 LB/UB，未证明时默认停止后续层。正式方案采用已验证六撤销 incumbent；Q3 固定该方案后重算。
- Alternatives considered: 继续使用旧方案 A；把类别撤销与调整合并为 `modified_A/B/C`；直接相信外部截图的完整最优性；继续以 19 撤销作为正式 incumbent。前两者不能精确表达高等级撤销保护，后两者缺少或忽略证据。
- Evidence / rationale: `revocation_bound.json` 记录总撤销目标值与 best bound 均为 6；`priority_prefix_run.json` 进一步证明 `R_A=0`。随后独立 CNF + CaDiCaL 对 `B≤3`、`M≤125`、`M_A≤15`、`M_B≤33` 的阈值均返回 `UNSAT`，并由连续半开区间、离散资源格和工作簿一致性检查复核六撤销动作。H=638、648 下的 `R≤5` 也分别被 CP-SAT 证明不可行，结合六撤销见证得到敏感性场景的 `R*=6`。
- Consequences: 在当前候选动作集和字典序解释下，Q2 可写“最少撤销 6 个”，并可条件地写 `R_B=4`、调整数 `M=126`、`M_A=16`、`M_B=34` 已逐层证明；末级归一化平移量 `S10=775` 尚未证明全局最优。用户已批准当前 `result2.xlsx` 作为 Q3 唯一输入，Q3 已据此重跑得到最多新增 141 台；旧 19 撤销与 Q3=203 均为 superseded 历史结果，Q3 不反向影响 Q2。
- Affected files: `.agents/skills/modeling-workflow/SKILL.md`、`scripts/solve_q2_cp_sat.py`、`scripts/import_q2_workbook.py`、`scripts/finalize_q2_six.py`、`outputs/q2/`、`outputs/q3/`、`paper/draft_sections/q2.md`、`paper/draft_sections/q3.md`
- Supersedes: DEC-20260911-001 的目标顺序和 19 撤销状态；DEC-20260911-003 的 Q2 数值；DEC-20260911-004 的固定背景与 203 数值
- Superseded by:

### DEC-20260911-006 — Q3 采用双编码与 142 台阈值闭合最大新增数

- Status: accepted
- Date: 2026-09-11
- Context: Q3 主模型返回 141 台和 `OPTIMAL`，但需要检查是否存在与 Q2 早期阶段相似的“只有可行解、没有可靠上界”问题。
- Decision: 保留固定批准 Q2 的资源格集合装填模型，并将同一 2,334 个候选独立重编码为候选两两冲突约束；同时直接测试 `sum(y)≥142` 的可行性。Q3 不增加题面外的布局美观、集中度或规则性目标。
- Alternatives considered: 仅引用一次 HiGHS 状态；用剩余面积除以 72 作为上界；为得到更整齐图形而加入人工偏好。前者证据单一，后两者分别过松和偏离题意。
- Evidence / rationale: 正式资源格模型得到 LB=UB=141；独立成对模型含 66,472 条冲突边，同样得到 LB=UB=141、`mip_gap=0`；加入 `sum(y)≥142` 后返回 `INFEASIBLE`。正式 141 台方案通过连续/离散冲突、边界和工作簿一致性验证。
- Consequences: 在批准的 `result2.xlsx`、`[0,643)×[0,100)` 和完整 C 类模板条件下，可以写“最大新增 141 台”。可能存在多个 141 台等价排布，但这不构成题面主目标的优化缺口；Q2 方案或资源域变化时必须重算。
- Affected files: `scripts/verify_q3_optimality.py`、`outputs/q3/q3_optimality_audit.json`、`outputs/q3/q3_optimization_audit.md`、`paper/draft_sections/q3.md`、`paper/draft_sections/model_optimization.md`
- Supersedes:
- Superseded by:

### DEC-20260912-001 — Q2–Q3 联合 Pareto 作为敏感性接口，不替代序贯主答案

- Status: accepted
- Date: 2026-09-12
- Context: 同一撤销数下不同 Q2 布局会产生不同 Q3 剩余容量；历史 19 撤销背景得到 Q3=203，而按 A/B 保护优先的统一链 19 撤销背景得到 Q3=106。用户要求分析这种差异，并评估是否可以用联合 Pareto 反向选择 Q2。
- Decision: 定义给定 Q2 布局的条件函数 N3*(x) 和最终活动量 T(x)=150-R(x)+N3*(x)，对 R=6,8,10,12,15,19 及历史 19 背景形成联合 Pareto 敏感性表。正式竞赛接口仍遵循 Q2 先求解、Q3 固定具体工作簿；联合 CP-SAT 只报告可行下界，未完成阈值上下界闭合前不得声称完整 F_r=max_{x:R(x)=r}N3*(x) 全局最优。
- Alternatives considered: 以 Q3 容量反向改写 Q2 正式目标；在未闭合联合上界时把 N3=162 或 187 写成六撤销联合最优；仅按撤销数而不保留完整占用集合比较。前两者缺少题面授权或最优性证据，后者无法解释同一 R=19 的 97 台差异，均拒绝。
- Evidence / rationale: Q2 R*=6 由 outputs/q2/revocation_bound.json 闭合；当前批准六撤销背景 Q3=141 由 outputs/q3/results.json 和 q3_optimality_audit.json 闭合；逐背景表位于 outputs/q2_q3_pareto/pareto_results_with_history.csv；联合探索在 R=6 下找到 N3≥162（固定 Q2 已证前缀）和 N3≥187（不固定次级前缀），但状态为可行 incumbent。
- Consequences: 论文可以把联合接口、非支配样本和证据分级作为方法亮点，但必须同时披露完整联合前沿未闭合；六撤销仍是 Q2 第一目标的全局最优，Q3 不能在序贯规则下推翻它。详细证明稿为 outputs/q2_q3_pareto/global_joint_pareto_proof.md。
- Affected files: outputs/q2_q3_pareto/global_joint_pareto_proof.md、outputs/q2_q3_pareto/summary_with_history.md、paper/draft_sections/model_optimization.md、paper/draft_sections/q2.md、paper/draft_sections/q3.md、paper/tex/main.tex
- Supersedes:
- Superseded by:

### DEC-20260912-002 — Q4 从 Q1 原始计划扩展 C 类间隔动作，当前只冻结可行上界

- Status: superseded
- Date: 2026-09-12
- Context: 问题四允许部分 C 类装备调整用频间隔时长，但 Q4 仍应从问题一原始计划消解冲突，不能把 Q2/Q3 的序贯接口误当作 Q4 输入。
- Decision: Q4 在 `[0,643)×[0,100)` 内从 Q1 的 150 条计划重新建模；保留频段 ±10、首次时间 ±5 和单动作互斥规则，仅为 C 类加入 `g'∈{0,…,18}` 的整数间隔候选。目标沿用 `R→R_A→R_B→M→M_A→M_B→S10`。截至本决定，3 台撤销已得到合法可行候选，但 `R≤2` 尚未证明不可行，因此不冻结“最少撤销 3 台”或后续层全局最优结论。
- Alternatives considered: 直接以 Q2 `result2.xlsx` 作为 Q4 输入；把 Q3 新增 C 类设备混入 Q4；用未声明的加权和替代字典序；均会改变题面接口或优先级含义，拒绝。
- Evidence / rationale: `outputs/q4/proof_R_le_3.json` 及独立验证给出 147 个活动计划；`outputs/q4/result4_workbook_validation_independent.json` 对当前工作簿回读仍为零连续/离散冲突。`R≤2` 的 clique、Bool、pairwise 和窄域运行均为 UNKNOWN，不能构成下界证明。
- Consequences: `outputs/q4/result4.xlsx` 是当前条件可行候选，不是最终全局最优工作簿；Q4 的详细证据、边界敏感性和审计限制见 `outputs/q4/summary.md` 与 `outputs/q4/q4_optimization_audit.md`。Q1–Q3 正式结果和接口不被本决定改写。
- Affected files: `work/q4/Q4_DIRECTION_MODEL_CARD.md`、`scripts/solve_q4_cp_sat.py`、`scripts/validate_q4.py`、`outputs/q4/`
- Supersedes:
- Superseded by: DEC-20260912-003

### DEC-20260912-003 — Q4 `R≤2` 六分支 SAT 全局不可行证明与最小撤销数

- Status: accepted
- Date: 2026-09-12
- Context: Q4 已找到 3 台撤销的独立验证可行方案，但整体 `R≤2` 初始 CP-SAT、MILP、SAT 和位集路线均未闭合，不能把求解器超时当作下界。
- Decision: 在 `H=643`、频率域 `[0,100)`、半开离散时频格和已冻结的有限合法动作集合下，先按外部冲突集合支配关系将 5953 个活动候选等价缩减为 5533 个，再穷尽 `R=2` 的六个类别配额 `(R_A,R_B,R_C)` 分支。六个分支均返回 `UNSAT/PROVED_INFEASIBLE`，结合 `R≤3` 可行见证，接受 `R_{Q4}^*=3` 作为最小撤销数结论。
- Alternatives considered: 继续引用整体模型 `UNKNOWN`；只固定少量撤销身份组合；把 3 台可行候选直接写成最优；这些都不能覆盖全部撤销身份或提供全局下界，拒绝。
- Evidence / rationale: 六个分支证据位于 `outputs/q4/proof_R_le_2_active_sat_r2_*.json`，覆盖与支配消元由 `outputs/q4/proof_R_le_2_global_coverage_validation.json` 独立重构核验为 `PASS`；上界见 `outputs/q4/proof_R_le_3.json` 与 `proof_R_le_3_validation.json`。
- Consequences: Q4 最小撤销层已闭合为 3 台；当前 `result4.xlsx` 的 `R_A、R_B、M、M_A、M_B、S10` 仍是条件候选或未完全证明的次级层，后续必须继续按字典序逐层核验，不能把当前工作簿称为完整次级全局最优。
- Affected files: `scripts/prove_q4_active_sat.py`、`scripts/verify_q4_r2_global_proof.py`、`outputs/q4/r2_global_proof_status.md`、`outputs/q4/summary.md`、`outputs/q4/q4_optimization_audit.md`、`outputs/q4/`
- Supersedes: DEC-20260912-002 中“只冻结可行上界、R≤2 尚未证明”的阶段性状态
- Superseded by:
```

## 先验库存与边界原文
来源：`references/design_priors/INDEX.md`（dirty工作区时间点快照）

```markdown
# Design priors — 2024–2025 CUMCM pre-contest freeze

Status: `PRE_CONTEST_20_COMPLETE_WITH_DECLARED_SCOPE / CORPUS_FROZEN`.

入口只读本 INDEX，再按当前题目选最多 3–5 张相关卡。历史材料不是当前题面、数据、结论或
2026 官方规则。达到20篇后停止新增语料检索、下载、抽取和模式扩展；原50篇目标降级为
赛后长期任务，不属于开赛条件。

## 实际库存（2026-09-09；以 `scripts/design_priors.py stats` 重算为准）

| 口径 | 数量 |
|---|---:|
| 去重候选身份 | 24 |
| 已确认完整全文 | 20 |
| 完整设计阅读 | 20 |
| 本科 A/B/C | 13（A 3、B 5、C 5） |
| 高职高专 D/E | 7（D 3、E 4） |
| 用户确认国一 | 1 |
| 独立核验国一 | 1 |
| 完整官方展示设计卡、奖项仍未核验 | 18 |

“完整设计阅读”要求正文主线读完，并查看摘要、总体框架、核心模型、关键结果和验证/局限页；
卡片还必须记录模型选择逻辑、claim–evidence、图表作用及可迁移/不可迁移项。仅下载全文、
只读摘要、仅机器抽取或未声明正文范围均不计数。长附录允许声明未逐行读，但不能伪装已执行。

用户种子 `CUMCM2025_USER_MINE` 为32页原 PDF，按用户明确确认保留
`user_confirmed / USER_CONFIRMED_NATIONAL_FIRST`，不重复核奖；SHA256 为
`c5de2708f65f5ebdc06557b45c77f7b4304fbe38a680100d6934f4b8de78b35d`。
`CUMCM2024-B196` 为同篇证据独立核验国一。其余18篇只可作为
`official_showcase_design` 使用，奖项状态均为 `UNVERIFIED`，不能从展示身份推断国一。

交接包中的 `ZHONGQING2026_EEG` 属 supplemental，不计入本库。官方原页仅本地研究，禁止
未经授权转载。采集器的 `NOT_READ_BY_COLLECTOR` 是原始采集记录；阅读事实由
`corpus.csv` 与 `cards.jsonl` 独立记录。

## 20篇完整卡与页码证据

页码均为1基物理 PDF 页或官方原图序号。详细的原文/本库判断、功能页、附录范围、负结果和
未读项见 `cards.jsonl`。

| paper_id | 正文/文献；附录边界 | 实际视觉范围与功能页举例 |
|---|---|---|
| CUMCM2024-B196 | P1–23 / P24；附录25–28 | 看P1–28；摘要1，框架3–4/8，模型9，结果12/19，验证20–23 |
| CUMCM2025_USER_MINE | P1–22 / P23；附录24–32 | 看正文及1/3/5/10/15/20/22；附录未逐行读 |
| CUMCM2024-D033 | P1–22 / P22–23；附录24–55 | 看P1–24/55；摘要1，框架2–3，模型4–13，结果14/19–20，局限22 |
| CUMCM2024-E010 | P1–27 / P28；附录29–39 | 看P1–29/39；摘要1–2，框架2–6，模型8–11，结果18–19/24–26，验证24 |
| CUMCM2024-E061 | P1–16 / P16–17；附录18–32 | 看P1–18；摘要1，框架2–3，模型6/8–9，结果7/10/13–15，局限15–16 |
| CUMCM2024-E218 | P1–27 / P27；附录28–62 | 看P1–29；摘要1，框架3/12，模型16–17/21–22，结果18/23–24，验证19/27 |
| CUMCM2025-D037 | P1–17上部 / P17中下部；附录18–37 | 看P1–23/36–37；摘要1，框架3–4，模型6–15，结果9/13/16，验证6/10/16 |
| CUMCM2025-E030 | P1–20 / P21；附录22–36 | 看P1–24/36；摘要1，框架2–4，模型8/10–11/13/17–18，结果9/12/15–20 |
| CUMCM2025-A196 | P1–33 / P33下部；附录34–98 | 看P1–35；摘要1，框架3–4，模型8/13/18/22/26/30，结果16/20/24/29/31 |
| CUMCM2025-B060 | P1–30 / P30–31；附录32–72 | 看P1–33/72；框架3/13，模型5–8/13–18，结果10–26，验证11–12/14/18/22–28 |
| CUMCM2025-B157 | P1–28 / P28；附录29–67 | 看P1–32/67；框架3/12/18–19，模型5–25，结果10–27，验证13–18/21–27 |
| CUMCM2025-C023 | P1–23 / P23–24；附录25–122 | 看P1–28/122；框架3/5/10/15/19，模型6–21，结果9/13–22，局限23 |
| CUMCM2025-C132 | P1–40 / P40；附录41–65 | 看P1–44/65；框架4/17/22/29/34/36–38，模型11–38，结果12–39，局限40 |
| CUMCM2024-A163 | P1–28 / P29；附录自P29下部至45 | 看P1–32/45；框架4–7，模型7–28，结果10–14/26–28，局限28 |
| CUMCM2024-A242 | P1–29 / P30；附录31–58 | 看P1–32/58；框架3/12/15–16，模型5–28，结果7–29，局限29 |
| CUMCM2024-B159 | P1–23 / P23；附录24–37 | 看P1–25；框架3/8，模型7/10/15/19，结果13/18/21，验证8/20/22–23 |
| CUMCM2024-B195 | P1–22；文献/附录边界P22–23 | 看P1–25；框架3/10，模型7/12/17/19，结果15/18/21，验证8/16/18/20/22 |
| CUMCM2024-C038 | 物理P1–45含正文/文献；附录46–61 | 看P1–47；框架3/24/33，模型15/27/38–39，结果21–22/30–31/41，验证42–44 |
| CUMCM2024-C063 | P1–34含正文/文献；附录35–49 | 看P1–35；框架3，模型12/17/23/33，结果18–19/27–28/34，验证28–29/34 |
| CUMCM2024-C234 | P1–25含正文/文献；附录26–45 | 看P1–27；框架3，模型8/12/19/22，结果14–15/20/23，局限20/23–24 |

“完整”只表示声明范围内的设计阅读，不表示原论文模型被复算、代码被执行、外部有效性被确认，
也不表示所有附录逐行阅读。新增12篇官方展示原页均完整取得且逐篇记录边界；未重复核验奖项。

## 冻结后的5个可调用模式

- P-001 上游输出成为下游具名接口；
- P-002 结论反查结果与验证对象；
- P-003 背景与决策证据分层、对象跨图一致；
- P-004 条件、示意图与公式编号一一对应；
- P-005 候选方法、共同指标、业务决定相邻。

这些模式由早期 pilot 形成，本轮新增论文的逐篇可迁移/不可迁移项已写入卡片，但冻结时不再
增加第六种模式或扩展架构。触发、边界和失败见 `patterns.md`、`visual_patterns.md`。

## 来源、计数与冻结规则

`corpus.csv` 独立记录来源、身份、全文、正文、视觉检查和奖项；`cards.jsonl` 保存逐篇证据；
`../papers/` 是 Git 忽略的私有原件。`scripts/design_priors.py stats` 的 pre-contest target 为20，
post-contest long-term target 为50。冻结后只做按当前题目检索，不再收集或扩充。

CARD_FIELDS：paper_id、problem_structure、question_to_model_mapping、model_choice_rationale、
parameter_provenance_quality、claim_evidence_map、cross_question_dependencies、validation_target、
negative_or_boundary_results、abstract_organization、language_observations、figure_roles、
layout_observations、strongest_design_choice、unsupported_or_weak_choice、transferable_patterns、
non_transferable_details、page_evidence、missing_or_unread_items。

维护检查：`python scripts/design_priors.py validate`、`python scripts/design_priors.py stats`。
冻结后不要运行 index/fetch，除非用户在赛后明确重新开启长期建设。
```

## 稳定手册短核心
来源：`docs/WINDOW_HANDOFF_GUIDE.md`；完整手册应与本包一起交接。

```markdown
# CUMCM2026 跨窗口交接与比赛使用手册

本文件是稳定、自包含的唯一操作手册。一次性的当前状态使用
`scripts/export_window_handoff.py` 生成 `WINDOW_PACKET.md`；不要再维护一套需要用户
手工同步的日志、队列或进度板。

2026 当届官方格式、页数、匿名、AI 使用声明、支撑材料和提交要求在官方文件到位前均为
`UNVERIFIED`。本手册只定义仓库内部生产、冻结、审阅和交接流程，不把往届经验升级为
官方要求。

## 1. 一页操作契约

### 固定路径与真实状态

- Builder / Production Lane：`C:\Users\ysw\Desktop\CUMCM2026`，通常为 `main`。
- Reviewer / Review Lane：首次真实 milestone 后才创建的同仓库独立 worktree，通常为
  `C:\Users\ysw\Desktop\CUMCM2026-review`。
- 当前事实先读：`docs/CURRENT_PROGRESS.md`。
- 跨问题长期决定：`docs/DECISIONS.md`。
- 每问可恢复状态：`outputs/qX/summary.md`。
- 临时和演练材料：`tmp/`；不能冒充正式赛题结果。

进入任何窗口先运行：

`` powershell
Set-Location C:\Users\ysw\Desktop\CUMCM2026
git status --short
Get-Content docs\CURRENT_PROGRESS.md
`` 

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
```

## 各问摘要
### `outputs/q1/summary.md`

```markdown
# D 题问题 1 里程碑摘要

## 问题与口径

问题 1 要求根据附件 1 的原始用频计划，找出所有在时间和频率两个维度同时重叠的装备对，并按附件 2 的 `result1.xlsx` 模板输出。每个重复事件均采用半开区间，若首次时间区间为 `[s_i,e_i)`、单次时长为 `d_i=e_i-s_i`、空闲间隔为 `g_i`，则第 `k` 次事件为

`` text
[s_i+k(d_i+g_i), e_i+k(d_i+g_i)),  k=0,...,n_i-1.
`` 

643 是按上述递推展开附件数据得到的最晚结束时刻，不是题面直接给出的常量。Q1 对原始事件做完整检测，不按人为时间终点裁切；展开结果恰好位于 `[0,643)×[0,100)`。

## 采用模型

采用精确穷举冲突检测。对任意两个不同计划，先判断固定频段是否相交，再枚举二者的重复事件；只要存在一对事件满足时间半开区间相交，就把该装备对记为一条冲突边。即使同一装备对有多次事件重叠，提交表中仍只记录一次。

## 核心结果

- 150 个计划展开为 1,300 个重复事件，共检查 `C(150,2)=11,175` 个候选装备对。
- 检出 **297 对**不同的冲突装备，占全部候选装备对的 **2.66%**。
- 297 对装备之间共有 **431 次**事件级重叠；二者不可混作同一指标。
- 共有 148 个装备至少参与一次冲突；`C007`、`C060` 是仅有的两个孤立装备。
- 冲突图包含 3 个连通分量，其中最大分量含 148 个装备；平均冲突度为 3.96，最大冲突度为 8。
- 最大冲突度装备为 `B009`、`B016`、`B024`、`B027`、`B030`、`C076`。

| 类别组合 | 可配对数 | 冲突对数 | 类别内冲突率 | 占全部冲突对 |
|---|---:|---:|---:|---:|
| A-A | 190 | 0 | 0.00% | 0.00% |
| A-B | 800 | 21 | 2.63% | 7.07% |
| A-C | 1,800 | 66 | 3.67% | 22.22% |
| B-B | 780 | 10 | 1.28% | 3.37% |
| B-C | 3,600 | 181 | 5.03% | 60.94% |
| C-C | 4,005 | 19 | 0.47% | 6.40% |

B-C 不仅贡献了最多的冲突对，其按可配对数归一化后的冲突率仍为六类组合中最高，因此 Q2 的消解重点应落在 B、C 类的耦合冲突上；但具体移动哪些计划必须由 Q2 的位移约束和目标函数决定，不能只按 Q1 度数贪心删除或平移。

## 验证

1. PDF 示例复核：A001 第二次使用为 `[100,105)`，通过。
2. 极值事件复核：C083 第 12 次使用为 `[641,643)`，通过。
3. 独立算法复核：以整数时频单元建立倒排索引，再由同一单元内的装备组合恢复冲突对，得到的 297 对与连续半开区间算法完全一致。
4. 独立重数复核：重新枚举事件矩形交集，431 次事件级重叠与主程序一致。
5. 提交表复核：`result1.xlsx` 保留原模板单工作表与三列标题，297 行与 `results.json`、`conflict_pairs.csv` 逐行一致，序号连续且无公式。

完整机器检查见 `validation.json`。验证基于原始附件 SHA-256 `b7f905cd2629f9a85b47db352be503404a0cd5b8f70b9209aafdf7e262f3449c`。

## 正式资产

- `results.json`：正式统计与完整冲突对。
- `conflict_pairs.csv`：带事件重叠次数的可读冲突清单。
- `result1.xlsx`：按附件 2 模板填写的提交结果表。
- `plot_data/`：类别冲突、装备冲突度、连通分量与事件重叠次数分布。
- `figures/fig_q1_conflict_structure.pdf`：论文矢量图。
- `figures/fig_q1_conflict_structure.svg`：保留文本元素的可编辑矢量图。
- `figures/fig_q1_conflict_structure.png`：彩色预览。
- `figures/fig_q1_conflict_structure_grayscale.png`：灰度可读性检查。
- `figures/fig_q1_conflict_structure.visual.toml`、`figures/fig_q1_conflict_structure.review.md`：图表审查契约与修改记录。
- `paper/draft_sections/q1.md`：问题 1 逐问闭环正文草稿。

## 图表说明

冲突结构图左侧给出按 A/B/C 排序的装备邻接矩阵，右侧给出各类别组合在其全部可能配对中的冲突率，条末标注“冲突对数/可配对数”。该图用于说明冲突的结构与相对密度；297 对的精确清单由 `result1.xlsx` 和 `conflict_pairs.csv` 承担。

生成脚本为 `scripts/solve_q1.py`、`scripts/validate_q1.py`、`scripts/plot_q1_conflicts.py` 和 `scripts/build_result1.mjs`。图表基于本里程碑的 `plot_data/` 与 `conflict_pairs.csv`，生成前基线 SHA 为 `b66fb88`。

## 后续接口

Q2 将把 150 个装备视为冲突图节点，以 297 条冲突边作为必须消除的约束来源；频率平移和时间平移均需作用于该装备的全部重复事件。Q2–Q4 统一采用已确认的固定时间域 `[0,643)`，并在后续执行 `H∈{638,643,648}` 的边界敏感性分析。
```

### `outputs/q2/summary.md`

```markdown
# D 题问题二：六撤销里程碑

状态：`FULL_LEXICOGRAPHIC_PROVED`。第一层最少撤销数已由 CP-SAT 上下界闭合证明为 **6**；随后用独立 CNF + CaDiCaL 对各层相邻阈值做不可行性证明，精炼方案 B 的七层字典序已全部闭合。

## 模型与目标

对 150 个计划分别枚举 `keep / frequency-shift / time-shift / revoke`，所有候选均展开完整重复事件。频移满足 `|df|≤10`，时移满足 `|dt|≤5`，一次只能改变一个参数；资源域为 `[0,643)×[0,100)`，区间采用半开口径。4,582 个候选通过 52,939 条资源格团约束实现全局冲突消解。

采用精炼方案 B 的字典序：总撤销数 `R` → A 类撤销数 `R_A` → B 类撤销数 `R_B` → 参数调整数 `M` → A、B 类调整数 `M_A,M_B` → 归一化平移量 `|df|/10+|dt|/5`。只有更高层已经证明时，下一层的“最优”才成立。

## 当前正式方案

| 类别 | 保留 | 调整 | 撤销 |
|---|---:|---:|---:|
| A | 4 | 16 | 0 |
| B | 2 | 34 | 4 |
| C | 12 | 76 | 2 |
| 合计 | 18 | 126 | 6 |

撤销计划为 `B009、B018、B024、B028、C027、C054`。频移绝对值合计 595，时移绝对值合计 90，十倍归一化平移分数为 `595+2×90=775`。

## 上下界与诚实边界

| 目标层 | LB | UB | 结论 |
|---|---:|---:|---|
| `R` | 6 | 6 | 已证明最优 |
| `R_A | R=6` | 0 | 0 | 已证明最优 |
| `R_B | R=6,R_A=0` | 4 | 4 | 已证明最优 |
| `M | R=6,R_A=0,R_B=4` | 126 | 126 | 已证明最优 |
| `M_A`（上述前缀固定） | 16 | 16 | 已证明条件最优 |
| `M_B`（上述前缀及 `M_A=16` 固定） | 34 | 34 | 已证明条件最优 |
| `S10`（上述前缀固定） | 775 | 775 | 已证明最优 |

`revocation_bound.json` 保存 CP-SAT 的 `objective=6`、`best_objective_bound=6` 证书；`proof/sat_b_le_3.json` 证明 `B≤3` 不可行，`proof/sat_adjust_le_125.json` 证明 `M≤125` 不可行，另两份 SAT 证据闭合 `M_A=16` 与 `M_B=34`；`proof/sat_shift_le_774_full.json` 在完整 4,582 个候选全集上证明 `S10≤774` 不可行。外部工作簿提供具体动作见证，动作本身由独立验证复核；次级最优性来自阈值不可行性证据。

## 独立验证

`six_revocation_candidate.json` 是从外部工作簿规范化得到的动作表。两份验证重新读取原始附件并确认：144 个活动计划全部重复事件无越界；连续与离散两套检查均零冲突；15,816 个资源格无重复、最大占用为 1；调整均为单参数整数平移，宽度、时长、间隔和次数不变。

正式 `result2.xlsx` 由模板重建，只填写实际改变的参数列，撤销行写“是”，并通过工作簿复核。旧 19 撤销结果与探针保留作历史诊断，但已被 supersede，不再作为正文主结果或 Q3 输入。用户已批准当前工作簿作为 Q3 唯一接口；Q3 已从该工作簿反向解析并完成独立最优性核验。

## 正式资产

- `results.json`、`result2.xlsx`、`validation.json`、`workbook_validation.json`；
- `revocation_bound.json`、`priority_prefix_run.json`；
- `six_revocation_candidate.json`、`six_revocation_validation.json`；
- `q2_proof_matrix.csv`、`proof/SAT_EVIDENCE_INDEX.md`、`proof/sat_evidence_validation.json` 及 `proof/` 下的独立 SAT/CP-SAT 阈值证据；
- `figures/fig_q2_solution_tradeoff.{pdf,svg,png}` 及灰度 QA。
```

### `outputs/q2_q3_pareto/summary.md`

```markdown
# Q2–Q3 联合 Pareto 扫描

固定资源域为 `[0,643)×[0,100)`。每一行先固定 Q2 总撤销数 R，按同一优先保护链生成一份条件 Q2 方案，再把该方案固定后求 Q3 最大新增 C 类数量。`A/B` 列格式为“保留/调整/撤销”。

| R | N3 | 150-R+N3 | A 保留/调整/撤销 | B 保留/调整/撤销 | M | Q2 状态 | Q3 状态 |
|---:|---:|---:|---:|---:|---:|---|---|
| 6 | 141 | 285 | 4/16/0 | 2/34/4 | 126 | FEASIBLE_INCUMBENT | OPTIMAL |
| 8 | 139 | 281 | 4/16/0 | 2/35/3 | 124 | FEASIBLE_INCUMBENT | OPTIMAL |
| 10 | 127 | 267 | 5/15/0 | 3/34/3 | 120 | FEASIBLE_INCUMBENT | OPTIMAL |
| 12 | 132 | 270 | 5/15/0 | 2/36/2 | 119 | FEASIBLE_INCUMBENT | OPTIMAL |
| 15 | 108 | 243 | 2/18/0 | 5/35/0 | 119 | FEASIBLE_INCUMBENT | OPTIMAL |
| 19 | 106 | 237 | 3/17/0 | 4/36/0 | 114 | FEASIBLE_INCUMBENT | OPTIMAL |

说明：这是联合敏感性实验，不改变正式 Q2/Q3 接口。`Q3` 只有在 `q3_optimality=PROVED` 且 `q3_upper_bound=N3` 时才可称为该固定 Q2 背景下的最优；Q2 的最后平移层若超时，只保留为可行方案。
```

### `outputs/q3/summary.md`

```markdown
# D 题问题三：固定六撤销 Q2 后的新增结果

问题三固定经用户批准的 `outputs/q2/result2.xlsx` 中的 144 个活动计划。工作簿先被反向解析为动作表并通过 Q2 独立验证，再只在剩余 `[0,643)×[0,100)` 资源中新增完整 C 类模板；不反向改变 Q2。

C 类模板宽 3、单次时长 2、间隔 8、使用 12 次，相邻起点步长为 10，每个计划占用 72 个资源格。整数起点共有 52,136 个，筛除与 Q2 冲突者后剩 2,334 个候选。0-1 集合装填模型选中 **141 台**，HiGHS 返回 `OPTIMAL`，上界同为 141，`mip_gap=0`。独立的候选两两冲突模型仍得到 141，并证明“至少 142 台”不可行。

固定 Q2 占用 15,816 个资源格；新增计划占用 10,152 个资源格；合并后 285 个活动计划共占 25,968 个不同资源格。独立验证重新检查全部重复事件、边界、Q2—Q3 冲突、Q3 内部冲突及工作簿逐行一致性，结果为 `PASS`。

141 小于旧 19 撤销 Q2 背景下的 203，是因为新 Q2 只撤销 6 个计划，保留背景更多、剩余容量更少。旧 203 已被 supersede，不能与新 `result2.xlsx` 配套使用。

正式资产：`q2_input_from_result2.json`（由批准的 `result2.xlsx` 解析）、`results.json`、`q3_optimality_audit.json`、`q3_optimization_audit.md`、`result3.xlsx`、`validation.json`、`figures/fig_q3_addition_layout.{pdf,svg,png}` 及 `plot_data/`。
```

### `outputs/q4/summary.md`

```markdown
# Q4 当前里程碑摘要

论文补齐与证据状态入口：`docs/Q4_PAPER_COMPLETION_PACKET_20260912.md`。

## 题目与模型

问题四从问题一的 150 条原始用频计划和问题一检出的冲突出发，不读取问题二的结果作为约束，也不混入问题三新增的 141 台 C 类装备。统一资源域为 `[0,643)×[0,100)`；重复事件按“单次占用时长 + 空闲间隔”递推，区间采用半开区间。

每条计划从保持、频段平移、首次时间平移、撤销中择一；C 类额外允许间隔变化 `δg∈{-8,…,-1,1,…,10}`，即调整后间隔 `g'∈{0,…,18}`。所有动作均在候选生成阶段展开完整重复事件，再用资源格至多占用一条约束求解。

## H=643 的当前证据

| 目标/阈值 | 结果 | 证据含义 |
|---|---:|---|
| `R≤5` | 可行 | `proof_R_le_5.json` 的 CP-SAT 阈值模型完成；不是“最少 5 台”证明 |
| `R≤4` | 可行 | `proof_R_le_4.json` 的 CP-SAT 阈值模型完成；不是“最少 4 台”证明 |
| `R≤3` | 可行 | `proof_R_le_3.json` 的 CP-SAT 阈值模型完成，独立重建验证 PASS |
| `R≤2` | 不可行（全局已证） | 六个 `R=2` 类别配额分支均为 `UNSAT`；覆盖核验 `PASS` |
| `R≤2`（支配消元 SAT） | `PROVED_INFEASIBLE` | `proof_R_le_2_global_coverage_validation.json` 及六个分支 JSON |

本轮进一步采用外部冲突集合支配消元，将 5953 个活动候选等价缩减为 5533 个；随后按
`(R_A,R_B,R_C)` 的六个非负整数分拆穷尽 `R=2`，六个独立 CaDiCaL SAT 分支均返回
`UNSAT/PROVED_INFEASIBLE`。独立重构确认候选数、分区覆盖和时间域一致，见
`proof_R_le_2_global_coverage_validation.json`；逐动作支配替换核验见
`proof_R_le_2_dominance_validation.json`。此前的资源格 CP-SAT、MILP、位集和冲突割
运行仍作为探索记录保留，但不再承担主证明。

因此在统一有限动作、整数网格和 `H=643` 口径下，可以报告

\[
R_{Q4}^*=3,
\]

其中上界来自 `proof_R_le_3.json` 及独立验证，下界来自 `R≤2` 六分支全局不可行证明。

## 当前条件候选

用于生成现有工作簿的候选是 `conditional_R3_RB1_chain.json`：在固定 `R=3`、`R_A=0`、`R_B=1` 后得到 `M=142` 的可行候选，末级 `S_{10}^{(4)}=943`。该工作簿仍可作为历史可行基线，但已被新的 SAT 见证否定为调整层最优：`proof_R3_RA0_RB1_M140_witness.json` 实际得到 `M=140`，`proof_R3_RA0_RB1_M139_witness.json` 实际得到 `M=139`，且二者均通过独立验证。`R_B=1`、真正的 `M` 最优值和 `S_{10}^{(4)}` 仍未全部闭合；`R=3` 的最小撤销数本身已经闭合。

候选的类别统计为：

| 类别 | 保留 | 调整 | 撤销 |
|---|---:|---:|---:|
| A | 0 | 20 | 0 |
| B | 0 | 39 | 1 |
| C | 5 | 83 | 2 |
| 合计 | 5 | 142 | 3 |

撤销计划为 `B029`、`C035`、`C075`。这只是旧工作簿条件可行见证；若固定 `R=3` 的次级层被改进，工作簿需要重建。新的 `M=140/139` 见证暂以 JSON 形式保存，待 `R_B` 与调整层闭合后再重建正式工作簿。

## 独立验证与工作簿

- `conditional_R3_RB1_validation.json`：从原始附件重建，连续区间冲突和离散资源格冲突均为 0，边界检查 PASS。
- `result4_workbook_validation_independent.json`：工作簿反向读取后仍得到 `147` 个活动计划、`16356` 个不同占用格、最大格占用数 1，报告目标与重算目标一致。
- `result4.xlsx` 按官方五列模板生成，只写入 145 条需要调整或撤销的计划，另有 5 条计划隐式保持不变。

`R≤2` 全局证明状态和分支覆盖单独记录于 [r2_global_proof_status.md](r2_global_proof_status.md)。

## 边界敏感性

在 `H=638` 和 `H=648` 下，均找到与 `R≤3` 相容的候选，且当前返回的撤销集合仍为 `A012、B018、B033`；两者的独立验证均 PASS。敏感性结果说明 3 台撤销候选对这两个边界扰动稳定，但不证明任一边界下的最小撤销数。

| 时间终点 | 候选动作数 | 资源格约束数 | 阈值 | 求解状态 | 独立验证 |
|---:|---:|---:|---:|---|---|
| 638 | 6040 | 53186 | `R≤3` | 可行 | PASS |
| 643 | 6103 | 53679 | `R≤3` | 可行 | PASS |
| 648 | 6116 | 53767 | `R≤3` | 可行 | PASS |

## 审计边界

定向固定撤销组合的 12 个子问题仍只是诊断证据；真正的全局下界来自六个类别配额 SAT 分支的完整覆盖。Q4 当前可以在论文中写成“在允许 C 类间隔调整后，最少撤销 3 台”，但应同时说明该结论针对统一的有限合法动作集合、离散资源域和 `H=643` 基准域；后续 `R=3` 内的 `R_A、R_B、M、S_{10}^{(4)}` 仍需分别闭合，不能把当前工作簿称为完整字典序最优。

求解与核验入口：

- 方向与接口：[Q4_DIRECTION_MODEL_CARD.md](../../work/q4/Q4_DIRECTION_MODEL_CARD.md)
- 求解器：[solve_q4_cp_sat.py](../../scripts/solve_q4_cp_sat.py)
- 独立核验：[validate_q4.py](../../scripts/validate_q4.py)
- 工作簿：[result4.xlsx](result4.xlsx)
```

## 恢复结论
- 当前任务已进入 D 题建模线；Q1 已完成，Q2 有可验证 incumbent，最优性边界见问题摘要。
- 接收者只根据本包随附题面、数据、结果、验证和图表审计，不猜测本机未附文件。
- 若继续 Builder 主线，优先加强 Q2 第一层下界/求解时间并完成 H 敏感性，再固定 Q2 进入 Q3。
- dirty快照只用于恢复讨论，不能声称其内容来自某个冻结commit。

## 附件
- `WINDOW_PACKET_attachments/paper/rebuild/build/main.pdf` <- `paper/rebuild/build/main.pdf`; WORKING_COPY_NOT_FROZEN; 320850 bytes; SHA256 `cfb6448d9979f02826515ef7bb8c9e4c4f69f2045add503c073404238e252cd6`
- `WINDOW_PACKET_attachments/outputs/q1/results.json` <- `outputs/q1/results.json`; WORKING_COPY_NOT_FROZEN; 41970 bytes; SHA256 `07446955fd3424e5fe80de49552260f069077c46a5ecc58e51dc6f9059282786`
- `WINDOW_PACKET_attachments/outputs/q1/validation.json` <- `outputs/q1/validation.json`; WORKING_COPY_NOT_FROZEN; 1038 bytes; SHA256 `a7cc78510054d63046a3c4a6a3ab72ae07137eeceda8668daa0200fc058df22c`
- `WINDOW_PACKET_attachments/outputs/q2/results.json` <- `outputs/q2/results.json`; WORKING_COPY_NOT_FROZEN; 40947 bytes; SHA256 `45f1c5cc769b29e4903951360ee435a7e2543a24067bb38fe5948847274e92db`
- `WINDOW_PACKET_attachments/outputs/q2/q2_proof_matrix.csv` <- `outputs/q2/q2_proof_matrix.csv`; WORKING_COPY_NOT_FROZEN; 1516 bytes; SHA256 `6f9f111490271c2c444728127c902f3f57d1a0b3901430c2e258da5b65d2498c`
- `WINDOW_PACKET_attachments/outputs/q2/validation.json` <- `outputs/q2/validation.json`; WORKING_COPY_NOT_FROZEN; 1396 bytes; SHA256 `f04172b32663bd690454e9e9c4ffe6d3e1589fbd2194c01b8910fa46f1738251`
- `WINDOW_PACKET_attachments/outputs/q2/proof/sat_shift_le_774_full.json` <- `outputs/q2/proof/sat_shift_le_774_full.json`; WORKING_COPY_NOT_FROZEN; 2238 bytes; SHA256 `ccba8f1e664e4eaf6f2903bd3be36e87184140be38464ff0129c527839b9ec93`
- `WINDOW_PACKET_attachments/outputs/q3/results.json` <- `outputs/q3/results.json`; WORKING_COPY_NOT_FROZEN; 43548 bytes; SHA256 `cb5673475fde52954efdfb5a744a5aca5808451d99d1ad59eafc0e7c791d96b3`
- `WINDOW_PACKET_attachments/outputs/q3/q3_optimality_audit.json` <- `outputs/q3/q3_optimality_audit.json`; WORKING_COPY_NOT_FROZEN; 1772 bytes; SHA256 `9a7451c0ccb149f102a171e5d9e6e97993682aa4a4944bf90b2f4eaaf9d128c4`
- `WINDOW_PACKET_attachments/outputs/q3/validation.json` <- `outputs/q3/validation.json`; WORKING_COPY_NOT_FROZEN; 1889 bytes; SHA256 `5a1dc7ec802ee5698af7e3a37c3625e24859a9a262c511ed12fd2f38adaea252`
- `WINDOW_PACKET_attachments/outputs/q4/summary.md` <- `outputs/q4/summary.md`; WORKING_COPY_NOT_FROZEN; 5110 bytes; SHA256 `a3739c182b71f79e027da3097d01ffc3c682375659f1a88954dc10fe2f0fdc82`
- `WINDOW_PACKET_attachments/outputs/q4/r2_global_proof_status.md` <- `outputs/q4/r2_global_proof_status.md`; WORKING_COPY_NOT_FROZEN; 4362 bytes; SHA256 `6d4aa7c4bbc13dc35a83171fe47f05ec38bf88f4de5a31ff522c61a0d6e57752`
- `WINDOW_PACKET_attachments/outputs/q4/proof_R_le_3_validation_final.json` <- `outputs/q4/proof_R_le_3_validation_final.json`; WORKING_COPY_NOT_FROZEN; 969 bytes; SHA256 `1bcf386936eb27c7e217460cd4f37ee0be79188ed760732da1a6c46f7740cab6`
- `WINDOW_PACKET_attachments/outputs/q4/proof_R_le_2_global_coverage_validation.json` <- `outputs/q4/proof_R_le_2_global_coverage_validation.json`; WORKING_COPY_NOT_FROZEN; 1682 bytes; SHA256 `d21effcd68042278be354354c957cd9399b4b85ecbfe065e3988a5456838ca08`
- `WINDOW_PACKET_attachments/outputs/q4/proof_R_le_2_dominance_validation.json` <- `outputs/q4/proof_R_le_2_dominance_validation.json`; WORKING_COPY_NOT_FROZEN; 144384 bytes; SHA256 `d04800c214037715443aed59799330160f8ad21bc665dc27da489a6f27b184ce`
- `WINDOW_PACKET_attachments/work/intake/FILE_MANIFEST.json` <- `work/intake/FILE_MANIFEST.json`; WORKING_COPY_NOT_FROZEN; 1802 bytes; SHA256 `bed53a1caac444d0944188e4b1eaf043bc4523430e2aaf41eaafff92bace54e0`
