# -*- coding: utf-8 -*-
"""Q4 组三候选 result.json / scout.json 聚合落盘（Prototype Engineer Q4）。
读各 run 目录产物 + 跑 canonical_evaluator（Q4 及各口径），写协议契约字段。
用法：python finalize_q4.py
"""
import io, json, os, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
TOURN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCOUTS = os.path.join(TOURN, "scouts")
EV = os.path.join(TOURN, "canonical_evaluator.py")
PY = sys.executable


def jload(p):
    return json.load(io.open(p, encoding="utf-8"))


def jdump(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False, indent=1))


def run_eval(question, sol_path, out_path, base_actions=None):
    cmd = [PY, EV, "--question", question, "--solution", sol_path, "--out", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return jload(out_path)


def scalar(obj_tuple):
    return obj_tuple[0] * 10**12 + obj_tuple[1] * 10**8 + obj_tuple[2] * 10**4 + obj_tuple[3]


def lex_t(t):
    return tuple(t)


REL = "runs/competitive/CS-20260911T071520-D2026/scouts"

# ---------- Q4-R22 ----------
d22 = os.path.join(SCOUTS, "Q4-R22", "run")
sol22 = os.path.join(d22, "solution_actions.json")
ev22 = run_eval("Q4", sol22, os.path.join(d22, "eval_q4.json"))
log22 = jload(os.path.join(d22, "r22_log.json"))
jdump(os.path.join(SCOUTS, "Q4-R22", "result.json"), {
    "question_id": "Q4", "idea_id": "Q4-R22",
    "status": "completed" if ev22["feasible"] else "failed",
    "feasible": ev22["feasible"],
    "objective": scalar(ev22["objective"]),
    "objective_tuple": ev22["objective"],
    "runtime_seconds": log22["wall_seconds_total"],
    "evaluator_invoked": True,
    "seed": "N/A (deterministic)",
    "solution_path": f"{REL}/Q4-R22/run/solution_actions.json",
    "failure_mode": None if ev22["feasible"] else "evaluator_infeasible",
})

# ---------- Q4-R41 ----------
d41 = os.path.join(SCOUTS, "Q4-R41", "run")
reps = []
for s in (11, 29, 47):
    rec_path = os.path.join(d41, f"sa_record_seed{s}.json")
    if not os.path.isfile(rec_path):
        reps.append({"seed": s, "missing": True})
        continue
    rec = jload(rec_path)
    solp = os.path.join(d41, f"solution_seed{s}.json")
    ev = run_eval("Q4", solp, os.path.join(d41, f"eval_seed{s}.json"))
    reps.append({"seed": s, "wall_seconds": rec["wall_seconds"], "moves": rec["moves_evaluated"],
                 "first_zero_violation_move": rec["first_zero_violation_move"],
                 "projection": rec.get("projection", {"applied": False}),
                 "feasible": ev["feasible"], "objective_tuple": ev["objective"],
                 "internal_recount_violations": rec["independent_recount_violations"],
                 "solution_path": f"{REL}/Q4-R41/run/solution_seed{s}.json"})
ok_reps = [r for r in reps if r.get("feasible")]
ok_reps.sort(key=lambda r: lex_t(r["objective_tuple"]))
med = ok_reps[len(ok_reps) // 2] if ok_reps else None
chosen = med
tuples = [r["objective_tuple"] for r in reps if r.get("feasible")]
spread = None
if tuples:
    ts = sorted(tuples, key=lex_t)
    spread = {"best": ts[0], "median": ts[len(ts) // 2], "worst": ts[-1]}
jdump(os.path.join(SCOUTS, "Q4-R41", "result.json"), {
    "question_id": "Q4", "idea_id": "Q4-R41",
    "status": "completed" if chosen else "failed",
    "feasible": bool(chosen),
    "objective": scalar(chosen["objective_tuple"]) if chosen else None,
    "objective_tuple": chosen["objective_tuple"] if chosen else None,
    "runtime_seconds": chosen["wall_seconds"] if chosen else max((r.get("wall_seconds") or 0) for r in reps),
    "evaluator_invoked": True,
    "seed": chosen["seed"] if chosen else "11,29,47 (all failed)",
    "solution_path": chosen["solution_path"] if chosen else None,
    "failure_mode": None if chosen else "no_replicate_reached_feasibility",
    "replicates": reps,
    "aggregation": "median over 3 replicates by lexicographic tuple (protocol TP-D2026-01)",
    "tuple_spread": spread,
})

# ---------- Q4-R11 ----------
d11 = os.path.join(SCOUTS, "Q4-R11", "run")
sol11 = os.path.join(d11, "solution_actions.json")
lay11 = jload(os.path.join(d11, "r11_layers.json")) if os.path.isfile(os.path.join(d11, "r11_layers.json")) else None
ev11 = None
if lay11 and os.path.isfile(sol11):
    ev11 = run_eval("Q4", sol11, os.path.join(d11, "eval_q4.json"))
dr = os.path.join(SCOUTS, "Q4-R11", "run_q2reduction")
layr = jload(os.path.join(dr, "r11_layers.json")) if os.path.isfile(os.path.join(dr, "r11_layers.json")) else None
evr_q2 = jload(os.path.join(dr, "eval_q2.json")) if os.path.isfile(os.path.join(dr, "eval_q2.json")) else None
evr_q4 = jload(os.path.join(dr, "eval_q4_on_q2sol.json")) if os.path.isfile(os.path.join(dr, "eval_q4_on_q2sol.json")) else None

inclusion = {
    "q2reduction_model": None if not layr else {
        "edges": layr["edges"], "vars": layr["vars"], "clauses": layr["clause_pairs"],
        "layers": layr["layers"]},
    "shared_solution_eval_Q2": None if not evr_q2 else {"feasible": evr_q2["feasible"], "tuple": evr_q2["objective"]},
    "shared_solution_eval_Q4": None if not evr_q4 else {"feasible": evr_q4["feasible"], "tuple": evr_q4["objective"]},
    "tuples_identical_on_shared_actions": (evr_q2 is not None and evr_q4 is not None
                                           and evr_q2["objective"] == evr_q4["objective"]
                                           and evr_q2["feasible"] == evr_q4["feasible"]),
    "q4_tuple_leq_q2_tuple": (ev11 is not None and evr_q2 is not None
                              and lex_t(ev11["objective"]) <= lex_t(evr_q2["objective"])),
    "q2sol_feasible_in_q4": (evr_q4 is not None and evr_q4["feasible"]),
}
if lay11:
    status = "completed" if (ev11 and ev11["feasible"]) else ("failed")
    jdump(os.path.join(SCOUTS, "Q4-R11", "result.json"), {
        "question_id": "Q4", "idea_id": "Q4-R11",
        "status": status,
        "feasible": bool(ev11 and ev11["feasible"]),
        "objective": scalar(ev11["objective"]) if ev11 else None,
        "objective_tuple": ev11["objective"] if ev11 else None,
        "runtime_seconds": lay11["wall_seconds_total"],
        "evaluator_invoked": True,
        "seed": f"CP-SAT random_seed={lay11['seed']}, workers={lay11['workers']} (deterministic)",
        "solution_path": f"{REL}/Q4-R11/run/solution_actions.json",
        "failure_mode": None if status == "completed" else "solver_no_solution",
        "layers": lay11["layers"],
        "inclusion_check_Q2_reduction": inclusion,
    })

jdump(os.path.join(SCOUTS, "Q4-R11", "run", "q2_inclusion_check.json"), inclusion)
print("finalize done:",
      "R22", ev22["objective"], "| R41", chosen["objective_tuple"] if chosen else None,
      "| R11", ev11["objective"] if ev11 else None)
