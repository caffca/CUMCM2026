# -*- coding: utf-8 -*-
"""bundle 视图：每问胜者路线的 feasible 结果摘要（字段全部来自权威结果件，经 result_writer 登记）。"""
import io, json, os, subprocess, sys

WRITER = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts\result_writer.py"
RUN = os.environ.get("DSH_RUN", "FULL-D2026-PROD-H")


def R(p):
    d = json.load(io.open(p, encoding="utf-8"))
    return d.get("result", d)


def emit(q, cid, extra):
    src = R(extra.pop("_src"))
    payload = {"question_id": q, "candidate_id": cid, "run_id": RUN, "feasible": True,
               "derived_from_authority": True, **extra,
               "note": "bundle 视图：字段镜像自本问权威结果件（无新增数值）"}
    if q == "Q2" or q == "Q4":
        payload["feasible"] = bool(src.get("residual_pairs_second_impl") == 0 and src.get("violations_second_impl", 0) == 0) if q == "Q4" \
            else bool(src.get("residual_pairs_second_impl") == 0)
    if q == "Q3":
        payload["feasible"] = bool(src.get("conflict_total_second_impl") == 0)
    tmp = f"runs/checks/bundle_view_{q}.src.json"
    json.dump(payload, io.open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    out = f"results/bundle_view_{q}.json"
    cmd = [sys.executable, WRITER, "--workspace", ".", "--payload", tmp, "--output", out,
           "--problem-id", q, "--role", "support", "--diagnostic",
           "--generator", "code/prod/make_bundle_views.py",
           "--input-file", "data/canonical_plans.csv"]
    if os.path.exists(out):
        cmd.append("--replace")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    print(q, "rc", r.returncode, (r.stdout or r.stderr)[-100:])
    return r.returncode == 0


ok = True
ok &= emit("Q1", "Q1-R21", {"_src": "results/Q1_detect.json",
                            "counts_edges": R("results/Q1_detect.json")["counts"]["edges"],
                            "edges_sha256": R("results/Q1_detect.json")["edges_sha256"]})
s2 = R("results/Q2_solution.json")
ok &= emit("Q2", "Q2-R51", {"_src": "results/Q2_solution.json", "objective_tuple": s2["objective_tuple"],
                            "objective_scalar": s2["objective_scalar"]})
s3 = R("results/Q3_solution.json")
ok &= emit("Q3", "Q3-R11", {"_src": "results/Q3_solution.json", "phi": s3["phi"], "ub_cp": s3.get("ub_cp"),
                             "gap_certified": s3.get("gap_certified")})
s4 = R("results/Q4_solution.json")
ok &= emit("Q4", "Q4-R11", {"_src": "results/Q4_solution.json", "objective_tuple": s4["objective_tuple"],
                             "objective_scalar": s4["objective_scalar"],
                             "revoke_gain_vs_q2": s4.get("revoke_gain_vs_q2")})
sys.exit(0 if ok else 1)
