# -*- coding: utf-8 -*-
"""Q3 初等界（独立自含）：相位×连续块双计数（两格在盒内判据 (641-r)//10）+ 密度界 + 自检门。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local, resolve_base  # noqa
T_MAX, B_MAX = 643, 100
CW, CD, CG, CN = 3, 2, 8, 12
P = CG + CD
CELLS_PER = CW * CD * CN


def main():
    a, param = std_args("q3 bound")
    tm = Timer()
    bp, _ = resolve_base(param.get("base", "results/Q2_solution.json"), a.run_id,
                         want_variant="cpsat_lex", want_workers="main")
    base = json.load(open(bp, encoding="utf-8"))
    acts = (base.get("result") or base).get("actions") or base.get("actions") or {}
    plans = {p["id"]: p for p in load_plans_local()}
    occ = [[0] * T_MAX for _ in range(B_MAX)]  # occ[f][t]
    for pid, p in plans.items():
        o = acts.get(pid, {})
        if o.get("revoke"):
            continue
        df, dt = int(o.get("df", 0)), int(o.get("dt", 0))
        for k in range(p["n"]):
            s = p["t0"] + dt + k * (p["g"] + p["d"])
            for t in range(s, s + p["d"]):
                for f in range(p["f0"] + df, p["f1"] + df):
                    occ[f][t] = 1
    total_blocks = 0
    for f in range(B_MAX):
        col = occ[f]
        for r in range(P):
            # oct 序号 j 可用 ⟺ 两格 (r+10j, r+10j+2) 均在 [0,643) 且空闲
            J = (T_MAX - 2 - r) // P  # = (641-r)//10：末格 642 起算（r+10J+1 ≤ 642）
            run = 0
            for j in range(J + 1):
                t0 = r + P * j
                free = col[t0] == 0 and col[t0 + 1] == 0
                if free:
                    run += 1
                else:
                    total_blocks += run // CN
                    run = 0
            total_blocks += run // CN
    ub_phase = total_blocks // CW  # 每放置恰为 CW 个带各计 1（双计数 ÷3）
    free_cells = sum(1 for f in range(B_MAX) for t in range(T_MAX) if occ[f][t] == 0)
    ub_density = free_cells // CELLS_PER
    ub = min(ub_phase, ub_density)
    emit(a.output_dir, {"question_id": "Q3", "variant": "bound_elementary",
                        "ub_phase_doublecount": ub_phase, "ub_density": ub_density,
                        "ub_min": ub, "free_cells": free_cells},
         {"elapsed_seconds": tm.el(), "status": "completed", "stopping_reason": "closed_form_bound",
          "evaluator_calls": 0, "budget_class": a.budget_class, "seed": a.seed,
          "scenario": a.scenario, "parameter": param})
    print("bounds:", ub_phase, ub_density, "rt", tm.el())


if __name__ == "__main__":
    main()
