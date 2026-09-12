# -*- coding: utf-8 -*-
"""生产波次驱动器 v2：长任务独占/成对波（每波独立进程 → deadline 1800 重置）。
用法：python code/prod/run_prod.py <wave_id|all|plan>  wave_id ∈ 1..8"""
import json, os, subprocess, sys

SR = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts\sharded_run.py"
RUN = os.environ.get("DSH_RUN", "FULL-D2026-PROD-H")
PLAN = "reports/execution/SHARD_PLAN.json"

WAVES = {
    "1": [("Q2", 0), ("Q1", 0)],
    "2": [("Q2", 1), ("Q2", 2)],
    "3": [("Q2", 3), ("Q2", 4), ("Q2", 5)],
    "4": [("Q2", 6), ("Q3", 0)],
    "5": [("Q3", 1), ("Q3", 2), ("Q3", 3)],
    "6": [("Q3", 4), ("Q3", 5), ("Q3", 6)],
    "7": [("Q4", 0), ("Q4", 1)],
    "8": [("Q4", 2)],
    "9": [("Q4", 3)],
}


def tasks_for(q, idx):
    plan = json.load(open(PLAN, encoding="utf-8"))
    return [t["task_id"] for t in plan["tasks"] if t["question_id"] == q and t["task_id"].endswith(f"-p{idx}")]


def launch(tasklist):
    cmd = [sys.executable, SR, "--workspace", ".", "--production", "--run-id", RUN,
           "--budget-class", "full", "--resume"]
    for t in tasklist:
        cmd += ["--task", t]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(cmd, env=env).returncode


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "plan"
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    if mode == "plan":
        r = subprocess.run([sys.executable, SR, "--workspace", ".", "--production", "--run-id", RUN,
                            "--budget-class", "full", "--check"], capture_output=True, text=True,
                           encoding="utf-8", env=env)
        print(r.stdout[-1500:], r.stderr[-800:])
        sys.exit(r.returncode)
    if mode == "aggregate":
        waves = []
    else:
        waves = list(WAVES) if mode == "all" else [mode]
    for w in waves:
        tl = []
        for q, i in WAVES[w]:
            t = tasks_for(q, i)
            assert len(t) == 1, (q, i, t)
            tl += t
        print(f"=== WAVE {w}: {tl}", flush=True)
        rc = launch(tl)
        import time as _t
        _t.sleep(2)
        st = open(os.path.join("runs", "fresh", RUN, "RUN_STATE.md"), encoding="utf-8").read()
        print(f"=== WAVE {w} launch_rc={rc}", flush=True)
        for t in tl:
            ln = next((l for l in st.splitlines() if l.startswith('| ' + t + ' ')), '')
            if "complete" not in ln:
                print("WAVE-INCOMPLETE", t, ln[:100], flush=True)
                sys.exit(3)
    # 聚合（aggregate 模式或 all 完成后）
    r = subprocess.run([sys.executable, SR, "--workspace", ".", "--production", "--run-id", RUN,
                        "--budget-class", "full", "--aggregate-only"],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    print(r.stdout[-800:], r.stderr[-500:])
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
