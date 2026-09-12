# -*- coding: utf-8 -*-
"""独立对照（Q3-R11 scout 目录内）：HiGHS LP 松弛上界，验证 CP-SAT 的 OPTIMAL=139 声明。
LP: max 1^T x s.t. A x <= 1（每时频格一行）, 0<=x<=1。若 v_LP < 140 ⇒ 整数最优 <=139（与 incumbent=139 会合）。
与 CP-SAT 完全不同的求解器族（HiGHS 单纯形/内点），作为第二腿证据。"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_q3 as C
import numpy as np
from scipy import sparse
from scipy.optimize import milp, LinearConstraint, Bounds
from collections import defaultdict

t0 = time.time()
base = C.build_base(); tm = C.make_tmask_table()
cands, by_f0 = C.gen_candidates(base["occ"], tm)
P = len(cands); assert P == 2123, P
cell2c = defaultdict(list)
for i, (f0, t) in enumerate(cands):
    for cell in C.cells_of(f0, t):
        cell2c[cell].append(i)
rows = []; cols = []
r = 0
for cell, lst in cell2c.items():
    if len(lst) >= 2:
        for i in lst:
            rows.append(r); cols.append(i)
        r += 1
nrows = r
A = sparse.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(nrows, P))
c = np.ones(P)
res = milp(c=-c, constraints=LinearConstraint(A, -np.inf, np.ones(nrows, dtype=float)),
           integrality=np.zeros(P, dtype=int), bounds=Bounds(np.zeros(P), np.ones(P)),
           options={"time_limit": 240, "presolve": True})
bound_val = (-res.fun) if res.fun is not None else None
out = {"lp_status": int(res.status), "lp_message": str(res.message),
       "lp_bound_max_formulation": bound_val,
       "lp_bound_floor": (int(np.floor(bound_val + 1e-9)) if bound_val is not None else None),
       "confirms_no_140": bool(bound_val is not None and bound_val < 140),
       "rows": nrows, "nnz": len(rows), "vars": P,
       "wall_s": round(time.time() - t0, 1)}
print(json.dumps(out, ensure_ascii=False))
json.dump(out, open(os.path.join(C.SCOUT_DIR, "lp_crosscheck_hiGHS.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
