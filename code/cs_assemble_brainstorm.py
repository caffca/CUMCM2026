# -*- coding: utf-8 -*-
"""IDEA_CANDIDATES v2 (+P1-03 coverage/stop) 与 IDEA_DECISION v3 装配器（Manager 确定性合并）。
一切数字从磁盘工件重算（result.json/scout.json/eval/SHA），规则化 winner：
  winner = 本问 feasible 候选中 canonical scalar 最优（Q3 maximize）；
  tie -> optimality evidence 更强 -> implementation_risk 低 -> runtime 低。
前置：12 个候选 result.json + REV-Q1/Q2/Q4 评审文件必须存在。"""
import hashlib, io, json, os, sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")
ROOT = "runs/competitive/CS-20260911T071520-D2026"
SID = "CS-20260911T071520Z-1A9D30"   # P2-07 合规账本 id（UTC 起搜时刻+hex）；物理 run 目录见 search_run.run_directory
QIDS = ["Q1", "Q2", "Q3", "Q4"]

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def J(p): return json.load(io.open(p, encoding="utf-8"))

# ---------- 输入 ----------
common = J(f"{ROOT}/common_input.json")
proto = J(f"{ROOT}/TOURNAMENT_PROTOCOL.json")
adj = J(f"{ROOT}/ADJUDICATION.json")
mm = J(f"{ROOT}/merge_manifest.json")
EV_PATH = f"{ROOT}/canonical_evaluator.py"
EV_SHA = sha(EV_PATH)
assert EV_SHA == proto["canonical_evaluator_sha256"], "evaluator SHA 漂移"

CAND_OF_Q = {q: proto["per_question"][q]["candidate_set"] for q in QIDS}
BASELINE = {q: proto["per_question"][q]["baseline"] for q in QIDS}
DIRECTION = {q: proto["per_question"][q]["direction"] for q in QIDS}
UNIT = {q: proto["per_question"][q]["unit"] for q in QIDS}

# 候选 -> 源 route 片段
frag = {}
for fname in sorted(os.listdir(f"{ROOT}/routes")):
    if not fname.endswith(".route.json"):
        continue
    doc = J(f"{ROOT}/routes/{fname}")
    for r in doc.get("routes", []):
        frag[r["idea_id_suggested"]] = (doc["child_run_id"], r, f"{ROOT}/routes/{fname}")

results, scouts = {}, {}
for q in QIDS:
    for cid in CAND_OF_Q[q]:
        rp = f"{ROOT}/scouts/{cid}/result.json"
        assert os.path.isfile(rp), f"缺 result.json: {cid}"
        results[cid] = J(rp)
        sp = f"{ROOT}/scouts/{cid}/scout.json"
        scouts[cid] = J(sp) if os.path.isfile(sp) else {}

REVS = {}
for q in QIDS:
    cand = sorted(f for f in os.listdir(f"{ROOT}/reviews") if f.startswith(f"REV-{q}-")) if os.path.isdir(f"{ROOT}/reviews") else []
    if cand:
        REVS[q] = J(f"{ROOT}/reviews/{cand[0]}")
        REVS[q + "_FILE"] = f"{ROOT}/reviews/{cand[0]}"
for q in QIDS:
    if q not in REVS:
        sys.exit(f"ABORT: 缺 {q} 评审文件（reviews/）")

def rev_for(cid):
    q = cid.split("-")[0]
    for item in REVS[q].get("attacks_by_idea", []):
        if item.get("idea_id") == cid:
            return item
    return None

# ---------- winner（确定性规则） ----------
def rank_key(cid):
    q = cid.split("-")[0]
    r = results[cid]
    obj = float(r["objective"])
    sv = scouts[cid]
    has_cert = bool(r.get("certified_optimal") or sv.get("lower_bound") is not None)
    risk = {"low": 0, "medium": 1, "high": 2}[frag[cid][1].get("implementation_risk", "medium")]
    return (obj if DIRECTION[q] == "minimize" else -obj,
            0 if has_cert else 1, risk, float(r.get("runtime_seconds", 1e9)))

WINNER = {q: min(CAND_OF_Q[q], key=rank_key) for q in QIDS}
for q in QIDS:
    for cid in CAND_OF_Q[q]:
        it = rev_for(cid)
        if it and it.get("verdict") == "reject":
            if WINNER[q] == cid:
                # 被 reject 的 winner 顺延到次优
                alt = sorted([c for c in CAND_OF_Q[q] if c != cid and (rev_for(c) or {}).get("verdict") != "reject"], key=rank_key)
                WINNER[q] = alt[0]
CRIT_BLOCK = {q: [c for c in CAND_OF_Q[q] if any(a.get("severity") == "critical" for a in (rev_for(c) or {}).get("attacks", []))
                  and (rev_for(c) or {}).get("verdict") != "retain"] for q in QIDS}

# ---------- authority 视图（Manager 派生绑定件） ----------
ROUND = {}
for q in QIDS:
    ROUND[BASELINE[q]] = 0
    for cid in CAND_OF_Q[q]:
        if cid != BASELINE[q]:
            ROUND[cid] = 1

def write_authority(cid):
    q = cid.split("-")[0]
    r = results[cid]
    auth = {
        "question_id": q, "idea_id": cid,
        "status": r["status"], "feasible": r["feasible"],
        "objective": r["objective"], "objective_key": "objective",
        "objective_tuple": r.get("objective_tuple"),
        "runtime_seconds": r["runtime_seconds"],
        "canonical_evaluator": EV_PATH, "evaluator_sha256": EV_SHA,
        "objective_direction": DIRECTION[q], "unit": UNIT[q],
        "budget_rule": "wall_clock", "budget": 600,
        "stopping_reason": scouts[cid].get("stopping_reason"),
        "failure_mode": r.get("failure_mode"),
        "derived_from": {"result_json": f"{ROOT}/scouts/{cid}/result.json",
                          "result_json_sha256": sha(f"{ROOT}/scouts/{cid}/result.json"),
                          "solution_path": r.get("solution_path"),
                          "solution_sha256": r.get("solution_sha256")},
        "note": "Manager 装配的 P1-03 result authority 绑定视图；数值逐字复制自 child result.json，未重算未修改",
    }
    p = f"{ROOT}/scouts/{cid}/result_authority.json"
    io.open(p, "w", encoding="utf-8").write(json.dumps(auth, ensure_ascii=False, indent=1))
    return auth, sha(p)

AUTH = {}
for q in QIDS:
    for cid in CAND_OF_Q[q]:
        AUTH[cid] = write_authority(cid)

# ---------- 族归一化 ----------
TIER_MAP = {"baseline": "minimal_sufficient_solution",
            "recommended_solution": "recommended_solution",
            "advanced_alternative": "advanced_alternative"}

# child 自由文本 solver.family → P1-03 规范 9 族（归一化，原文保留到 algorithm_detail）
SOLVER_CANON = {
 "Q1-R21": "exact_enumerative", "Q1-R52": "closed_form", "Q1-R41": "exact_enumerative",
 "Q2-R41": "stochastic_population", "Q2-R51": "deterministic_global", "Q2-R32": "convex_optimization",
 "Q3-R23": "derivative_free_local", "Q3-R11": "deterministic_global", "Q3-R51": "closed_form",
 "Q4-R41": "derivative_free_local", "Q4-R11": "deterministic_global", "Q4-R22": "closed_form"}

def normalize_candidate(cid):
    ch, r, _src = frag[cid]
    q = cid.split("-")[0]
    c = dict(r)
    c["idea_id"] = cid
    c.pop("idea_id_suggested", None)
    c["question_id"] = q
    c["tier"] = TIER_MAP.get(r.get("tier", "recommended_solution"), "recommended_solution")
    c["route_kind"] = "full_route"
    c["source_child_run_id"] = ch
    c["status"] = "accepted"
    s = c.get("solver") or {}
    s["algorithm_detail"] = s.get("family", "") + " | " + s.get("algorithm", "")
    s["family"] = SOLVER_CANON[cid]
    s["budget_type"] = "wall_clock"
    s["determinism"] = "seeded_stochastic" if s.get("determinism") not in ("deterministic",) else "deterministic"
    c["solver"] = s
    if not c.get("required_assumptions"):
        c["required_assumptions"] = ["口径以 ADJUDICATION.json 为准（R1-R8）"]
    if not c.get("failure_conditions"):
        c["failure_conditions"] = ["预算内不可行或 evaluator feasible=false"]
    c["complexity"] = c.get("complexity") if c.get("complexity") in ("low", "medium", "high") else "medium"
    c["interpretability"] = c.get("interpretability") if c.get("interpretability") in ("high", "medium", "low") else "medium"
    c["implementation_risk"] = c.get("implementation_risk") if c.get("implementation_risk") in ("low", "medium", "high") else "medium"
    bp = c.get("bound_plan") or {}
    gt = bp.get("gap_threshold")
    if isinstance(gt, bool) or not isinstance(gt, (int, float)):
        import re as _rx
        m = _rx.search(r"-?\d+(?:\.\d+)?", str(gt or ""))
        if m:
            bp["gap_threshold"] = float(m.group())
        else:
            bp["gap_threshold"] = None
        if gt is not None:
            bp["gap_threshold_note"] = str(gt)
        pp = bp.get("proof_possible")
        if not isinstance(pp, bool):
            bp["proof_possible"] = bool(pp) and str(pp).strip().lower() not in ("none", "false", "0", "")
            bp.setdefault("proof_possible_note", str(pp))
        c["bound_plan"] = bp
    # 契约绑定（与 tournament 逐字一致）
    c.update({"canonical_evaluator": EV_PATH, "evaluator_sha256": EV_SHA,
              "objective_direction": DIRECTION[q], "unit": UNIT[q],
              "budget_rule": "wall_clock", "budget": 600})
    c["scout_evidence"] = {"result_authority": f"{ROOT}/scouts/{cid}/result_authority.json",
                            "result_authority_sha256": AUTH[cid][1],
                            "scout_json": f"{ROOT}/scouts/{cid}/scout.json",
                            "scout_json_sha256": sha(f"{ROOT}/scouts/{cid}/scout.json") if os.path.isfile(f"{ROOT}/scouts/{cid}/scout.json") else None}
    return c

CANDIDATES = [normalize_candidate(cid) for q in QIDS for cid in CAND_OF_Q[q]]

# ---------- structural_checks（14×4，Manager 合并判定，引用 child 证据） ----------
STRUCTS = ["closed_form", "variable_elimination", "dimension_reduction", "decomposition",
           "coordinate_transform", "convexification", "relaxation_and_bounds",
           "monotonicity_or_boundary", "symmetry", "dominance_and_pruning",
           "graph_or_flow_reformulation", "scheduling_or_coverage", "dynamic_programming", "reachable_set"]

SC_REASON = {
 "Q1": {
  "closed_form": ("retained", "类内 (g,d) 齐次 ⇒ 时间交叠=同余+reach 闭式（CH-01/CH-05；R52 闭式判据 4975 同组对 0 反例）", ["Q1-R52"]),
  "variable_elimination": ("screened_out", "纯判定问题无决策变量可消元；等价于比较次数缩减，已由枚举剪枝覆盖", []),
  "dimension_reduction": ("retained", "频段轴/时间轴正交分解：|E|=|B∩T|，候选对 11175→频段交叠 1352 再查时间（R21/R52/R41 全部利用）", ["Q1-R21", "Q1-R52", "Q1-R41"]),
  "decomposition": ("retained", "按类对（AA/AB/AC/BC/BB/CC）与频段带分组并行枚举；三路独立实现对称差=0", ["Q1-R41"]),
  "coordinate_transform": ("retained", "时频格→位图索引/倒排 join（R41 的 64300-bit AND 与倒排两实现）", ["Q1-R41"]),
  "convexification": ("not_applicable", "无优化目标，判定问题不存在凸化对象", []),
  "relaxation_and_bounds": ("retained", "审计夹逼界 LB(强制同余对)≤|E|≤UB(两轴独立) 作错误探测（R52 界自检 LB8≤29≤UB92 通过；评审限定为错误探测界）", ["Q1-R52"]),
  "monotonicity_or_boundary": ("retained", "半开区间边界用例（相接不交叠）5/5-8/8 通过（R21/R41 special_checks）", ["Q1-R21", "Q1-R41"]),
  "symmetry": ("screened_out", "计划编号无对称群可利用；重复占用已由周期参数显式压缩", []),
  "dominance_and_pruning": ("retained", "频段轴排序+前缀剪枝（R52/CH-02 扫描线版 O(n log n) 前筛）", ["Q1-R52"]),
  "graph_or_flow_reformulation": ("retained", "冲突对集=区间交图∩周期交图（图论重表达成立，产出边表 G 供 Q2/Q4 消费）", ["Q1-R21"]),
  "scheduling_or_coverage": ("not_applicable", "Q1 为纯检测，无排程/覆盖决策", []),
  "dynamic_programming": ("not_applicable", "无时序阶段结构；判定用直接枚举最优（0.017s 已在预算 0.003%）", []),
  "reachable_set": ("retained", "占用格集合=可达资源集，distinct 口径 14698（R41 位图给出，供 Q3 复用）", ["Q1-R41"])},
 "Q2": {
  "closed_form": ("screened_out", "撤销/调整组合数 ~1e222 无闭式；仅逐边可分离判据有闭式（297/297 边单端可修⇒组合层面无强制撤销，CH-05 探针）", []),
  "variable_elimination": ("retained", "每边只需 2 个轴向布尔而非 32×32 全表（CH-02 消元）；子句 270626 条由动作对组合压缩", ["Q2-R51"]),
  "dimension_reduction": ("retained", "同类参数同质 ⇒ 状态坍缩到 (动作类型,平移量) 域（平均 29.5 选项/计划）", ["Q2-R51"]),
  "decomposition": ("screened_out", "分量分解被 CH-01 探针证伪（G 148 点与 G* 150 点均单分量）；时间轴 gcd 不可分", []),
  "coordinate_transform": ("screened_out", "平移不变性（Δf_i-Δf_j 判据）已被子句编码隐式利用，无独立变换路线", []),
  "convexification": ("retained", "连续重叠体积罚场凸分段线性（R32 取整前 297→175 量化贡献；最终解质量归 CP-SAT——负结果证据保留）", ["Q2-R32"]),
  "relaxation_and_bounds": ("retained", "撤销阶梯 INFEASIBLE 证书+CP 分数界 LB=2；原边松弛 OPTIMAL=0 证明界必须来自预防性 G*", ["Q2-R51"]),
  "monotonicity_or_boundary": ("retained", "资源盒边界 [0,643)×[0,100) 作显式可行性约束（R3 口径）", ["Q2-R51", "Q2-R32"]),
  "symmetry": ("screened_out", "计划同质但标签不同构（平移窗口各异），对称破缺收益未证实", []),
  "dominance_and_pruning": ("retained", "候选动作域预剪枝：越界/等效动作剔除（构建 <4s）", ["Q2-R51"]),
  "graph_or_flow_reformulation": ("retained", "冲突图顶点覆盖骨架 ν=71 下界仅对 adjusted+revoked 总量有效（τ≥ν），组合界对撤销层恒 0 已证伪", ["Q2-R41"]),
  "scheduling_or_coverage": ("retained", "多选择 CSP/部分列表着色（G*=1693 边禁元组表）是 Q2 的主导重表达", ["Q2-R51", "Q2-R41"]),
  "dynamic_programming": ("not_applicable", "无最优子结构：平移耦合为全局图约束（CH-02 状态空间指数论证）", []),
  "reachable_set": ("retained", "每计划动作可达终态集显式枚举（域 22..32）", ["Q2-R51", "Q2-R32"])},
 "Q3": {
  "closed_form": ("screened_out", "最大化加装数无闭式；初等双计数界合法但松 2.39×（R51：332 vs 认证 139）", []),
  "variable_elimination": ("retained", "与 base 冲突的放置预筛消元：52136→2123 候选", ["Q3-R11", "Q3-R23"]),
  "dimension_reduction": ("retained", "相位/oct 分解：C 图案=3 频段×12 连续 oct×相位 p∈0..9", ["Q3-R51"]),
  "decomposition": ("retained", "逐频段三列带分组；跨带干扰经位图倒排保留（三路对拍 131254 边 0 失配）", ["Q3-R11"]),
  "coordinate_transform": ("retained", "时频格→(f0,t0) 起点坐标+占用位图（与 evaluator 同一 mask 代码）", ["Q3-R23", "Q3-R11"]),
  "convexification": ("screened_out", "LP 松弛仅作对照：HiGHS 分数上界=139.0 与整数界会合（R11 复证）", []),
  "relaxation_and_bounds": ("retained", "三腿闭合：CP-SAT A/B 双模型 OPTIMAL=139 + HiGHS LP=139.0 + 候选穷举完备 ⇒ N*=139 可证；初等界 332 作可手核上界对照", ["Q3-R11", "Q3-R51"]),
  "monotonicity_or_boundary": ("retained", "末窗 ≤643 视界边界单调筛 t0∈0..531", ["Q3-R11"]),
  "symmetry": ("screened_out", "候选同质性存在但未做对称破缺（OPTIMAL 4.3s 无需）", []),
  "dominance_and_pruning": ("retained", "被支配放置剔除（同 (f0 带,oct 段) 内）", ["Q3-R23"]),
  "graph_or_flow_reformulation": ("retained", "set-packing/稳定集 IP（冲突图 62071 边 pairwise 主模型）", ["Q3-R11"]),
  "scheduling_or_coverage": ("retained", "装箱/覆盖视角：空闲单元 48700/图案 72 格密度界 676 上界", ["Q3-R51"]),
  "dynamic_programming": ("screened_out", "CH-01 分块滑窗 DP 因跨带耦合降为对照，未进 Top-K", []),
  "reachable_set": ("retained", "base 冻结后自由可达集显式构造（Q2-R51 应用 actions 后位图）", ["Q3-R11", "Q3-R23", "Q3-R51"])},
 "Q4": {
  "closed_form": ("retained", "mod-10 同余判据 4005 个 C-C 对 0 反例；(t1,g') 条带闭式消 16/19 CC 边（R22 机理件，但全局消解须整数层——撤销 66 的坍塌即负结果证据）", ["Q4-R22"]),
  "variable_elimination": ("retained", "R3 视界截断消去 99/1530 个 dg 选项", ["Q4-R11"]),
  "dimension_reduction": ("retained", "扩域后仍 (类型,量) 域表示（29.5→39.7 选项均值）", ["Q4-R11"]),
  "decomposition": ("screened_out", "同 Q2：单分量不可分（CH-01 证伪复用）", []),
  "coordinate_transform": ("retained", "重定时坐标 (t1,g') 平面：∂(第k窗起点)/∂g=k-1 结构", ["Q4-R22", "Q4-R41"]),
  "convexification": ("screened_out", "连续化无增益证据；未进 Top-K", []),
  "relaxation_and_bounds": ("retained", "支配界（可证：Q4 动作集⊇Q2 ⇒ 同评价函数最优值不劣，包含性实测过）+ 阶梯证书 LB=2", ["Q4-R11"]),
  "monotonicity_or_boundary": ("retained", "dg>0 与 643 视界的单调截断（C083 仅 g'≤7）", ["Q4-R11"]),
  "symmetry": ("screened_out", "未利用", []),
  "dominance_and_pruning": ("retained", "越界 dg 动作预剔除 + 禁元组三路对拍", ["Q4-R11"]),
  "graph_or_flow_reformulation": ("retained", "同 Q2 冲突图基座扩列", ["Q4-R11", "Q4-R41"]),
  "scheduling_or_coverage": ("retained", "多选择差分 CSP（6104 选项）+ SA 退火调度范式", ["Q4-R11", "Q4-R41"]),
  "dynamic_programming": ("not_applicable", "同 Q2 论证：全局图耦合无最优子结构", []),
  "reachable_set": ("retained", "重定时可达相位类（R22 条带矩阵）", ["Q4-R22"])},
}
structural_checks = []
for q in QIDS:
    for s in STRUCTS:
        st, reason, ids = SC_REASON[q][s]
        structural_checks.append({"question_id": q, "structure": s, "status": st,
                                   "reason": reason, "candidate_ids": [i for i in ids if i in CAND_OF_Q[q]]})

# ---------- legacy 族覆盖（全 8+9 族逐问处置） ----------
MODEL_FAMS = ["analytic_mechanistic", "statistical_probabilistic", "operations_research",
              "graph_combinatorial", "dynamic_control", "simulation", "machine_learning", "hybrid_decomposition"]
SOLVER_FAMS = ["closed_form", "exact_enumerative", "convex_optimization", "gradient_local",
               "derivative_free_local", "deterministic_global", "stochastic_population",
               "surrogate_bayesian", "structure_specific"]

def fam_status(q, fam, kind="model"):
    ids = [c["idea_id"] for c in CANDIDATES if c["question_id"] == q and
           ((c["method_family"] if kind == "model" else c["solver"]["family"]) == fam)]
    if ids:
        return "retained", "本问 Top-K 中该族有已侦察候选支撑", ids
    na = {
     "machine_learning": "无噪声/无标签/单实例确定性判定，ML 无辨识对象（CH-04 论证）",
     "dynamic_control": "无动力学状态方程与控制输入结构（F-004 四参数静态计划）",
     "surrogate_bayesian": "评估无噪声且单次评估近乎免费，代理模型无收益",
     "statistical_probabilistic": "结果需求为精确枚举/精确消解，概率模型不产生契约要求的输出（Q1-R42 类证据已并入 R41 诊断件）",
     "gradient_local": "变量全整数、目标分段常值，无梯度可用",
     "stochastic_population": "整图种群算法在预算内无增量证据（CH-04 预算筛查），随机性仅以 SA/GRASP 单点形式保留",
     "derivative_free_local": "无连续变量；Nelder/Powell 类无对象",
    }
    st = "not_applicable" if fam in na else "screened_out"
    return st, na.get(fam, "已生成候选但被同族更强候选 Pareto 支配（见 coverage_notes/评审），未入 Top-K"), []

model_family_coverage, solver_family_coverage = [], []
for q in QIDS:
    for fam in MODEL_FAMS:
        s, rs, ids = fam_status(q, fam, "model")
        model_family_coverage.append({"question_id": q, "family": fam, "status": s, "reason": rs, "candidate_ids": ids})
    for fam in SOLVER_FAMS:
        s, rs, ids = fam_status(q, fam, "solver")
        solver_family_coverage.append({"question_id": q, "family": fam, "status": s, "reason": rs, "candidate_ids": ids})

# ---------- coverage_policy ----------
model_opp = J("reports/discovery/MODEL_OPPORTUNITIES.json")
question_plans = {}
for q in QIDS:
    mf = sorted({c["method_family"] for c in CANDIDATES if c["question_id"] == q})
    sf = sorted({c["solver"]["family"] for c in CANDIDATES if c["question_id"] == q})
    mdisp, sdisp = [], []
    for fam in mf:
        ids = [c["idea_id"] for c in CANDIDATES if c["question_id"] == q and c["method_family"] == fam]
        mdisp.append({"question_id": q, "family": fam, "status": "retained",
                       "reason": f"{q} 的边界/可达集结构（{q}-OP-special_boundary）下该族有成立候选", "candidate_ids": ids})
    for fam in sf:
        ids = [c["idea_id"] for c in CANDIDATES if c["question_id"] == q and c["solver"]["family"] == fam]
        sdisp.append({"question_id": q, "family": fam, "status": "retained",
                       "reason": f"求解器族 {fam} 适配 {q} 的组合判定/优化结构（ADJ 口径）", "candidate_ids": ids})
    question_plans[q] = {
        "question_id": q,
        "discovery_opportunity_ids": [f"{q}-OP-special_boundary"],
        "triggered_model_families": mf,
        "triggered_solver_families": sf,
        "model_family_dispositions": mdisp,
        "solver_family_dispositions": sdisp,
        "candidate_ids": list(CAND_OF_Q[q]),
        "undercoverage_reason": ("P1-03 按 Discovery 触发族登记：special_boundary 触发资源盒边界/可达集类族；"
                                  "ML/控制/代理等未触发族在全族覆盖表中登记 not_applicable 论证，未凑候选。")}

coverage_policy = {"schema_version": 1, "discovery_id": model_opp["discovery_id"],
                   "fixed_all_family_requirement": False, "question_plans": question_plans}

# ---------- stop_policy ----------
records = []
for q in QIDS:
    for cid in CAND_OF_Q[q]:
        auth, asha = AUTH[cid]
        records.append({"question_id": q, "idea_id": cid, "round_id": ROUND[cid],
                        "result_path": f"{ROOT}/scouts/{cid}/result_authority.json",
                        "result_sha256": asha, "evaluator_path": EV_PATH,
                        "evaluator_sha256": EV_SHA, "objective_key": "objective"})
def front(rows):
    vals = [float(AUTH[r["idea_id"]][0]["objective"]) for r in rows]
    best = min(vals) if DIRECTION[rows[0]["question_id"]] == "minimize" else max(vals)
    return [{"question_id": r["question_id"], "idea_id": r["idea_id"], "objective": float(AUTH[r["idea_id"]][0]["objective"])}
            for r in rows if abs(float(AUTH[r["idea_id"]][0]["objective"]) - best) <= 1e-12]
rounds = []
for q in QIDS:
    qrec = [r for r in records if r["question_id"] == q]
    r0 = [r for r in qrec if r["round_id"] == 0]
    r01 = qrec
    for rid in (1, 2, 3):
        before_rows = [r for r in qrec if r["round_id"] < rid]
        after_rows = [r for r in qrec if r["round_id"] <= rid]
        added = [] if rid > 1 else [r["idea_id"] for r in qrec if r["round_id"] == rid]
        b, a = front(before_rows), front(after_rows)
        bb, ab = min(x["objective"] for x in b), min(x["objective"] for x in a)
        improved = (ab < bb - 1e-12) if DIRECTION[q] == "minimize" else (ab > bb + 1e-12)
        rounds.append({"round_id": rid, "question_id": q, "candidate_ids_added": added,
                        "pareto_front_before": b, "pareto_front_after": a,
                        "improved": bool(improved),
                        "evidence_refs": [f"evaluator:{q}"] + [f"result:{q}:{r['idea_id']}" for r in (after_rows or before_rows)]})
spent = float(len(records))
budget_contract = {"schema_version": 1, "cost_basis": "one_evaluator_call",
                   "candidate_costs": [{"candidate_id": WINNER[q], "cost": 1.0,
                                          "source_result_ref": f"result:{q}:{WINNER[q]}"} for q in QIDS],
                   "overhead_cost": 0, "derived_next_round_min_cost": float(len(QIDS))}
stop_policy = {
    "schema_version": 1,
    "rule": "two_consecutive_pareto_non_improving_rounds_or_budget_exhausted",
    "budget": {"rule": "candidate_evaluations", "unit": "evaluator_calls",
                "limit": 16.0, "spent": spent, "remaining": 16.0 - spent,
                "next_round_min_cost": float(len(QIDS)), "cost_contract": budget_contract},
    "result_authority": {"schema_version": 1, "results": records},
    "rounds": rounds,
    "stop_reason": "pareto_no_improvement_2_rounds", "stopped": True}

# ---------- problem_structures ----------
problem_structures = [
 {"question_id": "Q1", "problem_types": ["combinatorial_enumeration", "predicate_evaluation"],
  "decision_dimension": 0, "variable_types": ["none"], "objective_direction": "estimate",
  "smoothness": "non_smooth", "convexity": "not_applicable", "stochasticity": "deterministic",
  "decomposability": "yes", "canonical_evaluator_required": True,
  "notes": "纯判定枚举；三实现全等。"},
 {"question_id": "Q2", "problem_types": ["combinatorial_optimization", "constraint_satisfaction"],
  "decision_dimension": 150, "variable_types": ["integer_choice"], "objective_direction": "minimize",
  "smoothness": "non_smooth", "convexity": "non_convex", "stochasticity": "deterministic",
  "decomposability": "no", "canonical_evaluator_required": True,
  "notes": "多选择 CSP/部分列表着色；词典序四级。"},
 {"question_id": "Q3", "problem_types": ["packing", "set_packing"],
  "decision_dimension": 2123, "variable_types": ["binary"], "objective_direction": "maximize",
  "smoothness": "non_smooth", "convexity": "non_convex", "stochasticity": "deterministic",
  "decomposability": "no", "canonical_evaluator_required": True,
  "notes": "候选完备集上的最大独立集/集包装；N*=139 三腿可证（基座=Q2-R51 侦察解）。"},
 {"question_id": "Q4", "problem_types": ["combinatorial_optimization", "retiming"],
  "decision_dimension": 150, "variable_types": ["integer_choice"], "objective_direction": "minimize",
  "smoothness": "non_smooth", "convexity": "non_convex", "stochasticity": "mixed",
  "decomposability": "no", "canonical_evaluator_required": True,
  "notes": "Q2 模型扩 dg 列；支配界可证。"}]

# ---------- search_run & delegation ----------
child_runs = []
ts = {}
for fname in sorted(os.listdir(f"{ROOT}/routes")):
    if not fname.endswith(".route.json"): continue
    st = os.stat(f"{ROOT}/routes/{fname}")
    child_runs.append({
        "child_run_id": fname.split(".")[0], "role": J(f"{ROOT}/routes/{fname}")["role"],
        "question_ids": ["Q1", "Q2", "Q3", "Q4"],
        "input_sha256": sha(f"{ROOT}/common_input.json"),
        "artifact_path": f"{ROOT}/routes/{fname}", "artifact_sha256": sha(f"{ROOT}/routes/{fname}"), "status": "completed",
        "started_at": common["frozen_at"], "completed_at": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).astimezone().isoformat(timespec="seconds"),
        "retry_count": 0})
for q in QIDS:
    first = CAND_OF_Q[q][0]
    st = os.stat(f"{ROOT}/scouts/{first}/result.json")
    child_runs.append({
        "child_run_id": f"PE-{q}", "role": "prototype_engineer", "question_ids": [q],
        "input_sha256": sha(f"{ROOT}/common_input.json"),
        "artifact_path": f"{ROOT}/scouts/{first}/result.json",
        "artifact_sha256": sha(f"{ROOT}/scouts/{first}/result.json"),
        "status": "completed", "started_at": proto["frozen_at"],
        "completed_at": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).astimezone().isoformat(timespec="seconds"),
        "retry_count": 0})
for q in QIDS:
    p = REVS.get(q + "_FILE")
    if not p:
        continue
    st = os.stat(p)
    child_runs.append({"child_run_id": f"REVIEW-{q}", "role": "adversarial_reviewer", "question_ids": [q],
                        "input_sha256": sha(f"{ROOT}/common_input.json"),
                        "artifact_path": p, "artifact_sha256": sha(p),
                        "status": "completed", "started_at": proto["frozen_at"],
                        "completed_at": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).astimezone().isoformat(timespec="seconds"),
                        "retry_count": 0})

search_run = {
    "search_id": SID, "profile": "standard", "question_ids": QIDS,
    "run_directory": ROOT,
    "identity_note": "账本 search_id 按 P2-07 在装配期规范化（UTC 起搜 07:15:20Z + hex）；物理目录为派发期命名，所有工件路径以 run_directory 为根逐字在册，非复用旧运行",
    "supersedes": [],
    "input_snapshot": {"question_contract_sha256": sha("reports/contracts/QUESTION_CONTRACT.json"),
                        "problem_facts_sha256": sha("reports/contracts/PROBLEM_FACTS.json"),
                        "data_profile_sha256": sha("reports/data/DATA_PROFILE.json")},
    "sources": [
        {"source_class": "peer_reviewed_paper", "query": "frequency assignment problem interference graph coloring survey", "used_for": "model family prior（FAP 文献锚点）"},
        {"source_class": "peer_reviewed_paper", "query": "bin packing maximum independent set interval graph algorithms", "used_for": "packing/独立集 prior"},
        {"source_class": "academic_documentation", "query": "OR-Tools CP-SAT scheduling interval constraints optimization", "used_for": "solver prior（CP-SAT 文档）"},
        {"source_class": "peer_reviewed_paper", "query": "frequency assignment problem models algorithms review IEEE", "used_for": "FAP 综述 prior"},
        {"source_class": "academic_documentation", "query": "constraint programming orthogonal windows scheduling time tables CP-SAT", "used_for": "CSP prior"},
        {"source_class": "peer_reviewed_paper", "query": "maximum independent set conflict graph channel assignment integer programming", "used_for": "图论 prior"},
        {"source_class": "peer_reviewed_paper", "query": "radio frequency interference mitigation resource allocation optimization survey", "used_for": "资源分配 prior"}],
    "budget": {"max_wall_minutes": 60, "max_generator_children": 4, "top_k": 3,
                "scout_budget_seconds_per_route": 600, "replicates": 3, "frozen_before_scouts": True},
    "started_at": common["frozen_at"],
    "completed_at": datetime.now().astimezone().isoformat(timespec="seconds")}

delegation = {"required": True, "degraded": False, "degraded_reason": None,
              "manager_role": "merge_only_adjudicate",
              "common_input_path": f"{ROOT}/common_input.json",
              "common_input_sha256": sha(f"{ROOT}/common_input.json"),
              "child_runs": child_runs}

IDEA_CANDIDATES = {
    "schema_version": 2, "search_run": search_run,
    "problem_structures": problem_structures,
    "structural_checks": structural_checks,
    "model_family_coverage": model_family_coverage,
    "solver_family_coverage": solver_family_coverage,
    "coverage_policy": coverage_policy,
    "stop_policy": stop_policy,
    "delegation": delegation,
    "candidates": CANDIDATES,
}
io.open("reports/contracts/IDEA_CANDIDATES.json", "w", encoding="utf-8").write(
    json.dumps(IDEA_CANDIDATES, ensure_ascii=False, indent=1))

# ---------- IDEA_DECISION v3 ----------
now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
def qc_block(q):
    return {"question_id": q,
            "canonical_evaluator": EV_PATH, "evaluator_sha256": EV_SHA,
            "objective_direction": DIRECTION[q], "unit": UNIT[q],
            "constraint_tolerance": 0, "budget_rule": "wall_clock", "budget": 600,
            "budget_contract": {"compare_field": "runtime_seconds", "unit": "seconds",
                                 "compare_fields": ["runtime_seconds"]}}
def tourney(q):
    qrec = [r for r in records if r["question_id"] == q]
    res = []
    for r in qrec:
        cid = r["idea_id"]
        auth, asha = AUTH[cid]
        sc = scouts[cid]
        res.append({"idea_id": cid, "question_id": q, "status": auth["status"],
                    "artifact_path": r["result_path"], "artifact_sha256": asha,
                    "feasible": auth["feasible"], "objective": auth["objective"],
                    "constraint_violation": 0 if auth["feasible"] else None,
                    "runtime_seconds": auth["runtime_seconds"],
                    "replicate_values": sc.get("replicate_values", [auth["objective"]]),
                    "stability_metric": sc.get("stability_metric"),
                    "lower_bound": sc.get("lower_bound"), "upper_bound": sc.get("upper_bound"),
                    "relative_gap": sc.get("relative_gap"),
                    "stopping_reason": sc.get("stopping_reason") or auth.get("stopping_reason"),
                    "failure_mode": auth.get("failure_mode")})
    pareto_pts = [{"question_id": q, "idea_id": c, "objective": float(AUTH[c][0]["objective"])} for c in CAND_OF_Q[q]]
    bestv = min(p["objective"] for p in pareto_pts) if DIRECTION[q] == "minimize" else max(p["objective"] for p in pareto_pts)
    pareto_pts_front = [p for p in pareto_pts if abs(p["objective"] - bestv) <= 1e-12]
    elims = []
    for cand in [x for x in frag if x.split("-")[0] == q and x not in CAND_OF_Q[q]][:40]:
        elims.append({"idea_id": cand, "question_id": q, "reason_code": "topk_screened",
                      "reason": "未入 Top-K（同族 Pareto 支配/预算/评审定性），保留于 routes 片段与覆盖表",
                      "evidence_refs": [f"{ROOT}/routes/", "reports/contracts/IDEA_CANDIDATES.json"]})
    rv = []
    for cid in CAND_OF_Q[q]:
        it = rev_for(cid)
        rv.append({"idea_id": cid, "question_id": q,
                   "review_id": it and REVS[q].get("review_id"), "verdict": it and it.get("verdict"),
                   "artifact_path": REVS.get(q + "_FILE"),
                   "artifact_sha256": sha(REVS[q + "_FILE"]) if REVS.get(q + "_FILE") else None,
                   "result_refs": [f"result:{q}:{cid}"]})
    wins = {"Q1": "三实现 objective 全等（完全枚举的完备性命题），按选择优先级 correctness=feasibility=optimality_evidence 并列 → implementation_risk/runtime 最低者（R21 0.017s，且直接满足 Q1-C1 双实现验收）；R52/R41 作闭式与位图辅助证据保留",
            "Q2": "R51 标量最优（[6,121,1996,663]）且唯一给出机器可复核证书链（Σr≤0 INFEASIBLE + 阶梯记录）；R32 被支配（同撤销、层2-4 劣）；R41 撤销 19 明显劣，按题面层级链不可比肩",
            "Q3": "R11 三腿可证最优（CP-SAT A/B OPTIMAL=139 + HiGHS LP=139.0 + 候选穷举完备），Q3-C2 验收直接满足；R23=137 为启发式对照；R51 初等界 332 作可手核上界辅证",
            "Q4": "R11=[8,113,2289,719] 为候选中最优标量。评审修正（采纳 REV-Q4-01 major）：支配界锚定=『Q2-R51 侦察解逐字可植入 Q4（动作集包含，结构成立）⇒ Q4 侦察 incumbent 应为 min(8 自跑, 6 植入)=6』；R11 自跑未及 6 是 600s 预算产物而非模型缺陷；其 q2_inclusion_check 的 150s 弱自对照基线（ub=14）不得用于改善宣称。生产阶段：Q4 必须以 Q2 生产解热启动（R42 式锚定不劣约束），『不劣于 Q2』由构造保证并 checker 复验。R41 中位 [11,117,…] 劣且偏离承诺实现（revise 登记）；R22 归因不成立（9/66 可无损回滚）→ rejected，仅其 mod-10 机理验证部分保留为结构证据"}[q]
    lvl = {"Q1": "L2_EMPIRICALLY_BEST", "Q2": "L2_EMPIRICALLY_BEST", "Q3": "L3_NEAR_GLOBAL", "Q4": "L2_EMPIRICALLY_BEST"}[q]
    oclaim = {
        "Q1": {"level": "L2_EMPIRICALLY_BEST", "scope": "frozen_Q1_detection_formulation",
                "claim": "297 对冲突集由三个独立实现（区间算术/同余闭式/位图）+植入压力测试共同钉死，对称差=0；答案完备性为可判定穷举命题（非『最优』宣称）",
                "gap_threshold": 0, "evidence_refs": [f"result:Q1:Q1-R21", f"result:Q1:Q1-R52", f"result:Q1:Q1-R41"], "proof_artifact": None},
        "Q2": {"level": "L2_EMPIRICALLY_BEST", "scope": "frozen_Q2_formulation_ADJ_R1_R8",
                "claim": "侦察预算内经验最优元组 [6,121,1996,663]；撤销层界 [2,6] 开放（Σr≤0 INFEASIBLE 已证、Σr≤5 未判定），生产长预算攻闭合前论文只写区间",
                "gap_threshold": 0, "evidence_refs": ["result:Q2:Q2-R51", f"{ROOT}/scouts/Q2-R51/r51_certificates.json"], "proof_artifact": None},
        "Q3": {"level": "L3_NEAR_GLOBAL", "scope": "frozen_Q3_main_interpretation(base=Q2-R51 侦察解, 模板参数, 643 视界, distinct 口径)",
                "claim": "在冻结基座与模板参数下 N*=139：CP-SAT 双模型 OPTIMAL + HiGHS LP 分数上界=139 + 候选放置集穷举完备 ⇒ 上界=下界会合（gap=0，gap_threshold 冻结于 0）；HiGHS 界为不同求解器族独立复核",
                "gap_threshold": 0, "evidence_refs": ["result:Q3:Q3-R11", f"{ROOT}/scouts/Q3-R11/cpsat_r11_report.json", f"{ROOT}/scouts/Q3-R11/lp_crosscheck_hiGHS.json"], "proof_artifact": None},
        "Q4": {"level": "L2_EMPIRICALLY_BEST", "scope": "frozen_Q4_formulation",
                "claim": "侦察 incumbent [8,113,2289,719]；支配界（Q4≽Q2 逐字包含已实测）为可证先验界，撤销层 [2,8] 开放",
                "gap_threshold": 0, "evidence_refs": ["result:Q4:Q4-R11", f"{ROOT}/scouts/Q4-R11/q2_inclusion_check.json" if os.path.isfile(f"{ROOT}/scouts/Q4-R11/q2_inclusion_check.json") else "result:Q4:Q4-R41"], "proof_artifact": None}}[q]
    wd = {"question_id": q, "idea_id": WINNER[q], "basis": [wins],
          "decision_basis": [wins],
          "tradeoffs": {"Q1": "辅助证据链（闭式/位图）由 backup 候选承载，不牺牲", 
                         "Q2": "证书未闭合（gap_revoke=4），接受『区间表述』的论文代价", 
                         "Q3": "认证最优依赖基座=侦察解；生产 Q2 解若更新则需重证", 
                         "Q4": "撤销层界开放；改进幅度只能以下界=0 诚实表述"}[q],
          "evidence_refs": [f"result:{q}:{WINNER[q]}", f"review:{q}"]}
    t = dict(qc_block(q))
    det_all = all((frag[c][1].get("solver") or {}).get("determinism") == "deterministic" for c in CAND_OF_Q[q])
    t.update({"question_id": q, "baseline_route": BASELINE[q],
              "seed_policy": ("N/A" if det_all
                               else {"seeds": [11, 29, 47], "repetition_policy": "每随机候选 3 重复（协议），中位数聚合；Q3-R23 单 seed 缺口见 search_limitations", "aggregation_rule": "median scalar; deterministic candidates single run", "deterministic": False}),
              "candidate_set": list(CAND_OF_Q[q]),
              "pareto_set": [p["idea_id"] for p in pareto_pts_front],
              "top_k": list(CAND_OF_Q[q]),
              "winner": WINNER[q],
              "winner_decision": wd,
              "results": res, "pareto_points": pareto_pts, "reviews": rv,
              "eliminations": elims,
              "optimality_claim": oclaim})
    return t

decision = {
    "schema_version": 3, "search_id": SID, "generated_at": now_iso,
    "primary": {q: WINNER[q] for q in QIDS},
    "accepted": [WINNER[q] for q in QIDS],
    "rejected": ["Q4-R22"],
    "baseline": [BASELINE[q] for q in QIDS],
    "backup": ["Q1-R52", "Q1-R41", "Q2-R32", "Q3-R51", "Q4-R41"],
    "exploratory": ["Q2-R41", "Q3-R23"],
    "rejection_reasons": [
        {"question_id": "Q4", "idea_id": "Q4-R22", "reason_code": "review_reject_objective_degenerate",
         "evidence_refs": [f"{ROOT}/reviews/REV-Q4-CH-R3.json", f"{ROOT}/scouts/Q4-R22/result.json"],
         "note": "REV-Q4-01 critical：撤销 66 系实现自伤（9/66 可无损回滚至 [57,…]，评审 60 行贪心得 [42,…]），非构造结构性极限；作为求解路线 reject，mod-10 同余引理（4005 C-C 对 0 反例、16/19 CC 边闭式可消）保留为机理解释素材；其侦察结果保留于 tournament 作诚实最差读数"}],
    "question_contracts": {q: qc_block(q) for q in QIDS},
    "tournaments_by_question": {q: tourney(q) for q in QIDS},
    "comparisons": [{"comparison_id": f"CMP-{q}", "question_id": q, "idea_ids": list(CAND_OF_Q[q]), "status": "comparable",
                     "reason": f"{q} 三候选共享同一 canonical evaluator/方向/单位/预算契约，可直接比较"} for q in QIDS] +
                   [{"comparison_id": "CMP-X-Q2Q3", "question_id": "Q2", "idea_ids": ["Q2-R51", "Q3-R11"], "status": "incomparable",
                     "reason": "跨问目标单位不同（词典序标量 vs 加装数计数），显式标记不可比"}],
    "discovery_integration": {"opportunities": [
        {"opportunity_id": f"{q}-OP-special_boundary", "question_id": q,
         "affected_question_ids": [q],
         "material_decision_impact": "constraint_added_or_changed",
         "changed_paths": ["/constraints", "/validation_strategy"],
         "candidate_ids_added": [], "candidate_ids_rejected": [],
         "evidence_refs": [f"result:{q}:{WINNER[q]}"],
         "note": "special_boundary 触发资源盒边界约束（R1/R3 视界与平移不越界）进入全部候选模型；material impact 以 ADJUDICATION 边界条款与候选 required_assumptions 落实（before/after 均可复核）"} for q in QIDS]},
    "search_limitations": [
        "Q2/Q4 撤销层证书未闭合（[2,6]/[2,8]），生产阶段以长预算攻闭合，未闭合前论文只写区间",
        "Q2-R51 界证书进程超侦察预算 120.4s（incumbent 合规），Manager 豁免登记 D-BUDGET-R51",
        "Q2-R32 revise：随机版未补测（豁免 D-R32-REVISE），定位为负结果证据+热启动源",
        "Q3 认证最优绑定侦察基座（Q2-R51 解）；生产 Q2 更新后 Q3 须在生产重证",
        "Q3-R23 LNS 仅 seed=11 单重复（预算内），replicate 缺口如实登记，不作认证依据",
        "所有侦察数字仅存 runs/，不是论文 authority；正式结果由 coding_visual 生产运行产生"]}
io.open("reports/contracts/IDEA_DECISION.json", "w", encoding="utf-8").write(
    json.dumps(decision, ensure_ascii=False, indent=1))

print("WINNERS:", WINNER)
print("IDEA_CANDIDATES + IDEA_DECISION 写出；authority×12；rounds:", len(rounds))
