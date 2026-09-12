# -*- coding: utf-8 -*-
"""Q1 变体 B：时频位图（大整数 AND）+ 按频段倒排 join。独立实现，不 import 变体 A。"""
import os, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local  # noqa

T_MAX = 643


def bitmap_of(p):
    m = 0
    for k in range(p["n"]):
        s = p["t0"] + k * (p["g"] + p["d"])
        for t in range(s, s + p["d"]):
            for f in range(p["f0"], p["f1"]):
                m |= 1 << (t * 100 + f)
    return m


def main():
    a, param = std_args("q1 bitmap")
    tm = Timer()
    plans = load_plans_local()
    bm = [bitmap_of(p) for p in plans]
    inv = {}
    for idx, p in enumerate(plans):
        for k in range(p["n"]):
            s = p["t0"] + k * (p["g"] + p["d"])
            for t in range(s, s + p["d"]):
                for f in range(p["f0"], p["f1"]):
                    inv.setdefault(f, set()).add((t, idx))
    edges = []
    checked = set()
    for f, lst in inv.items():
        cand = {}
        for t, idx in lst:
            cand.setdefault(idx, []).append(t)
        ids = sorted(cand)
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                i, j = ids[x], ids[y]
                if (i, j) in checked:
                    continue
                checked.add((i, j))
                if bm[i] & bm[j]:
                    edges.append([plans[i]["id"], plans[j]["id"]])
    for i in range(len(plans)):
        for j in range(i + 1, len(plans)):
            if (i, j) not in checked and (bm[i] & bm[j]):
                raise SystemExit("inverted index missed a band")
    edges.sort()
    cp = {}
    for x, y in edges:
        k = "".join(sorted(x[0] + y[0]))
        cp[k] = cp.get(k, 0) + 1
    res = {"question_id": "Q1", "variant": "bitmap",
           "pairs_checked": len(plans) * (len(plans) - 1) // 2, "edges": edges,
           "counts": {"edges": len(edges), "AB": cp.get("AB", 0), "AC": cp.get("AC", 0),
                       "AA": cp.get("AA", 0), "BC": cp.get("BC", 0), "BB": cp.get("BB", 0),
                       "CC": cp.get("CC", 0)},
           "edges_sha256": hashlib.sha256(json.dumps(edges).encode()).hexdigest()}
    used = bin(0)
    agg = 0
    for m in bm:
        agg |= m
    res["distinct_cells"] = bin(agg).count("1")
    res["T_MAX"] = T_MAX
    emit(a.output_dir, res, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "all_pairs_enumerated", "evaluator_calls": 0,
                             "budget_class": a.budget_class, "seed": a.seed,
                             "scenario": a.scenario, "parameter": param})


if __name__ == "__main__":
    main()
