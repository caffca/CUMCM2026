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
- Consequences: **已废止**：该决策对应旧 19 撤销背景下的 Q3=203；当前正式结论为六撤销背景下 Q3=141，见 `outputs/q3/summary.md` 和 `DEC-20260911-006`。若 Q2 方案或 H 场景变化，仍必须重建占用矩阵并重新求解 Q3。Q3 结果不参与 Q2 目标选择。
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
