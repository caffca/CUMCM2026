# -*- coding: utf-8 -*-
"""REV-Q4-01 附件脚本 F：三项细粒度诊断
 F1. R22：阶段 I「16/19 CC 边闭式清零」在最终解中的存活情况（逐边判定消解方式）。
 F2. R11：dg 选项域计数复算（valid/potential/pruned_by_horizon）+ 撤销类别构成的层三代价可换性检查。
 F3. R41：sa_record 内部标量/元组与 evaluator 的一致性；三链能量标量化在本实例是否会串层。
"""
import io, json, os, sys
from itertools import combinations

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(RUN, "scouts", "Q4-R11", "code"))
import q4common as Q                                        # noqa: E402
sys.stdout.reconfigure(encoding="utf-8")

plans = Q.CE.load_plans()
d4 = Q.build_domains(plans, allow_gap=True)
out = {}

# ---------------- F1 ----------------
base = set(tuple(sorted(l)) for l in Q.CE.truth_conflicts(plans))
cc = sorted([e for e in base if plans[e[0]]["cls"] == "C" and plans[e[1]]["cls"] == "C"])
log22 = json.load(io.open(os.path.join(RUN, "scouts", "Q4-R22", "run", "r22_log.json"), encoding="utf-8"))
sol22 = json.load(io.open(os.path.join(RUN, "scouts", "Q4-R22", "run", "solution_actions.json"), encoding="utf-8"))


def kind_of(pid):
    a = sol22.get(pid, {})
    if a.get("revoke"):
        return "revoke"
    for k in ("df", "dt", "dg"):
        if a.get(k):
            return k
    return "none"


# 阶段 I 消解的边 = 完全落在有 cost 的分量内部
resolved_components = [c["component"] for c in log22["cc_components"] if c.get("cost")]
stageI_edges = [(i, j) for (i, j) in cc
                if any(set([i, j]).issubset(set(comp)) for comp in resolved_components)]
rows = []
for (i, j) in stageI_edges:
    ki, kj = kind_of(i), kind_of(j)
    survives = ("revoke" != ki and "revoke" != kj)
    rows.append(dict(edge=[i, j], kind_i=ki, kind_j=kj, both_endpoints_kept=survives,
                     survives_via_retiming=survives and ("dg" in (ki, kj))))
out["F1_r22_stage1_survival"] = dict(
    stage1_claim_resolved_edges=len(stageI_edges), cc_total=len(cc),
    failed_component_edges=[list(e) for e in cc if not any(set(e).issubset(set(c)) for c in resolved_components)],
    edges_with_both_endpoints_kept=sum(1 for r in rows if r["both_endpoints_kept"]),
    edges_surviving_via_retiming=sum(1 for r in rows if r["survives_via_retiming"]),
    rows=rows,
    conclusion=("阶段 I 宣称闭式清零 16/19 条 CC 边；在最终交付解中，两端点都未被撤销的只剩 "
                f"{sum(1 for r in rows if r['both_endpoints_kept'])} 条，其中靠改 g' 存活的 "
                f"{sum(1 for r in rows if r['survives_via_retiming'])} 条 ⇒ 同余构造成果几乎全部被阶段 II 的撤销覆盖，"
                "『机理证据』与『交付解』是两件事，报告若并列陈述易被读成后者体现了前者。"))

# ---------------- F2 ----------------
pot = val = 0
per = {}
for pid, p in sorted(plans.items()):
    if p["cls"] != "C":
        continue
    k = 0
    for v in range(-10, 11):
        if v == 0 or p["g"] + v < 1:
            continue
        pot += 1
        if Q.mask_int(p, dg=v) is not None:
            k += 1
            val += 1
    per[pid] = k
out["F2_r11_dg_domain"] = dict(potential=pot, valid=val, pruned=pot - val,
                               claimed=dict(potential=1530, valid=1431, pruned=99),
                               matches=(pot == 1530 and val == 1431 and pot - val == 99))
# 撤销构成：R11 撤了 1A+7B（ploss 340）；同撤销数若全部撤 C 类，层三代价 16
r11 = json.load(io.open(os.path.join(RUN, "scouts", "Q4-R11", "run", "solution_actions.json"), encoding="utf-8"))
revA = [p for p, a in r11.items() if a.get("revoke") and plans[p]["cls"] == "A"]
revB = [p for p, a in r11.items() if a.get("revoke") and plans[p]["cls"] == "B"]
revC = [p for p, a in r11.items() if a.get("revoke") and plans[p]["cls"] == "C"]
ploss_of_actual = 2 * (100 * len(revA) + 10 * len(revB) + len(revC))
out["F2_r11_revoke_mix"] = dict(revA=revA, revB=revB, revC=revC, n=len(r11),
                                revoke_ploss_actual=ploss_of_actual,
                                revoke_ploss_if_all_C=2 * (len(revA) + len(revB) + len(revC)),
                                note=("层一只数总量 ⇒ 8 个撤销位放在 C 类可把层三代价从 "
                                      f"{ploss_of_actual} 降到 {2*(len(revA)+len(revB)+len(revC))}；"
                                      "R11 的层三/层四 UNKNOWN，故该不对称未被优化，属可检验的改进方向（非正确性缺陷）"))

# ---------------- F3 ----------------
f3 = {}
for sd in (11, 29, 47):
    rec = json.load(io.open(os.path.join(RUN, "scouts", "Q4-R41", "run", f"sa_record_seed{sd}.json"),
                            encoding="utf-8"))
    t = [int(x) for x in rec["objective_tuple_internal"]]
    sc = t[0] * 10**12 + t[1] * 10**8 + t[2] * 10**4 + t[3]
    sol = json.load(io.open(os.path.join(RUN, "scouts", "Q4-R41", "run", f"solution_seed{sd}.json"), encoding="utf-8"))
    t2, s2 = Q.opt_scalar(plans, sol)
    ev = json.load(io.open(os.path.join(RUN, "scouts", "Q4-R41", "run", f"eval_seed{sd}.json"), encoding="utf-8"))
    f3[sd] = dict(record_tuple=t, record_scalar=rec["objective_scalar"], recomputed_scalar=sc,
                  actions_equal_to_record=(sol == rec["actions"]),
                  record_tuple_eq_evaluator=t == [int(x) for x in ev["objective"]],
                  feasible=ev["feasible"], viol_recount=rec["independent_recount_violations"],
                  best_viol=rec["best_violations"], projection=rec["projection"])
mx_ploss = sum(2 * Q.PRIO[p["cls"]] for p in plans.values())
out["F3_r41_internal_consistency"] = dict(per_seed=f3,
                                          tier_spacing_check=dict(max_ploss=mx_ploss,
                                                                  ploss_spacing=10**4,
                                                                  safe=mx_ploss < 10**4))
io.open(os.path.join(RUN, "reviews", "_tmp", "recheck_out_F.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1, default=str))
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
