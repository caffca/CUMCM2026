# -*- coding: utf-8 -*-
"""Q3 生产调度器：按 parameter.variant 子进程分发（进程级独立）。"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = {"enum": "q3v_enum.py", "cpsat_a": "q3v_cpsat.py", "cpsat_b": "q3v_cpsat.py",
       "lp_hiGHS": "q3v_cpsat.py", "bound_elementary": "q3v_bound.py", "check": "q3v_check.py",
       "synth": "q_synth.py"}


def main():
    a, param = std_args("q3 dispatcher")
    v = str(param.get("variant", "enum"))
    cmd = [sys.executable, os.path.join(HERE, MAP[v]), "--run-id", a.run_id, "--stage", a.stage,
           "--seed", str(a.seed), "--scenario", a.scenario, "--parameter", a.parameter,
           "--output-dir", a.output_dir, "--budget-class", a.budget_class]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.stderr.write((r.stdout or "") + "\n" + (r.stderr or "") + "\n")
        raise SystemExit(r.returncode)


if __name__ == "__main__":
    main()
