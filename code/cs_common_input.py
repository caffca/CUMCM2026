# -*- coding: utf-8 -*-
"""Competitive Search common_input 构建器（Manager 产物）。
嵌入：QUESTION_CONTRACT/PROBLEM_FACTS/结构/机会/数据画像 + 150计划表 + Q1冲突对账基础事实
+ route fragment 契约说明 + 冻结预算。输出 runs/competitive/<search_id>/common_input.json。"""
import hashlib, io, json, os, re, sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

# ---- 数据加载与确定性冲突对账（事实计算，非路线） ----
plans = []
for line in io.open("data/canonical_plans.csv", encoding="utf-8").read().splitlines()[1:]:
    a = line.split(",")
    plans.append(dict(id=a[0], cls=a[0][0], f=(int(a[2]), int(a[3])), t=(int(a[4]), int(a[5])),
                      g=int(a[6]), n=int(a[7]), d=int(a[5]) - int(a[4])))
assert len(plans) == 150

def slots(p):
    return [(p["t"][0] + k * (p["g"] + p["d"]), p["t"][0] + k * (p["g"] + p["d"]) + p["d"])
            for k in range(p["n"])]

def band_overlap(a, b):
    return max(0, min(a["f"][1], b["f"][1]) - max(a["f"][0], b["f"][0]))

def time_overlap(a, b):
    ta, tb = slots(a), slots(b)
    pairs = [(x, y) for x in ta for y in tb if min(x[1], y[1]) - max(x[0], y[0]) > 0]
    return pairs

conflicts = []
for i in range(150):
    for j in range(i + 1, 150):
        a, b = plans[i], plans[j]
        if band_overlap(a, b) > 0:
            tp = time_overlap(a, b)
            if tp:
                conflicts.append(dict(pair=[a["id"], b["id"]], cls_pair="".join(sorted(a["cls"] + b["cls"])),
                                      band_overlap=band_overlap(a, b), slot_pairs=len(tp)))
by_cp = {}
for c in conflicts:
    by_cp[c["cls_pair"]] = by_cp.get(c["cls_pair"], 0) + 1
involved = set()
for c in conflicts:
    involved.update(c["pair"])
T_MAX = max(p["t"][0] + (p["n"] - 1) * (p["g"] + p["d"]) + p["d"] for p in plans)

now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
search_id = "CS-%s-D2026" % now
run_dir = os.path.join("runs", "competitive", search_id)
os.makedirs(os.path.join(run_dir, "routes"), exist_ok=True)
os.makedirs(os.path.join(run_dir, "scouts"), exist_ok=True)
os.makedirs(os.path.join(run_dir, "reviews"), exist_ok=True)

qc = json.load(io.open("reports/contracts/QUESTION_CONTRACT.json", encoding="utf-8"))
pf = json.load(io.open("reports/contracts/PROBLEM_FACTS.json", encoding="utf-8"))
ps = json.load(io.open("reports/discovery/PROBLEM_STRUCTURE.json", encoding="utf-8"))
eda = json.load(io.open("reports/discovery/EDA_FINDINGS.json", encoding="utf-8"))
mo = json.load(io.open("reports/discovery/MODEL_OPPORTUNITIES.json", encoding="utf-8"))
dp = json.load(io.open("reports/data/DATA_PROFILE.json", encoding="utf-8"))
dc = json.load(io.open("reports/data/DATA_CONTRACT.json", encoding="utf-8"))
ds = json.load(io.open("reports/data/DATASET_SNAPSHOT.json", encoding="utf-8"))

ROUTE_FRAGMENT_CONTRACT = """每个 child 输出一个 JSON：{"child_run_id","role","question_ids",
 "routes":[...], "coverage_notes":{"structural_opportunities_checked":[...],
 "families_not_applicable":[{"family","reason(引用题目结构)"}]}}。
routes[] 每项 = 完整候选路线（一条 route = 问题重表达+模型/表示+结构变换+求解器族与算法+可行性路径+
上下界/最优性证据计划+侦察实验计划+实现风险与预算），字段：
{"idea_id_suggested":"Qx-Ryz","question_id","tier":"baseline|recommended_solution|advanced_alternative",
 "method_family":"analytic_mechanistic|statistical_probabilistic|operations_research|graph_combinatorial|dynamic_control|simulation|machine_learning|hybrid_decomposition",
 "problem_reformulation":"一句话重表达","model":{"family","representation","decision_variables":[],
   "objective_id","constraint_ids":[],"equations_summary":"只写足以区分路线的数学结构"},
 "transformations":["decomposition",...],
 "solver":{"family","algorithm","fit_reason(必须引用问题结构事实，禁止空话)","stopping_rule",
   "budget_type":"wall_clock|function_evaluations","determinism":"deterministic|stochastic",
   "seed_protocol"},
 "bound_plan":{"lower_bound_method","upper_bound_method","gap_metric","gap_threshold","proof_possible"},
 "scout_plan":{"required","metrics":["feasible","objective","runtime","stability","gap"],"special_checks":[]},
 "required_assumptions":[],"failure_conditions":[],"strengths":[],"weaknesses":[],
 "validation_plan":[],"complexity":"low|medium|high","interpretability":"low|medium|high",
 "implementation_risk":"low|medium|high","status":"proposed"}
红线：只提候选不选赢家；无适用路线时输出空 routes + 结构化 not_applicable 理由；
不同路线必须来自不同问题重表达/模型结构/求解范式（换优化器库名不算）；
禁止出现『结果表明/显著提升/最终证明/该方法有效解决/最佳模型为』等结论词；
fit_reason 必须引用 PROBLEM_FACTS/结构事实编号或具体组合结构。"""

common = {
 "search_id": search_id,
 "problem_id": "D2026",
 "profile": "standard",
 "frozen_at": datetime.now().astimezone().isoformat(timespec="seconds"),
 "budget": {"max_wall_minutes": 60, "max_generator_children": 4, "bound_children": 1,
            "top_k": 3, "scout_budget_seconds_per_route": 600, "replicates": 3,
            "frozen_before_scouts": True,
            "note": "标准档冻结预算；看到结果后禁止调整（用户未另给预算）"},
 "user_preferences": {"language": "zh-CN", "engine": "latex", "hil": "auto",
                      "priority_rule": "题面 A>B>C；正确性>可行性>最优性证据>目标值>稳定性>运行时>可解释性"},
 "solver_environment": {"ortools_cpsat": "9.15 @ F:/dsh_envlibs/mathmodel（PYTHONPATH 指向该目录可 import）",
                        "python": "3.14", "other": ["numpy", "pandas", "networkx", "scipy"]},
 "question_contract": qc,
 "problem_facts": pf,
 "problem_structure": ps,
 "eda_findings": eda,
 "model_opportunities": mo,
 "data_profile": dp,
 "data_contract": dc,
 "dataset_snapshot": {k: ds.get(k) for k in ("dataset_id", "raw_input_sha256", "class_profile")},
 "computed_data_facts": {
   "horizon_note": "时间视界 T_MAX=621Δt（既有150计划占用的最晚结束点）；频段 0..99",
   "T_MAX_delta_t": T_MAX,
   "q1_conflict_pairs_reference_check": {
     "method": "半开区间 [a,b) 交叠 => max(0,min(b1,b2)-max(a1,a2))>0；两计划的占用时段集合（n 次周期重复，slot_k=[t1+(k-1)(g+d),+d)）任一交叠且频段交叠 => 冲突对",
     "total_conflict_pairs": len(conflicts),
     "by_class_pair": by_cp,
     "plans_involved": len(involved),
     "caveat": "此为 Manager 用区间算术算出的基础数据事实（与题面口径一致），供 scout 理解问题规模；scout 可复核但不得据此编造实验结论"},
   "occupancy_cells_total": 100 * T_MAX,
   "occupancy_cells_used": sum((p["f"][1]-p["f"][0]) * p["d"] * p["n"] for p in plans),
 },
 "plans_table_compact": [[p["id"], p["f"][0], p["f"][1], p["t"][0], p["t"][1], p["g"], p["n"]] for p in plans],
 "route_fragment_contract": ROUTE_FRAGMENT_CONTRACT,
 "output_rules": {
   "allowed_read": "仅本文件（common_input.json）",
   "allowed_write": "仅自己的 runs/competitive/%s/routes/<child_run_id>.route.json" % search_id,
   "forbidden": ["读取 routes/ 下其他 child 文件", "读取 Manager 排序/旧论文/旧结果",
                "浏览任何本届赛题讨论或现成答案（竞赛合规红线）",
                "把侦察数字写进 results/ 或论文"]},
}
out = os.path.join(run_dir, "common_input.json")
io.open(out, "w", encoding="utf-8").write(json.dumps(common, ensure_ascii=False, indent=1))
print(json.dumps({"search_id": search_id, "common_input": out,
                  "common_input_sha256": sha(out),
                  "conflict_pairs": len(conflicts), "by_class_pair": by_cp,
                  "plans_involved": len(involved), "T_MAX": T_MAX,
                  "cells_used_ratio": round(sum((p['f'][1]-p['f'][0])*p['d']*p['n'] for p in plans)/(100.0*T_MAX), 4)},
                 ensure_ascii=False, indent=1))
