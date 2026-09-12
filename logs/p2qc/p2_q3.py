# -*- coding: utf-8 -*-
"""P2-3：独立校验 results/Q3_solution.json 的 selected（新增 C 计划）与 Q2 调整后基座的兼容性。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

CW, CD, CG, CN = P.C_W, P.C_D, P.C_G, P.C_N


def cplan(f0, t0, idx):
    return {"id": f"N{idx:03d}", "cls": "C", "f0": f0, "f1": f0 + CW,
            "t0": t0, "t1": t0 + CD, "d": CD, "g": CG, "n": CN}


def main():
    plans = P.load_plans()
    pmap = {p["id"]: p for p in plans}
    q2 = P.rj(os.path.join("results", "Q2_solution.json"))
    acts = q2["actions"]
    q3 = P.rj(os.path.join("results", "Q3_solution.json"))
    selected = [tuple(x) for x in q3["selected"]]

    # 基座：Q2 actions 应用后（撤销者删除）
    base = []
    for pid in sorted(pmap):
        o = acts.get(pid, {})
        if o.get("revoke"):
            continue
        base.append(P.shift(pmap[pid], df=int(o.get("df", 0)), dt=int(o.get("dt", 0))))

    dup = len(selected) != len(set(selected))
    # 逐计划合法域
    bound_bad = []
    news = []
    for i, (f0, t0) in enumerate(sorted(selected)):
        news.append(cplan(f0, t0, i))
        last_end = t0 + (CN - 1) * (CG + CD) + CD
        if not (0 <= f0 and f0 + CW <= P.B_MAX):
            bound_bad.append({"pair": [f0, t0], "why": f"f0+3={f0+CW} 越出 100"})
        if t0 < 0 or last_end > P.T_MAX:
            bound_bad.append({"pair": [f0, t0], "why": f"末周期终点 {last_end} > {P.T_MAX}"})
    # 与基座冲突（题面判据：频段半开交叠 且 存在时隙交叠）
    vs_base, base_witness = [], None
    for nc in news:
        for bp in base:
            if P.conflict(nc, bp):
                vs_base.append([nc["id"], bp["id"]])
                if base_witness is None:
                    base_witness = {"new": nc, "base": bp}
    # C 之间冲突
    vs_self, _ = P.all_conflicts(news)

    # 独立重枚举候选集（第三实现：互斥格集合法 + 解析判定），并与权威 n_cand 对账
    occ = set()
    for bp in base:
        for (s, e) in P.slot_list(bp):
            for t in range(s, e):
                for f in range(bp["f0"], bp["f1"]):
                    occ.add((t, f))
    f0max = P.B_MAX - CW
    t0max = P.T_MAX - ((CN - 1) * (CG + CD) + CD)
    my_cands = set()
    for f0 in range(0, f0max + 1):
        for t0 in range(0, t0max + 1):
            cells = {(t, f) for k in range(CN) for t in range(t0 + k * (CG + CD), t0 + k * (CG + CD) + CD)
                     for f in range(f0, f0 + CW)}
            if cells.isdisjoint(occ):
                my_cands.add((f0, t0))
    sel_set = set(selected)
    sel_not_cand = sorted(sel_set - my_cands)

    # 极大性检验（1-加）：不存在任何候选可无冲突地加入现有 140 台
    addable = []
    for (f0, t0) in my_cands:
        cand = cplan(f0, t0, 999)
        hit = False
        for nc in news:
            if abs(nc["f0"] - cand["f0"]) >= CW:
                continue
            if P.conflict(nc, cand):
                hit = True
                break
        if not hit:
            addable.append([f0, t0])

    res = {
        "check": "Q3_solution 独立复算",
        "c_plan_template": {"CW": CW, "CD": CD, "CG": CG, "CN": CN,
                            "period": CG + CD, "f0_allowed": [0, f0max], "t0_allowed": [0, t0max]},
        "selected_rows_mine": len(selected), "phi_auth": q3["phi"], "rows_auth": q3["rows"],
        "phi_eq_rows": q3["phi"] == len(selected) == q3["rows"],
        "duplicate_selected": dup,
        "domain_violations": bound_bad,
        "conflicts_vs_base_mine": len(vs_base), "conflicts_vs_base_auth": q3["conflicts_vs_base"],
        "conflicts_internal_mine": len(vs_self), "conflicts_internal_auth": q3["conflicts_internal"],
        "base_plans_used": len(base),
        "cand_universe_mine": len(my_cands), "cand_universe_grid": (f0max + 1) * (t0max + 1),
        "n_cand_auth": q3["n_cand"], "cand_count_second_impl_auth": q3.get("cand_count_second_impl"),
        "cand_equal_auth": len(my_cands) == q3["n_cand"],
        "selected_subset_of_candidates": not sel_not_cand, "selected_not_in_candidates": sel_not_cand,
        "maximality_1_add_addable": addable[:10], "addable_count": len(addable),
        "sha_mine": P.sha_of_edges([[a, b] for a, b in sorted((list(s) for s in sel_set))]) if False else None,
        "auth_selected_sha256": q3.get("selected_sha256"),
        "ub_auth": {"ub_phase": q3.get("ub_phase"), "ub_density": q3.get("ub_density"),
                    "ub_lp": q3.get("ub_lp"), "ub_cp": q3.get("ub_cp"), "ub_min": q3.get("ub_min"),
                    "gap_certified": q3.get("gap_certified"), "status": q3.get("status"),
                    "proven_optimal": q3.get("proven_optimal")},
        "free_cells_mine": P.T_MAX * P.B_MAX - len(occ),
        "base_distinct_cells_mine": len(occ),
        "density_upper_bound_check": (P.T_MAX * P.B_MAX - len(occ)) // (CN * CD * CW),
    }
    # selected 指纹（自定义口径：排序后的 [f0,t0] 列表 json）
    res["sha_mine"] = P.sha_of_edges([list(s) for s in sorted(sel_set)])
    res["sha_equal_auth"] = res["sha_mine"] == q3.get("selected_sha256")
    res["verdict"] = P.verdict(
        not dup and not bound_bad and len(vs_base) == 0 and len(vs_self) == 0
        and res["phi_eq_rows"] and res["cand_equal_auth"] and not sel_not_cand
        and len(addable) == 0
    )
    P.wr("p2_q3_report.json", res)
    print(json.dumps(res, ensure_ascii=False, indent=1)[:3500])


if __name__ == "__main__":
    main()
