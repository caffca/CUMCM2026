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

## Accepted decisions

### DEC-20260911-001 — Q2/Q4 多目标采用“主词典序 + 政策/Pareto 对照”

- Status: accepted
- Date: 2026-09-11
- Context: 题面要求少撤销、少调整、按 A/B/C 优先级尽量保持原计划并减少位移，但没有规定目标之间的数值交换权重。
- Decision: 正式主结果预先采用题面顺序的逐层词典序：总撤销数、总调整计划数、A/B 类保持、归一化总位移和最大位移。另求优先级优先情景与有界 $\varepsilon$-约束/Pareto 情景，量化加强保护 A/B 的代价；替代情景不得用于事后更换主目标。
- Alternatives considered: 任意加权和；让类别优先级压倒总体撤销/调整数量；只求一个方案而不做目标口径敏感性。
- Evidence / rationale: 逐层固定前序最优值无需虚构交换权重，可精确复现题面文字顺序；情景/Pareto 对照能揭示高优先级保护与总体调整成本的真实冲突，并避免离散加权和遗漏非支撑 Pareto 解。
- Consequences: Q2、Q4 必须使用相同可行域定义和目标协议，统一报告分类撤销/调整/保持数、原始与归一化位移、最大位移、零冲突复核和求解状态。只有前层目标固定后，后层偏好才参与决策。
- Affected files: `D题/D题_建模分析全过程与决策记录.md`, `docs/CURRENT_PROGRESS.md`, 后续 Q2/Q4 求解代码、结果表与论文正文。
- Supersedes: none
- Superseded by: none

### DEC-20260911-002 — 四问共享统一周期冲突检测器

- Status: accepted
- Date: 2026-09-11
- Context: Q1 直接检测冲突，Q2/Q4 需要生成候选状态兼容边并复验排程，Q3 需要过滤新增候选；若分别实现判交逻辑，半开端点、周期展开和计划对去重容易产生口径漂移。
- Decision: 建立唯一的“状态调整—周期展开—二维半开区间判交—计划对去重”实现，供 Q1–Q4 共同调用；检测器返回冲突见证窗，最终排程另由统一验证入口复核。先冻结接口、测试和验收门槛，再开始编码。
- Alternatives considered: 每问独立实现检测器；直接使用时频栅格作为唯一检测方法；先写求解器、最后再补验证器。
- Evidence / rationale: 当前仅有 1,300 个展开窗，精确枚举足以作为透明基线；统一实现能使候选建模与事后验证保持同一冲突定义，而缩小栅格法可作为独立交叉检查。
- Consequences: Q1 输出、Q2/Q4 冲突边、Q3 候选过滤和最终零冲突结论均依赖同一核心接口；检测器变更必须重跑端点、周期、C083、全量展开、去重和缩小栅格对照测试。计划路径与顺序见 `D题/D题_建模分析全过程与决策记录.md` 第 5.1 节。
- Affected files: 后续 `src/d_problem/`, `scripts/solve_d_q1.py`, `tests/d_problem/`, Q1–Q4 求解与输出。
- Supersedes: none
- Superseded by: none

### DEC-20260911-003 — Q2 状态扩展主模型与资源单元团编码

- Status: accepted
- Date: 2026-09-11
- Context: Q2 允许每个计划在保留、仅调频、仅调时和撤销中选择一种状态；状态改变后冲突关系也随之改变。需要在结构准确性、可审计最优性和实现规模之间作出路线选择。
- Decision: 冻结 Q2 的数学骨架为“有限候选状态 + 状态级兼容约束 + T/P/E 逐层目标”，不直接用原始计划冲突图代替状态图。当前数据得到 4,582 个合法状态和 270,626 条状态冲突边；全量边集作为可审计参考，正式 CP-SAT 使用按资源单元建立的 at-most-one 团约束（在整数半开区间下与全边集等价），并加入不改变可行域的隐含强传播约束。懒惰冲突切割保留为可扩展对照，只有在每轮主问题均 OPTIMAL 且分离器无漏检时才能承担严格证明。直接二维 NoOverlap2D 与 GA/PSO/退火不作为当前主模型。
- Alternatives considered: 只对原始冲突图删点；直接在连续平移变量上写二维大 $M$ 不相交约束；全量预生成兼容图；精确懒惰切割；黑盒元启发式直接给出主结论。
- Evidence / rationale: 候选数和状态边数来自独立整数位集探测脚本，1,000 对随机候选状态与统一逐窗检测器复核一致；资源单元团对全状态边逐条覆盖测试通过，Q1--Q2 回归测试 14/14 通过；3 组真实四计划子集的全组合穷举与 edge/cell/lazy 三种 CP-SAT 目标向量完全一致。全模型已给出 C<=5 INFEASIBLE 与 C=6 零冲突可行证书；T 后续层仍受搜索 gap 限制，P 方案八层已证。矩形编码预处理成本过高，懒惰短跑未满足逐轮最优条件，因此不把二者的潜在速度写成事实。
- Consequences: Q2 报告必须同时给出状态数、审计边数、团数、求解状态、上下界/gap 和统一零冲突复验。C*=6 可严格报告；T 的 M=120 及后续层若未达到 bound=objective，只能报告 incumbent。P/E 仅作为预先声明的政策对照。三维 $(t,f,k)$ 只作占用审计/示意，不替代状态变量或二维零冲突验证。
- Affected files: `D题/D题_建模分析全过程与决策记录.md`, `docs/CURRENT_PROGRESS.md`, 后续 `src/d_problem/` 候选生成/目标/求解模块、`outputs/q2/` 结果与论文 Q2。
- Supersedes: none
- Superseded by: none

### DEC-20260912-001 — 完整方法矩阵与同口径对照

- Status: accepted
- Date: 2026-09-12
- Context: 本地 T/P/E 与队友 B 的差异主要来自多目标政策协议；若只保留一套结果，无法区分“目标取舍”与“模型/实现错误”。
- Decision: 在最终选定主线前，完整运行 T、P、E 以及队友 B 所代表的优先保护协议；所有方案固定同一原始数据、半开区间、完整周期展开、单参数动作、Q2 平移边界、时间域假设和统一冲突验证器。每套 Q2 排程分别作为独立 Q3 输入；Q4 从原始 Q1 冲突重新求解，不把任何 Q2 结果直接移植为 Q4。论文同时报告完整目标向量、类别受影响数、求解上下界/状态、运行成本和零冲突复核，并把不同协议解释为政策/Pareto 对照，而不是未经声明的同一目标下竞争。
- Alternatives considered: 只运行主线；用不同数据或不同验证器分别运行各方案；把 T/P/E/B 的单项最优数字拼接成一个“混合最优解”；只比较总调整数而忽略撤销和类别保护。
- Evidence / rationale: 当前已观察到相同总撤销数下 T 与 B 的调整数、A/B/C 受影响数不同，且本地 T 的后续层尚未全局证明。统一方法矩阵可揭示代价—保护权衡，并使论文对目标顺序的敏感性有可追溯证据；但只有在每套方案完成独立可行性和必要最优性验证后，才能使用“最优”措辞。
- Consequences: 建立 Q2/Q3/Q4 的方案运行矩阵和统一结果表；未达到 LB=UB 或缺少可复核证书的方案标为 incumbent/conditional，不得升级为全局最优。Q3 的新增数量必须带上对应 Q2 标签与 (H)、C 模板；不同 Q2 背景不得横向混接。
- Affected files: `D题/Q2_解题与验证阶段报告.md`, `D题/本地与队友D分支对比审计_待核验.md`, `docs/CURRENT_PROGRESS.md`, 后续 `outputs/q2/`, `outputs/q3/`, `outputs/q4/` 和论文正文。
- Supersedes: none
- Superseded by: none

### DEC-20260912-002 — T 方案优先闭环，队友 B 暂不完整复跑

- Status: accepted
- Date: 2026-09-12
- Context: 完整运行 T/P/E/B 的对照矩阵有助于论文展示，但当前 T 方案的总调整层尚未闭合，是影响主线正确性和 Q3 接口的首要问题。
- Decision: 先集中解决本地 T 方案：在已证明的 $R=6$ 前缀上闭合或明确标注 $M$ 及后续 A/B 保护、位移层，完成统一零冲突验证和 Q2 正式结果；随后仅基于冻结的 T 排程运行 Q3，并从原始 Q1 冲突推进 Q4。队友 B 不再完整复跑，只保留已完成的只读分支审计结果作为外部交叉证据/可选敏感性对照，不作为 T 的 Q3 输入或主线替代。
- Alternatives considered: 先完整运行所有政策方案；直接采用队友 B 的 Q2/Q3；在 T 的 $M$ 未闭合前推进 Q3。
- Evidence / rationale: Q3 的新增数量依赖具体 Q2 排程；混用不同 Q2 背景会破坏跨问接口。当前 T 已有 $R=6$ 严格前缀，但 $M=120$ 仍是 incumbent，因此先闭合 T 能最大程度降低主线风险和无效计算。
- Consequences: 后续计算资源优先用于 T 的目标层、证明和结果表；所有 T 结果保持同一候选状态、资源团约束和统一验证器。B 的证据缺口不阻塞 T，但在论文中不得将 B 的条件结果写成 T 的结果。
- Affected files: `docs/CURRENT_PROGRESS.md`, `D题/Q2_解题与验证阶段报告.md`, `D题/本地与队友D分支对比审计_待核验.md`, 后续 `outputs/q2/`, `outputs/q3/`, `outputs/q4/` 和论文正文。
- Supersedes: DEC-20260912-001（仅就“完整运行队友 B”部分）
- Superseded by: none

### DEC-20260912-003 — T 方案改用结构化分解搜索，状态模型保留为审计基线

- Status: accepted
- Date: 2026-09-12
- Context: 全状态候选模型在 $C=6$ 面上可稳定找到 $M=120$，但对 $M\le119$ 的 CP-SAT、SAT 和有限域 CSP 阈值试验均在有界时间内为 `UNKNOWN`。单纯增加全局搜索时间不能区分模型缺陷与组合搜索难度，也无法满足比赛期间的结果交付风险。
- Decision: 暂停把“全状态模型继续加时”作为 T 的唯一主线，采用“动作层—几何层”结构化搜索：先决定保留/频移/时移/撤销标签及撤销身份，再在给定标签下求解频移/时移的几何可行重排；用大邻域局部精确修复寻找 incumbent，用统一检测器进行全局复验。原有限状态模型、资源单元团和状态冲突边仍保留为可行域审计基线和最终阈值验证器。
- Alternatives considered: 继续延长全状态 CP-SAT；直接采用 NoOverlap2D；只按原始 Q1 冲突图做删点；使用 GA/PSO 等黑盒启发式替代可行性检查。
- Evidence / rationale: $H=648$ 只新增 7 个候选状态，未改善短时 $M$；LNS/CSP 能独立复现 $C=6,M=120$ 零冲突排程且 LNS 将位移降至约 805--812，但没有发现 $M=119$；直接 NoOverlap2D 全实例限时未返回可用结果。这些结果支持“结构化搜索值得继续”，但不支持把任一 incumbent 写成全局最优。
- Consequences: Q2 论文必须区分严格的 $C^*=6$、T 的可行 incumbent 及未闭合的 $M$；后续 Q3 只能明确标注其所依赖的 T 排程版本。若动作—几何分解仍不能闭合 $M$，保留上下界和求解状态，不以 P、LNS 或队友 B 结果拼接替代 T。
- Affected files: `D题/Q2_解题与验证阶段报告.md`, `docs/CURRENT_PROGRESS.md`, `tmp/lns_q2.py`, `tmp/csp_q2_search.py`, `tmp/nooverlap2d_q2.py`, 后续 `outputs/q2/` 与论文正文。
- Supersedes: DEC-20260912-002（仅就 T 的求解路线）
- Superseded by: none

### DEC-20260912-004 — 设备级状态为语义主模型，禁止 Q1 边松弛替代全局约束

- Status: accepted
- Date: 2026-09-12
- Context: 用户指出每台设备的频段、首次时间、周期和次数均为确定参数，担心全状态 one-hot 模型掩盖设备结构；同时只约束 Q1 原始冲突边会得到异常低调整数。
- Decision: 将“一个设备选择一个完整状态”的有限域 CSP 作为语义主模型；保留候选状态/资源格团模型作为审计基线，使用共享平移 `NoOverlap2D` 和 SCIP cell-clique MILP 做独立交叉核验。所有模型必须约束平移后**全部最终计划对**无冲突，不能只约束 Q1 原始 297 对。
- Alternatives considered: 只按 Q1 冲突图删点；把每次重复窗当作独立设备变量；仅依赖直接 `NoOverlap2D`；仅依赖单一求解器的最优状态。
- Evidence / rationale: 设备级 CSP、紧凑几何模型和 SCIP 均复现 (C=6,M=120) 的零冲突可行排程；只约束 Q1 边虽得到 (M=82)，但最终统一检测发现 113 个新冲突。该反例证明原始边松弛不符合 Q2 的全局消解语义。
- Consequences: 论文需把“设备状态域、全局兼容关系、周期同步”作为模型核心，另报不同求解器的上下界和复验；(M=120) 仍只称可行 incumbent，除非后续取得 (M\le119) 的不可行证书。探索性几何脚本中的频宽必须使用 (f_{end}-f_{start})，不得误用时间持续时长。
- Affected files: `D题/Q2_替代模型探索与语义审计.md`, `D题/Q2_解题与验证阶段报告.md`, `docs/CURRENT_PROGRESS.md`, `tmp/table_csp_q2.py`, `tmp/nooverlap2d_compact.py`, `tmp/disjunctive_shift_q2.py`, `tmp/milp_q2_scip.py`, `tmp/q2_original_edges_only.py`。
- Supersedes: DEC-20260912-003（仅就“动作层—几何层作为唯一下一主线”的表述）
- Superseded by: none

### DEC-20260912-005 — 冻结 Q2-T-incumbent-v1 并条件启动 Q3

- Status: accepted
- Date: 2026-09-12
- Context: Q2 的撤销层已闭合为 $C^*=6$，但调整层 $M$ 仍只有 $M=120$ 的零冲突 incumbent；Q3 的输入必须是一个明确、可复核且不可随探索运行漂移的 Q2 排程。
- Decision: 将 `outputs/q2/Q2-T-incumbent-v1.json` 冻结为 Q3 输入快照。固定时频域 `[0,100)\times[0,643)`、整数半开区间和 C 模板 `(频宽,持续,间隔,次数)=(3,2,8,12)`；Q3 对所有合法初始位置生成候选，先用统一检测器过滤 Q2 冲突，再用时频资源单元 at-most-one 团约束最大化新增计划数。
- Alternatives considered: 等待 Q2 的 $M\le119$ 证明后再开始 Q3；直接沿用队友 B 的 Q3；只检查 Q1 原始冲突边；使用未固定的“当前最新”Q2 文件作为输入。
- Evidence / rationale: Q2 快照包含 150 项完整状态并通过统一复验（1277 个使用窗、冲突数 0）。Q3 实算生成 52,136 个原始候选、过滤后 2,452 个候选，CP-SAT 资源单元模型返回 `OPTIMAL=138` 且 best bound=138；将同一候选集改写为 89,989 条逐候选冲突边后仍得到 `OPTIMAL=138`。与 138 个新增状态合并后共 288 项计划、2,933 个使用窗，统一检测器冲突数 0。
- Consequences: Q3 结论“最多 138 台”只对 `Q2-T-incumbent-v1`、`H=643` 和上述 C 模板成立。若后续 Q2 得到不同排程，必须重新运行 Q3；Q2 的 $M\le119$ 有界证明可并行进行，不阻塞本次 Q3 阶段交付。
- Affected files: `scripts/solve_d_q3.py`, `outputs/q2/Q2-T-incumbent-v1.json`, `outputs/q2/Q2-T-incumbent-v1.md`, `outputs/q3/result3.xlsx`, `outputs/q3/solver_report.json`, `outputs/q3/selected_Q2-T-incumbent-v1.json`, `outputs/q3/summary.md`, `docs/CURRENT_PROGRESS.md`。
- Supersedes: none
- Superseded by: none

### DEC-20260912-006 — Q4 从原始 Q1 重求并冻结条件性 incumbent

- Status: accepted
- Date: 2026-09-12
- Context: Q4 允许 C 类改变相邻使用间隔；该新增状态会改变后续所有周期窗口，因而不能把 Q2 的排程行直接当作 Q4 的固定背景，也不能把 Q2 的 `C<=5` 证明自动移植到扩展后的可行域。
- Decision: Q4 以附件 1 原始 150 个计划为输入，复用 Q2 的有限状态、资源单元团和统一周期检测器，仅为 C 类加入满足 `|delta_g|<=10`、`g' >= 0` 且末窗不越过 `H=643` 的 gap 状态。当前正式文件采用 T 目标协议，并将 `C=6,M=115,P_A=14` 的排程标为条件性 incumbent；不宣称 Q4 全局词典序最优。
- Alternatives considered: 固定 Q2 排程后只修 gap；把 Q2 的 `C*=6` 当作 Q4 首层证书；只用原始 Q1 冲突边；用任意加权和替代逐层词典序；在未验证零冲突前直接写 result4。
- Evidence / rationale: Q4 生成 6,103 个状态，其中 1,521 个为 C-only gap 状态；Q2 的 4,582 个状态全部被包含。状态冲突边 444,561 条、资源单元团 53,679 个，1,000 条抽样边与统一检测器一致，且全量跨计划边/团诱导候选对 missing=extra=0。当前排程展开 1,277 个使用窗，冲突数和边界违规均为 0，Excel 变更清单 121/121 行读回一致；`C<=5` 限时 180 s 为 `UNKNOWN`，固定 `C=6,M=115` 后的 `P_A=14` 为 `FEASIBLE` 且下界 3。
- Consequences: `outputs/q4/result4.xlsx`、`selected_T.json` 和 `solver_report.json` 成为当前 Q4 可行性基线；论文必须绑定 `H=643`、T 口径、候选生成规则和求解状态，区分“可行 incumbent”与“严格最优”。后续若取得 `C<=5` 不可行证书、改善 `M` 或更换时间域，必须重跑并更新 Q4 主文件。
- Affected files: `src/d_problem/q4_candidates.py`, `scripts/solve_d_q4.py`, `outputs/q4/`, `D题/Q4_解题与验证阶段报告.md`, `D题/D题_建模分析全过程与决策记录.md`, `docs/CURRENT_PROGRESS.md`。
- Supersedes: none
- Superseded by: none
