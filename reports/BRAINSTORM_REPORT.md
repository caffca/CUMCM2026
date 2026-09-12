# BRAINSTORM REPORT — 2026 CUMCM D 题《时频冲突检测与消解》Competitive Search

search_id：CS-20260911T071520Z-1A9D30（物理目录 runs/competitive/CS-20260911T071520-D2026/）· profile=standard · contract v2 + P1-00/01/03

## 1. 问题卡片

| 问 | 决策对象 | 核心结构 | canonical 评价 |
|---|---|---|---|
| Q1 | 冲突计划对集合 | 频段半开区间交叠 × 周期占用窗（p=g+Δ 周期，F-005）交叠；11175 对全判定 | symdiff vs 基准（minimize，0=完备且无伪） |
| Q2 | 每计划{保持/调频段/调时间/撤销} | 带撤销色部分列表着色 / 全势边 G*(1693) 差分 CSP | 词典序标量 1e12·rev+1e8·adj+1e4·ploss+mag（minimize） |
| Q3 | 新增 C 计划放置集 | 空闲可达集上的 3带×12oct×相位 集包装（候选完备枚举） | 加装数 count（maximize）+ 上下界会合 |
| Q4 | Q2 动作集扩 C 类 dg（±10，g'≥1，末窗≤643） | 重定时差分（∂窗k/∂g=k-1）+ 扩域差分 CSP | 同 Q2 标量 |

口径冻结：ADJUDICATION.json R1–R8（视界 643、distinct 占用、平移不越盒、词典序四级、Q3 主口径、Q4 间隔规则、半开冲突语义、撤销释放资源）。

## 2. 路线总览（48 条完整路线 → 12 条 Top-K 侦察）

5 个独立生成 child：structure(CH-01,12) / exact(CH-02,12) / continuous(CH-03,6) / alternative(CH-04,9) / bound(CH-05,9)。
合并校验：字段完整、fingerprint 两两不同、无禁用结论词；族覆盖与结构机会逐项处置见 IDEA_CANDIDATES.coverage_policy / structural_checks。
被证伪后排除的结构：按频段/时间轴硬分解、逐边匹配撤销下界（恒 0）、跨类 gcd 闭式、DP 精确化、网络流、MINLP。

## 3. 侦察与评审摘要（每候选一次真实原型运行，冻结 evaluator 复算）

**Q1（Top-K=3）**：R21 逐对区间算术（0.017s）、R52 类内同余闭式+跨类回退（0.28s，闭式在 4975 同组对与枚举 0 反例）、R41 位图/倒排+1000 轮植入压力测试（12.9s，注入/删除召回各 1.000）。三份 solution **逐字节同 SHA**（297 对，AB21/AC66/BC181/BB10/CC19）。评审：3×retain。

**Q2（Top-K=3）**：R51 全势边子句 CP-SAT+撤销阶梯（547s，[6,121,1996,663]，Σr≤0 INFEASIBLE 证书、界 [2,6] 开放）；R32 连续罚场引导（391s，[6,123,2205,762]，连续层贡献量化 297→175，修复退化为全量重解的**负结果证据**）；R41 GRASP 3-seed（中位 [19,96,1853,491]，撤销极差 9——作启发式对照）。评审：R51/R41 retain（附生产复现要求），R32 revise（处置见决策日志 D-R32-REVISE）。独立复核亮点：CH-REV-A 全量重算 G* 1693 边/270626 组合零差异，堵住 CH-05 警示#2a 的"漏边假 OPTIMAL"风险。

**Q3（Top-K=3，基座=R51 冻结解）**：R11 set-packing CP-SAT 双模型 OPTIMAL=bound=139 + HiGHS LP=139.0 + 候选 2123 穷举完备 ⇒ **N\*=139 三腿闭合**（评审 CH-REV-A 用独立实现重算三腿全部成立，另附基座敏感性 134/136/139）；R23 贪心+LNS（3-seed 137/137/137，stability=0）；R51 相位×块双计数初等界 332（÷3 合法性经 139 解实证 417=3×139；尾幽灵块瑕疵登记，生产界码改 (641-r)//10）。评审：R11/R51 retain（minor），R23 revise→补跑 3 seed 闭环。

**Q4（Top-K=3）**：R11 扩域 CSP（锚定重算后 objective=[6,121,1996,663]，anchored=true，植入自 Q2-R51 解并四项机器断言 ALL_PASS；自跑 [8,113,…] 未支配植入锚，如实保留；workers=1/8 复现比对落盘）；R41 重定时 SA（3-seed [16,105]/[11,117]/[10,112]，中位 11）；R22 解析条带构造（[66,43,…]，评审复算 9/66 撤销可无损回滚 ⇒ **reject as solver route**，其 mod-10 同余引理（4005 C-C 对 0 反例、16/19 CC 边闭式可消解）保留为机理解释素材）。评审：R11/R41 revise（闭环完成）、R22 reject。

## 4. 收敛决策（每问独立 tournament，选择优先级 correctness≻feasibility≻optimality_evidence≻objective≻stability≻runtime≻explainability）

| 问 | winner | 等级 | 依据一句话 |
|---|---|---|---|
| Q1 | **Q1-R21** | L2_EMPIRICALLY_BEST | 三实现全等 symdiff=0；R21 直接满足 Q1-C1 双实现验收且 runtime 最低；R52/R41 为辅助证据链 |
| Q2 | **Q2-R51** | L2_EMPIRICALLY_BEST | 唯一带机器可复核证书链的精确路线；[2,6] 界开放如实登记，生产长预算攻闭合 |
| Q3 | **Q3-R11** | **L3_NEAR_GLOBAL** | 三腿会合 gap=0（评审独立复算成立）；作用域限定=冻结基座（生产 Q2 更新须重证） |
| Q4 | **Q4-R11** | L2_EMPIRICALLY_BEST | 支配界锚定植入解 [6,…]；间隔自由度的收益判定冻结至生产热启动（生产=Q2 生产解 warm-start + 不劣锚定约束） |

## 5. 淘汰与理由（要点；全量在 IDEA_CANDIDATES/DECISION 账本）

- 36 条未入 Top-K：同族 Pareto 支配 / 预算不可完成（整图分支定价、52136 顶点精确 MIS、大种群元启发、GNN/RL）/ DGP 不符（ML/控制/代理无对象）。
- Q1-R42（统计零模型）：不产出契约必需输出，其置换检验并入 R41 诊断件。
- Q4-R22：critical objective_degenerate（撤销 66 为实现自伤而非构造极限）→ rejected；叙述层诚实但机器登记层不实。
- Q4-R52：从未被侦察（AMD-01 协议对齐登记），不得进入账本。

## 6. 限制与交接（→ 2analysis-modeling / 8validation-plan / 3coding-visual）

1. **生产预算分级**（D-BUDGET-001）：Q2 词典序四层+撤销阶梯以小时级后台跑；Q4 必须 Q2 生产解热启动；Q3 在生产 Q2 解上重证 N\*。
2. **界闭合风险**：撤销层 [2,6] 若生产仍不闭合，论文写区间+证书脚本，禁写"最优"。
3. **checker 纪律**（TF-3/4）：生产 checker 必须第二独立实现、自行先判 g'≥1（冻结 evaluator 对非法 g' 崩溃 exit=1 的负例行为不得进入生产路径）；R22 教训——"撤销前扫无损回滚"作为修复后处理强制步骤。
4. **复现性**：R51/R11 类 CP-SAT 生产运行做 workers=1 对照；GRASP 只引用区间结论。
5. **runs/competitive 数字永不进 results/ 或论文**；本阶段全部 objective 只是路线证据。
