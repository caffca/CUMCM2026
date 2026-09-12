# -*- coding: utf-8 -*-
import io, py_compile
p = "logs/wp_build_req.py"
s = io.open(p, encoding="utf-8").read()
a = '''WIN = {"Q1": ("Q1-R21", "results/Q1_detect.json", f"runs/fresh/{RUN}/tasks/Q1-Q1-R21-main-N-A-p0/attempts/001/execution_metrics.json"),
       "Q2": ("Q2-R51", "results/Q2_solution.json", f"runs/fresh/{RUN}/tasks/Q2-Q2-R51-main-N-A-p0/attempts/001/execution_metrics.json"),
       "Q3": ("Q3-R11", "results/Q3_solution.json", f"runs/fresh/{RUN}/tasks/Q3-Q3-R11-main-N-A-p1/attempts/001/execution_metrics.json"),
       "Q4": ("Q4-R11", "results/Q4_solution.json", f"runs/fresh/{RUN}/tasks/Q4-Q4-R11-main-N-A-p0/attempts/001/execution_metrics.json")}'''
b = '''WIN = {"Q1": ("Q1-R21", "results/bundle_view_Q1.json", f"runs/fresh/{RUN}/tasks/Q1-Q1-R21-main-N-A-p0/attempts/001/execution_metrics.json"),
       "Q2": ("Q2-R51", "results/bundle_view_Q2.json", f"runs/fresh/{RUN}/tasks/Q2-Q2-R51-main-N-A-p0/attempts/001/execution_metrics.json"),
       "Q3": ("Q3-R11", "results/bundle_view_Q3.json", f"runs/fresh/{RUN}/tasks/Q3-Q3-R11-main-N-A-p1/attempts/001/execution_metrics.json"),
       "Q4": ("Q4-R11", "results/bundle_view_Q4.json", f"runs/fresh/{RUN}/tasks/Q4-Q4-R11-main-N-A-p0/attempts/001/execution_metrics.json")}'''
assert a in s
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("result_ref -> bundle views")
