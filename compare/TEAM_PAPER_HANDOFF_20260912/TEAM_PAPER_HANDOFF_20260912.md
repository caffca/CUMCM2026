# CUMCM2026 D 题论文团队交接包

> 版本：2026-09-12  
> 面向对象：队友、接手本项目的 Codex/本地 Builder、论文终稿整理者  
> 证据原则：以当前工作区重新生成的结果、独立核验文件和本交接包所列路径为准；旧稿只用于追溯，不作为新结论证据。

## 0. 先看这里：交接规则

这份文件不是普通提纲，而是当前项目的“事实台账 + 复现入口 + 论文同步清单”。接手者应先读本文件，再读同目录的 `WINDOW_PACKET.md` 和 `README.md`，最后按问题读取 `outputs/q1/`—`outputs/q4/` 的摘要与证据文件。

状态标记统一如下：

- **PROVED / 已证明**：有可行见证与下界/阈值不可行证据，且证据文件明确闭合。
- **CONDITIONAL / 条件最优**：在固定 Q2 方案、固定资源域、固定模板或固定目标前缀下成立，不能外推。
- **FEASIBLE WITNESS / 条件可行见证**：只证明有一组合法方案，不证明该层最优。
- **SENSITIVITY / 敏感性**：用于边界或跨问诊断，不替代题面主答案。
- **STALE / 待同步**：工作区中存在较早的论文文字或旧台账，不能覆盖更新后的结果证据。
- **SUPERSEDED / 已废弃**：旧模型、旧数字或旧排版，不能作为正文结论。

特别注意：当前工作区是**脏工作树**，本交接包记录的是 2026-09-12 的工作副本状态，不等同于一个干净、已提交、已冻结的 Git 版本。不要依据 `HEAD` 自动推断所有结果都已提交，也不要覆盖原始数据、旧稿或正式结果。

## 1. 论文基本信息

| 项目 | 当前内容 |
|---|---|
| 论文题目 | **时频资源离散化与字典序整数优化的装备用频冲突检测与消解** |
| 题目 | CUMCM2026 D 题：时频冲突检测与消解 |
| 研究目标 | 在离散时间—频率资源域内，完整展开重复用频事件，识别计划冲突；在题面给定的动作规则和类别优先级下消解冲突；固定问题二方案后评估新增 C 类容量；再在允许 C 类改变重复间隔的扩展动作集内求最小撤销层。 |
| 当前论文源稿 | `paper/rebuild/` |
| 当前编译 PDF | `paper/rebuild/build/main.pdf` |
| 当前支撑包 | `paper/rebuild/支撑材料_Q4完整稿_20260912.zip` |
| 旧稿 | `paper/tex/`，保留不动，不作为新证据来源 |
| 当前 PDF | 20 页，A4；已完成 XeLaTeX 编译和页面检查 |
| 统一图表风格 | 低饱和蓝—橙/蓝—青类别色；连续变量采用感知均匀色图；当前论文使用 B 配色 |

### 1.1 当前版本身份

- 仓库根目录：`C:\Users\ysw\Desktop\CUMCM2026`
- Git 分支：`main`
- 当前 HEAD：`c5d1b3baa55a72f211abfdf794acd415644aef21`
- 工作树：**DIRTY**，存在大量用户修改和未跟踪文件；本包不是该工作树的提交快照。
- 原始附件路径：`data/raw/D题/`，默认只读。
- 论文新稿路径：`paper/rebuild/`。
- 旧版路径：`paper/tex/`，不得覆盖、删除或拿来证明新结果。

### 1.2 当前正式文件指纹

这些哈希是交接时点的识别信息，不替代科学验证：

| 文件 | SHA-256 |
|---|---|
| `paper/rebuild/build/main.pdf` | `CFB6448D9979F02826515EF7BB8C9E4C4F69F2045ADD503C073404238E252CD6` |
| `paper/rebuild/支撑材料_Q4完整稿_20260912.zip` | `E6DF4E83FCC4CE4712E9FD2FA0EC433643A9B01894F64BD6BAAE98E6CFE44813` |
| `data/raw/D题/D题.pdf` | `04945C2DB24CD6CB659DE55E6A23DDD43553EC61BC1C7741010A7EAC220712A9` |
| `data/raw/D题/附件/附件1.xlsx` | `B7F905CD2629F9A85B47DB352BE503404A0CD5B8F70B9209AAFDF7E262F3449C` |

## 2. 一页版结论摘要

统一表示为“计划 → 重复使用事件 → 离散时频资源格”。对每条计划按“单次使用时长 + 空闲间隔”展开全部事件，采用半开区间；基准资源域为 `[0,643)×[0,100)`。问题一在 150 条计划上展开 1,300 个事件，枚举 11,175 个计划对，得到 297 对冲突装备和 431 次事件级重叠，其中 B—C 类冲突 181 对、按全部 B—C 可能配对归一化的冲突率为 5.03%。问题二对每条计划枚举保留、频移、时移和撤销动作，形成 4,582 个合法动作，用 52,939 条资源格互斥约束求解；当前最新证据将条件字典序七层全部闭合为 `(R,R_A,R_B,M,M_A,M_B,S10)=(6,0,4,126,16,34,775)`，正式方案保留/调整/撤销为 A `4/16/0`、B `2/34/4`、C `12/76/2`，144 个计划无冲突。问题三冻结该具体 Q2 方案，枚举 52,136 个完整 C 类起点，筛得 2,334 个可行候选，用集合装填和独立成对冲突编码均得到固定背景下最大新增 141 台，142 台不可行。问题四从 Q1 的 150 条原始计划重新起算，只给 C 类增加整数间隔动作，得到 6,103 个合法动作；支配消元后对两台撤销的六种类别分支全部作 SAT 检验，均不可行，而三台撤销有独立验证的可行见证，因此当前有限整数动作集合、`H=643` 下的最小撤销层为 `R_Q4^*=3`。Q4 的 `R=3` 内次级目标仍未完整闭合；现有 142 调整、`R_B=1`、`S10^(4)=943` 只能作为条件可行候选或历史基线。

## 3. 输入数据与来源

### 3.1 原始题面与附件

| 文件 | 作用 | 是否作为当前证据 |
|---|---|---|
| `data/raw/D题/D题.pdf` | 官方题面/约束/附件说明 | 是，题意来源 |
| `data/raw/D题/D题_1.3题面对照边界核查.md` | 对题面第 1—3 问和边界的人工对照记录 | 是，解释性核验 |
| `data/raw/D题/附件/附件1.xlsx` | 150 条原始用频计划 | 是，所有 Q1—Q4 的基础数据 |
| `data/raw/D题/附件/附件2/result1.xlsx` | Q1 输出模板 | 只作为输出格式 |
| `data/raw/D题/附件/附件2/result2.xlsx` | Q2 输出模板/外部工作簿格式 | 只作为模板；当前 Q2 正式方案另有 `outputs/q2/result2.xlsx` |
| `data/raw/D题/附件/附件2/result3.xlsx` | Q3 输出模板 | 只作为输出格式 |
| `data/raw/D题/附件/附件2/result4.xlsx` | Q4 输出模板 | 只作为输出格式 |

原始附件的完整文件清单和 SHA-256 在 `work/intake/FILE_MANIFEST.json`。本交接 ZIP 的 `source_attachments/` 也附了一份题面、附件 1 和模板，便于队友离线检查；不要把模板当作新的观测数据。

### 3.2 原始数据规模与字段

- 实际计划：150 条；附件 1 共 151 行，其中首行为表头。
- 计划编号唯一；类别数量为 A/B/C = 20/40/90。
- 每条计划保留 5 个字段：装备编号、频段区间、首次时间区间、间隔时长、使用次数。
- 频段宽度取 3、10 或 15；首次时间宽度取 2、3 或 5；间隔取 8、40 或 60；使用次数取 3、4 或 12。
- 数据审计：无空值、无重复行、无错误单元格；频段位于 `[0,100)`。
- 原始文件只读；清洗、展开、候选动作和模型输入全部写入 `outputs/` 或临时工作目录。

## 4. 关键变量与统一口径

以下是给队友和 Codex 的最小符号字典；正式论文中的“符号—含义”表位于 `paper/rebuild/sections/symbols.tex`，但其中关于 `S10` 的旧表述需要按第 13 节同步。

| 符号 | 含义 |
|---|---|
| `I` | 原始用频计划集合，共 150 条 |
| `i,j` | 计划/装备索引 |
| `k` | 同一计划内的重复事件序号 |
| `[f_i^-,f_i^+)` | 计划 i 的频段半开区间 |
| `[s_i,e_i)` | 计划 i 的首次时间半开区间 |
| `l_i=e_i-s_i` | 单次使用时长 |
| `g_i` | 空闲间隔时长 |
| `n_i` | 重复使用次数 |
| `E_i` | 计划 i 的完整重复事件集合 |
| `C_ij` | 计划 i、j 是否存在计划层冲突 |
| `A_i` | 计划 i 的候选动作集合 |
| `x_ia` | 计划 i 是否选动作 a 的 0—1 变量 |
| `K_ia` | 动作 `(i,a)` 展开后占用的资源格集合 |
| `c=(t,f)` | 离散时间—频率资源格 |
| `R,R_A,R_B` | 总撤销数、A 类撤销数、B 类撤销数 |
| `M,M_A,M_B` | 总调整数、A 类调整数、B 类调整数 |
| `S10` | Q2 已闭合前缀下的归一化平移量整数值；最新证据为 775 |
| `δf,δt` | 频率平移量、首次时间平移量 |
| `δg` | Q4 C 类间隔调整量，`g'=8+δg` |
| `p` | Q3 的完整 C 类候选起点 |
| `y_p` | 是否选择 Q3 候选 p 的 0—1 变量 |
| `K_p` | Q3 候选 p 的完整资源格集合 |
| `O_c` | 固定 Q2 方案对资源格 c 的占用指示量 |
| `H` | 时间域右端点，基准为 643，敏感性取 638、643、648 |
| `S10^(4)` | Q4 固定撤销层下的末级变化量指标 |

### 4.1 不可改变的事件展开口径

对计划 `i`，第 `k` 次使用事件为

`I_ik = [s_i + k(l_i+g_i), e_i + k(l_i+g_i))`, `k=0,...,n_i-1`。

这里的步长是 `l_i+g_i`，不是 `g_i`。A001 题面示例和 C083 的末次事件共同确认了这一点。所有区间采用半开形式：一段事件在 `t` 结束、另一段在 `t` 开始时不算重叠。

## 5. 数据预处理（DP-1—DP-3）

### DP-1：字段审计与计划级输入

150 条唯一计划、字段完整，A/B/C=20/40/90；原始计划与输出模板分离。证据：`work/intake/DATA_AUDIT.md`、`work/intake/FILE_MANIFEST.json`、`outputs/q1/summary.md`。

### DP-2：重复事件与离散化

先从首次区间、单次时长、间隔、次数递推完整事件，再把事件映射到整数时频资源格。由完整数据展开得到基准域 `[0,643)×[0,100)`；643 是数据驱动的最晚结束边界，不是题面直接给出的全局常数。

### DP-3：跨问题接口

- Q1：读取 150 条原始计划，输出计划层冲突边和事件级重叠统计。
- Q2：读取 Q1 的冲突背景，但必须对每个调整动作重新展开全部事件；不允许只修首次事件。
- Q3：只读取已经验证的 Q2 具体工作簿，冻结 144 个活动计划及其占用格，不反向改变 Q2。
- Q4：从 Q1 的 150 条原始计划独立起算，不读取 Q2 的撤销方案，也不混入 Q3 新增的 141 台。

## 6. 问题一：冲突检测

### 6.1 模型与算法

对任意不同计划 `i,j`，若频段区间相交且存在一对重复事件时间区间相交，则 `C_ij=1`。算法是：

1. 先用频段区间相交做预筛；
2. 对剩余计划对展开全部重复事件并做半开区间相交判断；
3. 计划层同一对只保留一条冲突边，事件级重叠次数另行计数；
4. 用离散资源格倒排索引独立重建冲突图。

### 6.2 结果（PROVED / 直接枚举）

| 指标 | 结果 |
|---|---:|
| 原始计划 | 150 |
| 重复事件 | 1,300 |
| 计划对枚举 | 11,175 |
| 冲突装备对 | 297（2.66%） |
| 事件级重叠 | 431 |
| 参与冲突的装备 | 148；C007、C060 孤立 |
| 连通分量 | 3；最大分量 148 |
| 平均冲突度 / 最大冲突度 | 3.96 / 8 |
| B—C 冲突对 | 181，占全部冲突对 60.94%；B—C 归一化冲突率 5.03% |

297 是计划对指标，431 是事件重叠指标，不能混写。Q1 的 297 条冲突边是 Q2 的硬约束背景。

### 6.3 验证与证据

- 连续半开区间算法与离散资源格算法得到同一组 297 对冲突。
- 事件级重叠重算为 431；`result1.xlsx`、`results.json`、`conflict_pairs.csv` 逐行一致。
- A001 第二次事件和 C083 最后一次事件用于核验步长与边界。
- 主要文件：`outputs/q1/summary.md`、`outputs/q1/results.json`、`outputs/q1/validation.json`、`outputs/q1/conflict_pairs.csv`、`outputs/q1/result1.xlsx`。
- 求解/核验脚本：`scripts/solve_q1.py`、`scripts/validate_q1.py`。

## 7. 问题二：冲突消解与条件字典序优化

### 7.1 动作集合与硬约束

每条计划从 `keep / frequency-shift / time-shift / revoke` 中选择一个动作；频移满足 `|δf|≤10`，时移满足 `|δt|≤5`，一次不能同时改变频率和时间；单次时长、间隔、使用次数保持不变；所有完整重复事件必须落在 `[0,643)×[0,100)`。

对每个资源格 `c` 约束

`Σ_(i,a): c∈K_ia x_ia ≤ 1`，且每条计划恰选一个动作 `Σ_a x_ia=1`。

基准场景共形成 4,582 个合法动作、52,939 条资源格团约束；等价的候选成对冲突边为 270,626 条。主求解器为 CP-SAT；关键阈值另以 CNF/CaDiCaL 检查。

### 7.2 目标与最新证明状态

采用不引入人为权重的条件字典序：

`(R, R_A, R_B, M, M_A, M_B, S10)`，其中 `S10=Σ_i(|δf_i|+2|δt_i|)`。

**当前最新结果证据（应优先于较早论文文字）**：

| 层级 | 条件 | LB | UB/见证 | 状态 |
|---|---|---:|---:|---|
| `R` | 无 | 6 | 6 | PROVED |
| `R_A` | `R=6` | 0 | 0 | PROVED |
| `R_B` | `R=6,R_A=0` | 4 | 4 | PROVED，`B≤3` UNSAT |
| `M` | 上述前缀 | 126 | 126 | PROVED，`M≤125` UNSAT |
| `M_A` | 上述前缀、`M=126` | 16 | 16 | PROVED，`M_A≤15` UNSAT |
| `M_B` | 上述前缀、`M_A=16` | 34 | 34 | PROVED，`M_B≤33` UNSAT |
| `S10` | 上述完整前缀 | 775 | 775 | PROVED，`S10≤774` 全候选 UNSAT |

因此，当前权威结果文件将 Q2 标为 `FULL_LEXICOGRAPHIC_PROVED`，完整值为：

`(R,R_A,R_B,M,M_A,M_B,S10)=(6,0,4,126,16,34,775)`。

### 7.3 正式方案与验证

| 类别 | 保留 | 调整 | 撤销 |
|---|---:|---:|---:|
| A | 4 | 16 | 0 |
| B | 2 | 34 | 4 |
| C | 12 | 76 | 2 |
| 合计 | 18 | 126 | 6 |

撤销计划：`B009、B018、B024、B028、C027、C054`。144 个活动计划占用 15,816 个不同资源格；频移绝对值总和 595，时移绝对值总和 90，`S10=595+2×90=775`。连续半开区间与离散资源格检查均为零冲突、零越界、零重复占用。

### 7.4 Q2 证据入口

- 总撤销证书：`outputs/q2/revocation_bound.json`。
- 完整结果：`outputs/q2/results.json`。
- 正式动作表：`outputs/q2/six_revocation_candidate.json`、`outputs/q2/result2.xlsx`。
- 独立验证：`outputs/q2/six_revocation_validation.json`、`outputs/q2/validation.json`、`outputs/q2/workbook_validation.json`。
- 阈值矩阵：`outputs/q2/q2_proof_matrix.csv`。
- SAT 证据：`outputs/q2/proof/sat_b_le_3.json`、`sat_adjust_le_125.json`、`sat_adjust_a_le_15.json`、`sat_adjust_b_le_33.json`、`sat_shift_le_774_full.json`。
- 证据索引：`outputs/q2/proof/SAT_EVIDENCE_INDEX.md`。
- 求解/核验脚本：`scripts/solve_q2_cp_sat.py`、`scripts/prove_q2_thresholds.py`、`scripts/validate_q2.py`。

### 7.5 Q2 的边界与版本同步提醒

最新 `outputs/q2/` 证据已经把 `S10=775` 闭合；但当前 `paper/rebuild/main.tex` 摘要、`sections/q2.tex` 的“最优性边界”、`sections/model_assumptions.tex`/`symbols.tex` 和附录仍有“`S10` 只是可行上界、尚未证明”的旧文字。这是**论文同步问题，不是新的模型结论**。接手者应先决定是否采用最新完整证明；若采用，统一更新摘要、问题分析、Q2 正文、符号表、模型检验和附录，并重新编译 PDF。不能让同一版论文同时出现两种状态。

## 8. 问题三：固定 Q2 后的最大新增 C 类装备

### 8.1 固定接口

Q3 只读取已验证的 Q2 `result2.xlsx`：144 个活动计划、15,816 个已占用资源格。Q3 不重新移动或撤销 Q2 计划，也不把新增容量反向写回 Q2。

### 8.2 候选生成

C 类模板为：频段宽 3、单次时长 2、间隔 8、使用 12 次，相邻起点步长 10；每个完整候选占用 `3×2×12=72` 个资源格。起点范围为 `f0=0,...,97`、`t0=0,...,531`，共 `98×532=52,136` 个完整候选；与冻结 Q2 背景不冲突的候选为 2,334 个。

### 8.3 模型、结果与验证

建立 0—1 集合装填：最大化 `Σ_p y_p`，对每个资源格 `c` 约束 `Σ_(p:c∈K_p) y_p ≤ 1-O_c`。HiGHS 资源格模型得到 141，独立候选两两冲突模型也得到 141；加入 `Σ_p y_p≥142` 后不可行。因此：

> **在当前具体 Q2 方案、`[0,643)×[0,100)` 资源域和给定 C 类模板下，最大新增数量为 141 台。**

新增方案占用 10,152 个资源格；与 Q2 合并后共有 285 个活动计划、25,968 个不同资源格。Q2—Q3、Q3 内部及边界检查全部 PASS。

### 8.4 Q3 证据入口与边界

- 输入接口：`outputs/q3/q2_input_from_result2.json`。
- 结果与审计：`outputs/q3/results.json`、`outputs/q3/q3_optimality_audit.json`、`outputs/q3/q3_optimization_audit.md`。
- 独立验证：`outputs/q3/validation.json`、`outputs/q3/result3.xlsx`。
- 求解/核验脚本：`scripts/solve_q3.py`、`scripts/verify_q3_optimality.py`、`scripts/validate_q3.py`。
- 141 不是任意 Q2 背景的普适最大值；改变 Q2 具体布局、时间域或 C 类模板必须重算。

## 9. 问题四：允许 C 类改变间隔后的再优化

### 9.1 输入与动作

Q4 从 Q1 的 150 条原始计划独立开始，不读取 Q2 结果，不混入 Q3 新增计划。保留 Q2 的 keep/frequency-shift/time-shift/revoke 框架，并额外允许 C 类间隔 `g'∈{0,...,18}`，即 `δg∈{-8,...,-1,1,...,10}`；每个动作都重新展开全部重复事件，并在 `[0,643)×[0,100)` 内检查。

### 9.2 最小撤销层（PROVED）

- 合法动作：6,103 个，其中活动候选 5,953 个。
- 按同一计划的外部冲突集合进行安全支配消元：5,953 → 5,533 个；420 个被消去动作均有同计划、冲突集合为其子集的保留动作，替换核验 PASS。
- `R≤3`：有可行见证，独立连续/离散/重建验证 PASS。
- `R≤2`：按 `(R_A,R_B,R_C)` 的六种分拆 `(0,0,2),(0,1,1),(0,2,0),(1,0,1),(1,1,0),(2,0,0)` 建立 SAT 分支，六支均 `UNSAT/PROVED_INFEASIBLE`。
- 少于 2 台撤销可以补足到恰好 2 台而不制造新冲突，所以六分支覆盖了 `R≤2`。

结论：

> **在当前有限整数动作集合、离散时频资源格和 `H=643` 基准域下，问题四最小撤销数为 `R_Q4^*=3`。**

### 9.3 Q4 当前条件候选（不是完整次级最优）

用于当前 `result4.xlsx` 的条件链固定 `R=3,R_A=0,R_B=1`，给出 142 个调整、末级指标 `S10^(4)=943`，类别构成为 A `0/20/0`、B `0/39/1`、C `5/83/2`（保留/调整/撤销），撤销 `B029、C035、C075`。该工作簿通过独立回读：147 个活动计划、16,356 个不同资源格、最大占用 1、无连续/离散冲突、无越界。

但是，新的 SAT 可行见证已经得到 `M=140` 和 `M=139` 的方案（文件 `outputs/q4/proof_R3_RA0_RB1_M140_witness.json`、`...M139_witness.json`），说明 142 不能继续被称为该固定前缀下的最优调整数。`R_B=1`、真正的 `M` 最优值、`M_A/M_B` 和 `S10^(4)` 仍未全部闭合。因此 Q4 论文只能把 142/943 写成条件可行候选或历史基线。

### 9.4 Q4 敏感性与证据入口

| H | 合法动作数 | 资源格约束数 | 当前证据 |
|---:|---:|---:|---|
| 638 | 6,040 | 53,186 | `R≤3` 可行且独立验证 PASS；未证明该边界的最小值 |
| 643 | 6,103 | 53,679 | `R=3` 最小撤销层已闭合 |
| 648 | 6,116 | 53,767 | `R≤3` 可行且独立验证 PASS；未证明该边界的最小值 |

主要文件：`outputs/q4/summary.md`、`outputs/q4/r2_global_proof_status.md`、`outputs/q4/proof_R_le_3_validation_final.json`、`outputs/q4/proof_R_le_2_global_coverage_validation.json`、`outputs/q4/proof_R_le_2_dominance_validation.json`、`outputs/q4/q4_secondary_proof_matrix.md`、`outputs/q4/result4.xlsx`。脚本：`scripts/solve_q4_cp_sat.py`、`scripts/verify_q4_dominance_certificate.py`、`scripts/validate_q4.py`。

## 10. Q2—Q3 联合敏感性（S-Q23-1）

该实验研究“改变 Q2 背景会怎样影响 Q3 容量”，不替代正式的 Q2→Q3 顺序答案。固定总撤销数扫描 `R∈{6,8,10,12,15,19}` 时，得到的 Q3 最大新增数为：

| R | 6 | 8 | 10 | 12 | 15 | 19 |
|---:|---:|---:|---:|---:|---:|---:|
| N3 | 141 | 139 | 127 | 132 | 108 | 106 |
| 状态 | FEASIBLE_INCUMBENT | FEASIBLE_INCUMBENT | FEASIBLE_INCUMBENT | FEASIBLE_INCUMBENT | FEASIBLE_INCUMBENT | FEASIBLE_INCUMBENT |

这些数值说明完整 Q2 占用布局比“只看撤销数”更重要，但各扫描背景没有全部闭合完整字典序最优；联合 CP-SAT 找到的 `N3≥162` 或 `N3≥187` 也只是可行下界，不能写成联合全局最优。证据：`outputs/q2_q3_pareto/summary.md`、`outputs/q2_q3_pareto/pareto_results.json`、`docs/DECISIONS.md` 的 `DEC-20260912-001`。是否把它放进正文，应由队友根据篇幅和叙事需要决定；最稳妥位置是“模型检验/敏感性分析”或附录。

## 11. 证据台账（压缩版）

| ID | 当前结论 | 状态 | 主要证据 | 适用范围 |
|---|---|---|---|---|
| DP-1 | 150 条唯一计划，字段完整，A/B/C=20/40/90 | PROVED | `work/intake/DATA_AUDIT.md`、`FILE_MANIFEST.json` | 原始附件 |
| DP-2 | 事件步长 `l+g`，半开区间，基准域 `[0,643)×[0,100)` | PROVED | `outputs/q1/validation.json`、`outputs/q1/summary.md` | 全部问题；边界改变需重算 |
| DP-3 | Q1→Q2→Q3 单向；Q4 从 Q1 原始输入独立开始 | ACCEPTED INTERFACE | `docs/DECISIONS.md`、各问 summary | 当前论文建模链 |
| Q1-1 | 1,300 事件，11,175 计划对 | PROVED | `outputs/q1/results.json` | 原始 150 条计划 |
| Q1-2 | 297 冲突装备对，431 事件重叠 | PROVED | `outputs/q1/results.json`、`validation.json` | 计划层/事件层分开统计 |
| Q1-3 | 148 个参与冲突，最大连通分量 148 | DESCRIPTIVE | `outputs/q1/results.json`、plot data | 结构描述，不直接定动作 |
| Q1-4 | B—C 181 对，归一化冲突率 5.03% | PROVED | `outputs/q1/plot_data/`、`results.json` | 冲突结构定位 |
| Q1-5 | Q1 冲突清单作为 Q2 硬约束输入 | ACCEPTED INTERFACE | `outputs/q1/summary.md`、`scripts/solve_q2_cp_sat.py` | 调整后必须重新展开 |
| Q2-1 | 4,582 动作，52,939 资源格团约束 | PROVED MODEL SCALE | `outputs/q2/summary.md`、`results.json` | `H=643`、动作规则固定 |
| Q2-2 | `R*=6` | PROVED | `revocation_bound.json`、validation | 基准域；H 敏感性另列 |
| Q2-3 | 前缀 `(6,0,4,126,16,34)` | PROVED | `q2_proof_matrix.csv`、SAT JSON | 条件字典序 |
| Q2-4 | A/B/C `4/16/0`,`2/34/4`,`12/76/2` | PROVED FEASIBLE | `six_revocation_candidate.json`、validation | 144 活动计划 |
| Q2-5 | H=638/643/648 均得到最少撤销 6 | SENSITIVITY | `outputs/q2/boundary_sensitivity.json` | 仅主撤销层 |
| Q2-6 | `S10=775` | PROVED IN LATEST EVIDENCE; PAPER STALE | `sat_shift_le_774_full.json` | 固定完整前缀、有限动作集 |
| Q3-1 | 固定 Q2 144 个活动计划 | CONDITIONAL INTERFACE | `q2_input_from_result2.json` | Q2 改变即需重算 |
| Q3-2 | 52,136 起点→2,334 可行候选 | PROVED ENUMERATION | `results.json`、audit | C 模板与域固定 |
| Q3-3 | 最大新增 141 | CONDITIONAL PROVED | `results.json`、HiGHS audit | 固定 Q2/域/模板 |
| Q3-4 | 141 可行且 142 不可行 | PROVED CROSS-ENCODING | `q3_optimality_audit.json` | 当前冻结背景 |
| Q3-5 | 合并 285 计划、25,968 格 | VERIFIED | `validation.json` | 当前 Q2+Q3 |
| Q4-1 | 6,103 动作，支配消元 5,953→5,533 活动动作 | PROVED REDUCTION | Q4 proof files | Q4 有限动作集 |
| Q4-2 | `R≤3` 可行，`R≤2` 六分支 UNSAT | PROVED | `r2_global_proof_status.md` | `H=643` |
| Q4-3 | `R_Q4*=3` | PROVED MINIMUM LAYER | `proof_R_le_3_validation_final.json` + six UNSAT | 不含次级层 |
| Q4-4 | 142/943 条件候选；M=140/139 新见证 | FEASIBLE / NOT OPTIMAL | Q4 witness JSONs | 次级字典序未闭合 |
| S-Q23-1 | `N3=(141,139,127,132,108,106)` | SENSITIVITY ONLY | `outputs/q2_q3_pareto/` | 不改写顺序主答案 |

## 12. 当前论文结构与排版状态

`paper/rebuild/main.tex` 当前结构如下：

1. 标题与摘要（摘要显式列出模型、算法和关键数字）；
2. 问题重述（问题背景、问题提出、Q1—Q4）；
3. 问题分析（不增加二级标题，按 Q1—Q4 分段）；
4. 一级标题“模型假设与符号说明”，其中 3 条核心假设 + 两列表格“符号—含义”；
5. 独立一级标题“数据预处理”（DP-1—DP-3）；
6. 模型建立与求解（Q1—Q4）；
7. 模型检验、模型优缺点评价、AI 工具使用声明、参考文献、附录。

当前已实现的用户版式要求：

- 标题单行：`时频资源离散化与字典序整数优化的装备用频冲突检测与消解`；
- 模型假设与符号说明合并为一个一级标题；
- 假设压缩为 3 条，不堆叠无关假设；
- 符号表只保留“符号—含义”两列，一个符号一行；
- 数据预处理独立为一级标题；
- 图表由 LaTeX 自动编号，避免手工把编号放在左上角；
- 当前编译稿使用统一 B 科研配色；流程图暂从正文撤出，用户将自行重画回字型流程图；
- 图 3、图 6 的核心证据由三线表承载，避免重复制图；
- 旧 `paper/tex/` 保留，不覆盖。

### 12.1 论文当前需要同步的地方（优先级 P1）

1. **Q2 的 `S10` 状态冲突**：最新 `outputs/q2` 证据为已证明 `775`，而 `paper/rebuild/main.tex` 摘要、`sections/q2.tex`、`sections/problem_analysis.tex`、符号表和附录仍写“只是一组可行上界”。接手者必须统一成一个版本；推荐采用最新证据并重写相关句子。
2. **Q4 的问题重述文字**：`sections/problem_restatement.tex` 仍有“第四问本阶段暂不运行”的旧句，但当前正文已经包含 Q4 最小撤销层。若保留 Q4 正文，应改为当前 Q4 范围和证据边界。
3. **Q4 次级结果不可升级**：即使更新 Q2 的 `S10`，也不能把 Q4 的 142、943 或 `R_B=1` 写成完整字典序最优。
4. **摘要、符号表、Q2 正文、模型检验、附录必须同版**：禁止只改摘要而让正文保留相反状态。

## 13. 图表与科研配色交接

当前图表原则是“图服务于证据，不重复三线表”：

- Q1：冲突矩阵/结构图可展示冲突集中位置，精确数字由类别统计表承担。
- Q2：类别构成图展示 A/B/C 的保留—调整—撤销结构；证明层级优先用三线表，不再额外堆证明阶梯图。
- Q3：候选起点与最终选中起点布局图展示几何结构；141/142 的精确最大性由表格和审计文件承担。
- Q4：最小撤销层用证据表；条件候选不应画成“最终最优”宣传图。
- 流程图：用户自行重画回字型；现有旧流程图只作结构参考，不能直接当终稿。
- 所有正式图应保留 PDF、SVG 和 PNG/灰度 QA；不要从 PNG 反读数字。

## 14. 已失败、已废弃或必须避免的路线

1. **重复步长 `kg`**：错误地把间隔当作起点步长；已由 A001 题面示例否定，统一改为 `k(l+g)`。
2. **旧 Q2 的 19 次撤销**：是限时可行 incumbent，旧 Q3=203 依赖该背景；现在被六撤销证据 supersede。
3. **旧 Q3 的 203 台**：不能与当前六撤销 `result2.xlsx` 配套，当前固定背景结论是 141。
4. **H=638 的旧越界结果**：曾允许完整事件超过边界，已修正候选筛选；旧结果不能引用。
5. **只检查首次事件**：会漏掉重复事件冲突；Q2/Q3/Q4 都必须完整展开。
6. **用“剩余面积/72”代替 Q3 集合装填**：不能保证完整模板的每个重复事件可行。
7. **把限时可行解当全局最优**：Q2 早期 CP-SAT/MILP 运行、Q4 早期超时/异常/未找到解均不构成证明。
8. **Q2—Q3 联合扫描反写正式答案**：联合 Pareto 目前是敏感性诊断；不得用 `N3≥162/187` 替代固定 Q2 后的 141。
9. **Q4 固定撤销组合的定向子问题**：只能作为诊断；`R≤2` 的全局结论必须依赖六个类别配额分支覆盖。
10. **旧图和旧版排版**：`paper/tex/`、旧流程图、旧多重图例和旧图号不作为新终稿资产。

## 15. 复现与检查命令

以下命令用于队友在副本中复核；不要在未备份时直接运行会覆盖 `outputs/` 的求解脚本。

### 15.1 编译当前论文

```powershell
Set-Location C:\Users\ysw\Desktop\CUMCM2026\paper\rebuild
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

### 15.2 生成当前支撑包

```powershell
Set-Location C:\Users\ysw\Desktop\CUMCM2026
pwsh -NoProfile -File scripts/build_submission_support_package.ps1
```

### 15.3 各问核验入口

```powershell
python scripts/validate_q1.py
python scripts/validate_q2.py
python scripts/verify_q3_optimality.py
python scripts/validate_q3.py
python scripts/verify_q4_dominance_certificate.py
python scripts/validate_q4.py
```

Q1/Q2/Q3/Q4 主求解脚本分别为 `solve_q1.py`、`solve_q2_cp_sat.py`、`solve_q3.py`、`solve_q4_cp_sat.py`。重新求解前必须确认附件路径、依赖版本和输出目录，最好使用副本或临时输出目录；不要用 `git reset --hard`、`git clean -fd`、覆盖 `data/raw/` 或删除旧稿。

## 16. 接手后的精确工作清单

### 必做（进入下一版 PDF 前）

1. 阅读本文件、`WINDOW_PACKET.md`、`docs/DECISIONS.md` 和四个 `outputs/q*/summary.md`。
2. 用 `work/intake/FILE_MANIFEST.json` 核对题面和附件哈希。
3. 决定是否采用最新 Q2 `S10=775` 全证明；推荐采用，并同步摘要、Q2 正文、符号表、模型检验和附录。
4. 把问题重述中“Q4 暂不运行”的旧句改成 Q4 当前范围，或明确从论文删除 Q4；不能两者同时保留。
5. 重新编译 20 页 PDF，检查摘要、符号表、Q2 证明表、Q3 141、Q4 `R*=3` 和 AI 声明。
6. 更新支撑包，使 PDF、源稿、结果文件和证据状态来自同一版本。

### 可选增强

1. 继续闭合 Q4 `R=3` 内的 `R_A→R_B→M→M_A→M_B→S10^(4)`；在闭合前保留 142/943 为条件候选。
2. 决定是否把 S-Q23-1 放进“模型检验—敏感性分析”或附录。
3. 按用户回字型流程图重新导出 SVG，并让 LaTeX 自动编号。
4. 进行一次评委视角检查：题意匹配、目标顺序、单位、边界、结果—表格—正文一致性、AI 使用声明和官方提交要求。

## 17. 允许做与不允许做的事情

### 默认允许

- 读取并分析本包和仓库中的数据、脚本、结果、论文源文件；
- 在 `paper/rebuild/`、`outputs/` 的派生文件和说明文件上做可追溯修改；
- 重新生成 PDF、图表和支撑包；
- 在副本中重跑核验、补充 Q4 次级证明或敏感性分析。

### 必须先确认/不得自动做

- 不覆盖或删除 `data/raw/`、`paper/tex/`、用户提供的原始附件和旧正式结果；
- 不把条件候选、敏感性 incumbent 或限时可行解改写成全局最优；
- 不改变 Q2→Q3 单向接口，不把 Q3 容量反向写回 Q2；
- 不把 Q4 新增间隔动作混入 Q2/Q3；
- 不进行 destructive Git 操作，不自动 merge、rebase、push 或 cherry-pick；
- 不把网页搜索到的论文或历史范文当作当前题目的数据、阈值或结论证据。

## 18. 文件索引

### 本 ZIP 内

- `README.md`：解压后阅读顺序和包内容。
- `TEAM_PAPER_HANDOFF_20260912.md`：本主交接台账。
- `WINDOW_PACKET.md`：按交接技能生成的动态工作区状态包。
- `WINDOW_PACKET_attachments/`：当前 PDF、结果 JSON/CSV、关键证明和摘要附件。
- `paper_source/`：当前 `paper/rebuild` 的 LaTeX 源文件和结构说明（不含庞大 build 缓存）。
- `selected_scripts/`：Q1—Q4 的求解/核验脚本副本。
- `source_attachments/`：题面、原始附件 1、输出模板和边界对照文件。
- `current_artifacts/`：当前 20 页 PDF和现有 Q4 支撑包。

### 仓库内权威入口

- 状态板：`docs/CURRENT_PROGRESS.md`
- 长期决定：`docs/DECISIONS.md`
- Q1：`outputs/q1/summary.md`
- Q2：`outputs/q2/summary.md`、`outputs/q2/q2_proof_matrix.csv`
- Q3：`outputs/q3/summary.md`
- Q4：`outputs/q4/summary.md`、`outputs/q4/r2_global_proof_status.md`
- Q1—Q3 旧台账：`work/evidence/Q123_NEW_CONCLUSION_EVIDENCE.md`（时间较早、排除 Q4；仅作历史追溯，不能覆盖本包最新 Q2/Q4 状态）
- 论文源稿：`paper/rebuild/`
- 旧稿：`paper/tex/`（保留但不引用）

## 19. 给下一位 Codex 的最短提示词

```text
你接手的是 CUMCM2026 D 题论文重建项目。先读 TEAM_PAPER_HANDOFF_20260912.md 和 WINDOW_PACKET.md。
不要使用 paper/tex 旧稿作为证据，不要覆盖 data/raw。当前主链是：150 条计划 -> 1300 个重复事件 -> Q1 297 冲突对 -> Q2 六撤销条件字典序 -> 固定 Q2 后 Q3 最大新增 141 -> Q4 独立起算并证明最小撤销层 R*=3。
最新 outputs/q2 证据把 S10=775 也闭合，但 paper/rebuild 文字尚未完全同步；先做一致性修复，再编译 PDF。Q3 的 141 只适用于批准的具体 Q2 方案；Q4 的 142/943 只是条件候选，不能写成次级最优。所有结论都要保留证据路径、适用范围和验证边界。
```
