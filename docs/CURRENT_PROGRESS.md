# Current Progress

## Selected Problem

TBD

## Current Goal

Waiting for the selected problem, complete statement, and all attachments.

## Modeling Spine

TBD

## Problem Status

| Problem | Status | Current method | Key result | Next |
|---|---|---|---|---|
| TBD | waiting | TBD | TBD | receive problem and attachments |

## Current Best Results

TBD

## Paper Status

TBD

## Important Decisions

TBD

## Immediate Next Actions

1. Provide the selected problem and complete attachments.
2. Start with题意拆解、数据检查和第一问 baseline。

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
