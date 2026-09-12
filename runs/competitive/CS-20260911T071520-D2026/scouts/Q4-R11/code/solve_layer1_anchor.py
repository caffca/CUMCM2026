# -*- coding: utf-8 -*-
"""REV-Q4-01 / TF-1：层 1（min Σr）锚定重跑。
模型 = 与 solve_r11 完全同一 Q4 构建器；hint = Q2-R51 植入解；附加约束 Σr ≤ rev-cap(6)。
预算 cap 秒、workers 可配；输出 incumbent(Σr 的 ub/lb、闭合性) + 快照解 + 全元组 evaluator 复核。
用法：python solve_layer1_anchor.py --workers 8 --cap 300 --hint <sol> --rev-cap 6 --out-dir run_anchor --tag w8
"""
import argparse, io, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import q4common as Q
from solve_r11 import build_model, state_to_actions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cap", type=float, default=300.0)
    ap.add_argument("--hint", required=True)
    ap.add_argument("--rev-cap", type=int, default=6)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    t0 = time.time()
    plans = Q.CE.load_plans()
    doms = Q.build_domains(plans, allow_gap=True)
    edges, forb = Q.build_edges(plans, doms)
    hint = json.load(io.open(a.hint, encoding="utf-8"))
    m, solver, x, exprs, n_clauses = build_model(plans, doms, edges, forb, hint, a.workers, a.seed)
    rev = exprs[0]
    m.Add(rev <= a.rev_cap)  # 上界锚：任何 incumbent 不劣于植入解第一级
    m.Minimize(rev)
    solver.parameters.max_time_in_seconds = a.cap
    st = solver.Solve(m)
    sname = solver.StatusName(st)
    rec = {"tag": a.tag, "workers": a.workers, "cap_seconds": a.cap, "seed": a.seed,
           "rev_cap": a.rev_cap, "hint": os.path.basename(a.hint),
           "status": sname,
           "edges": len(edges), "clauses": n_clauses,
           "wall_seconds_model": round(time.time() - t0, 1)}
    if sname in ("OPTIMAL", "FEASIBLE"):
        ub = int(round(solver.ObjectiveValue())); lb = int(round(solver.BestObjectiveBound()))
        rec.update({"revoke_ub": ub, "revoke_lb": lb, "closed": sname == "OPTIMAL"})
        sol = state_to_actions(doms, x, solver)
        obj = list(Q.CE.objective_tuple(plans, sol, allow_gap=True))
        rec["snapshot_objective_tuple_internal"] = obj
        sp = os.path.join(a.out_dir, f"solution_layer1_{a.tag}.json")
        io.open(sp, "w", encoding="utf-8").write(json.dumps(sol, ensure_ascii=False, indent=1))
        import subprocess
        subprocess.run([sys.executable, os.path.join(Q.TOURN_DIR, "canonical_evaluator.py"),
                        "--question", "Q4", "--solution", sp,
                        "--out", os.path.join(a.out_dir, f"eval_q4_layer1_{a.tag}.json")],
                       capture_output=True)
        ev = json.load(io.open(os.path.join(a.out_dir, f"eval_q4_layer1_{a.tag}.json"), encoding="utf-8"))
        rec["evaluator_tuple"] = ev["objective"]; rec["evaluator_feasible"] = ev["feasible"]
    rec["total_wall_seconds"] = round(time.time() - t0, 1)
    io.open(os.path.join(a.out_dir, f"layer1_anchor_{a.tag}.json"), "w", encoding="utf-8").write(
        json.dumps(rec, ensure_ascii=False, indent=1))
    print(f"[L1/{a.tag}] {sname} lb={rec.get('revoke_lb')} ub={rec.get('revoke_ub')} "
          f"tuple={rec.get('evaluator_tuple')} wall={rec['total_wall_seconds']}s", flush=True)


if __name__ == "__main__":
    main()
