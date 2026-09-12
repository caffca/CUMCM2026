# -*- coding: utf-8 -*-
"""P2-1：从 CSV 独立重算全部冲突对（纯解析区间算术，O(n^2)），与 results/Q1_detect.json 对账。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

def main():
    plans = P.load_plans()
    counts, integrity = P.data_integrity(plans)
    edges, checked = P.all_conflicts(plans)

    q1 = P.rj(os.path.join("results", "Q1_detect.json"))
    auth_edges = [list(e) for e in q1["edges"]]
    auth_set, mine_set = set(map(tuple, auth_edges)), set(map(tuple, edges))

    only_auth = sorted(auth_set - mine_set)
    only_mine = sorted(mine_set - auth_set)
    symdiff = len(only_auth) + len(only_mine)

    # 生产实现里 edges 已 sort()，此处按其口径复算 sha（同时尝试我方排序键口径）
    sha_mine = P.sha_of_edges([list(e) for e in sorted(mine_set)])
    sha_auth_field = q1["edges_sha256"]
    variant_shas = {k: v.get("edges_sha256") for k, v in (q1.get("per_variant") or {}).items()}

    mine_cp = P.classpair_counts([list(e) for e in sorted(mine_set)])
    auth_cp = q1["counts"]

    # 逐对冲突的最小见证（防止“巧合相等”）：抽 5 条边给出具体 k,l 见证；再抽 5 条非边给出否证
    pmap = {p["id"]: p for p in plans}
    witnesses = []
    for a, b in [list(e) for e in sorted(mine_set)][:5]:
        ok, r = P.conflict(pmap[a], pmap[b], reason=True)
        witnesses.append({"pair": [a, b], "ok": ok, "k_l": r[:2], "slots": [list(r[2]), list(r[3])],
                          "band": [pmap[a]["f0"], pmap[a]["f1"], pmap[b]["f0"], pmap[b]["f1"]]})
    nonex = []
    shown = 0
    for i in range(len(plans)):
        for j in range(i + 1, len(plans)):
            a, b = plans[i]["id"], plans[j]["id"]
            if (a, b) in mine_set or (b, a) in mine_set:
                continue
            ok, r = P.conflict(pmap[a], pmap[b], reason=True)
            band = P.band_hit(pmap[a], pmap[b])
            nonex.append({"pair": [a, b], "band_overlap": band, "time_overlap_exists": (not ok) if band else None})
            shown += 1
            if shown >= 5:
                break
        if shown >= 5:
            break

    involved = sorted({x for e in mine_set for x in e})
    isolated = sorted(set(pmap) - set(involved))

    res = {
        "check": "Q1_detect 独立重算",
        "n_plans": len(plans), "class_counts": counts, "csv_integrity_bad": integrity,
        "pairs_checked_mine": checked, "pairs_checked_auth": q1["pairs_checked"],
        "edges_mine": len(edges), "edges_auth": len(auth_edges), "edges_auth_field": auth_cp["edges"],
        "symdiff": symdiff, "only_in_authority": only_auth, "only_in_p2": only_mine,
        "sha_mine": sha_mine, "sha_auth_field": sha_auth_field, "sha_equal": sha_mine == sha_auth_field,
        "per_variant_shas": variant_shas,
        "counts_mine": {k: mine_cp.get(k, 0) for k in ["AB", "AC", "BC", "AA", "BB", "CC"]},
        "counts_auth": {k: auth_cp.get(k, 0) for k in ["AB", "AC", "BC", "AA", "BB", "CC"]},
        "counts_equal": {k: mine_cp.get(k, 0) == auth_cp.get(k, 0) for k in ["AB", "AC", "BC", "AA", "BB", "CC"]},
        "involved_mine": len(involved), "involved_auth": q1["involved_plans"],
        "isolated_mine": isolated, "isolated_auth": q1["isolated_plans"],
        "T_MAX_mine_derivation": 600 + 30 + 12 + 1,
        "T_MAX_auth": q1["T_MAX"],
        "max_slot_end_over_all_plans": max(e for p in plans for (s, e) in P.slot_list(p)),
        "witness_edges": witnesses, "witness_nonedges": nonex,
        "auth_evaluator_counts": q1.get("evaluator_counts"),
        "auth_three_way_max_symdiff": q1.get("three_way_max_symdiff"),
        "auth_all_three_sha_equal": q1.get("all_three_sha_equal"),
    }
    res["verdict"] = P.verdict(
        symdiff == 0 and res["sha_equal"] and res["pairs_checked_mine"] == res["pairs_checked_auth"]
        and all(res["counts_equal"].values()) and len(involved) == q1["involved_plans"]
        and isolated == sorted(q1["isolated_plans"]) and not integrity
    )
    path = P.wr("p2_q1_report.json", res)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    print("WROTE", path)


if __name__ == "__main__":
    main()
