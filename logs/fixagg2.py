# -*- coding: utf-8 -*-
import io, py_compile
p = "code/prod/run_prod.py"
s = io.open(p, encoding="utf-8").read()
a = """    r = subprocess.run([sys.executable, SR, "--workspace", ".", "--run-id", RUN,
                        "--plan", f"runs/fresh/{RUN}/SHARD_PLAN.json", "--aggregate-only"],
                       capture_output=True, text=True, encoding="utf-8", env=env)"""
b = """    r = subprocess.run([sys.executable, SR, "--workspace", ".", "--production", "--run-id", RUN,
                        "--budget-class", "full", "--aggregate-only"],
                       capture_output=True, text=True, encoding="utf-8", env=env)"""
assert a in s, "aggregate anchor"
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("aggregate args fixed")
