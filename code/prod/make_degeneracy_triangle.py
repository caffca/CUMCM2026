# -*- coding: utf-8 -*-
"""退化三角执行闭合件：设计三端点（解析认证）+ run-H 真实 aggregate 绑定，经 writer 登记为诊断件。"""
import hashlib, io, json, os, subprocess, sys

WRITER = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts\result_writer.py"
RUN = os.environ.get("DSH_RUN", "FULL-D2026-PROD-H")
AGG = f"runs/fresh/{RUN}/SHARD_AGGREGATE.json"


def R(p):
    d = json.load(io.open(p, encoding="utf-8"))
    return d.get("result", d)


def main():
    deg = json.load(io.open("reports/methodology/optimization_degeneracy.json", encoding="utf-8"))
    q2, q3, q4 = R("results/Q2_solution.json"), R("results/Q3_solution.json"), R("results/Q4_solution.json")
    fulls = {"Q2": q2["objective_tuple"][0], "Q3": q3["phi"], "Q4": q4["objective_tuple"][0]}
    probs = []
    for p in deg.get("problems", []):
        p = dict(p)
        if p.get("id") in fulls:
            p["full"] = fulls[p["id"]]
            p["full_note"] += f"；run-{RUN[-1]} 实际认证值={fulls[p['id']]}"
            if p.get("constraint_only"):
                p["constraint_dominance_ratio"] = round((p["constraint_only"] - p["full"]) / p["constraint_only"], 4)
        probs.append(p)
    agg_bytes = open(AGG, "rb").read()
    payload = {
        "artifact": "degeneracy_triangle", "diagnostic": True,
        "question_ids": ["Q2", "Q3", "Q4"],
        "design": deg.get("design"),
        "problems": probs,
        "execution_evidence": {
            "run_id": RUN, "budget_class": "full", "complete": True, "authoritative": True,
            "aggregate_file": AGG.replace("\\", "/"),
            "aggregate_sha256": hashlib.sha256(agg_bytes).hexdigest(),
            "note": ("三端点解析/认证值绑定当前权威 run 聚合：full 角取自 run 认证解（Q2/Q4 第一级、Q3 Φ），"
                     "objective_only/constraint_only 为冻结输入的解析端点（0 与全撤销/全不可加），可独立复算。"),
        },
    }
    tmp = "runs/checks/degeneracy_triangle.src.json"
    json.dump(payload, io.open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    cmd = [sys.executable, WRITER, "--workspace", ".", "--payload", tmp,
           "--output", "results/degeneracy_triangle.json", "--problem-id", "Q2",
           "--problem-id", "Q3", "--problem-id", "Q4", "--role", "support", "--diagnostic",
           "--generator", "code/prod/make_degeneracy_triangle.py",
           "--input-file", "data/canonical_plans.csv"]
    if os.path.exists("results/degeneracy_triangle.json"):
        cmd.append("--replace")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    print("writer rc", r.returncode, (r.stdout or r.stderr)[-160:])
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
