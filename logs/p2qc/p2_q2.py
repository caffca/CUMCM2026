# -*- coding: utf-8 -*-
"""P2-2：独立应用 results/Q2_solution.json 的 actions，重算调整后冲突集 + 逐计划合规。"""
import json
import os
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

WP = {"A": 100, "B": 10, "C": 1}   # ADJ R4 权重（本脚本自行按裁定重述，非 import）


def main():
    plans = P.load_plans()
    pmap = {p["id"]: p for p in plans}
    sol = P.rj(os.path.join("results", "Q2_solution.json"))
    acts = sol["actions"]

    # --- 结构检查：每个动作只允许一个参数（F-008 单参数规则）---
    shape_bad = []
    for pid, o in acts.items():
        if pid not in pmap:
            shape_bad.append(f"{pid}: 未知计划 id")
            continue
        keys = set(o)
        if keys not in ({"revoke"}, {"df"}, {"dt"}):
            shape_bad.append(f"{pid}: 非法动作键组合 {sorted(keys)}")
            continue
        if "revoke" in keys and o["revoke"] is not True:
            shape_bad.append(f"{pid}: revoke 值非 True: {o['revoke']!r}")
        for k in ("df", "dt"):
            if k in keys:
                v = o[k]
                if not isinstance(v, int) or isinstance(v, bool):
                    shape_bad.append(f"{pid}: {k} 非整数 {v!r}")
                elif v == 0:
                    shape_bad.append(f"{pid}: {k}=0 被记为调整（虚计调整数）")

    # --- 逐计划合规 ---
    viol = []
    adjusted = []
    revoked = []
    for pid, o in acts.items():
        p = pmap[pid]
        if o.get("revoke"):
            revoked.append(pid)
            continue
        if "df" in o:
            df = o["df"]
            if abs(df) > P.DF_MAX:
                viol.append({"id": pid, "rule": "|df|<=10", "value": df})
            if p["f0"] + df < 0:
                viol.append({"id": pid, "rule": "f0+df>=0", "value": p["f0"] + df})
            if p["f1"] + df > P.B_MAX:
                viol.append({"id": pid, "rule": "f1+df<=100", "value": p["f1"] + df})
            adjusted.append(pid)
        elif "dt" in o:
            dt = o["dt"]
            if abs(dt) > P.DT_MAX:
                viol.append({"id": pid, "rule": "|dt|<=5", "value": dt})
            if p["t0"] + dt < 0:
                viol.append({"id": pid, "rule": "t0+dt>=0", "value": p["t0"] + dt})
            adjusted.append(pid)
        else:
            shape_bad.append(f"{pid}: 空动作")

    # 额外（FMS mask-form / ADJ R3）：平移后所有 slot 必须整体落于 [0,643)
    horizon_bad = []
    for pid, o in acts.items():
        if o.get("revoke"):
            continue
        q = P.shift(pmap[pid], df=int(o.get("df", 0)), dt=int(o.get("dt", 0)))
        bad = P.horizon_violation(q)
        if bad:
            horizon_bad.append({"id": pid, "action": o, "why": bad})

    kept = sorted(set(pmap) - set(acts))
    counts_sum_ok = len(revoked) + len(adjusted) + len(kept) == len(plans)

    # --- 独立重算调整后冲突集 ---
    final = []
    for pid in sorted(pmap):
        o = acts.get(pid, {})
        if o.get("revoke"):
            continue
        final.append(P.shift(pmap[pid], df=int(o.get("df", 0)), dt=int(o.get("dt", 0))))
    edges2, checked2 = P.all_conflicts(final)

    # --- 独立重算词典序元组 [rev, adj, PL, MG] ---
    rev = len(revoked)
    adj = len(adjusted)
    pl = sum(WP[pmap[pid]["cls"]] * (2 if acts[pid].get("revoke") else 1) for pid in acts)
    mg = sum(abs(v) for pid in adjusted for v in acts[pid].values()
             if isinstance(v, int) and not isinstance(v, bool))
    mine_tuple = [rev, adj, pl, mg]
    auth_tuple = list(sol["objective_tuple"])

    by_class = collections.defaultdict(lambda: {"kept": 0, "adjusted": 0, "revoked": 0})
    for pid in pmap:
        c = pmap[pid]["cls"]
        o = acts.get(pid, {})
        if o.get("revoke"):
            by_class[c]["revoked"] += 1
        elif o:
            by_class[c]["adjusted"] += 1
        else:
            by_class[c]["kept"] += 1
    by_class = {k: dict(v) for k, v in sorted(by_class.items())}

    auth_table = P.rj(os.path.join("results", "Q2_table1.json")) if os.path.exists(os.path.join(P.ROOT, "results", "Q2_table1.json")) else {}

    # 冲突消解覆盖性：原 297 条边两端是否都得到处理（至少一端被调整或撤销）
    q1edges = [list(e) for e in P.rj(os.path.join("results", "Q1_detect.json"))["edges"]]
    untouched_pairs = []
    for a, b in q1edges:
        if a not in acts and b not in acts:
            untouched_pairs.append([a, b])

    res = {
        "check": "Q2_solution 独立复算",
        "n_plans": len(plans),
        "shape_bad": shape_bad,
        "compliance_violations": viol,
        "horizon_violations_ADR3": horizon_bad,
        "revoked": sorted(revoked), "n_revoked": len(revoked),
        "n_adjusted": len(adjusted), "n_kept": len(kept),
        "sum_equals_150": counts_sum_ok, "sum_value": len(revoked) + len(adjusted) + len(kept),
        "by_class_mine": by_class,
        "post_conflict_edges_mine": len(edges2),
        "post_pairs_checked": checked2,
        "post_conflict_edges_auth_field": {"residual_pairs": sol.get("residual_pairs"),
                                            "residual_pairs_second_impl": sol.get("residual_pairs_second_impl"),
                                            "compliance_violations": sol.get("compliance_violations")},
        "objective_tuple_mine": mine_tuple,
        "objective_tuple_auth": auth_tuple,
        "objective_tuple_equal": mine_tuple == auth_tuple,
        "objective_scalar_auth": sol.get("objective_scalar"),
        "objective_scalar_mine": 10**12 * mine_tuple[0] + 10**8 * mine_tuple[1] + 10**4 * mine_tuple[2] + mine_tuple[3],
        "original_edges_all_touched": len(untouched_pairs) == 0,
        "untouched_conflict_pairs": untouched_pairs[:20],
        "auth_revoke_fields": {"revoke": sol.get("revoke"), "objective_tuple[0]": auth_tuple[0],
                               "revocation.upper_incumbent": sol["revocation"]["upper_incumbent"]},
        "table1_auth": auth_table,
        "hint_source": sol.get("hint_source"),
        "hint_role": sol.get("hint_role"),
    }
    res["verdict"] = P.verdict(
        not shape_bad and not viol and not horizon_bad and len(edges2) == 0 and counts_sum_ok
        and res["objective_tuple_equal"] and not untouched_pairs
        and res["n_revoked"] == sol.get("revoke") == auth_tuple[0]
    )
    P.wr("p2_q2_report.json", res)
    print(json.dumps({k: v for k, v in res.items() if k not in ("table1_auth",)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
