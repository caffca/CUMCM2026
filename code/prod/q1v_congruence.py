# -*- coding: utf-8 -*-
"""Q1 变体 C：类内同余闭式 + 跨类回退枚举。独立实现。"""
import os, sys, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local  # noqa

T_MAX = 643


def main():
    a, param = std_args("q1 congruence")
    tm = Timer()
    plans = load_plans_local()
    byc = {}
    for p in plans:
        byc.setdefault(p["cls"], []).append(p)
    for c, xs in byc.items():
        assert len({(x["g"], x["d"], x["n"]) for x in xs}) == 1, "类内参数须齐次（前提断言）"
    edges = []
    closed_checked = 0
    fallback = 0
    def overlap_interval(a, b):
        sa = [(a["t0"] + k * (a["g"] + a["d"]), a["t0"] + k * (a["g"] + a["d"]) + a["d"]) for k in range(a["n"])]
        sb = [(b["t0"] + k * (b["g"] + b["d"]), b["t0"] + k * (b["g"] + b["d"]) + b["d"]) for k in range(b["n"])]
        return any(min(x[1], y[1]) - max(x[0], y[0]) > 0 for x in sa for y in sb)
    for i in range(len(plans)):
        for j in range(i + 1, len(plans)):
            x, y = plans[i], plans[j]
            if min(x["f1"], y["f1"]) - max(x["f0"], y["f0"]) <= 0:
                continue
            if x["cls"] == y["cls"]:
                g, d, n = x["g"], x["d"], x["n"]
                P = g + d
                assert 2 * (d - 1) < P, "闭式前提 2(d-1)<P"
                dt = y["t0"] - x["t0"]
                r = dt % P
                reach = abs(dt) <= (n - 1) * P + (d - 1)
                hit = r < d or (P - r) < d
                closed_checked += 1
                hit_e = hit and reach
            else:
                fallback += 1
                hit_e = overlap_interval(x, y)
            if hit_e:
                edges.append([x["id"], y["id"]])
    edges.sort()
    cp = {}
    for xx, yy in edges:
        k = "".join(sorted(xx[0] + yy[0]))
        cp[k] = cp.get(k, 0) + 1
    res = {"question_id": "Q1", "variant": "congruence",
           "closed_form_pairs": closed_checked, "fallback_pairs": fallback,
           "edges": edges,
           "counts": {"edges": len(edges), "AB": cp.get("AB", 0), "AC": cp.get("AC", 0),
                       "AA": cp.get("AA", 0), "BC": cp.get("BC", 0), "BB": cp.get("BB", 0),
                       "CC": cp.get("CC", 0)},
           "edges_sha256": hashlib.sha256(json.dumps(edges).encode()).hexdigest()}
    emit(a.output_dir, res, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "all_pairs_enumerated", "evaluator_calls": 0,
                             "budget_class": a.budget_class, "seed": a.seed,
                             "scenario": a.scenario, "parameter": param})


if __name__ == "__main__":
    main()
