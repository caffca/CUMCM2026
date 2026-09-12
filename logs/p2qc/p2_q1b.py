# -*- coding: utf-8 -*-
"""P2-1b：半开区间口径敏感性——若把相接误判为交叠（闭区间口径），冲突数会如何变化。
用于证明 297 这个数字对口径是稳定的、且权威实现没有把'相接'误计入。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa


def conflict_closed(p, q):
    """错误口径示范：闭区间 [a,b] 交叠（>=）——相接会被误判为冲突。"""
    if min(p["f1"], q["f1"]) - max(p["f0"], q["f0"]) < 0:
        return False
    for a in P.slot_list(p):
        for b in P.slot_list(q):
            if min(a[1], b[1]) - max(a[0], b[0]) >= 0:
                return True
    return False


def main():
    plans = P.load_plans()
    edges, _ = P.all_conflicts(plans)
    eset = {tuple(e) for e in edges}
    closed = []
    touch_band = []
    touch_time = []
    for i in range(len(plans)):
        for j in range(i + 1, len(plans)):
            a, b = plans[i], plans[j]
            x, y = sorted((a["id"], b["id"]))
            if conflict_closed(a, b) and (x, y) not in eset:
                closed.append([x, y])
            if a["f1"] == b["f0"] or b["f1"] == a["f0"]:
                touch_band.append([x, y])
            sa, sb = set(P.slot_list(a)), set(P.slot_list(b))
            if sa and sb and any(ea == s2 for (s1, ea) in sa for (s2, e2) in sb) and (x, y) not in eset:
                touch_time.append([x, y])
    # 硬非空交集判据（内部有公共整数格） vs 半开解析判据
    cells_hit = []
    occ = {}
    for p in plans:
        s = set()
        for (a, b) in P.slot_list(p):
            for t in range(a, b):
                for f in range(p["f0"], p["f1"]):
                    s.add((t, f))
        occ[p["id"]] = s
    for i in range(len(plans)):
        for j in range(i + 1, len(plans)):
            if occ[plans[i]["id"]] & occ[plans[j]["id"]]:
                cells_hit.append(sorted([plans[i]["id"], plans[j]["id"]]))
    res = {
        "check": "Q1 口径敏感性",
        "edges_halfopen_mine": len(edges),
        "edges_if_closed_intervals": len(edges) + len(closed),
        "extra_pairs_only_if_closed": [list(e) for e in closed][:20],
        "n_extra_pairs_only_if_closed": len(closed),
        "band_touching_pairs": len(touch_band),
        "band_touching_examples": touch_band[:5],
        "time_endpoint_touching_nonconflict_pairs": len(touch_time),
        "time_touch_examples": touch_time[:5],
        "edges_by_distinct_cells": len(cells_hit),
        "cells_agree_with_halfopen":
            {tuple(sorted(e)) for e in edges} == {tuple(sorted(e)) for e in cells_hit},
    }
    res["verdict"] = P.verdict(res["edges_halfopen_mine"] == 297 and res["cells_agree_with_halfopen"]
                               and res["n_extra_pairs_only_if_closed"] > 0)
    P.wr("p2_q1b_sensitivity.json", res)
    print(json.dumps(res, ensure_ascii=False, indent=1)[:2500])


if __name__ == "__main__":
    main()
