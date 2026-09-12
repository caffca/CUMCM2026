# -*- coding: utf-8 -*-
"""P2-6：hint 链完整性——Q2_solution.hint_source 指向的侦察解存在性、动作合法性、rev 数、
以及它是否只是搜索起点（与最终解的差异）。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

WP = {"A": 100, "B": 10, "C": 1}


def tup(acts, pmap):
    rev = adj = pl = mg = 0
    for pid, o in acts.items():
        c = pmap[pid]["cls"]
        if o.get("revoke"):
            rev += 1
            pl += 2 * WP[c]
        elif o:
            adj += 1
            pl += WP[c]
            mg += sum(abs(v) for v in o.values() if isinstance(v, int) and not isinstance(v, bool))
    return [rev, adj, pl, mg]


def main():
    plans = P.load_plans()
    pmap = {p["id"]: p for p in plans}
    sol = P.rj(os.path.join("results", "Q2_solution.json"))
    hint_rel = sol["hint_source"]
    hint_abs = os.path.join(P.ROOT, hint_rel)
    exists = os.path.isfile(hint_abs)
    out = {"check": "hint 链", "hint_source_field": hint_rel, "hint_role_field": sol.get("hint_role"),
           "path_exists": exists, "resolved_abs": hint_abs}
    if exists:
        raw = json.load(open(hint_abs, encoding="utf-8"))
        acts = raw.get("actions") if isinstance(raw, dict) and "actions" in raw else raw
        out["file_top_keys"] = list(raw)[:8] if isinstance(raw, dict) else None
        out["is_plain_actions_map"] = isinstance(acts, dict) and all(isinstance(v, dict) for v in acts.values())
        acts = {k: v for k, v in acts.items() if isinstance(v, dict)}
        rev = [k for k, v in acts.items() if v.get("revoke")]
        illegal = []
        for pid, o in acts.items():
            if pid not in pmap:
                illegal.append({"id": pid, "why": "未知计划"})
                continue
            ks = set(o)
            if ks not in ({"revoke"}, {"df"}, {"dt"}):
                illegal.append({"id": pid, "why": f"键组合 {sorted(ks)}"})
                continue
            p = pmap[pid]
            if "df" in o and (abs(o["df"]) > P.DF_MAX or p["f0"] + o["df"] < 0 or p["f1"] + o["df"] > P.B_MAX):
                illegal.append({"id": pid, "why": f"df={o['df']} 非法"})
            if "dt" in o:
                q = P.shift(p, dt=o["dt"])
                if abs(o["dt"]) > P.DT_MAX or P.horizon_violation(q):
                    illegal.append({"id": pid, "why": f"dt={o['dt']} 非法/越界"})
        # hint 解自身的残余冲突（独立复算）
        fin = []
        for pid in sorted(pmap):
            o = acts.get(pid, {})
            if o.get("revoke"):
                continue
            fin.append(P.shift(pmap[pid], df=int(o.get("df", 0)), dt=int(o.get("dt", 0))))
        he, _ = P.all_conflicts(fin)
        ht = tup(acts, pmap)
        out["hint_n_actions"] = len(acts)
        out["hint_revoke_ids"] = sorted(rev)
        out["hint_revoke_count"] = len(rev)
        out["hint_illegal_actions"] = illegal
        out["hint_residual_conflicts_mine"] = len(he)
        out["hint_tuple_mine"] = ht
        final_acts = sol["actions"]
        out["final_revoke_count"] = sum(1 for v in final_acts.values() if v.get("revoke"))
        out["hint_rev_eq_6"] = len(rev) == 6
        out["hint_rev_eq_final_rev"] = len(rev) == out["final_revoke_count"]
        out["hint_equals_final_actions"] = acts == final_acts
        out["n_actions_differing"] = sum(1 for pid in set(acts) | set(final_acts)
                                         if acts.get(pid) != final_acts.get(pid))
        # 侦察目录配套件（FMS 引用的 star_edges.json）
        sd = os.path.dirname(hint_abs)
        out["scout_dir_files"] = sorted(os.listdir(sd))[:20]
        star = os.path.join(sd, "star_edges.json")
        out["star_edges_exists"] = os.path.isfile(star)
        if os.path.isfile(star):
            st = json.load(open(star, encoding="utf-8"))
            if isinstance(st, list):
                out["star_edges_size_mine"] = len(st)
            else:
                out["star_edges_top_keys"] = sorted(st)[:10]
                e = st.get("edges")
                out["star_edges_size_mine"] = len(e) if isinstance(e, (list, dict)) else st.get("stats", {}).get("star_edges")
                out["star_edges_stats"] = st.get("stats")
            out["star_edges_size_auth_in_Q2_solution"] = sol.get("gstar_edges")
    out["verdict"] = P.verdict(exists and out.get("hint_revoke_count") == 6 and not out.get("hint_illegal_actions"))
    P.wr("p2_hint_report.json", out)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
