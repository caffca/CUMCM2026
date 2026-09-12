# D 题证据链队友上传说明

更新时间：2026-09-12（Asia/Shanghai）

## 接收对象与仓库状态

本文件面向需要在另一台电脑或网页窗口复核、上传证据的队友。当前 canonical repo 为
`C:/Users/ysw/Desktop/CUMCM2026`，分支 `main`，HEAD
`c5d1b3baa55a72f211abfdf794acd415644aef21`。工作区有未提交的历史建模、论文和本轮
证据整理改动，不能把该 HEAD 冒充为包含本轮全部文件的 frozen SHA；上传时以本包内实际
文件和 `PACKAGE_MANIFEST.json` 为准。原始附件未改动，`data/raw/D题/附件/附件1.xlsx`
SHA-256 为 `b7f905cd2629f9a85b47db352be503404a0cd5b8f70b9209aafdf7e262f3449c`。

## 当前目标

让队友拿到一套可逐文件复核的 Q2 完整字典序证据、Q3 与 Q2 的输入绑定、Q4 最少撤销
证明及当前工作簿，并说明哪些结论已闭合、哪些仍只是可行上界。所有路径均相对于仓库
根目录；ZIP 可直接交给队友上传。

## 已完成的证据整理

### Q2

当前正式目标向量为
`(R,R_A,R_B,M,M_A,M_B,S10)=(6,0,4,126,16,34,775)`。`results.json` 的状态为
`FULL_LEXICOGRAPHIC_PROVED`。`R` 的 CP-SAT 上下界证据与五个相邻阈值的独立
CaDiCaL `UNSAT` 文件共同闭合七层；末级文件使用完整 4,582 个候选全集。五个 SAT
文件和 CP-SAT 撤销下界/前缀汇总文件均包含 `evidence_metadata`，记录固定前缀、阈值、
公式规模、求解时间、求解器版本、生成脚本、复现命令、原始输入哈希和对应可行见证。
历史命令未被日志记录的地方明确标记 `historical_command_verified=false`。

应上传：

- `outputs/q2/summary.md`
- `outputs/q2/result2.xlsx`
- `outputs/q2/six_revocation_candidate.json`
- `outputs/q2/six_revocation_validation.json`
- `outputs/q2/workbook_validation.json`
- `outputs/q2/revocation_bound.json`
- `outputs/q2/priority_prefix_run.json`
- `outputs/q2/proof/sat_b_le_3.json`
- `outputs/q2/proof/sat_adjust_le_125.json`
- `outputs/q2/proof/sat_adjust_a_le_15.json`
- `outputs/q2/proof/sat_adjust_b_le_33.json`
- `outputs/q2/proof/sat_shift_le_774_full.json`
- `outputs/q2/proof/SAT_EVIDENCE_INDEX.md`
- `outputs/q2/proof/sat_evidence_validation.json`

旧的 `priority_prefix_run.json` 的 FEASIBLE/未证明快照已移入 `legacy_snapshot`，
不会再覆盖当前正式状态。

### Q3

`outputs/q3/q2_input_from_result2.json` 现在明确绑定 `outputs/q2/result2.xlsx`，并保存
该工作簿和候选 JSON 的 SHA-256、144 个活动计划、15,816 个占用资源格、Q2 目标向量、
`H=643`、资源域和 C 类模板 `(3,2,8,12)`。Q3 的两套独立优化/阈值证据均为 141，
142 不可行；结论范围是“固定这一具体 Q2 背景下条件最优”。

应上传：

- `outputs/q3/q2_input_from_result2.json`
- `outputs/q3/result3.xlsx`
- `outputs/q3/results.json`
- `outputs/q3/validation.json`
- `outputs/q3/q3_optimality_audit.json`
- `outputs/q3/q3_optimization_audit.md`

### Q4

六个 `R=2` 类别配额分支文件都返回 `UNSAT`，覆盖
`(0,0,2),(0,1,1),(0,2,0),(1,0,1),(1,1,0),(2,0,0)`，并有全局覆盖和支配消元核验，
故最少撤销层 `R^*=3` 已闭合。

仓库曾有 M=142 工作簿，也有 M=140、M=139 和 M=136 的独立可行见证。由于 M=136
已经通过独立验证且严格优于 M=139，当前正式工作簿已统一为 M=136：

`(R,R_A,R_B,M,M_A,M_B,S10^(4))=(3,0,1,136,19,36,924)`。

M=136 只是固定前三层前缀下的当前最好可行上界；`M≤135` 及后续次级层没有完整
相邻阈值不可行证明。M=139/M=140 仍按审计要求上传，且不再被标为当前最好方案。

应上传：

- `outputs/q4/proof_R_le_3.json`
- `outputs/q4/proof_R_le_3_validation_final.json`
- 六个 `outputs/q4/proof_R_le_2_active_sat_r2_*.json`
- `outputs/q4/proof_R_le_2_dominance_validation.json`
- `outputs/q4/proof_R_le_2_global_coverage_validation.json`
- `outputs/q4/r2_global_proof_status.md`
- `outputs/q4/proof_R3_RA0_RB1_M140_witness.json`
- `outputs/q4/proof_R3_RA0_RB1_M139_witness.json`
- `outputs/q4/result4.xlsx`
- `outputs/q4/result4_selected.json`
- `outputs/q4/result4_workbook_validation.json`
- `outputs/q4/q4_secondary_proof_matrix.md`
- `outputs/q4/summary.md`

`result4_workbook_validation.json` 记录 Artifact Tool 导出、工作簿回读、动作集合一致性
和独立验证路径；M=136 的独立回读文件为
`outputs/q4/result4_M136_workbook_validation_independent.json`。旧工作簿以带
`legacy_20260912` 后缀的副本保留，便于追溯但不应当作为当前接口。

## 复现和上传材料

- `README_REPRO.md`：Python、OR-Tools、SciPy/HiGHS、python-sat/CaDiCaL、Node 版本和
  Q1–Q4 完整命令。
- `requirements-cumcm.txt`：补充了 Q2/Q4 SAT 所需的 `python-sat==1.9.dev15`。
- `PACKAGE_MANIFEST.json`：上传包内每个文件的相对路径、大小和 SHA-256；同时记录 raw
  附件哈希、分支/HEAD 和工作区 dirty 状态。
- `comparison/`：统一口径的当前/历史方案对比材料；每个方案目录含
  `summary.md`、`solver_report.json`、`validation.json` 和 `selected_or_workbook`，
  总表为 `comparison/UNIFIED_COMPARISON_REPORT.md`。

## 仍需队友执行的动作

1. 解压 `docs/team_upload_20260912_v8.zip`，按 `PACKAGE_MANIFEST.json` 检查文件完整性。
2. 复现环境后运行 `README_REPRO.md` 中的验证命令；重点核对 Q2 五个 `UNSAT`、Q3 的
   141/142 阈值和 Q4 六个类别分支。
3. 将 ZIP 上传到队伍共享位置，并在论文中只采用包内 canonical 文件；若重新求得更小
   的已验证上界，必须同步替换正式工作簿、selected JSON、validation 和摘要。

## 授权边界

本轮只修改派生证据、文档和正式输出副本；没有修改 `data/raw`，没有删除历史结果，
没有执行 destructive Git 操作，也没有把限时 `UNKNOWN` 或 SAT 可行见证升级为最优性
证明。队友可以在自己的分支复现、核验和上传，但应保留上述 SHA、适用范围和“当前最好
可行但未闭合”的 Q4 证据边界。
