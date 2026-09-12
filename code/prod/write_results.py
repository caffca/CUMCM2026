# -*- coding: utf-8 -*-
"""权威结果批量写入：production run 完成后，把各 task payload 经 result_writer
登记为 results/*.json（authority + diagnostic），并生成 COVERAGE_PLAN/OBSERVED。
用法：python code/prod/write_results.py --run-id <RUN>"""
import argparse, glob, json, os, subprocess, sys

WRITER = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts\result_writer.py"

# task 变体 → (结果文件, role, problem_id, kind)
PLAN = {
    "Q1": [("synth", None), ("full_triple", "results/Q1_detect.json", "paper_authority", "Q1")],
    "Q2": [("cpsat_lex", None)],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--only", default=None, help="逗号分隔 question id 子集")
    a = ap.parse_args()
    run_root = os.path.join("runs", "fresh", a.run_id)
    agg_path = os.path.join(run_root, "SHARD_AGGREGATE.json").replace("\\", "/")
    agg = json.load(open(agg_path, encoding="utf-8"))
    assert agg.get("budget_class") == "full" and agg.get("authoritative") is True, "aggregate 非 full/authoritative"
    tasks = {t["task_id"]: t for t in agg.get("tasks", [])}
    # 每个 task 的 payload 路径与 variant/workers 索引
    by_var = {}
    for tid, t in tasks.items():
        ad = sorted(glob.glob(os.path.join(run_root, "tasks", tid, "attempts", "*")))
        if not ad:
            continue
        d = ad[-1]
        pp = os.path.join(d, "payload.json")
        em = os.path.join(d, "execution_metrics.json")
        if not os.path.isfile(pp):
            continue
        pv = json.load(open(pp, encoding="utf-8"))
        by_var.setdefault(t.get("question_id"), []).append(
            {"task_id": tid, "payload": pp.replace("\\", "/"), "metrics": em, "var": pv.get("variant"),
             "workers": pv.get("workers"), "assembled": bool(pv.get("assembled")), "task": t})
    # coverage 工件
    plan = json.load(open(agg["plan_file"], encoding="utf-8"))
    cov_contract = plan.get("coverage_policy") or plan.get("coverage_contract") or {}
    cov_path = os.path.join(run_root, "COVERAGE_PLAN.json")
    json.dump(cov_contract, open(cov_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    observed = {"cases_complete": [t["coverage_case_id"] for t in agg.get("tasks", [])
                                    if t.get("complete") or t.get("state") == "complete"],
                "total_cases": len(agg.get("tasks", [])), "run_id": a.run_id}
    obs_path = os.path.join(run_root, "COVERAGE_OBSERVED.json")
    json.dump(observed, open(obs_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    TARGETS = [
        # question, variant, workers, result_file, role, authority, generator
        ("Q1", "full_triple", None, "results/Q1_detect.json", "paper_authority", True, "code/prod/q1_solve.py"),
        ("Q2", "cpsat_lex", 4, "results/Q2_main_w4.json", "model_output", False, "code/prod/q2v_cpsat.py"),
        ("Q2", "check", None, "results/Q2_check.json", "model_output", False, "code/prod/check_q2.py"),
        ("Q2", "synth", None, "results/Q2_solution.json", "paper_authority", True, "code/prod/q2_solve.py"),
        ("Q3", "bound_elementary", None, "results/Q3_bound.json", "paper_authority", True, "code/prod/q3_solve.py"),
        ("Q3", "check", None, "results/Q3_check.json", "model_output", False, "code/prod/q3v_check.py"),
        ("Q3", "synth", None, "results/Q3_solution.json", "paper_authority", True, "code/prod/q3_solve.py"),
        ("Q4", "check", None, "results/Q4_check.json", "model_output", False, "code/prod/q4v_check.py"),
        ("Q4", "synth", None, "results/Q4_solution.json", "paper_authority", True, "code/prod/q4_solve.py"),
    ]
    only = set((a.only or "").split(",")) if a.only else None
    os.makedirs("results", exist_ok=True)
    for q, var, workers, out, role, authority, gen in TARGETS:
        if only and q not in only:
            continue
        rec = None
        for c in by_var.get(q, []):
            v_ok = (c["var"] == var and not c.get("assembled")) or (var == "synth" and c.get("assembled"))
            if v_ok and (workers is None or c["workers"] == workers):
                rec = c
        if rec is None:
            print("SKIP (no payload)", q, var, workers)
            continue
        m = json.load(open(rec["metrics"], encoding="utf-8"))
        ex = {"function_evaluations": int(m.get("evaluator_calls") or 1),
              "elapsed_seconds": float(m.get("elapsed_seconds") or 0),
              "stopping_reason": str(m.get("stopping_reason") or "completed"),
              "seeds": [], "scenario": "main"}
        exj = os.path.join(os.path.dirname(rec["payload"]), "_execution_for_writer.json")
        json.dump(ex, open(exj, "w", encoding="utf-8"), ensure_ascii=False)
        inputs = [b["path"] for b in rec["task"].get("input_bindings", [])]
        cmd = [sys.executable, WRITER, "--workspace", ".",
               "--payload", rec["payload"], "--source-payload", rec["payload"],
               "--output", out, "--problem-id", q, "--role", role,
               "--generator", gen]
        if authority:
            cmd += ["--execution-json", exj, "--aggregate", agg_path,
                    "--coverage-plan", cov_path.replace("\\", "/"),
                    "--coverage-id", str((cov_contract.get("coverage_plan_id") or plan.get("coverage_plan_id"))),
                    "--observed-coverage-json", obs_path.replace("\\", "/")]
        for i in inputs:
            cmd += ["--input-file", i.replace("\\", "/")]
        if not authority:
            cmd.append("--diagnostic")
        if os.path.exists(out):
            cmd.append("--replace")
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        ok = r.returncode == 0
        print(("OK  " if ok else "FAIL") + f" {out} <- {rec['task_id']}")
        if not ok:
            print((r.stdout or "")[-900:], (r.stderr or "")[-900:])


if __name__ == "__main__":
    main()
