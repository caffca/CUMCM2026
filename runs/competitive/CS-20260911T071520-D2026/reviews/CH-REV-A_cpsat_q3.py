# -*- coding: utf-8 -*-
"""CH-REV-A: independent CP-SAT model-B rebuild for Q3 (leg-b of the N*=139 claim)."""
import json, io, os, time
from collections import defaultdict

ROOT = r"F:\2026 数模\D题重跑\D题\runs\competitive\CS-20260911T071520-D2026"
T_MAX, B_MAX, W, D, G, N = 643, 100, 3, 2, 8, 12
PERIOD, SPAN = 10, 112
F0_MAX, T0_MAX = 97, 531

ci = json.loads(io.open(os.path.join(ROOT, "common_input.json"), encoding="utf-8").read())
plans = {r[0]: dict(f0=r[1], f1=r[2], t0=r[3], t1=r[4], g=r[5], n=r[6], d=r[4]-r[3])
         for r in ci["plans_table_compact"]}
sol_q2 = json.loads(io.open(os.path.join(ROOT, "scouts", "Q2-R51", "solution_actions.json"), encoding="utf-8").read())
occ = [0]*B_MAX
for pid, p in plans.items():
    a = sol_q2.get(pid) or {}
    if a.get("revoke"):
        continue
    df, dt = int(a.get("df", 0)), int(a.get("dt", 0))
    P = p["g"] + p["d"]
    for k in range(p["n"]):
        s = p["t0"] + dt + k*P
        for t in range(s, s + p["d"]):
            for f in range(p["f0"]+df, p["f1"]+df):
                occ[f] |= 1 << t
TM = [sum(0b11 << (t0 + k*PERIOD) for k in range(N)) for t0 in range(T0_MAX+1)]
cands = []
for f0 in range(F0_MAX+1):
    o3 = occ[f0] | occ[f0+1] | occ[f0+2]
    for t0 in range(T0_MAX+1):
        if (TM[t0] & o3) == 0:
            cands.append((f0, t0))
P_ = len(cands)
assert P_ == 2123
cell2c = defaultdict(list)
for i, (f0, t0) in enumerate(cands):
    for k in range(N):
        for t in range(t0 + k*PERIOD, t0 + k*PERIOD + D):
            for f in range(f0, f0 + W):
                cell2c[t*B_MAX + f].append(i)

from ortools.sat.python import cp_model
results = {}
for tag, workers, seed in (("B_w8_s7", 8, 7), ("B_w1_s0", 1, 0)):
    m = cp_model.CpModel()
    x = [m.NewBoolVar("x%d" % i) for i in range(P_)]
    for cell, lst in cell2c.items():
        if len(lst) >= 2:
            m.Add(sum(x[i] for i in lst) <= 1)
    m.Maximize(sum(x))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = 300.0
    s.parameters.num_search_workers = workers
    s.parameters.random_seed = seed
    t0_ = time.time()
    st = s.Solve(m)
    ok_sol = s.StatusName(st) in ("OPTIMAL", "FEASIBLE")
    results[tag] = {"status": s.StatusName(st),
                    "value": int(round(s.ObjectiveValue())) if ok_sol else None,
                    "best_bound": int(s.BestObjectiveBound()),
                    "wall_s": round(time.time()-t0_, 2)}
    sel = sorted(cands[i] for i in range(P_) if ok_sol and s.Value(x[i]))
    # independent re-verify of returned placement set
    cols = [0]*B_MAX
    viol = 0
    for (f0, t0) in sel:
        b = TM[t0]
        for f in range(f0, f0+W):
            if cols[f] & b:
                viol += 1
            cols[f] |= b
    results[tag]["n_selected"] = len(sel)
    results[tag]["internal_viol"] = viol
print(json.dumps(results, ensure_ascii=False, indent=1))
