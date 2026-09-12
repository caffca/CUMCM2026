# D 题证据包复现说明

本文件给队友用于复核当前证据包。命令均从仓库根目录执行；推荐把探索输出写入
`tmp/repro/`，不要覆盖 `outputs/` 中的正式结果。原始附件只读：
`data/raw/D题/附件/附件1.xlsx` 的 SHA-256 为
`B7F905CD2629F9A85B47DB352BE503404A0CD5B8F70B9209AAFDF7E262F3449C`。

## 环境版本

- Python 3.12.10
- OR-Tools 9.15.6755（Q2/Q4 CP-SAT）
- SciPy 1.18.1、HiGHS/PyHiGHS `highspy` 1.15.1（Q3 集合装填）
- `python-sat` 1.9.dev15；`cadical195` 后端为 CaDiCaL 1.9.5
- Node.js v24.19.0；`@oai/artifact-tool` 由工作区依赖运行时提供

精确 Python 依赖见 [requirements-cumcm.txt](requirements-cumcm.txt)。若使用本机 Python，
先执行 `python -m pip install -r requirements-cumcm.txt`；CaDiCaL 由 python-sat 的
`cadical195` 后端调用，不需要另装系统二进制。

## Q1

```text
python -m scripts.solve_q1 --input data/raw/D题/附件/附件1.xlsx --output-dir tmp/repro/q1
```

检查 `tmp/repro/q1/results.json`、`conflict_pairs.csv` 与 `validation.json`（若运行脚本
生成）中的冲突对和事件级重叠数。

## Q2 主模型和完整七层证据链

```text
python -m scripts.solve_q2_cp_sat --input data/raw/D题/附件/附件1.xlsx --horizon 643 --scheme priority_protected --mode chain --known-revocations 6 --known-revocations-evidence outputs/q2/revocation_bound.json --stage-time-limit 180 --time-limit 180 --workers 8 --seed 20260911 --output tmp/repro/q2/priority_chain.json
python -m scripts.validate_q2 --input data/raw/D题/附件/附件1.xlsx --result outputs/q2/six_revocation_candidate.json --output tmp/repro/q2/six_validation.json --horizon 643
python -m scripts.validate_result2_workbook --result outputs/q2/six_revocation_candidate.json --workbook outputs/q2/result2.xlsx --output tmp/repro/q2/workbook_validation.json
```

五个相邻阈值的独立 SAT 命令如下。`UNSAT` 才是不可行下界，`SAT` 只提供可行见证。

```text
python -m scripts.prove_q2_sat --input data/raw/D题/附件/附件1.xlsx --horizon 643 --probe b_le_3 --solver cadical195 --output tmp/repro/q2/sat_b_le_3.json
python -m scripts.prove_q2_sat --input data/raw/D题/附件/附件1.xlsx --horizon 643 --probe adjust_le_125 --solver cadical195 --output tmp/repro/q2/sat_adjust_le_125.json
python -m scripts.prove_q2_sat --input data/raw/D题/附件/附件1.xlsx --horizon 643 --probe adjust_a_le_15 --solver cadical195 --output tmp/repro/q2/sat_adjust_a_le_15.json
python -m scripts.prove_q2_sat --input data/raw/D题/附件/附件1.xlsx --horizon 643 --probe adjust_b_le_33 --solver cadical195 --output tmp/repro/q2/sat_adjust_b_le_33.json
python -m scripts.prove_q2_shift_sat --input data/raw/D题/附件/附件1.xlsx --horizon 643 --solver cadical195 --time-limit 900 --no-dominance --output tmp/repro/q2/sat_shift_le_774_full.json
```

正式阈值文件的 `evidence_metadata` 保存固定前缀、阈值、变量/约束/子句计数、构造和
求解时间、求解器版本、源文件哈希、生成脚本及对应见证。历史实际命令未被日志记录的，
字段明确标为 `historical_command_verified=false`。

## Q3

Q3 必须读取 `outputs/q3/q2_input_from_result2.json`，而不是只按撤销台数重构 Q2。

```text
python -m scripts.solve_q3 --input data/raw/D题/附件/附件1.xlsx --q2-result outputs/q2/results.json --output-dir tmp/repro/q3 --horizon 643 --time-limit 180
python -m scripts.validate_q3 --input data/raw/D题/附件/附件1.xlsx --q2-result outputs/q2/results.json --q3-result tmp/repro/q3/results.json --workbook outputs/q3/result3.xlsx --output tmp/repro/q3/validation.json --horizon 643
```

当前接口记录 Q2 工作簿 SHA-256、144 个活动计划、15,816 个占用格、目标向量
`[6,0,4,126,16,34,775]`、`H=643` 和 C 类模板 `(3,2,8,12)`；Q3 的 141 是在该
具体背景下的条件最优，不是所有 Q2 布局的联合最优。

## Q4

主层 CP-SAT 复现命令：

```text
python -m scripts.solve_q4_cp_sat --input data/raw/D题/附件/附件1.xlsx --horizon 643 --mode chain --objectives revoke,revoke_A,revoke_B,adjust,adjust_A,adjust_B,normalized_shift --time-limit 300 --workers 8 --seed 20260911 --output tmp/repro/q4/chain.json
```

`R≤2` 的全局下界由六个类别配额分支分别复现（将 `A=0,B=0,C=2` 替换为表中其余五组）：

```text
python -m scripts.prove_q4_active_sat --input data/raw/D题/附件/附件1.xlsx --horizon 643 --target-active 148 --exact-revokes 2 --revoke-category-count A=0 --revoke-category-count B=0 --revoke-category-count C=2 --compact-category-cardinality --solver cadical195 --time-limit 300 --output tmp/repro/q4/R2_A0B0C2.json
```

六组为 `(0,0,2),(0,1,1),(0,2,0),(1,0,1),(1,1,0),(2,0,0)`，每组必须返回
`UNSAT/PROVED_INFEASIBLE`，不能只固定两台设备身份。

当前正式工作簿由 M=136 见证重建：

```text
$env:Q4_RESULTS_PATH = 'C:/Users/ysw/Desktop/CUMCM2026/outputs/q4/result4_selected.json'
$env:Q4_OUTPUT_PATH = 'C:/Users/ysw/Desktop/CUMCM2026/outputs/q4/result4.xlsx'
$env:Q4_PREVIEW_PATH = 'C:/Users/ysw/Desktop/CUMCM2026/tmp/artifact-q4/result4_m136_preview.png'
$env:Q4_VALIDATION_PATH = 'C:/Users/ysw/Desktop/CUMCM2026/outputs/q4/result4_workbook_validation.json'
& 'C:/Users/ysw/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' scripts/build_result4.mjs
Remove-Item Env:Q4_RESULTS_PATH,Env:Q4_OUTPUT_PATH,Env:Q4_PREVIEW_PATH,Env:Q4_VALIDATION_PATH
python -m scripts.import_q4_workbook --input data/raw/D题/附件/附件1.xlsx --workbook outputs/q4/result4.xlsx --output tmp/repro/q4/result4_import.json
python -m scripts.validate_q4 --input data/raw/D题/附件/附件1.xlsx --result tmp/repro/q4/result4_import.json --output tmp/repro/q4/result4_validation.json --horizon 643
```

M=139、M=140 的 SAT 文件和验证文件仍随包提供，但它们已经被 M=136 的已验证见证
严格支配；当前工作簿不应再由旧 M=142 链生成。

## 证据边界

Q2 当前七层证据在有限动作集、`H=643` 和方案 B 字典序下闭合。Q4 只闭合最少撤销层
`R^*=3`；M=136 是固定 `R=3,R_A=0,R_B=1` 前缀下当前最好可行上界，尚未证明
`M≤135` 不可行。因此包内把“可行见证”和“最优性证明”分开标记。
