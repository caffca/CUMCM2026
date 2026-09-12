# -*- coding: utf-8 -*-
"""P2-4：独立校验 results/Q4_solution.json（含 dg 重定时）：动作合法性、T_MAX 截断声明、调整后 0 冲突。"""
import json
import os
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

WP = {"A": 100, "B": 10, "C": 1}


def main():
    plans = P.load_plans()
    pmap = {p["id"]: p for p in plans}
    sol = P.rj(os.path.join("results", "Q4_solution.json"))
    acts = sol["actions"]

    shape_bad, viol, dg_bad, cls_bad, horizon_bad = [], [], [], [], []
    revoked, adjusted = [], []
    for pid, o in acts.items():
        if pid not in pmap:
            shape_bad.append(f"{pid}: 未知计划")
            continue
        keys = set(o)
        if keys not in ({"revoke"}, {"df"}, {"dt"}, {"dg"}):
            shape_bad.append(f"{pid}: 非法键组合 {sorted(keys)}")
            continue
        p = pmap[pid]
        if o.get("revoke"):
            if o["revoke"] is not True:
                shape_bad.append(f"{pid}: revoke 值 {o['revoke']!r}")
            revoked.append(pid)
            continue
        adjusted.append(pid)
        if "df" in o:
            v = o["df"]
            if not isinstance(v, int) or isinstance(v, bool) or v == 0:
                shape_bad.append(f"{pid}: df 非法 {v!r}")
            if abs(v) > P.DF_MAX:
                viol.append({"id": pid, "rule": "|df|<=10", "value": v})
            if p["f0"] + v < 0 or p["f1"] + v > P.B_MAX:
                viol.append({"id": pid, "rule": "band 0..100", "value": [p["f0"] + v, p["f1"] + v]})
        if "dt" in o:
            v = o["dt"]
            if not isinstance(v, int) or isinstance(v, bool) or v == 0:
                shape_bad.append(f"{pid}: dt 非法 {v!r}")
            if abs(v) > P.DT_MAX:
                viol.append({"id": pid, "rule": "|dt|<=5", "value": v})
            if p["t0"] + v < 0:
                viol.append({"id": pid, "rule": "t0+dt>=0", "value": p["t0"] + v})
        if "dg" in o:
            v = o["dg"]
            if not isinstance(v, int) or isinstance(v, bool) or v == 0:
                shape_bad.append(f"{pid}: dg 非法 {v!r}")
            if abs(v) > P.DG_MAX:
                dg_bad.append({"id": pid, "rule": "|dg|<=10", "value": v})
            if p["g"] + v < 1:
                dg_bad.append({"id": pid, "rule": "g+dg>=1", "value": p["g"] + v})
            if p["cls"] != "C":
                cls_bad.append({"id": pid, "cls": p["cls"], "dg": v})   # R6：仅 C 可调间隔
        q = P.shift(p, df=int(o.get("df", 0)), dt=int(o.get("dt", 0)), dg=int(o.get("dg", 0)))
        bad = P.horizon_violation(q)
        if bad:
            horizon_bad.append({"id": pid, "action": o, "why": bad})

    kept = sorted(set(pmap) - set(acts))

    # --- 独立重算调整后冲突（slot 用新 g'）---
    final = []
    for pid in sorted(pmap):
        o = acts.get(pid, {})
        if o.get("revoke"):
            continue
        final.append(P.shift(pmap[pid], df=int(o.get("df", 0)), dt=int(o.get("dt", 0)),
                             dg=int(o.get("dg", 0))))
    edges, checked = P.all_conflicts(final)

    # --- T_MAX 截断声明独立复算（C 类的 dg 选项中会因越界/非法间隔被丢弃的个数）---
    dropped_mine, drop_detail = 0, []
    for p in plans:
        if p["cls"] != "C":
            continue
        for d in range(-P.DG_MAX, P.DG_MAX + 1):
            if d == 0:
                continue
            gp = p["g"] + d
            if gp < 1:
                dropped_mine += 1
                drop_detail.append({"id": p["id"], "dg": d, "reason": f"g'={gp}<1"})
                continue
            last_end = p["t0"] + (p["n"] - 1) * (gp + p["d"]) + p["d"]
            if last_end > P.T_MAX:
                dropped_mine += 1
                drop_detail.append({"id": p["id"], "dg": d,
                                    "reason": f"末周期终点 {p['t0']}+{p['n']-1}*({gp}+{p['d']})+{p['d']}={last_end} > {P.T_MAX}"})
    # 抽 3 个被丢弃的选项做手工算式复述
    samples = []
    for rec in drop_detail:
        p = pmap[rec["id"]]
        gp = p["g"] + rec["dg"]
        slots = [(p["t0"] + k * (gp + p["d"]), p["t0"] + k * (gp + p["d"]) + p["d"]) for k in range(p["n"])]
        samples.append({"id": rec["id"], "orig": {"f0": p["f0"], "f1": p["f1"], "t0": p["t0"], "t1": p["t1"],
                                                  "g": p["g"], "n": p["n"], "d": p["d"]},
                        "dg": rec["dg"], "g_prime": gp, "last_slot": list(slots[-1]),
                        "horizon": P.T_MAX, "dropped": rec["reason"]})
        if len(samples) >= 3:
            break
    # 反向抽 3 个被采用的 dg 动作，验证其未被截断（末周期终点 ≤ 643）
    kept_dg = []
    for pid, o in acts.items():
        if "dg" in o:
            p = pmap[pid]
            gp = p["g"] + o["dg"]
            le = p["t0"] + (p["n"] - 1) * (gp + p["d"]) + p["d"]
            kept_dg.append({"id": pid, "dg": o["dg"], "g": p["g"], "g_prime": gp, "last_end": le,
                            "within_horizon": le <= P.T_MAX})

    # --- 元组独立复算 ---
    rev, adj = len(revoked), len(adjusted)
    pl = sum(WP[pmap[pid]["cls"]] * (2 if acts[pid].get("revoke") else 1) for pid in acts)
    mg = sum(abs(v) for pid in adjusted for v in acts[pid].values() if isinstance(v, int) and not isinstance(v, bool))
    mine_tuple = [rev, adj, pl, mg]
    auth_tuple = list(sol["objective_tuple"])

    by_class = collections.defaultdict(lambda: {"kept": 0, "adjusted": 0, "revoked": 0})
    for pid in pmap:
        c = pmap[pid]["cls"]
        o = acts.get(pid, {})
        by_class[c]["revoked" if o.get("revoke") else ("adjusted" if o else "kept")] += 1
    by_class = {k: dict(v) for k, v in sorted(by_class.items())}

    res = {
        "check": "Q4_solution 独立复算",
        "shape_bad": shape_bad, "violations": viol, "dg_violations": dg_bad,
        "nonC_dg_actions": cls_bad, "horizon_violations": horizon_bad,
        "n_revoked": rev, "n_adjusted": adj, "n_kept": len(kept),
        "sum_equals_150": rev + adj + len(kept) == 150,
        "by_class_mine": by_class, "by_class_auth": sol.get("by_class"),
        "by_class_equal": by_class == {k: dict(v) for k, v in sol.get("by_class", {}).items()},
        "post_conflict_edges_mine": len(edges), "post_conflict_edges_auth": sol.get("residual_pairs"),
        "post_pairs_checked": checked,
        "dg_dropped_mine": dropped_mine, "dg_dropped_auth": sol.get("dg_options_dropped_by_horizon"),
        "dg_dropped_equal": dropped_mine == sol.get("dg_options_dropped_by_horizon"),
        "dg_dropped_c_option_space": sum(1 for p in plans if p["cls"] == "C") * 20,
        "dropped_samples_manual": samples,
        "applied_dg_actions_manual_check": kept_dg,
        "objective_tuple_mine": mine_tuple, "objective_tuple_auth": auth_tuple,
        "objective_tuple_equal": mine_tuple == auth_tuple,
        "scalar_mine": 10**12 * mine_tuple[0] + 10**8 * mine_tuple[1] + 10**4 * mine_tuple[2] + mine_tuple[3],
        "scalar_auth": sol.get("objective_scalar"),
        "options_total_mine": None,
        "revoked_ids": sorted(revoked),
        "q2_planted_check": {"planted_q2_tuple": sol.get("planted_q2_tuple"),
                             "planted_q2_residual_auth": sol.get("planted_q2_residual"),
                             "planted_q2_feasible_auth": sol.get("planted_q2_feasible")},
    }

    # 复算 Q2 生产解植入 Q4 域后的残余冲突（用新 g 域）
    q2acts = P.rj(os.path.join("results", "Q2_solution.json"))["actions"]
    fin2 = []
    for pid in sorted(pmap):
        o = q2acts.get(pid, {})
        if o.get("revoke"):
            continue
        fin2.append(P.shift(pmap[pid], df=int(o.get("df", 0)), dt=int(o.get("dt", 0))))
    e2, _ = P.all_conflicts(fin2)
    res["q2_planted_residual_mine"] = len(e2)

    res["verdict"] = P.verdict(
        not shape_bad and not viol and not dg_bad and not cls_bad and not horizon_bad
        and len(edges) == 0 and res["sum_equals_150"] and res["dg_dropped_equal"]
        and res["objective_tuple_equal"] and res["by_class_equal"]
        and all(s["dropped"] for s in samples) and all(k["within_horizon"] for k in kept_dg)
    )
    P.wr("p2_q4_report.json", res)
    print(json.dumps(res, ensure_ascii=False, indent=1)[:5000])


if __name__ == "__main__":
    main()
