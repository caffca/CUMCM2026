# CUMCM2026 pre-contest readiness finalization

Date: 2026-09-09

Status: `PRE_CONTEST_FREEZE_ACTIVE` (local snapshot subsequently authorized by the user)

Scope: repository organization and synthetic end-to-end verification only; no 2026 contest problem has
been selected or solved.

## Outcome

The repository now has a verified Builder-first rehearsal, a bounded dynamic handoff exporter, an
independent frozen Review rehearsal, an actually rendered four-page Chinese PDF, and a frozen
20-paper design-prior library. Builder remains responsible for the complete first draft; Review and a
web GPT window are post-freeze acceptance/refinement layers rather than production dependencies.

No main-repository stage, commit, push, merge, rebase or cherry-pick was performed during the
finalization verification reported below. The user subsequently authorized one local pre-contest
snapshot of the approved workflow files; its identity is recorded by Git history and the new status
WINDOW_PACKET. Generated rehearsal outputs remain outside that commit. No push, merge, rebase,
cherry-pick or formal Review Lane creation is authorized.

## Four opening chains

| Chain | Actual evidence | Result / boundary |
|---|---|---|
| Builder independently produces a complete draft | Isolated `tmp/contest-rehearsal-v3` performed task decomposition, complete integer enumeration, Q1→Q2 dependency use, conservation/capacity assertions, bounded correction, frozen plot data, formal figure, question prose and a four-page PDF before Review began. | PASS for the explicit synthetic task. No extra human prompt was needed after the task statement. One wrong-cwd render was blocked and retried once; one unsuitable Chinese-text assertion was replaced by `pdftotext`. No rehearsal step remains incomplete. This is not proof for an unseen real problem. |
| Dynamic WINDOW_PACKET | `tmp/handoff/WINDOW_PACKET_FINAL.md` embeds current progress, decisions, design-prior freeze state and the handoff guide; five copied attachments include the frozen packet, results, plot data, PNG and full PDF. | PASS. The status packet is correctly marked `WORKING_STATUS`; the embedded Q1 packet retains frozen SHA provenance. |
| Frozen independent Review | Builder presentation SHA `3c1e04882f7d5e38a94287fe85f89a93085d1232`; Review worktree parent remains that SHA. Builder's later dirty sentinel is 999 while Review and the frozen packet retain 56. Review-only commit `f2140263f77871b3b9bbcda5b10e7a2e8ff33c1a` is isolated. | PASS. `gpt-5.6-terra/high` visual critic returned KEEP, P0 none, P1 none, one optional P2 spacing note. It wrote no Builder files and nothing was merged/cherry-picked. |
| Multi-page Chinese publication | `output/pdf/CUMCM2026_synthetic_rehearsal.pdf`, SHA256 `59e64d92384815ed1fa81529f13634b2d36c89f3bb508c84fbd3d606ad8f9f3c`, 117,964 bytes, four A4 pages. | PASS for the ReportLab/pypdf/SimHei/Poppler path. Structural/render checks found required Chinese prose, formula, table, figure, second question, reference and appendix; all four page images were inspected. 2026 official format remains UNVERIFIED. |

The Builder used a real `gpt-5.6-sol/xhigh` read-only figure specification. The invoking root verified the
frozen plot-data identity, executed the plot, integrated it into prose/PDF, and kept responsibility for
the artifact. Review help was not provided during production.

## Design-prior freeze

- Candidates: 24 unique identities.
- Complete local fulltexts: 20.
- Complete design readings: 20 exactly; `pre_contest_frozen=true`.
- Complete-problem distribution: A/B/C/D/E = 3/5/5/3/4.
- Group coverage: 13 undergraduate A/B/C and 7 vocational D/E papers.
- Prize provenance: 1 `user_confirmed`, 1 independently verified; 18 additional complete official
  showcase design readings remain award `UNVERIFIED`.
- The 12-paper final batch was A196, B060, B157, C023, C132, A163, A242, B159, B195, C038, C063 and
  C234. Every official page set was complete; every body mainline and all required functional-page
  classes were read. Appendices were only boundary/scope checked where declared, and no historical
  scientific result was executed or promoted.
- Search, download, extraction and pattern expansion stopped at 20. The former 50-paper goal is
  post-contest only.

The first post-merge counter reported 18 because B159/B195 retained stale `pages.json` files alongside
newer complete collector manifests. `fulltext_present` was minimally corrected to accept any fully
hash-verified local page manifest rather than fail on the stale record. No raw paper was replaced or
deleted; the next validation reported 20.

## Approved changes in this turn

- Unified Builder complete-draft ownership and normal completion in `AGENTS.md`, the orchestrator,
  modeling, shadow-review, paper-review and handoff skills, `README.md`, the figure guide and the
  self-contained `docs/WINDOW_HANDOFF_GUIDE.md`.
- Added the bounded `scripts/export_window_handoff.py` status/frozen exporter and validated its
  attachment, path and credential guards.
- Added the internal rehearsal generator and targeted multi-page PDF checker; copied the hash-identical
  accepted PDF to `output/pdf/`.
- Completed the 12-paper approved batch, merged exactly 20 cards, preserved award provenance, restored
  the 16-entry collection report, and recorded the pre-contest cap/post-contest 50 boundary.
- Updated current progress and environment evidence. No new agent role, database, registry, daemon,
  recurring task or separate manual log was introduced.

## Historical dirty versus current approval

At turn start, main was already dirty at
`db7f9c0062ce5607907824a2f7809474441e41e6`, with no staged files. Historical dirty included modified
`AGENTS.md`, `README.md`, `.gitignore`, three existing skills, current-progress/environment/figure and
reference-analysis docs, `src/visualization/style.py`, plus untracked orchestration/design-prior skills,
`.codex/`, orchestration/design-upgrade docs, `references/design_priors/`, `scripts/`, visualization
export and figure tests. Those changes were preserved.

This turn's approved edits overlap several of those historical paths; their pre-turn copies are retained
under `tmp/handoff-v3-before/`. New turn-specific deliverables are the handoff guide/exporter, paper
rehearsal/checker, final PDF, this report, the 12 approved raw official page sets (Git-ignored), the
completed 20-card inventory, and isolated scratch/review evidence. This report does not attribute the
entire current dirty tree to this turn.

## Test evidence

- `scripts/design_priors.py validate`: `CORPUS/CARDS SCHEMA PASS`.
- `scripts/design_priors.py stats`: 24 identities, 20 fulltexts, 20 complete reads, 18 official-showcase
  design reads, pre-contest target 20, `pre_contest_frozen=true`.
- Python compilation: design-prior, handoff-export, rehearsal-build and PDF-check scripts compile.
- Final PDF check: four 210×297 mm pages and all required structural markers; Poppler 26.07.0 rendered
  four page PNGs in `tmp/final-pdf-qa/pages/`.
- Frozen exporter: complete for declared q1 at the 40-character SHA; result is 56, not the Builder dirty
  sentinel. Invalid SHA, traversal and `.env` attachment tests each exited 2.
- Git worktree check: Review parent is the exact presentation SHA, Review result is 56, Builder working
  result is 999, and Review tree is clean after its isolated report commit.
- `git diff --check` passed; CRLF conversion warnings are informational. Main staged set remained empty.
- One combined-audit inline Python inventory expression had a PowerShell quoting `SyntaxError`; the
  equivalent read-only PowerShell inventory check then passed with 20 cards, 20 unique card IDs,
  20 complete corpus rows and 16 collector-report records. Other checks in that command had passed.
- `scripts/governance_check.py` is not present in the current slimmed repository, so it was not recreated;
  the relevant targeted checks above were used instead.

## Still unverified / opening inputs

1. 2026 official notice, paper template/format, AI-tool rules, support-material and submission rules are
   absent; all remain `UNVERIFIED`.
2. The selected 2026 problem and all attachments are absent, so the real-problem Builder run, real
   scientific claims and final official-format manuscript cannot yet be validated.

Named custom-role auto-discovery remains `CONFIGURED_NOT_RUNTIME_VERIFIED`, but it is not an opening
blocker: the actually verified fallback is an explicit read-only Sol/xhigh specification/patch followed
by root execution. CTeX remains unavailable because `ctexart.cls` is missing, while the existing
multi-page ReportLab path is verified. Neither gap justifies pre-contest architecture expansion.
