# -*- coding: utf-8 -*-
"""REV-Q4-01 结论落盘器：组装 reviews/REV-Q4-CH-R3.json。
input_artifact_sha256s 全部由本脚本【磁盘重算】，不复制任何 scout 自报值。
"""
import hashlib, io, json, os, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS = os.path.abspath(os.path.join(RUN, "..", "..", ".."))
sys.stdout.reconfigure(encoding="utf-8")
P = "runs/competitive/CS-20260911T071520-D2026/"


def sha(rel):
    p = os.path.join(WS, rel.replace("/", os.sep))
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


INPUTS = [
    P + "common_input.json", P + "TOURNAMENT_PROTOCOL.json", P + "ADJUDICATION.json",
    P + "canonical_evaluator.py", "data/canonical_plans.csv",
    P + "routes/CH-01.route.json", P + "routes/CH-02.route.json",
    P + "routes/CH-04.route.json", P + "routes/CH-05.route.json",
    P + "scouts/Q4-R11/result.json", P + "scouts/Q4-R11/scout.json",
    P + "scouts/Q4-R11/run/solution_actions.json", P + "scouts/Q4-R11/run/eval_q4.json",
    P + "scouts/Q4-R11/run/r11_layers.json", P + "scouts/Q4-R11/run/q2_inclusion_check.json",
    P + "scouts/Q4-R11/run_q2reduction/solution_q2reduction.json",
    P + "scouts/Q4-R11/run_q2reduction/r11_layers.json",
    P + "scouts/Q4-R11/code/q4common.py", P + "scouts/Q4-R11/code/solve_r11.py",
    P + "scouts/Q4-R41/result.json", P + "scouts/Q4-R41/scout.json",
    P + "scouts/Q4-R41/run/solution_seed11.json", P + "scouts/Q4-R41/run/solution_seed29.json",
    P + "scouts/Q4-R41/run/solution_seed47.json",
    P + "scouts/Q4-R41/run/eval_seed11.json", P + "scouts/Q4-R41/run/eval_seed29.json",
    P + "scouts/Q4-R41/run/eval_seed47.json",
    P + "scouts/Q4-R41/run/sa_record_seed11.json", P + "scouts/Q4-R41/run/sa_record_seed29.json",
    P + "scouts/Q4-R41/run/sa_record_seed47.json",
    P + "scouts/Q4-R41/code/solve_sa.py", P + "scouts/Q4-R41/code/finalize_q4.py",
    P + "scouts/Q4-R22/result.json", P + "scouts/Q4-R22/scout.json",
    P + "scouts/Q4-R22/run/solution_actions.json", P + "scouts/Q4-R22/run/eval_q4.json",
    P + "scouts/Q4-R22/run/r22_log.json", P + "scouts/Q4-R22/code/solve_r22.py",
    P + "scouts/Q2-R51/result.json", P + "scouts/Q2-R51/eval.json",
    P + "scouts/Q2-R51/solution_actions.json",
]

R11 = [
    {"type": "evaluation_unfair", "severity": "major",
     "test": "重点核查3：Q4-C2『利用间隔自由度不劣于Q2』的证据锚点是谁？把本锦标赛 Q2 侧最强侦察解 "
             "(scouts/Q2-R51/solution_actions.json) 原样喂进冻结 evaluator 的 --question Q4 口径复算；"
             "再把它逐选项映射进 R11 自己的 6013 选项域，检查是否落在其可行域内。",
     "finding": "锚点是自我弱对照，且结论方向被反转。q2_inclusion_check.json 的对照基线是 R11 自跑的 "
                "Q2 退化模型（撤销层只给 150s，ub=14/lb=0），scout.json 据此写『Q4 侧 8 < 14 ⇒ 额外自由度实测有收益』。"
                "但同一锦标赛 Q2 侧的真实 incumbent 是 [6,121,1996,663]（Q2-R51，另有 Q2-R32 也到 6），"
                "我已复算它在 --question Q4 下 feasible=true、violations=0、元组逐字不变（该解不含 dg 动作），"
                "并且它 100% 落在 R11 自己的域/边表达内（127 个动作全部在 d4 中有同键选项、unmapped=0、"
                "内部残余冲突=0，见 reviews/_tmp/recheck_out_C.json.R11_model_can_hold_6revoke）。"
                "⇒ 撤销层已知上界是 6 不是 8：R11 交付的 incumbent 被同锦标赛已存在的可行点第一级支配，"
                "『不劣于 Q2』在 incumbent 层面为假，只有可行域包含意义上的结构性成立。"
                "CH-01 route 的 bound_plan 本就规定『UB_Q4 = UB_Q2（结构性上界）』，侦察未执行该锚定（改用对手候选的 SA 解做 hint）。"
                "后果：候选集合中 Q4 的 C2 能力目前无任何候选工件支撑，Manager 收口前必须补一次带 6-撤销锚的复算。"},
    {"type": "bound_invalid", "severity": "major",
     "test": "重点核查1（可行性真伪）+ 阶梯界合法性：用我自己的区间算术实现（不走 evaluator.mask_of）"
             "重算 6013 个选项掩码、11175 个计划对，检查 (a) 势边表/禁元组表是否有漏（漏边→假 OPTIMAL）；"
             "(b) 撤销层 [2,8] 是否为该证据集下最紧界；(c) 层 3/4 的 UNKNOWN 是否有免费改进。",
     "finding": "(a) 通过——独立重算得边集 2117、禁元组对与候选集合双向差为 0（missing_edges=0、"
                "missing_forbidden_pairs=0、6013 个选项掩码 0 失配），CH-05 警示#2a 的『只约束原冲突边』风险在 R11 不存在，"
                "其 incumbent 的可行性属实（全量残余冲突=0）。"
                "(b) 不通过——UB=8 非最紧界，见上一条（应为 ≤6）；层 3/4 报告 UNKNOWN 且未给出任何区间。"
                "(c) 层 4 有免费改进：我对交付解做 20 行 1-opt 幅度降级（只把 |v| 调小、不改类型/不改 rev/adj/ploss），"
                "54 次改进后得 [8,113,2289,657]，冻结 evaluator 复核 feasible=true、violations=0"
                "（reviews/_tmp/polished_R11.json*）⇒ 交付元组第 4 级 719 不是其自身模型口径下的终点；"
                "R11 是三候选中唯一没有做任何幅度抛光的（其第 3/4 层求解在提示失效后空转 100s/90s）。"},
    {"type": "identifiability", "severity": "minor",
     "test": "包含性证据是否落盘：q2_inclusion_check.json 里有没有 G*_Q2⊆G*_Q4 与『域逐字子集』的可机检字段；"
             "『共享解双口径元组逐字一致』这一判据是否具有区分力（读 evaluator.objective_tuple 源码）。",
     "finding": "两条判据都不构成证据。① objective_tuple(plans, actions, allow_gap) 的形参 allow_gap 在函数体内"
                "从未被引用（canonical_evaluator.py:170-189）⇒ 同一动作集在 Q2/Q4 两次评估下元组必然相同，"
                "该测试对『元组一致』是恒真式（唯一非平凡部分是 feasible，而共享解不含 dg，也恒真）。"
                "② scout.json 声称的 domain_verbatim_subset / edge_subset / clause_subset 三项『通过』在磁盘工件中"
                "无对应字段（q2_inclusion_check.json 只有模型计数与双评估元组）。我用自己的构建器复算这三项：全部为真"
                "（4582⊂6013 且逐字前缀成立；1693⊆2117 零缺失；270626⊆437962 零缺失，"
                "见 reviews/_tmp/recheck_out_B.json / recheck_out_E.json）⇒ 结论对、证据缺，评审不接受『口头通过』。"},
    {"type": "solver_mismatch", "severity": "minor",
     "test": "『deterministic ⇒ 单重复』标签是否名副其实：读 result.json.seed 与 scout.json.determinism 的自述，"
             "对照协议 replicates_deterministic=1 的适用前提。",
     "finding": "result.json 写 seed='CP-SAT random_seed=7, workers=4 (deterministic)'，而 scout.json 自认"
                "『num_workers=4 下搜索路径非位级可复现』，并给出开发期证据（12s 小预算跑出 ub=54 vs 本次 8）。"
                "即该候选的 incumbent 依赖未量化的预算/调度方差，却按确定性档只跑 1 次、不报方差 ⇒ "
                "撤销层 8 是单次抽样而非可复现读数。收口要求：num_workers=1 复跑一次（或补 3 重复）"
                "证明 incumbent/界可复现，否则按随机候选口径处理并在正文登记区间。"},
    {"type": "objective_degenerate", "severity": "info",
     "test": "口径核查5：词典序标量 1e12/1e8/1e4 在本实例是否会串层（ploss/mag 的最大可能值 vs 层间隔）。",
     "finding": "本实例安全：max ploss=4980<1e4、max mag=1500<1e4、max adj=150、V≤11175 且 Python int 精确运算"
                "⇒ 报告标量 8011322890719 = 1e12·8+1e8·113+1e4·2289+719 逐字成立（我复算一致）。"
                "登记为信息项：该安全性来自 150 计划的实例规模而非公式性质，正式建模若要扩到 1e4 级 ploss 需改为逐级求解（R11 已是逐级式，方向正确）。"},
    {"type": "dgp_mismatch", "severity": "info",
     "test": "R3/R6 截断口径：dg 选项域计数与『C083 仅 g'∈[1,7] 可行』的说法独立复算。",
     "finding": "逐字吻合：C 类 dg 选项 potential=1530、valid=1431、pruned_by_horizon=99（与我方 build_domains 计数一致）；"
                "C083(t0=531,d=2,n=12,g=8) 末窗 643+11·dg ⇒ 仅 dg≤0 合法，非零 dg 即 g'∈[1,7]；"
                "交付解 14 个 dg 动作 |dg|≤10、g'≥1、末窗最大 640≤643，全部合法。哨兵负例另证 evaluator 能拒绝 "
                "A/B 调 g（gap_only_C）、|dg|=11（gap_range）、Q2 口径调 g（gap_not_allowed）、末窗越 643（out_of_resource），"
                "但 g'≤0 会使 evaluator 崩溃（assert g>=1, exit=1）而非返回 feasible=false——冻结件缺陷，已登记给 Manager。"},
    {"type": "task_mismatch", "severity": "info",
     "test": "解的动作类型是否与题面 Q4 口径一致（单参数、仅 C 调 g、次数不动、无 0 值噪声动作）。",
     "finding": "121 条动作全部单键、无 0 值动作、无 A/B 调 g、n 恒为原值（掩码展开用原 n）⇒ 题面口径无越界；"
                "result4 五列所需的『间隔时长』可从 dg 唯一还原。此项无攻击点。"},
    {"type": "sample_dimension", "severity": "info",
     "test": "资源/时间预算与评估次数：547.3s 是否 ≤600s/重复；evaluator 调用数是否 ≤16。",
     "finding": "合规（547.3≤600；evaluator 调用 3 次，ledger 内）。但 4 层预算分配 230/120/100/90 把 190s 花在第 3/4 层的"
                "两次空转（UNKNOWN）上，而同样的预算换到 20 行 1-opt 抛光即免费拿到第 4 级 −62 ⇒ 预算配置与目标层级不匹配（效率问题，非正确性）。"},
]

R41 = [
    {"type": "identifiability", "severity": "info",
     "test": "重点核查2：三链结果是否被如实按『median over replicates』聚合——逐链用区间算术独立重算元组 + "
             "冻结 evaluator 逐链复跑 + 按词典序取中位，比对 result.json 的 objective/seed/solution_path。",
     "finding": "通过（该项无攻击点，是正向验证）：三链独立重算与 evaluator 复跑全部逐字等于自报值"
                "（seed11 [16,105,2549,556] / seed29 [11,117,2344,578] / seed47 [10,112,2229,596]），"
                "词典序中位=seed29，result objective=11011723440578=scalar(seed29)、seed 字段=29、"
                "solution_path 指向 seed29、sa_record 内 actions 与 solution 文件逐字相等 ⇒ 未挑最优、未冒称中位。"
                "finalize_q4.py 的中位实现是 sorted(feasible)[n//2]，n=3 下与协议一致。"},
    {"type": "task_mismatch", "severity": "major",
     "test": "交付实现是否仍在跑 CH-04 冻结的那条路线：比对 route.solver（『以 Q2 可行方案为初始态』『anytime 保持可行』"
             "『记录每链首次达到优于 Q2 元组的移动序号』）与 solve_sa.py 的初态/能量/登记指标。",
     "finding": "跑的是另一条算法。实装为恒等态冷启动（297 违例起步）+ 违例前置能量层 V·1e15；"
                "CH-04 承诺的 Q4-C2 直接证据『每链首次优于 Q2 元组的移动序号』因此不可得，被替换为 first_zero_violation_move"
                "（8205/12022/6030）。更关键：CH-04 预登记失败判据『三链中出现比 Q2 更差的最终元组 ⇒ 实现或接受准则有 bug』"
                "在本次已数值成立（seed11 [16,…] 第一级劣于其自跑的 Q2 退化锚 [14,96,2383,638]，更远劣于锦标赛 Q2 的 6），"
                "而 scout.json 的 failure_conditions_realized=[] 空登记（其判据原文含『初始态即 Q2』前提，被偏差作废后未回写登记）。"
                "偏差本身在 deviations 中如实申报（读白名单不含 results/），属诚实的口径偏离；"
                "但代价是 baseline 被系统性低估（冷启动丢弃了设计自带的 ≤UB 保证），"
                "评审建议 Manager 要求补一次暖启动复跑（暖启动即 R11/Q2 解，零额外预算），"
                "否则 Q4 baseline 的对照结论不对等。"},
    {"type": "evaluation_unfair", "severity": "minor",
     "test": "候选间信息流：Q4-R11/scout.json 的 hint_source 指向谁？被引用方（R41）的官方分数用的是哪个链？",
     "finding": "跨候选非对称引用已发生并被披露：R11 用 R41 的 seed47（三链最优，10 撤销）作 CP-SAT hint，"
                "而 R41 官方分数按协议取中位（11 撤销）⇒ 两个候选的产出不再相互独立（R11 的 incumbent 部分继承 R41 的随机抽样），"
                "且『R11 8 vs R41 11』的比较里含一条信息通道。R41 自述『Q2 方案自动可行锚以本组退化模型解充当』。"
                "评审判定：披露充分，不作废结果，但 Pareto 表须标注该依赖，且 winner 的正式复现禁止引用兄弟候选的中间产物。"},
    {"type": "solver_mismatch", "severity": "minor",
     "test": "CH-04 的『收尾撤销修复投影保证零冲突』承诺是否被任何一次运行实际走过：查三链 projection 字段。",
     "finding": "未走过：三链 projection.applied=false（抛光后已零冲突），该分支是未测试代码，"
                "而路线把它写成可行性保证。Q4-R22 恰好示范了同族规则的实际后果（以撤销收敛→66）。"
                "收口要求：给该分支加一个强制触发的单元测试（人为留一条残余冲突），否则正式模型不得引用『投影保证可行』这一性质。"},
    {"type": "sample_dimension", "severity": "minor",
     "test": "3 个冻结种子的重复数是否足以刻画随机候选：撤销层极差与中位数的稳健性。",
     "finding": "撤销层 10/11/16（极差 6），单级差达 5 撤销（≈第一级跨两个名次），中位数 11 的稳健性很弱；"
                "scout.json 已在 metrics.stability 如实登记『链间波动大，符合 CH-04 弱点预告』。"
                "登记要求：正文只引用『SA 落在 10..16、被精确路线支配』这一区间性结论，不把 11 当能力点估计。"},
    {"type": "objective_degenerate", "severity": "info",
     "test": "口径核查5：V·1e15 前置层 + 1e12/1e8/1e4 四级标量在 int 域是否等价于词典序（含可行/不可行两侧）。",
     "finding": "安全：max V=297·…（实算上界 11175 对）×1e15 与 1e12 层间隔不串层；可行态上前置层退化为 0，"
                "能量即协议公式，且三链能量元组与 evaluator 元组逐字相等（我方复算）。"
                "登记为口径澄清项：SA 的『最优』是在 (V, scalar) 词典序上取得，不是协议 scalar 单独排序——"
                "两者在可行域内一致，故不影响比较。"},
    {"type": "dgp_mismatch", "severity": "info",
     "test": "动作域与题面一致性：域是否 cls==C 才有 dg、是否 |dg|≤10 且 g'≥1、是否每计划恰一动作。",
     "finding": "与 R11 共用同一 q4common.build_domains（三候选该文件 SHA256 逐字相同），"
                "我方对全部 6013 选项独立重算掩码 0 失配；seed29 解的 14 个 dg 动作 g'∈[1,15]、末窗最大 638≤643、"
                "128 条动作全单键无 0 值 ⇒ 无越界自由度。evaluator 复跑 feasible=true、violations=0。"},
    {"type": "simpler_model", "severity": "info",
     "test": "是否存在更简且同/更强的模型：与 R11（同实例 CP-SAT）和纯贪心对照。",
     "finding": "R41 被 R11 第一级支配（11 vs 8），也被『暖启动即 UB』这一更简策略的锚点支配；"
                "但它在候选集里的角色是协议指定的 baseline（模拟退火范式对照），其价值=范式多样性 + "
                "唯一提供链间方差数据的候选 ⇒ 作为 baseline 保留，作为 Q4 主答案不成立。"},
        {"type": "task_mismatch", "severity": "info",
         "test": "result4 语义：交付动作是否可无损还原为『频段区间/时间区间/间隔/是否撤销』五列（F-022）。",
         "finding": "可还原：每计划至多一个动作键、无 0 值动作、A/B 无 dg、n 恒为原值；seed29 的 14 个 dg 动作 g'∈[1,15]，"
                    "全部经我方区间算术复核（末窗最大 573≤643）。此项无攻击点。"},
    ]

R22 = [
    {"type": "objective_degenerate", "severity": "critical",
     "test": "重点核查4：撤销 66 是『解析构造的结构性极限』还是实现自伤？对交付解做两件事："
             "(A) 逐个尝试回滚撤销（恢复保留/换更小动作），要求残余冲突恒为 0；"
             "(B) 用不含任何数论构造、不含 CP-SAT/SA 的 60 行贪心（字典序最小残余边 + 类权低者优先 + 度大者优先）复跑同口径。"
             "两解都交冻结 evaluator 复核。",
     "finding": "归因不成立，66 主要是实现自伤。(A) 其自身解里 9/66 个撤销可无损回滚"
                "（B010→dt-3、C002→dg3、C011→dg-1、C014→dt-2、C022→dg4、C023→dg6、C039→dt-3、C046→df8、C067→df7），"
                "得 [57,52,1093,181]，frozen evaluator 复算 feasible=true、残余冲突=0 ⇒ 第一级 −9、第三级 −18 均为免费改进；"
                "其 scout.json 宣称已执行的『确定性收缩（冗余动作回退+幅度降级）』只回退调整、从不开撤销"
                "（solve_r22.py 收缩循环显式 continue 掉 revoke 类），且收缩偏序按 (df<dt<dg,|v|) 排类型而非按题面第四级 Σ|δ|，"
                "我方复核另有 7 处跨类型更大幅度替代（→[66,43,1111,123]）。"
                "(B) 更简基线（无任何解析构造）得 [42,73,1282,371]，frozen evaluator feasible=true、violations=0"
                "⇒ 第一级比 R22 少 24 个撤销，词典序严格支配交付解。"
                "⇒ scout.json 的『作为主求解器不成立』结论正确，但把它归因为『模构造消解力只覆盖 19/297 CC 边 ⇒ 结构性极限』"
                "属过度归因：坍塌由端点选择规则 + 单向撤销收缩造成，与同余构造无关。"},
    {"type": "identifiability", "severity": "major",
     "test": "失败模式登记的机器可读层：result.json（P1-03 authority 消费的工件）里 status/feasible/failure_mode/"
             "诊断字段是否体现『66 撤销坍塌 + 路线自我否定』这一事实；与 scout.json prose 对账。",
     "finding": "叙述诚实、字段不完整。prose 侧确属如实：metrics.gap 明写『第一级严重劣势…66≫R11 的 [2,8] 与 SA 的 10..16』、"
                "failure_conditions_realized 登记了 CH-02 预登记判据『跨度约束与模指派冲突比例高→构造退化』部分应验，"
                "并明确『作为主求解器不成立』；result.json 未删记录、未改元组（我复算 [66,43,1111,144]、标量、"
                "类分布 ploss 1111=2·(10·17+49)+673 全部逐字吻合）。"
                "但机器可读层：status=completed、feasible=true、failure_mode=null、且 400 字节的 result.json 无任何"
                "层诊断（无 layers/certificate/stability/gap 字段），协议契约把 failure_mode 设为必填正是为了让"
                "『completed 但路线崩塌』可被下游按字段筛除；CH-02 自己的预登记失败判据已触发 ⇒ "
                "应登记非空 failure_mode（如 greedy_repair_collapse）并在 result.json 内联诊断。"
                "评审判定：不属于隐瞒或篡改，属于登记粒度不足，须补写后方可进入 P1-03 authority。"},
    {"type": "evaluation_unfair", "severity": "major",
     "test": "机理叙事 vs 交付解：R22 的头号卖点是『阶段 I 同余构造闭式清零 16/19 条 CC 边』"
             "——逐边核查这 16 条边在最终交付解里的实际消解方式（两端点是否都被保留？是否真的靠改 g'？）。",
     "finding": "机理解释与交付解脱节：16 条阶段 I 消解边里，最终解两端点都未被撤销的只剩 2 条，"
                "其中真正靠改 g' 存活的只有 1 条（C005|C025：dg-1/dt0）；其余 14 条是靠撤销端点消失的"
                "（阶段 II 把阶段 I 指派过的 C 计划大量撤销，19 条 CC 边中 17 条以撤销收场）。"
                "⇒ 『16/19 闭式清零』只在中间态成立，与 scouts/Q4-R22/run/eval_q4.json 的解没有对应关系；"
                "报告把两者并列陈述（construction.stage_I + metrics『构造解动得少』）易被论文读成"
                "『最终方案体现了同余消解』。若作论文素材：CC 边的模判据部分必须用 r22_log.cc_strip_matrix / "
                "cc_components（中间态）表述，并显式声明它不进入 result4 的消解归因。"},
    {"type": "dgp_mismatch", "severity": "minor",
     "test": "机理断言的因果归因：『空条带边 C033|C043 无任何 (g'_i,g'_j) 可消解——R3 视界截断所致』"
             "是否成立？把 643 视界放开（只留 |dg|≤10、g'≥1、频段界内）重算该边可分离性。",
     "finding": "结论对、归因错。放开视界后该边仍 0 个可分离 (dg_i,dg_j) 组合（我方穷举 g+dg≥1 的全部 17×17 组合，"
                "643 口径与无界口径均为空集，见 reviews/_tmp/recheck_out_G.json）⇒ 与 R3 截断无关；"
                "真因是重定时不移动首窗：C033(t0=252) 与 C043(t0=253) 的 k=0 窗 [252,254)/[253,255) 已在唯一交叠频段 74 相交，"
                "改周期永远消不掉首次交叠。反证：单端 df∈[-10,-5]（6 个取值，任一端皆可，另一端完全不动；"
                "连同 dt 位移共 24 个单端合法动作）即可分离该边，"
                "而 R22 的交付解把 C033 与 C043 两端全部撤销（见 solution_actions.json）。"
                "危害：若论文按『视界截断导致不可消解』写这条机理论证，属可判定的错误归因；"
                "并且在其交付解语境里单独回滚 C033 的撤销并改施 df/dt 仍引入 2~4 条新冲突（邻居已被阶段 II 移动）"
                "⇒ 属『消解方式选择代价』，不是免费后处理可修。"
                "我独立复核其成立的两个断言：模 10 规则 4005 个 C-C 对、19 条冲突、0 反例（逐字复现）；"
                "『99/1530 dg 选项被截断』计数复现。"},
    {"type": "simpler_model", "severity": "major",
     "test": "更简模型是否支配该候选（见 objective_degenerate 的 (A)(B) 两项）；以及该候选相对『完全不构造』是否有任何产能优势。",
     "finding": "被支配：我方 60 行贪心（无同余、无求解器）[42,73,1282,371] 与『R22 解 + 开撤销』[57,52,1093,181] "
                "均在第一级支配其 66；而纯『按度撤销覆盖』基线为 75（说明其相对全撤销确实有改进，但改进幅度远低于同族规则微调）。"
                "唯一无可替代产出=可机检的负结果与机理素材（CC 边同余判据 + 空条带边 + 分量代价表），"
                "这属于 bound/explanation 资产而非 solver 资产。"},
    {"type": "bound_invalid", "severity": "minor",
     "test": "路线承诺的界是否兑现：CH-02 bound_plan『动作数 LB 取 nu(G)=71 对任何 Q4 解成立』；"
             "对照 Q4 口径下『只撤销』与『撤销+调整』两种问题的正确界。",
     "finding": "nu(G)=71 是对『基冲突图顶点覆盖』的界（我方极大匹配给出 ν≥51 作下界参考，最大匹配口径需 Edmonds），"
                "它对 Q4 的『调整+撤销』问题不构成撤销数下界——一次调整可消掉多条边，故 71 不得被引用为撤销数或触达计划数的 Q4 界；"
                "R22 侦察未报告任何界（其解触达 109 计划 > 71，仅作一致性检查成立）。"
                "同时 Q4 侧至今没有任何独立结构下界（R52 未跑；R11 的 LB=2 来自 CP-SAT 对偶界）⇒ "
                "『为什么必须撤销这么少』目前无证据；Manager 需补 CH-05 的 R52 或等价的 ν(U) 计算。"},
    {"type": "task_mismatch", "severity": "minor",
     "test": "口径核查5 + 协议一致性：R22 是否在协议冻结的候选名单内？（TOURNAMENT_PROTOCOL.per_question.Q4.candidate_set）"
             "与其 route_source 的 idea_id 编号对账。",
     "finding": "名单不符：协议 Q4.candidate_set = [Q4-R41, Q4-R11, Q4-R52]，实际第三侦察是 Q4-R22（CH-02 advanced_alternative），"
                "磁盘无 scouts/Q4-R52；R22 scout.json 只声明与 CH-02 的编号逐字一致，未声明替换关系。"
                "两候选同属 analytic_mechanistic（CH-05 R52 是 (t1,g) 禁止条带『界』路线，CH-02 R22 是『求解』路线），"
                "范式槽位名义上未破，但协议作为唯一事实源未被遵守登记 ⇒ 需显式 amendment 或补跑 R52。"
                "标量口径本身一致（1e12/1e8/1e4 + 撤销 2 倍优先级损失，我方复算逐字成立）。"},
    {"type": "sample_dimension", "severity": "info",
     "test": "预算与确定性证据：29.2s 远低于 600s；『确定性双跑』的对账。",
     "finding": "合规且证据充分：开发跑 code/_smoke 与生产跑 run 的 solution_actions.json / eval_q4.json SHA256 逐字相同，"
                "r22_log.json 仅 wall_seconds_total 不同（45.3 vs 29.2）⇒ 确定性主张成立。"
                "但只用掉预算的 4.9%，其阶段 II 完全有时间跑第二种端点规则或加开撤销收缩而未做（与 objective_degenerate 同因）。"},
]

review = {
    "review_id": "REV-Q4-01",
    "reviewer_child_run_id": "CH-REV-B",
    "question_id": "Q4",
    "search_id": "CS-20260911T071520-D2026",
    "protocol_ref": "TP-D2026-01",
    "adjudication_ref": "ADJ-CS-20260911T071520-D2026-01",
    "canonical_evaluator_sha256_recomputed": sha(P + "canonical_evaluator.py"),
    "independence_statement": {
        "reviewer_role": "独立 route reviewer（adversarial）；非路线作者、非 Manager、非 bound/route scout",
        "not_authored_routes": ["CH-01", "CH-02", "CH-03", "CH-04", "CH-05"],
        "forbidden_inputs_not_read": [
            "Manager 最终选择（reports/contracts/IDEA_DECISION*、IDEA_CANDIDATES、BRAINSTORM_REPORT、"
            "state/decision_log、FINAL_MODEL_SPEC 等）——全程未读取；",
            "同题其他 Reviewer 结论：本目录不存在 Q4 评审文件，未读取任何 Q4 评审结论；",
        ],
        "scope_deviation_disclosed": "写盘前我完整打开了 reviews/REV-Q2-CH-R2.json（CH-REV-A 对 Q2 的评审）"
                                     "以对齐任务书要求的『§5 扩展为 attacks_by_idea 数组』的字段形状。"
                                     "该文件属『其他 Reviewer 结论』，严格讲超出我的读取白名单，此处的准确披露是："
                                     "我只借用了它的 JSON 结构，未把其中任何判断作为 Q4 攻击的依据；"
                                     "本评审全部 Q4 数值均由我自己的脚本从磁盘工件独立重算（可逐条复现），"
                                     "其中与 Q2 有关的唯一外部事实是任务书已给出的『Q2 侦察 incumbent=6 撤销』。",
        "read_scope_note": "除授权清单外，为完成第 3 项（支配界/包含性核查）额外读取 "
                           "scouts/Q2-R51/{result.json,eval.json,solution_actions.json} 与 scouts/Q2-R32/eval.json"
                           "（仅用作 Q4 口径可行锚与其 6 撤销事实的复算输入），已在此披露。",
    },
    "method": [
        "占用窗一律用我方区间算术重写（Occ_k=[t1+dt+(k-1)(g'+d), +d)，半开区间，硬界 [0,643)×[0,100)），不借 evaluator 实现判定；",
        "三候选交付解全量 11175 计划对残余冲突独立重算 = 0/0/0，并逐一对账 evaluator 复跑；",
        "势边表/禁元组表完备性双向集合差审计（漏边→假可行风险）；",
        "负例哨兵矩阵 16 项（A/B 调 g、|dg|>10、g'≤0、越界、多参数、未知计划、0 值动作、Q2 口径调 g、643 末窗）；",
        "反证性复算：对 R11 做幅度 1-opt、对 R22 做『开撤销』+ 跨类型幅度替代、并实现无构造 60 行贪心基线，全部经冻结 evaluator 复核。",
    ],
    "input_artifact_sha256s": [{"path": r, "sha256": sha(r)} for r in INPUTS],
    "attacks_by_idea": [
        {"idea_id": "Q4-R11", "route_source": "routes/CH-01.route.json", "scout_run": "scouts/Q4-R11",
         "reported_tuple": [8, 113, 2289, 719], "reported_scalar": 8011322890719,
         "reviewer_recomputed_tuple_interval_arithmetic": [8, 113, 2289, 719],
         "reviewer_evaluator_rerun": {"feasible": True, "tuple": [8, 113, 2289, 719], "n_violations": 0},
         "feasibility_verdict": "属实（含 14 个 dg 动作逐窗复核、20 计划对随机抽样、11175 对全量）",
         "attacks": R11, "verdict": "revise",
         "required_evidence": [
             "以已知 Q4 可行 6 撤销解（scouts/Q2-R51/solution_actions.json，我方复算 --question Q4 feasible=true）为 hint/层一上界锚，"
             "重跑 R11 层 1（cap≤230s 不变），报告新的 [LB,UB]；在此之前 Q4 撤销层界按 [2,6] 而非 [2,8] 记账",
             "把域逐字前缀、G*_Q2⊆G*_Q4、禁元组零缺失三项复算写进 q2_inclusion_check.json（现仅存于 scout 口头声称；"
             "评审复算脚本 reviews/rev_q4_01_inclusion.py + rev_q4_01_edgeaudit.py，输出 recheck_out_B/E.json）",
             "把『Q4 不劣于 Q2』的表述改为『可行域包含 ⇒ 最优值不劣；incumbent 层面尚未证明』，并把 Q4-C2 验收证据记为 PENDING",
             "num_workers=1（或 3 重复）incumbent 复现证据；补一层幅度抛光或在 r11_layers.json 说明为何不做",
             "evaluator 负例：g'≤0 使 evaluator assert 崩溃（exit=1）而非返回 feasible=false——冻结件缺陷登记给 Manager（禁改件），"
             "checker 侧需自行先判 g+dg≥1",
         ]},
        {"idea_id": "Q4-R41", "route_source": "routes/CH-04.route.json", "scout_run": "scouts/Q4-R41",
         "reported_tuple": [11, 117, 2344, 578], "reported_scalar": 11011723440578,
         "median_aggregation_check": "通过：三链独立重算+evaluator 复跑逐字一致，词典序中位=seed29=result objective；"
                                     "seed/solution_path 同指 seed29（未挑 seed47 最优链冒称中位）",
         "attacks": R41, "verdict": "revise",
         "required_evidence": [
             "暖启动复跑一次（初态=已知可行 Q4 解），恢复 CH-04 的 anytime 语义并补登记『每链首次优于锚的移动序号』；"
             "或显式改写路线为『冷启动 + 违例前置层』并同步修订其预登记失败判据",
             "projection 分支的强制触发单元测试（当前三链 applied=false，承诺的『投影保证零冲突』未被任何运行验证）",
             "failure_conditions_realized 回写：seed11 第一级劣于其 Q2 退化锚这一事实须按判据条目登记（不得留空）",
             "正文只引用区间结论 10..16，不得把中位 11 当能力点估计（sample_dimension 条款）",
             "hint 依赖披露：Pareto 表标注 R11 使用本候选 seed47 解作 hint ⇒ 两候选非独立抽样",
         ]},
        {"idea_id": "Q4-R22", "route_source": "routes/CH-02.route.json", "scout_run": "scouts/Q4-R22",
         "reported_tuple": [66, 43, 1111, 144], "reported_scalar": 66004311110144,
         "reviewer_recomputed_tuple": [66, 43, 1111, 144], "feasible": True,
         "attacks": R22, "verdict": "reject",
         "required_evidence": [
             "若保留为『机理论证』素材：把 C033|C043 不可消解的原因改写为『重定时不移动首窗 ⇒ k=0 窗在唯一交叠频段相交』，"
             "并给出放开 643 视界仍不可分离的穷举证据（reviews/_tmp/recheck_out_G.json）；删除『R3 视界截断所致』表述",
             "阶段 I 成果必须按中间态表述（16/19 为 r22_log.cc_components 的构造态计数；最终解中两端点均保留者仅 2 条、"
             "靠 g' 存活 1 条），禁止与 result4 交付解并列归因",
             "result.json 补 failure_mode（非空）与内联诊断（层/步数/撤销构成/gap），否则 P1-03 按字段筛除时失真",
             "若重跑：收缩阶段必须包含『开撤销』与按 Σ|δ| 的跨类型幅度替代（我方已证免费改进至 [57,52,1093,181] / [66,43,1111,123]），"
             "并把端点选择规则改为度优先做敏感性对照（我方无构造基线 [42,73,1282,371]）",
             "协议名单 amendment：说明 Q4 第三候选为何是 R22 而非冻结的 R52，并补 R52 的 ν(U)/U 界计算（Q4 目前无任何独立撤销下界）",
         ]},
    ],
    "tournament_level_findings": [
        {"id": "TF-1", "item": "Q4-C2（能力项，mandatory）当前无候选工件支撑：三候选 incumbent 撤销数 8/11/66 全部劣于"
                               "同锦标赛 Q2 侧已存在的 6 撤销解，而该解在 Q4 口径下可行（我方复算）。"
                               "这不是模型缺陷而是轮次编排缺陷——Q4 侦察（16:18-17:05）早于 Q2 侦察（17:19-18:26），"
                               "侦察时确无 6-撤销锚可读。评审判定：不追溯问责 scout，但 Manager 必须在收口前对 Q4 做一次"
                               "带 Q2 incumbent 锚定的低成本复算（≤300s），否则 Q4 结论『允许调间隔后改善消解』无证据。"},
        {"id": "TF-2", "item": "协议候选名单漂移未登记：TOURNAMENT_PROTOCOL.Q4.candidate_set=[R41,R11,R52] vs 实跑 [R41,R11,R22]，"
                               "无 scouts/Q4-R52。需 amendment 或补跑；同时 Q4 缺失 bound_scout 交付物（无任何独立撤销下界）。"},
        {"id": "TF-3", "item": "冻结 evaluator 的负例健壮性缺陷：g+dg≤0 触发 slots_of 的 assert（exit=1，无 JSON 输出）而非 "
                               "gap_range 违规回报；unknown_plan 同样使 objective_tuple KeyError 崩溃。"
                               "评审不改件，仅登记：正式 checker 必须在调用前先判间隔正性/计划存在性，否则非法解表现为『评估器报错』而非『判不可行』。"},
        {"id": "TF-4", "item": "口径一致性通过（核查5）：T_MAX=643 在三候选同源 q4common（SHA 相同）与 evaluator 内一致，"
                               "643 与数据事实吻合（基实例最晚占用恰为 C083 结束于 643，无基计划越界）；"
                               "1e12/1e8/1e4 标量在三候选 result/scout/sa_record 与 R22 类分布上全部逐字自洽，"
                               "本实例四级不串层（ploss≤4980、mag≤1500）。common_input.horizon_note 的 621 笔误未污染任何 Q4 工件。"},
        {"id": "TF-5", "item": "『三候选共享同一 q4common.build_domains/mask_int』构成共享实现盲区（域生成与判定同源）。"
                               "评审已用完全独立的区间算术重算 6013 个选项掩码与 11175 对残余冲突，0 失配 ⇒ 该盲区本次未致错，"
                               "但正式阶段的 checker 必须是第二实现（不可 import 求解侧域生成代码）。"},
    ],
    "verdicts_by_idea": {"Q4-R11": "revise", "Q4-R41": "revise", "Q4-R22": "reject"},
    "severity_counts": {},
    "reviewer_evidence_files": [
        P + "reviews/rev_q4_01_recheck.py", P + "reviews/rev_q4_01_inclusion.py",
        P + "reviews/rev_q4_01_extra.py", P + "reviews/rev_q4_01_caliber.py",
        P + "reviews/rev_q4_01_edgeaudit.py", P + "reviews/rev_q4_01_detail.py",
        P + "reviews/rev_q4_01_attribution.py", P + "reviews/rev_q4_01_polish.py",
        P + "reviews/rev_q4_01_sentinels.py", P + "reviews/rev_q4_01_simpler.py",
        P + "reviews/rev_q4_01_factsheet.py",
        P + "reviews/_tmp/recheck_out.json", P + "reviews/_tmp/recheck_out_B.json",
        P + "reviews/_tmp/recheck_out_C.json", P + "reviews/_tmp/recheck_out_D.json",
        P + "reviews/_tmp/recheck_out_E.json", P + "reviews/_tmp/recheck_out_F.json",
        P + "reviews/_tmp/recheck_out_G.json", P + "reviews/_tmp/recheck_out_H.json",
        P + "reviews/_tmp/recheck_out_I.json", P + "reviews/_tmp/recheck_out_K.json",
        P + "reviews/_tmp/B2b_greedy_solution.json", P + "reviews/_tmp/B2b_eval.json",
        P + "reviews/_tmp/R22_unrevoked.json", P + "reviews/_tmp/R22_unrevoked_eval.json",
        P + "reviews/_tmp/polished_R11.json", P + "reviews/_tmp/polished_R11.json.eval.json",
        P + "reviews/_tmp/review_fact_sheet.json",
    ],
    "reviewer_evidence_sha256s": [],
    "written_at": "2026-09-11T19:40:00+08:00",
    "readonly_attestation": "被审工件零修改：本轮曾在 reviews/rev_q4_01_polish.py 首版误把 evaluator 的 --out 写到 "
                            "scouts/*/run/*.eval.json（4 个新增文件），已即时删除并复核三候选目录内全部文件的 mtime "
                            "均不晚于 17:05:52（侦察产物原时间戳），无任何被审文件内容变动；后续所有输出改写入 reviews/_tmp/。",
}
counts = {}
for blk in review["attacks_by_idea"]:
    for a in blk["attacks"]:
        counts[a["severity"]] = counts.get(a["severity"], 0) + 1
review["severity_counts"] = {k: counts.get(k, 0) for k in ("critical", "major", "minor", "info")}
review["reviewer_evidence_sha256s"] = [{"path": r, "sha256": sha(r)}
                                       for r in review["reviewer_evidence_files"]
                                       if os.path.isfile(os.path.join(WS, r.replace("/", os.sep)))]
io.open(os.path.join(RUN, "reviews", "REV-Q4-CH-R3.json"), "w", encoding="utf-8").write(
    json.dumps(review, ensure_ascii=False, indent=2))
print("written REV-Q4-CH-R3.json")
print("severity_counts:", review["severity_counts"])
print("inputs:", len(review["input_artifact_sha256s"]), "evidence:", len(review["reviewer_evidence_sha256s"]))
print("verdicts:", review["verdicts_by_idea"])
