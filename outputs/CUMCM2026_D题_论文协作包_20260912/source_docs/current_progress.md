# Current Progress

## Selected Problem

D — 时频冲突检测与消解

## Current Goal

Execute the frozen implementation plan in order: build one canonical periodic conflict detector, preserve a traceable Q2 incumbent for the downstream interface, complete the conditional Q3 result, and re-solve Q4 from the raw Q1 plans with the same layer-by-layer evidence boundary.

## Modeling Spine

Periodic time-frequency rectangles → exact conflict detection → finite-state conflict resolution → fixed-domain C-plan packing → C-interval adjustment extension.

Current primary interpretation: use the data-derived fixed resource domain `[0,643) × [0,100)` for Q2–Q4. The value 643 is the maximum final end after expanding all repetitions, not an explicit official constant. Use `H=648` only as a named sensitivity scenario.

## Problem Status

| Problem | Status | Current method | Key result | Next |
|---|---|---|---|---|
| Q1 | baseline complete | one canonical periodic half-open interval detector with conflict witnesses | 297 conflict pairs; independent grid cross-check and readable category figure agree | integrate Q1 table/figure into paper, then feed Q2 |
| Q2 | T incumbent frozen for downstream; strict M layer still open | device-level finite-domain CSP/state model as semantic spine, with geometry/MILP cross-checks | `Q2-T-incumbent-v1`: $C=6$, $M=120$, global conflict count 0; $C\le5$ infeasible under $H=643$; $M\le119$ bounded proof still UNKNOWN | use the frozen snapshot as Q3 input; continue a finite M-proof run without blocking Q3 |
| Q3 | primary solve complete on frozen T input | fixed-domain C-template candidate packing with exact resource-cell cliques | 52,136 raw candidates; 2,452 survive Q2 filtering; `OPTIMAL=138`; merged conflict count 0 under `H=643` | record conditional result and sensitivity to future Q2 replacements |
| Q4 | conditional T incumbent available; global lexicographic proof open | raw-Q1 finite-state model with C-only gap states, resource-cell cliques and common validator | 6,103 states; C=6, M=115, P_A=14 incumbent; canonical conflicts 0 | keep C<=5/M/P_A proof attempts bounded; report incumbent honestly; add P/E only if budget allows |

## Current Best Results

Current Q2 evidence remains layered rather than a single claimed optimum. Data audit: 150 plans expand to 1,300 use windows; the complete raw-plan envelope is `[0,643)`, while 533 is only the maximum end of a first-use interval. On the exact state model, `C<=5` is infeasible and a valid `C=6` schedule exists. The frozen T incumbent has `M=120` with a solver lower bound of 88, so 120 is not called proven. Using that exact snapshot, Q3's resource-cell packing model returns 138 new C plans with CP-SAT `OPTIMAL` and a canonical merged conflict count of 0. The Q3 value is conditional on this Q2 snapshot, horizon and C template.

Q4 is now implemented from the raw Q1 plans. It adds 1,521 legal C-only gap states to the
4,582 Q2 states (6,103 total), yielding 444,561 audited state-conflict edges and 53,679
resource-cell cliques. The current T incumbent fixes `C=6,M=115` and obtains `P_A=14`
in a bounded protection-layer run; the complete schedule has 1,277 occurrences, zero
canonical conflicts and zero boundary violations. The Q4 first layer `C<=5` run is
`UNKNOWN`, and the protection layer has a lower bound of 3, so this is a conditional
incumbent rather than a strict Q4 lexicographic optimum.

## Paper Status

Problem statement and modeling-preanalysis Markdown exist under `D题/`. A durable modeling-process and decision record has been started; question-level paper sections have not yet been written.

## Q2 Evidence Log — 2026-09-11

| Evidence | Status / interpretation |
|---|---|
| `outputs/q2/solver_T_cells_budget5.json` | exact full-state cell-clique model; `C<=5` INFEASIBLE in 188.17 s |
| `outputs/q2/solver_T_cells_lexfixed.json` | zero-conflict T incumbent on certified `C=6` face; `M=120`, first later layer not proven |
| `outputs/q2/solver_T_cells_budgetM119.json` | `C=6, M<=119` UNKNOWN after 300 s; no infeasibility claim |
| `outputs/q2/solver_T_fixed_cancel_probe.json` | fixing the six T-incumbent cancellation identities gives conditional `M=120` OPTIMAL in 2.38 s; not a global proof |
| `outputs/q2/solver_T_cells_tiebreak120_300.json` | conditional `C=6,M=120` search; feasible `P_A=15`, not proven |
| `outputs/q2/solver_P_cells_verified.json` | priority-first P after equivalent propagation strengthening; all 8 layers OPTIMAL, canonical conflicts 0 |
| `src/d_problem/candidates.py`, `q2_model.py` | 4,582 states, exact bit masks, 270,626 audit edges, equivalent cell-clique constraints, 210 exact implied cancel-links |
| `outputs/q2/edge_equivalence_audit.json` | all 270,626 state edges cross-checked against the canonical detector; zero mismatches |
| `outputs/q2/subset_validation.json` | 3 real four-plan subsets exhaustively enumerated; edge/cell/lazy CP-SAT vectors all match exact enumeration and validate with zero conflicts |
| `outputs/q2/solver_T_edges_budget5.json` | independent pairwise-edge CP-SAT representation was `UNKNOWN` after 300 s; supports using the equivalent cell-clique encoding for the main run, not an optimality claim |
| `tmp/q2_t_m119_run_20260912/solver_report.json` | fixed `C=6`, tested `M<=119` with cell cliques for 600 s; status `UNKNOWN` (no infeasibility claim) |
| `tmp/q2_t_keep_max_20260912.json` | equivalent fixed-`C=6` model maximizing unchanged plans; 24 kept / 120 adjusted feasible, upper bound on keep was 56 after 600 s; canonical validation PASS |
| `tmp/q2_t_keep_ge25_20260913.json` | objective-free feasibility test for `C=6`, keep >=25 (`M<=119`); status `UNKNOWN` after 600 s, no feasibility or infeasibility claim |
| `tmp/q2_t_sat_edges_m120_sanity_20260913.json` | independent pairwise-conflict SAT encoding; `C=6, M<=120` is SAT in 0.66 s, reproduces the current T vector and passes canonical validation |
| `tmp/q2_t_sat_edges_m119_glucose60_20260913.json` | same SAT encoding with `C=6, M<=119`; 375,881 clauses, Glucose4 status `UNKNOWN` after 60 s |
| `tests/d_problem/` unittest discovery | 14/14 core conflict, candidate, objective and tiny-solver tests passed with the bundled Python runtime |
| `tmp/q2_h648/solver_T.json` | Q2 time-bound sensitivity: `H=648`, 4,589 states; `C=6` feasible with `M=121`, lower bound 84; not an improvement/proof |
| `tmp/q2_lns_result_20260918.json`, `tmp/q2_lns_result_block35_20260919.json`, `tmp/q2_lns_result_block70_20260920.json`, `tmp/q2_lns_focuskeep_20260923.json` | induced exact large-neighborhood repair; all keep `C=6,M=120`, reduce displacement to about 805--812; no $M=119$ witness |
| `tmp/q2_csp_keep25_20260921.json`, `tmp/q2_csp_h648_keep25_20260922.json` | independent finite-domain CSP forward-checking search for `C=6, keep>=25`; both UNKNOWN within bounded runs |
| `tmp/nooverlap2d_q2.py` | direct optional-rectangle `NoOverlap2D` probe; full instance did not return a usable result within the bounded run, so not adopted |
| `tmp/table_csp_q2.py` + `tmp/q2_table_csp_h643.json` | device-level finite-domain integer variables with 1,693 binary forbidden tables; `C=6`, `M=120`, lower bound 91, canonical conflicts 0 |
| `tmp/nooverlap2d_compact.py` + `tmp/q2_nooverlap2d_compact_h643_hint.json` | shared frequency/time shift variables and optional synchronized rectangles; `C=6`, `M=120`, lower bound 74, canonical conflicts 0 |
| `tmp/disjunctive_shift_q2.py` + `tmp/q2_disjunctive_shift_h643.json` | direct parameter-level disjunctive CP with shared starts and 10,906 occurrence clauses; `C=6`, `M=120`, lower bound 55, canonical conflicts 0 |
| `tmp/milp_q2_scip.py` + `tmp/q2_milp_scip_h643_hint.json` | independent SCIP 0--1 MILP with 52,939 resource-cell cliques; `C=6`, `M=120`, best bound about 89.73, canonical conflicts 0 |
| `tmp/q2_original_edges_only.py` + `tmp/q2_original_edges_only_h643.json` | invalid Q1-edge-only relaxation: apparent `M=82` but 113 conflicts after full final-schedule audit; negative control for the need for global constraints |
| `tmp/q2_h648_c5_report.json` | permissive H=648 test with `C<=5` remained `UNKNOWN` in 120 s; it does not certify that `C*=6` is horizon-invariant |
| `tmp/q2_h1000_report.json` + `tmp/q2_h1000_selected.json` | effectively unbounded Q2 time test (same 4,589 states as H=648 because shifts are only ±5); `C=6`, `M=120`, lower bound 84, canonical conflicts 0; no evidence that H=643 alone causes the high M |
| `outputs/q2/solver_T_cells_budgetM119_v2.json` | fresh 180 s threshold run with `C=6, M<=119`, cell cliques and frozen incumbent hint | `UNKNOWN`; no infeasibility certificate |
| `outputs/q2/Q2-T-incumbent-v1.json` / `.md` | byte-identical frozen snapshot and downstream usage boundary | Q2 input for Q3; `C=6,M=120`, conflict 0 |
| `scripts/solve_d_q3.py` + `outputs/q3/solver_report.json` | fixed-domain C-template set-packing solve on frozen Q2 | 52,136 raw, 2,452 compatible, resource-cell CP-SAT `OPTIMAL=138`, merged conflict 0 |
| `outputs/q3/pairwise_crosscheck.json` | same Q3 candidates expressed as 89,989 pairwise conflict edges | independent CP-SAT `OPTIMAL=138`, best bound 138 |
| `src/d_problem/q4_candidates.py`, `scripts/solve_d_q4.py` | raw-Q1 Q4 state generator and T solver with C-only gap adjustment | 6,103 states; Q2 state IDs are a subset; shared mask/canonical sample passes |
| `outputs/q4/solver_T_budgetC5.json` | Q4 first-layer threshold test | `C<=5` is `UNKNOWN` after 180 s; no infeasibility claim |
| `outputs/q4/solver_report.json` | current Q4 fixed-prefix run | `C=6,M=115,P_A=14`, `P_A` FEASIBLE with LB=3; `proven_optimal=false` |
| `outputs/q4/result4.xlsx` | current Q4 template output | 121 changed/cancelled rows; full selected state list has 150 plans; canonical conflict 0 |
| `scripts/audit_q4_cell_edges.py` + `outputs/q4/cell_edge_equivalence.json` | Q4 full edge/clique equivalence | 444,561 cross-plan pairs, missing=0, extra=0 |
| `scripts/validate_d_q4_result.py` + `outputs/q4/result4_readback_check.json` | Q4 Excel adapter readback | 121/121 changed rows match selected states; 0 field mismatches |
| `D题/Q2_替代模型探索与语义审计.md` | device-level formulation, compact geometry, MILP/CSP cross-checks, frequency-width correction, global-conflict counterexample, and model-selection recommendation |
| `outputs/q2/plot_data/q2_policy_tradeoff_stage.json` + `figures/fig_q2_policy_tradeoff_stage.*` | staged T/P/E comparison; T/E status labels preserved in source and caption |
| `D题/Q2_解题与验证阶段报告.md` | question-level model, route comparison, result table, paper wording and next tasks |
| `D题/Q2_模型质量与验证方案.md` | evidence hierarchy, small-subset limits, robustness metrics, and why R² is not applicable |
| `D题/本地与队友D分支对比审计_待核验.md` | user-provided teammate comparison; separates independently verified local facts from remote claims pending artifact audit |

The detailed reasoning, route comparison, objective definitions, and caveats are maintained in
`D题/D题_建模分析全过程与决策记录.md` §6.2.6, §6.5 and the timeline; Q4's question-level
write-up is `D题/Q4_解题与验证阶段报告.md`.

## Important Decisions

- Primary modeling convention: fixed frequency domain `[0,100)` and fixed time domain `[0,643)`.
- This is a transparent data-derived minimum-cover assumption, subject to replacement if an official clarification provides a different planning horizon.
- `H=648` is a sensitivity scenario, not the primary no-resource-increase definition.
- Q2/Q4 primary decision rule is strict text-order lexicographic optimization: total cancellations, total adjusted plans, A/B preservation, then normalized displacement. Priority-first and epsilon/Pareto solutions are comparison scenarios, not post-hoc replacements for the primary objective.
- Q2 model-route evaluation: use the state-expanded exact compatibility model as the mathematical backbone. The current data yield 4,582 legal Q2 states and 270,626 incompatible state pairs. Resource-cell at-most-one cliques are an exact reformulation of those edges under integer half-open semantics and are the current CP-SAT encoding; precomputed edges remain the audit reference, while exact lazy conflict-cut generation is optional because short runs did not prove each master layer.
- Q4 extends the same state model only with C-class gap states satisfying `|delta_g|<=10`, nonnegative adjusted gap and the fixed-horizon boundary. The Q4 state set contains all Q2 states; current result4 is a conditional T incumbent and its first cancellation layer remains unproved.
- One conflict engine will serve Q1 detection, Q2/Q4 compatibility generation, Q3 candidate filtering and all final schedule validation. The planned modules, tests and T/P/E run matrix are recorded in `D题/D题_建模分析全过程与决策记录.md`; they are plans, not completed artifacts.
- Visualization convention: Q1/Q2 use the same 2D time-frequency coordinates for auditable occupancy and before/after comparison; a time-frequency-usage-index 3D view is optional local structure/appendix only, never the sole zero-conflict proof.

## Immediate Next Actions

1. Treat the device-level CSP/state formulation as the semantic spine and use the compact geometry/MILP outputs only as independent cross-checks; do not replace a valid model solely because its search is faster on a relaxation.
2. Use LNS induced exact repair to search for improved incumbents, and only use SAT/CP-SAT threshold runs after the candidate action pattern has been reduced; close or honestly bound `M` with explicit status.
3. Keep `outputs/q2/Q2-T-incumbent-v1.json` immutable as the declared Q3 input; do not use teammate-B Q3 as a T result.
4. Keep P/E and the audited teammate-B package as optional policy/Pareto references; do not spend the main-line budget on a complete B rerun before T is closed.
5. Build T Q2/Q3 plot-ready tables and figures from the common metrics; 3D `(t,f,k)` remains local/appendix evidence rather than the sole proof.
6. Continue Q4 only through bounded, evidence-producing runs: attempt an independent `C<=5`
   certificate and/or improve the fixed-prefix `M`/protection incumbent; do not upgrade the
   current conditional vector to a strict optimum. If no certificate closes, retain the
   current result4 and its bounds in the paper.

Q2 reporting gate: the result may be frozen for downstream work as `C*=6` (strict under H=643) plus a verified zero-conflict `M=120` incumbent. It must not be labeled full lexicographic optimum unless a future bounded run closes `M<=119` as infeasible.

Q3 reporting gate: `outputs/q3/result3.xlsx` is the exact result for `Q2-T-incumbent-v1`,
`H=643`, and the homogeneous C template `(width,duration,gap,count)=(3,2,8,12)`. The
solver returned `OPTIMAL`, with 138 selected plans and best bound 138; the merged schedule
passes the canonical detector with zero conflicts. This is a conditional Q3 maximum, not a
statement that every possible Q2 incumbent would yield 138.

Q4 reporting gate: `outputs/q4/result4.xlsx` is a valid conditional T incumbent for the raw
Q1 instance under `H=643` and the C-only gap extension. Its current vector is
`(C,M,P_A,C_A,P_B,C_B,S_sum,S_max)=(6,115,14,1,38,5,806,10)`, with 0 canonical conflicts.
The unrestricted Q4 `C` layer and the `C<=5` threshold are not closed (`UNKNOWN`), and the
`P_A` layer has lower bound 3. The paper must label the vector conditional/incumbent and
preserve the solver report; it must not call it globally lexicographic optimal.

## Pre-contest Infrastructure — 2026-09-09

No 2026 modeling task has started; selected problem, official statement and attachments remain TBD.

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
cherry-pick or formal Review Lane creation is authorized. The pre-contest freeze policy is active:
stop repository optimization and await the official problem and attachments; only a real P0 blocker
can justify a bounded architecture repair.
