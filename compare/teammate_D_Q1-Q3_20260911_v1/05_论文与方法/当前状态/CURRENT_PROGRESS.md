# Current Progress

## Selected Problem

D 题：时频冲突检测与消解

## Current Goal

完成 Q2 模型优化审计与 Q3 独立最优性闭合，形成可供队员审计和论文整合的 Markdown；审计后再进入 Q4。

## Modeling Spine

计划行 → 重复使用事件展开 → 半开区间冲突检测 → 约束消解/新增计划优化 → 结果模板与论文统计。
当前已完成 intake；Q2 主目标与优先级前缀已完成证明，Q3 已从批准的 `result2.xlsx` 重新导入并完成最优装填和独立验证。

## Problem Status

| Problem | Status | Current method | Key result | Next |
|---|---|---|---|---|
| D / intake | complete | PDF + 5 个 XLSX + 用户 Markdown 对照；频率/时间/二维占用分析 | 已纠正重复事件语义：相邻起点步长=单次时长+空闲间隔；经验时间包络为 `[0,643)`；C 类步长为 10 | 作为 Q1–Q4 的统一输入口径 |
| D / Q1 | milestone complete | 正确重复递推 + 半开区间精确枚举；离散时频单元独立复核 | 150 个计划、1,300 个事件；297 对冲突，431 次事件级重叠；结果表已生成 | 将 297 条冲突边作为 Q2 硬约束输入 |
| D / Q2 | milestone complete / interface approved | CP-SAT 候选动作 + 资源格团约束 + 独立 CNF/CaDiCaL 阈值证明 + 双重独立复核 | `R*=6`、`R_A*=0`、`R_B*=4`、`M*=126`、`M_A*=16`、`M_B*=34` 已按条件字典序逐层证明；末级 `S10=775` 仅为可行上界 | Q3 已读取批准的 `result2.xlsx`；方案变化时需重跑 |
| D / Q3 | milestone complete / optimum independently audited | 从批准 `result2.xlsx` 导入固定六撤销 Q2 + 完整 C 类候选枚举 + 资源格/成对冲突两种 0-1 编码 | 两种编码均闭合到 141；`sum(y)≥142` 不可行；独立可行性验证 PASS | Q2 方案变化时必须同步重算 |
| D / Q4 | pending | 尚未建模 | 未计算 | 先读取 Q3/Q2 的固定资源与边界口径，建立间隔调整模型 |

## Current Best Results

Q1 正式结果：在 11,175 个候选装备对中检出 297 对冲突装备（2.66%），其中 B-C 为 181 对，类别内冲突率 5.03%；148 个装备构成一个大连通分量，C007、C060 为孤立装备。连续区间算法与独立离散时频单元算法完全一致。正式资产见 `outputs/q1/`。

Q2 当前正式方案：150 个计划枚举为 4,582 个候选动作，CP-SAT 使用 52,939 条资源格团约束。总撤销目标的 LB=UB=6，固定 `R=6` 后 A 类撤销为 0；独立 CaDiCaL 证明 `B≤3`、`M≤125`、`M_A≤15`、`M_B≤33` 均不可行，因此条件字典序前缀为 `(R,R_A,R_B,M,M_A,M_B)=(6,0,4,126,16,34)`。正式方案为 A 类 4/16/0、B 类 2/34/4、C 类 12/76/2，144 个活动计划占用 15,816 个资源格，连续/离散检查均零冲突。末级 `S10=775` 暂不宣称全局最优。

Q3 当前结果：从批准的 `result2.xlsx` 反向解析出 144 个活动计划和 15,816 个已占用单元，在 52,136 个完整 C 类候选起点中筛得 2,334 个与 Q2 不冲突的候选；资源格集合装填与 66,472 条成对冲突约束两种编码均得到 141，且“至少 142 台”阈值模型不可行。因此 Q3 题面主目标的 LB=UB=141；合并后 285 个活动计划占用 25,968 个不同单元，独立验证通过。旧 203 对应旧 19 撤销背景，已 supersede。

## Paper Status

已完成问题一、问题二和问题三逐问闭环 Markdown 正文 `paper/draft_sections/q1.md`、`q2.md`、`q3.md`，并新增 `paper/draft_sections/model_optimization.md` 作为 Q2–Q3 模型优化待整合稿。Q2/Q3 的审计说明分别位于 `outputs/q2/q2_optimization_audit.md` 与 `outputs/q3/q3_optimization_audit.md`。官方论文格式规范未随题面附件提供，尚未排版为正式整篇论文。

## Important Decisions

D 题已进入当前工作线。用户正式确认 Q2–Q4 统一采用数据驱动时间包络 `[0,643)`，所有调整后事件不得越界；Q3 固定 Q2 结果并新增继承附件结构的 C 类设备。边界敏感性取 `H∈{638,643,648}`。Q2 已采用精炼方案 B；Q4 的多目标优先级仍需在建模时显式说明。Q2 和 Q3 保持单向接口，Q3 剩余容量不回写 Q2。

Q2 采用精炼方案 B `R→R_A→R_B→M→M_A→M_B→S_n` 和 CP-SAT 资源格团约束；未证明的字典序层不得固定后继续形成正式最优结论。H<643 的完整重复包络边界规则继续有效。Q3 采用完整 C 类模板集合装填并固定 Q2，不反向影响 Q2。正式图提供 PDF/SVG/PNG 与灰度预览。

## Immediate Next Actions

1. 由用户审计 Q2/Q3 优化说明与 Q3=141 的独立最优性证据。
2. 审计后在 Q2/Q3 固定接口基础上建立 Q4 模型。
3. 图表重绘放到模型结果稳定后的统一视觉阶段；如需完整字典序最优，再单独处理 Q2 末级 `S10`，不改变当前 Q3 接口。

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
