# Q2-R51 原型实现说明（Prototype Engineer：D 题竞争搜索 Q2 组）

## 0. 一句话结论
全势冲突边 G\* 上的 CP-SAT 成对不相容子句模型 + 撤销阶梯，在 547.3s 内给出
**可行解 (撤销6, 调整121, 优先级损失1996, 幅度663)**，经 `canonical_evaluator.py --question Q2`
复算 `feasible=true`、`n_violations=0`；撤销层下界只到 2（`Σr≤5` 深证明 116.5s 仍 UNKNOWN）
⇒ **gap_revoke = 4，未闭合**，因此本路线**不支持**"撤销数最优"的表述，只能写"在 [2,6] 内"。

## 1. 口径绑定（全部按 ADJUDICATION.json）
| 项 | 采用值 | 出处 |
|---|---|---|
| 时间资源盒 | `T_MAX=643`，占用必须整体落于 `[0,643)` | R1 |
| 区间 | 频段/时间一律半开 `[a,b)` | R7/F-023 |
| 边界 | 平移后任何窗越界 ⇒ 动作无效 | R3 |
| 目标 | 词典序 `(撤销, 调整, Σw·被改, Σ\|δ\|)`，撤销优先级损失 2 倍 | R4 |
| 冲突判据 | 频段交叠 ∧ 存在窗交叠，每对至多计一次 | R7 |
| 撤销语义 | 撤销计划资源视为空闲（不产生任何共占） | R8/F-007 |
| 数据 | `data/canonical_plans.csv`（与 evaluator 同文件同列序） | — |

## 2. 关键设计：为什么必须 G\*
- 原冲突边只有 297 条，但**调整会新造冲突**。只约束 297 条边 ⇒ 模型被放松 ⇒ 假 OPTIMAL
  （CH-05 警示 2a）。本实现把子句加在 G\* = **1693** 条"全势冲突边"上，共 **270626** 条
  二元子句（每对计划枚举其动作邻域内所有同格共占组合）。
- 判定用解析式而非掩码枚举（快两个数量级）：
  - 频段交叠 ⇔ `δf = df_i - df_j ∈ [f0_j-f1_i+1, f1_j-f0_i-1]`
  - 时间交叠 ⇔ `δt = dt_i - dt_j ∈ ⋃_{k,l}[c-di+1, c+dj-1]`，`c=(t0_j+l·P_j)-(t0_i+k·P_i)`
- 三重防呆（全部通过并落盘）：
  1. `assert 原冲突边 297 ⊆ G*`（`star_covers_base=true`）；
  2. `code/q2_common.py` 的 `--selftest`：解析式 vs 掩码暴力，400 对随机抽样 × 全动作组合，
     **集合差 = 0**；
  3. 最终方案交 evaluator 复算（`eval.json`）。
- 未做列剪枝（CH-05 探针：只保留"至少修好一条原边"的动作列 ⇒ 报 OPTIMAL=(0,98,585) 但
  残留 121 对冲突）；未保留重复恒等动作列（避免 0.5/0.5 分数解零代价满足全部子句）。

## 3. 词典序四级的实现（逐级锁定，非大 M）
```
L1  min Σr            （48s，FEASIBLE 21，界 2）
    地板测试 Σr≤0     （6.2s，INFEASIBLE ⇒ 撤销数≥1）
    可行性阶梯        Σr≤13→12? 实测：13(F)→9(F)→7(F)→6(UNKNOWN×3)→深证明 Σr≤6 OPTIMAL r=6
L2  min Σadj | Σr≤6   （131.5s，FEASIBLE 121，界 84）
L3  min Σploss | 前两层（56.7s，FEASIBLE 1996，界 422）
L4  min Σ|δ|  | 前三层 （95.7s，FEASIBLE 663，界 321）
```
预算按任务书切分：层1 ≤300s（含阶梯与深证明），其余层共享剩余；到预算即用当前 incumbent + 界。

**经验事实（值得进论文的方法学点）**：带 `min Σr` 目标的模式在同样预算内常常连 cap 内解都找不到
（实测 Σr≤26 用 20s/29s 均 UNKNOWN），而**纯可行性判定 + 上一步解作 hint** 的阶梯只要 5-15s/步。
所以撤销层靠"阶梯下压 + 边界赌 INFEASIBLE"，不靠目标模式。

## 4. 界与证书状态（本组最关键的一条）
- 撤销层：`UB=6`（evaluator 复算的可行 incumbent），`LB=2`
  （来源：min Σr 的 CP 分数界=2；地板证书 Σr≤0 INFEASIBLE 只给 ≥1；
  relaxation（仅 297 原边的真子句集）= 0，无信息）。
- `Σr≤5` 深证明：全势边模型 + 116.5s ⇒ **UNKNOWN** ⇒ 无 INFEASIBLE 证书 ⇒ gap 未闭合。
- 层2-4 的界是"**在 Σr≤6 锁定条件下的条件界**"：adjusted 84 ≤ · ≤ 121，
  priority 422 ≤ · ≤ 1996，magnitude 321 ≤ · ≤ 663。不参与全局标量下界。
- 证书文件：`cpsat_report.json`（stages/ladder/certs）、`r51_certificates.json`（阶段二）。

## 5. 文件
```
code/q2_common.py            共享内核（动作枚举、掩码、G* 子句表、元组复刻）+ --selftest
code/solve_r51.py            阶段一：G* 建模 + 词典序四级 + 撤销阶梯（本候选的 600s 预算本体）
code/cert_r51.py             阶段二：relaxation 下界 + Σr≤k 深证明（额外界证据，见预算申报）
code/assemble_artifacts.py   result.json / scout.json 装配（权威值只取 evaluator 输出）
star_edges.json              G* 与其动作级不相容组合表（缓存，1693 边/270626 组合）
solution_actions.json        {"A007":{"df":-2}, ...} 只列被改/撤销者（127 条）
eval.json                    evaluator 输出：feasible=true, objective=[6,121,1996,663]
cpsat_report.json / r51_certificates.json / r51_phase2_log.txt / run_log.txt
result.json / scout.json     协议契约产物
DEV_LOG.md                   全部开发/子预算运行的如实登记（含被清理的 smoke 产物数值）
```

## 6. 预算合规申报
`runtime_seconds=547.3` 是产出该 incumbent 的词典序求解本体（≤600s ✓）。
其后另跑了一个独立"下界/证书加强"进程 120.4s（**未**替换 incumbent，仅确认 Σr≤5 仍无法判定），
候选合计 667.7s > 600s ⇒ 已在 `result.json.budget_disclosure` 与本文件显式申报，请 Manager 按
"本体 547.3s + 额外界证据 120.4s"的口径使用。
