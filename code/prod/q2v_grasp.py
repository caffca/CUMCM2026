# -*- coding: utf-8 -*-
"""Q2 变体：GRASP+局部搜索（baseline 对照，独立于 CP-SAT 变体，不 import 其代码）。"""
import os, sys, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local  # noqa

T_MAX, B_MAX, DFM, DTM = 643, 100, 10, 5
WP = {"A": 100, "B": 10, "C": 1}


def cells(p, df=0, dt=0):
    m = 0
    for k in range(p["n"]):
        s = p["t0"] + dt + k * (p["g"] + p["d"])
        if s < 0 or s + p["d"] > T_MAX:
            return None
        for t in range(s, s + p["d"]):
            for f in range(p["f0"] + df, p["f1"] + df):
                if f < 0 or f >= B_MAX:
                    return None
                m |= 1 << (t * B_MAX + f)
    return m


def main():
    a, param = std_args("q2 grasp")
    tm = Timer()
    seed = int(param.get("grasp_seed", a.seed if str(a.seed).isdigit() else 11))
    budget = float(param.get("budget", 240))
    rcl = int(param.get("rcl", 3))
    rng = random.Random(seed)
    plans = load_plans_local()
    opts = {}
    for p in plans:
        lst = [("id", 0)]
        for d in range(-DFM, DFM + 1):
            if d and cells(p, df=d) is not None:
                lst.append(("df", d))
        for d in range(-DTM, DTM + 1):
            if d and cells(p, dt=d) is not None:
                lst.append(("dt", d))
        lst.append(("rv", 0))
        opts[p["id"]] = lst
    masks = {p["id"]: [cells(p, df=v if k == "df" else 0, dt=v if k == "dt" else 0)
                       if k != "rv" else 0 for k, v in opts[p["id"]]] for p in plans}
    ids = sorted(opts)
    # 潜在边：包络位图非零交
    emvs = {}
    for pid in ids:
        u = 0
        for m in masks[pid]:
            u |= m
        emvs[pid] = u
    P = {p["id"]: p for p in plans}
    base_edges = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            x, y = ids[i], ids[j]
            if emvs[x] & emvs[y]:
                bad = set()
                for ki, mi in enumerate(masks[x]):
                    for kj, mj in enumerate(masks[y]):
                        if mi & mj:
                            bad.add((ki, kj))
                base_edges.append((x, y, bad))
    idxof = {pid: {opt: k for k, opt in enumerate(opts[pid])} for pid in ids}

    def objective(cur):
        rev = adj = pl = mg = 0
        for pid, o in cur.items():
            k, v = o
            if k == "rv":
                rev += 1; pl += 2 * WP[pid[0]]
            elif k != "id":
                adj += 1; pl += WP[pid[0]]; mg += abs(v)
        return (rev, adj, pl, mg)

    best = None
    starts = 0
    while tm.el() < budget:
        starts += 1
        cur = {pid: ("id", 0) for pid in ids}
        occ = {pid: masks[pid][idxof[pid][("id", 0)]] for pid in ids}
        frontier = [(x, y, bad) for (x, y, bad) in base_edges if bad]
        rng.shuffle(frontier)
        guard = 0
        while guard < 200000:
            guard += 1
            dirty = []
            for (x, y, bad) in frontier:
                if occ[x] & occ[y]:
                    dirty.append((x, y))
            if not dirty:
                break
            x, y = rng.choice(dirty)
            cands = []
            for pid in (x, y):
                for o in opts[pid]:
                    cands.append((pid, o))
            scored = []
            for pid, o in cands:
                k, v = o
                newocc = masks[pid][idxof[pid][o]]
                old = occ[pid]
                others = [q for q in ids if q != pid and (emvs[pid] & emvs[q])]
                viol = sum(1 for q in others if newocc & occ[q]) - sum(1 for q in others if old & occ[q])
                trial = dict(cur); trial[pid] = o
                scored.append((viol, objective(trial), pid, o))
            feas = [s for s in scored if s[0] <= 0]
            pool = (feas or scored)
            pool.sort(key=lambda s: (s[0], s[1]))
            pick = pool[0] if rng.random() < 0.6 else pool[min(len(pool) - 1, rng.randrange(min(rcl + 1, len(pool))))]
            pid, o = pick[2], pick[3]
            cur[pid] = o
            occ[pid] = masks[pid][idxof[pid][o]]
        t = objective(cur)
        if best is None or t < best[0]:
            best = (t, dict(cur))
    res = {"question_id": "Q2", "variant": "grasp", "grasp_seed": seed, "restarts": starts,
           "objective_tuple": list(best[0]),
           "objective_scalar": 10**12 * best[0][0] + 10**8 * best[0][1] + 10**4 * best[0][2] + best[0][3],
           "actions": {p: ({"revoke": True} if k == "rv" else {k: v}) for p, (k, v) in best[1].items() if k != "id"}}
    emit(a.output_dir, res, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "time_budget", "evaluator_calls": starts,
                             "budget_class": a.budget_class, "seed": seed,
                             "scenario": a.scenario, "parameter": param})


if __name__ == "__main__":
    main()
