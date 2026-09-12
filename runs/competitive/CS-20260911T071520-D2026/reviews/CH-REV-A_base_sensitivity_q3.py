# -*- coding: utf-8 -*-
"""CH-REV-A: base-sensitivity probe for Q3 N*=139 — same pipeline over other Q2 scout solutions."""
import hashlib, io, json, os, time
from collections import defaultdict

ROOT = r"F:\2026 数模\D题重跑\D题\runs\competitive\CS-20260911T071520-D2026"
T_MAX, B_MAX, W, D, G, N = 643, 100, 3, 2, 8, 12
PERIOD, SPAN = 10, 112
F0_MAX, T0_MAX = 97, 531

ci = json.loads(io.open(os.path.join(ROOT, "common_input.json"), encoding="utf-8").read())
plans = {r[0]: dict(f0=r[1], f1=r[2], t0=r[3], t1=r[4], g=r[5], n=r[6], d=r[4]-r[3])
         for r in ci["plans_table_compact"]}


def occ_from(actions_path):
    sol = json.loads(io.open(actions_path, encoding="utf-8").read())
    occ = [0]*100
    for pid, p in plans.items():
        a = sol.get(pid) or {}
        if a.get("revoke"):
            continue
        df, dt = int(a.get("df", 0)), int(a.get("dt", 0))
        P = p["g"]+p["d"]
        for k in range(p["n"]):
            s = p["t0"]+dt+k*P
            for t in range(s, s+p["d"]):
                for f in range(p["f0"]+df, p["f1"]+df):
                    occ[f] |= 1 << t
    return occ


TM = [sum(0b11 << (t0 + k*PERIOD) for k in range(N)) for t0 in range(T0_MAX+1)]

from ortools.sat.python import cp_model


def optimum_for(name, path):
    t0_ = time.time()
    occ = occ_from(path)
    cands = []
    for f0 in range(F0_MAX+1):
        o3 = occ[f0] | occ[f0+1] | occ[f0+2]
        for t0 in range(T0_MAX+1):
            if (TM[t0] & o3) == 0:
                cands.append((f0, t0))
    m = cp_model.CpModel()
    x = [m.NewBoolVar("x%d" % i) for i in range(len(cands))]
    cell2c = defaultdict(list)
    for i, (f0, t0) in enumerate(cands):
        for k in range(N):
            for t in range(t0+k*PERIOD, t0+k*PERIOD+D):
                for f in range(f0, f0+W):
                    cell2c[t*B_MAX+f].append(i)
    for cell, lst in cell2c.items():
        if len(lst) >= 2:
            m.Add(sum(x[i] for i in lst) <= 1)
    m.Maximize(sum(x))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = 240.0
    s.parameters.num_search_workers = 8
    s.parameters.random_seed = 0
    st = s.Solve(m)
    used = sum(bin(v).count("1") for v in occ)
    print("%s: cands=%d status=%s N*=%s bound=%s used_cells=%d wall=%.1fs" %
          (name, len(cands), s.StatusName(st),
           int(round(s.ObjectiveValue())) if s.StatusName(st) in ("OPTIMAL", "FEASIBLE") else None,
           int(s.BestObjectiveBound()), used, time.time()-t0_))


optimum_for("base=Q2-R51", os.path.join(ROOT, "scouts", "Q2-R51", "solution_actions.json"))
optimum_for("base=Q2-R32", os.path.join(ROOT, "scouts", "Q2-R32", "solution_actions.json"))
optimum_for("base=Q2-R41(seed11)", os.path.join(ROOT, "scouts", "Q2-R41", "solution_actions_seed11.json"))
