# -*- coding: utf-8 -*-
"""Q1 变体 A：逐对区间算术（双内实现：A1 逐(k,m)对；A2 区间并压缩+两指针）。独立自含。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local  # noqa

HORIZON = 643


def slots(p):
    return [(p["t0"] + k * (p["g"] + p["d"]), p["t0"] + k * (p["g"] + p["d"]) + p["d"]) for k in range(p["n"])]


def band_overlap(a, b):
    return min(a["f1"], b["f1"]) - max(a["f0"], b["f0"]) > 0


def time_overlap_bruteforce(a, b):
    sa, sb = slots(a), slots(b)
    for x in sa:
        for y in sb:
            if min(x[1], y[1]) - max(x[0], y[0]) > 0:
                return True
    return False


def merge_union(iv):
    out = []
    for s, e in sorted(iv):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def overlap_two_pointer(ma, mb):
    i = j = 0
    while i < len(ma) and j < len(mb):
        if min(ma[i][1], mb[j][1]) - max(ma[i][0], mb[j][0]) > 0:
            return True
        if ma[i][1] <= mb[j][1]:
            i += 1
        else:
            j += 1
    return False


def main():
    a, param = std_args("q1 interval")
    tm = Timer()
    plans = load_plans_local()
    merged = {p["id"]: merge_union(slots(p)) for p in plans}
    edges = []
    n2 = 0
    for i in range(len(plans)):
        for j in range(i + 1, len(plans)):
            x, y = plans[i], plans[j]
            hit1 = band_overlap(x, y) and time_overlap_bruteforce(x, y)
            hit2 = band_overlap(x, y) and overlap_two_pointer(merged[x["id"]], merged[y["id"]])
            if hit1 != hit2:
                raise SystemExit(f"internal A1/A2 mismatch {x['id']}-{y['id']}")
            if hit1:
                edges.append([x["id"], y["id"]])
            n2 += 1
    # 边界用例：相接不交叠 / 交叠必中
    bc_fail = 0
    def check(s1, e1, s2, e2, expect):
        ok = (min(e1, e2) - max(s1, s2) > 0) == expect
        return 0 if ok else 1
    cases = [((165, 170), (170, 175), False), ((165, 170), (167, 172), True),
             ((0, 2), (2, 4), False), ((35, 40), (100, 105), False), ((35, 40), (38, 42), True),
             ((96, 100), (100, 104), False), ((531, 533), (639, 641), False), ((531, 533), (632, 634), True)]
    for c in cases:
        bc_fail += check(c[0][0], c[0][1], c[1][0], c[1][1], c[2])
    edges.sort()
    import hashlib
    cp = {}
    for x, y in edges:
        k = "".join(sorted(x[0] + y[0]))
        cp[k] = cp.get(k, 0) + 1
    res = {"question_id": "Q1", "variant": "interval", "impl_A2_internal_equal": True,           "pairs_checked": n2, "edges": edges,
           "counts": {"edges": len(edges), "AB": cp.get("AB", 0), "AC": cp.get("AC", 0),
                       "AA": cp.get("AA", 0), "BC": cp.get("BC", 0), "BB": cp.get("BB", 0),
                       "CC": cp.get("CC", 0)},
           "edges_sha256": hashlib.sha256(json.dumps(edges).encode()).hexdigest(),
           "boundary_cases_failed": bc_fail, "T_MAX": HORIZON}
    emit(a.output_dir, res, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "all_pairs_enumerated", "evaluator_calls": 0,
                             "budget_class": a.budget_class, "seed": a.seed,
                             "scenario": a.scenario, "parameter": param})


if __name__ == "__main__":
    main()
