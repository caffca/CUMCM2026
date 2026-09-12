# -*- coding: utf-8 -*-
"""FMS v4 装配器（重写）：polymorphic kind 字段齐备；computation_contract 与 winner route
solver 逐字一致；参数 source_path/source_sha256 自洽（同源计算）；formulation_sha256 用官方 fms_v4。"""
import hashlib, io, json, os, sys, datetime

sys.path.insert(0, r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\6verity\scripts")
import fms_v4  # noqa

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

ROOT = "runs/competitive/CS-20260911T071520-D2026"
EV = f"{ROOT}/canonical_evaluator.py"; EV_SHA = sha(EV)
ADJ = f"{ROOT}/ADJUDICATION.json"; ADJ_SHA = sha(ADJ)
PF = "reports/contracts/PROBLEM_FACTS.json"; PF_SHA = sha(PF)
STAR = f"{ROOT}/scouts/Q2-R51/star_edges.json"; STAR_SHA = sha(STAR)
DEC = "reports/contracts/IDEA_DECISION.json"; DEC_SHA = sha(DEC)
CANDS = json.load(io.open("reports/contracts/IDEA_CANDIDATES.json", encoding="utf-8"))
CIDX = {c["idea_id"]: c for c in CANDS["candidates"]}
DECJ = json.load(io.open(DEC, encoding="utf-8"))
WIN = {q: DECJ["primary"][q] for q in ["Q1", "Q2", "Q3", "Q4"]}
SID = DECJ["search_id"]

def P(pid, val, unit, source, source_path, deriv=""):
    e = {"id": pid, "value": val, "unit": unit, "source": source,
         "source_sha256": sha(source_path), "source_path": source_path}
    if deriv: e["derivation"] = deriv
    return e

def R(rid, kind, expr, units_, var=None, evd=None):
    e = {"id": rid, "relation_kind": kind, "expression": expr, "units": units_}
    if var: e["variables"] = var
    if evd: e["evidence_refs"] = evd
    return e

def dbind(q):
    return {"question_id": q, "opportunity_ids": [f"{q}-OP-special_boundary"],
            "finding_ids": [f"{q}-F-special_boundary"], "affected_question_ids": [q],
            "material_decision_impacts": ["constraint_added_or_changed"],
            "formulation_paths": ["/constraints", "/numerical_precision"],
            "selected_candidate_ids": [WIN[q]], "rejected_candidate_ids": [],
            "evidence_refs": ["reports/discovery/MODEL_OPPORTUNITIES.json", ADJ]}

# planner 任务展开（production planner 从 budget.planner_task_expansion 派生 tasks）
_SB = {"l1": 800, "ladder": 250, "l2": 300, "l3": 100, "l4": 50}
EXP = {
 "Q1": {"impl": "code/prod/q1_solve.py", "timeout": 600, "wall": 1200,
        "cases": [{"variant": "interval"}, {"variant": "bitmap"}, {"variant": "congruence"},
                   {"variant": "check", "stress_trials": 400}]},
 "Q2": {"impl": "code/prod/q2_solve.py", "timeout": 1700, "wall": 1700,
        "cases": [{"variant": "cpsat_lex", "workers": 4, "stage_budget": _SB,
                    "hint": "runs/competitive/CS-20260911T071520-D2026/scouts/Q2-R51/solution_actions.json"},
                   {"variant": "cpsat_lex", "workers": 1, "stage_budget": _SB,
                    "hint": "runs/competitive/CS-20260911T071520-D2026/scouts/Q2-R51/solution_actions.json"},
                   {"variant": "grasp", "grasp_seed": 11, "budget": 240},
                   {"variant": "grasp", "grasp_seed": 29, "budget": 240},
                   {"variant": "grasp", "grasp_seed": 47, "budget": 240},
                   {"variant": "check", "solution": "@Q2MAIN"},
                   {"variant": "synth", "question": "Q2"}]},
 "Q3": {"impl": "code/prod/q3_solve.py", "timeout": 1500, "wall": 1500,
        "cases": [{"variant": "enum", "base": "@Q2MAIN"},
                   {"variant": "cpsat_a", "base": "@Q2MAIN", "limit": 600},
                   {"variant": "cpsat_b", "base": "@Q2MAIN", "limit": 600},
                   {"variant": "lp_hiGHS", "base": "@Q2MAIN"},
                   {"variant": "bound_elementary", "base": "@Q2MAIN"},
                   {"variant": "check", "solution": "@Q3MAIN", "base": "@Q2MAIN"},
                   {"variant": "synth", "question": "Q3"}]},
 "Q4": {"impl": "code/prod/q4_solve.py", "timeout": 1700, "wall": 1700,
        "cases": [{"variant": "cpsat_lex", "workers": 4, "stage_budget": _SB,
                    "q2_solution": "@Q2MAIN", "anchor": True},
                   {"variant": "cpsat_lex", "workers": 1, "stage_budget": _SB,
                    "q2_solution": "@Q2MAIN", "anchor": True},
                   {"variant": "check", "solution": "@Q4MAIN"},
                   {"variant": "synth", "question": "Q4"}]},
}

def _sha(p):
    return hashlib.sha256(open(p.replace("/", os.sep), "rb").read()).hexdigest()

def cc(kind, impl, mfamily, algorithm, det, exec_mode, stop, budget, verif, bounds_=None, seed="N/A", qid=None):
    x = EXP[qid]
    bud = ({} if qid == "Q1" else
           {"wall_clock_seconds": x["wall"], "timeout_seconds": x["timeout"],
            "planner_task_expansion": {"scenarios": ["main"], "parameter_cases": x["cases"]}})
    e = {"component_type": kind, "implementation": x["impl"],
         "implementation_sha256": _sha(x["impl"]),
         "version": "prod-v1", "method_family": mfamily, "algorithm": algorithm,
         "deterministic": det, "execution_mode": exec_mode, "stopping_rule": stop,
         "budget": bud, "seed_policy": seed, "bounds": bounds_, "resampling": None,
         "integrator": None, "verification_method": verif}
    return e

# ================= Q1: analytical =================
s1 = CIDX[WIN["Q1"]]["solver"]
q1 = {
 "problem_id": "Q1", "formulation_kind": "analytical",
 "analysis_unit": "用频计划对 (i,j), i<j",
 "assumption_ids": ["A1-half-open", "A2-periodic-slots", "A3-horizon-643"],
 "parameters": [
   P("N_PLANS", 150, "count", "附件1（题面 F-013）", "附件/附件1.xlsx"),
   P("B_MAX", 100, "band_index", "题面 F-001", PF),
   P("T_MAX", 643, "time_index", "ADJUDICATION R1", ADJ, "max_i max_k (t0+k*(g+d)+d)，A001 例证钉死"),
   P("N_PAIRS", 11175, "count", "组合数 C(150,2)", PF)],
 "states": [],
 "governing_relations": [
   R("slot-formula", "definition", "slot_i(k)=[t0_i+k*(g_i+d_i), t0_i+k*(g_i+d_i)+d_i), k=0..n_i-1", "time_index", ["t0","g","d","n"], ["F-005"]),
   R("cells-def", "definition", "U(i)={(f,tau): f∈[f0_i,f1_i), tau∈∪_k slot_i(k)}（整数格半开）", "band_index*time_index", ["f0","f1"], ["F-001","F-006"]),
   R("conflict-pred", "theorem", "(i,j)∈E ⟺ U(i)∩U(j)≠∅ ⟺ 频段半开交叠>0 ∧ ∃k,m: slot_i(k)∩slot_j(m)≠∅", "bool", ["U"], ["F-006","F-023"]),
   R("result-card", "derived", "|E|=297；AB21/AC66/BC181/BB10/CC19；involved=148/150（C007、C060 孤立）", "count", ["E"], ["三实现对账"])],
 "transformations": [
   {"id": "T1-normalize", "operation": "xlsx 区间字符串→整数四列（无损）", "input_refs": ["附件/附件1.xlsx"], "output_refs": ["data/canonical_plans.csv"], "unit_effect": "→整数格"},
   {"id": "T2-bitmap", "operation": "U(i) 编码为 64300-bit 大整数", "input_refs": ["cells-def"], "output_refs": ["conflict-pred"], "unit_effect": "交叠→位与"}],
 "outputs": [
   {"id": "out-E", "type": "edge_set", "unit": "count", "expression": "E（297 对，(id_a,id_b) 升序）", "source_state_ids": ["conflict-pred"]},
   {"id": "out-stats", "type": "stat_bundle", "unit": "count", "expression": "总数/按类对/冲突度分布/孤立集", "source_state_ids": ["result-card"]}],
 "evaluator": {"canonical_evaluator": EV, "evaluator_sha256": EV_SHA, "interface": "python canonical_evaluator.py --question Q1 --solution pairs.json"},
 "computation_contract": cc("analytical_verifier", "code/prod/q1_solve.py",
   s1["family"], s1["algorithm"], True, "single_pass", "全部 11175 对完成", None,
   "三实现两两对称差=0；独立第二实现 checker；半开边界用例", qid="Q1"),
 "numerical_precision": {"policy": "symbolic_exact", "absolute_tolerance": None, "relative_tolerance": None, "rounding": "无浮点"},
 "route_binding": {"question_id": "Q1", "search_id": SID, "idea_id": WIN["Q1"], "idea_decision_sha256": DEC_SHA},
 "discovery_binding": dbind("Q1"),
 "formulation_sha256": "",
 # analytical 专有
 "variables_domains": [
   {"id": "f", "type": "integer", "domain": "0..99", "unit": "band_index", "role": "频段格"},
   {"id": "tau", "type": "integer", "domain": "0..642", "unit": "time_index", "role": "时间格"},
   {"id": "E", "type": "set", "domain": "150 计划的两两组合", "unit": "count", "role": "冲突对集（待判定输出）"}],
 "identities_theorems": [
   R("thm-congruence", "theorem", "同类 (g,d,n) 齐次，P=g+d：时间交叠 ⟺ Δt1 mod P ∈ S_d 且 |Δt1|≤(n-1)P+(d-1)", "bool", ["P"], ["L2","L7"]),
   R("thm-exhaustive", "theorem", "E 由有限判定式（半开区间交非空）完全决定，11175 对穷举⇒完备且可复算", "bool", ["E"], ["F-006"])],
 "derivation_target": {"target": "冲突对集合 E 及其统计量", "quantity": "|E| 与按类分布", "unit": "count"},
 "closed_form_solution": {"expression": "E = {(i,j): [f0_i,f1_i)∩[f0_j,f1_j)≠∅ ∧ ∃k,m slot_i(k)∩slot_j(m)≠∅}", "evaluation": "|E|=297（三独立实现同结果）"},
 "applicability_conditions": [R("cond-halfopen", "assumption", "所有区间半开 [a,b)，端点相接不算交叠", "bool", [], ["A1-half-open"]),
   R("cond-horizon", "assumption", "时间格限于 [0,643)", "time_index", [], ["ADJ R1"])],
 "verification_special_case": {"case": "A001 第三次占用窗 [165,170)：与起点 [170,175) 相接计划不应判冲突；与 [167,..) 交叠计划必须判冲突", "expected": "相接不交叠=0 冲突、交叠>0=冲突（R21/R41 边界用例通过）"},
 "result_keys": ["results/Q1_detect.json", "results/Q1_stats.json"],
 "figure_ids": ["fig-q1-grid-conflict", "fig-q1-degree-dist", "fig-q1-classpairs"],
 "paper_section": "问题一",
 "input_bindings": [{"path": "data/canonical_plans.csv", "sha256": sha("data/canonical_plans.csv")}],
 "notes": "三实现同结果=答案唯一性证据；错误口径(g=周期)复算 237 仅诊断不入结论。"}

def opt_problem(q, constraints, domain, out_src, bound_low, bound_up, reskeys, figs, extra_params, direction, obj_expr, obj_unit, checks, verif, stop, budget, impl):
    s = CIDX[WIN[q]]["solver"]
    return {
     "problem_id": q, "formulation_kind": "optimization",
     "analysis_unit": "用频计划动作向量 a=(a_1..a_150)" if q != "Q3" else "新增 C 放置子集 x⊆候选集",
     "assumption_ids": ["A1-half-open","A2-periodic-slots","A3-horizon-643","A4-one-param","A5-lex-chain","A6-boundary-box"] if q != "Q3" else ["A1-half-open","A2-periodic-slots","A3-horizon-643","A7-main-interpretation","A8-template-C"],
     "parameters": [
       P("E-SET", 297, "count", "Q1 冻结边集", "data/canonical_plans.csv", "Q1 三实现对账"),
       P("GSTAR", 1693, "count", "star_edges.json（评审独立重算 0 差）", STAR),
       P("T_MAX", 643, "time_index", "ADJUDICATION R1", ADJ)] + extra_params,
     "states": [{"id": "a", "type": "action_vector", "unit": "无量纲", "domain": domain, "description": "各计划终态动作（或候选选择向量 x）"}],
     "governing_relations": [
       R("mask-form", "definition", "U(i;a_i)：平移/重定时后占用格集，越出 [0,100)×[0,643) 者非法", "band_index*time_index", ["a"], ["F-005","ADJ R3"]),
       R("pair-incompat", "constraint", "∀(i,j)∈G*,∀(α,β): U(i;α)∩U(j;β)=∅ 才可行（AllowedAssignments/二元子句）", "bool", ["U"], ["F-006","CH-05警示2a"]),
       R("single-choice", "constraint", "∀i Σ_α x_iα=1（Q3：x_p∈{0,1} 且 Σ_{p∋cell}x_p≤1）", "count", ["x"], ["F-008"]),
       R("lex-obj", "objective", obj_expr, obj_unit, ["r","adj","ploss","mag"], ["ADJ R4"])],
     "transformations": [
       {"id": "T-lex", "operation": "词典序四级→逐级锁定", "input_refs": ["lex-obj"], "output_refs": ["cc"], "unit_effect": "多目标→单目标序列"},
       {"id": "T-table", "operation": "禁元组表→CP-SAT 子句/AllowedAssignments", "input_refs": ["pair-incompat"], "output_refs": ["cc"], "unit_effect": "组合约束→子句库"}],
     "outputs": [
       {"id": "out-actions", "type": "assignment", "unit": "无量纲", "expression": out_src, "source_state_ids": ["a"]},
       {"id": "out-obj", "type": "scalar", "unit": obj_unit, "expression": "Φ(a*) 与元组", "source_state_ids": ["a"]},
       {"id": "out-bounds", "type": "bound_cert", "unit": "count", "expression": "各层 (UB,LB,status,证书)", "source_state_ids": []}],
     "evaluator": {"canonical_evaluator": EV, "evaluator_sha256": EV_SHA, "interface": f"python canonical_evaluator.py --question {q} --solution <sol>.json"},
     "computation_contract": cc("optimization_solver", impl, s["family"], s["algorithm"], True, "background_long_budget", stop, budget, verif, qid=q),
     "numerical_precision": {"policy": "symbolic_exact", "absolute_tolerance": None, "relative_tolerance": None, "rounding": "整数域"},
     "route_binding": {"question_id": q, "search_id": SID, "idea_id": WIN[q], "idea_decision_sha256": DEC_SHA},
     "discovery_binding": dbind(q),
     "formulation_sha256": "",
     # optimization 专有
     "decision_variables": [
       {"id": "x_ia", "type": "binary", "domain": "{0,1}", "unit": "无量纲", "role": "计划 i 选动作 α（Q3：候选 p 是否选用）"}],
     "objective": {"id": f"obj-{q}", "direction": direction, "expression": obj_expr, "unit": obj_unit},
     "constraints": [
       {"id": "c-single", "expression": "∀i Σ_α x_iα=1（每计划恰一个终态）", "tolerance": 0, "unit": "无量纲", "kind": "structural"},
       {"id": "c-incompat", "expression": "G* 上任意两终态占用不交（表格/子句）", "tolerance": 0, "unit": "无量纲", "kind": "hard"},
       {"id": "c-bound", "expression": "|df|≤10,|dt|≤5"+(", |dg|≤10∧g'≥1（仅C）" if q=="Q4" else ""), "tolerance": 0, "unit": "band_index/time_index", "kind": "hard"},
       {"id": "c-box", "expression": "所有占用窗 ⊆ [0,643)×[0,100)", "tolerance": 0, "unit": "无量纲", "kind": "hard"}],
     "feasibility_evaluator": {"canonical_evaluator": EV, "evaluator_sha256": EV_SHA, "checks": checks},
     "bounds": {"lower": bound_low, "upper": bound_up, "method": "阶梯 INFEASIBLE 证书 + CP/LP 传播界", "gap_definition": "层内 UB−LB"},
     "solver": {"family": s["family"], "algorithm": "词典序逐级锁定 + 撤销阶梯证书（详见 computation_contract.algorithm）"},
     "result_keys": reskeys, "figure_ids": figs,
     "paper_section": {"Q2":"问题二","Q3":"问题三","Q4":"问题四"}[q],
     "input_bindings": [{"path": STAR, "sha256": STAR_SHA}],
     "notes": constraints}

q2 = opt_problem("Q2",
  "单参数 F-008、禁调次数/间隔 F-009、幅度 F-012、边界 ADJ R3、优先级 ADJ R4；G* 全势边防假 0 撤销。侦察 incumbent [6,121,1996,663]，撤销层界 [2,6] 开放。",
  "A_i={identity}∪{df:1≤|df|≤10}∪{dt:1≤|dt|≤5}∪{revoke}", "a*（result2 行：编号+调整后频段/时间+撤销标记）",
  "撤销阶梯（Σr≤k INFEASIBLE）", "各层 CP-SAT incumbent",
  ["results/Q2_solution.json","results/Q2_table1.json"], ["fig-q2-hero-lex","fig-q2-table1","fig-q2-ladder"],
  [P("DFMAX",10,"band_index","题面 F-012",PF), P("DTMAX",5,"time_index","题面 F-012",PF),
   P("W-PRIO","A100/B10/C1(revoke x2)","priority_loss","ADJUDICATION R4",ADJ)],
  "minimize", "lex_min(rev,adj,Σw·changed,Σ|δ|)，标量 Φ=1e12·rev+1e8·adj+1e4·ploss+mag", "scalar_objective",
  ["零冲突（Q1 检测器复跑=0 对）","每计划至多调一项","|df|≤10/|dt|≤5","次数/间隔不变","频段0..99 & 时间[0,643)","表1聚合与 result2 行一致"],
  "canonical evaluator + 独立第二实现 checker；workers=1 复现对照（TF-5）", "四层 OPTIMAL 或各级预算耗尽记录 incumbent+bound", {"wall_clock_seconds":7200},
  "code/q2_solve.py + code/check_q2.py")

q4 = opt_problem("Q4",
  "仅 C 可 dg(Q4-F019)，g'=8+dg≥1，R3 截断剔除 99/1530 dg 选项；支配界：域⊇Q2⇒opt 不劣（可证，植入锚 [6,121,1996,663] 已实测）。生产=Q2 解热启动+不劣锚定。",
  "A_i=Q2域∪{dg(仅C):1≤|dg|≤10}", "a*（result4 行：编号+频段/时间/间隔+撤销标记）",
  "支配界（Q2 生产解逐字植入=上界）+ 撤销阶梯", "CP-SAT incumbent",
  ["results/Q4_solution.json","results/Q4_table1.json"], ["fig-q4-vs-q2","fig-q4-dg-dist"],
  [P("DFMAX",10,"band_index","题面 F-012",PF), P("DTMAX",5,"time_index","题面 F-012",PF),
   P("DGMAX",10,"time_index","题面 Q4-F019",PF), P("GPRIME-MIN",1,"time_index","ADJUDICATION R6",ADJ)],
  "minimize", "lex_min(rev,adj,Σw·changed,Σ|δ|+Σ|dg|)，标量同 Q2（含 dg 入幅度层）", "scalar_objective",
  ["零冲突","单参数","幅度含 |dg|≤10 且 g'≥1","仅 C 调 g","次数不变","边界盒","表1一致"],
  "canonical evaluator + 独立第二实现 checker（先判 g'≥1）；workers=1 复现", "四层 OPTIMAL 或记录 incumbent+bound", {"wall_clock_seconds":7200},
  "code/q4_solve.py + code/check_q4.py")

q3 = opt_problem("Q3",
  "加装=空闲时频格带冲突集包装；作用域限定：侦察基座(=Q2-R51 解)认证 N*=139（三腿：CP-SAT 双模型 OPTIMAL=bound + HiGHS LP=139.0 + 候选穷举完备）；生产随 Q2 解重算。初等界 332 宽松可手核（界码用 (641-r)//10 防尾幽灵）。备查口径 2B 仅灵敏度。",
  "x_p∈{0,1}, p∈候选放置（侦察基座 |P|=2123；全枚举 52136 预筛）", "selected placements（result3 行：序号/频段区间/时间区间）",
  "构造解 + CP-SAT incumbent", "CP-SAT best bound / HiGHS LP / 双计数 332",
  ["results/Q3_solution.json","results/Q3_bound.json"], ["fig-q3-utilization","fig-q3-bound-meet"],
  [P("CW",3,"band_index","附件1 C 模板","附件/附件1.xlsx"), P("CD",2,"time_index","附件1 C 模板","附件/附件1.xlsx"),
   P("CG",8,"time_index","附件1 C 模板","附件/附件1.xlsx"), P("CN",12,"count","附件1 C 模板","附件/附件1.xlsx"),
   P("SPAN",112,"time_index","11*10+2 末窗跨度",ADJ)],
  "maximize", "max Φ=Σ_p x_p（s.t. 干扰对不共存 / 逐格容量≤1）", "count",
  ["候选与基座零冲突","放置间零冲突","行数=Φ","末窗≤643 & 频段≤99","界≥构造断言"],
  "canonical evaluator + 独立 checker；界码自检门（UB≥已知构造）", "OPTIMAL 且 LB=UB 会合，否则记区间降格表述", {"wall_clock_seconds":3600},
  "code/q3_pack.py + code/check_q3.py + code/q3_bound.py")

units = {"delta_f":"频段格(1)","delta_t":"时间格(1)","band_index":"整数 0..99","time_index":"整数 0..642",
         "count":"计划/对数(无量纲)","priority_loss":"加权(100/10/1)","scalar_objective":"词典序安全标量"}
io.open("reports/methodology/unit_registry.json","w",encoding="utf-8").write(json.dumps(units,ensure_ascii=False,sort_keys=True))
UNIT_SHA = sha("reports/methodology/unit_registry.json")

SPEC = {"schema_version": 4, "contract_rev": 1, "project": "2026 CUMCM D",
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "generated_by": "code/fms_build.py (methodology_review)",
        "unit_registry_sha256": UNIT_SHA, "problems": []}
for p in [q1, q2, q3, q4]:
    p["formulation_sha256"] = fms_v4.compute_formulation_sha256(p, UNIT_SHA)
    SPEC["problems"].append(p)
io.open("reports/FINAL_MODEL_SPEC.json","w",encoding="utf-8").write(json.dumps(SPEC,ensure_ascii=False,indent=1))
print("FINAL_MODEL_SPEC.json written")
for p in SPEC["problems"]:
    print("  ", p["problem_id"], p["formulation_sha256"][:16])
