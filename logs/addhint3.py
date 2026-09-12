# -*- coding: utf-8 -*-
import io, py_compile

p = "code/fms_build.py"
s = io.open(p, encoding="utf-8").read()
a = '''        "cases": [{"variant": "cpsat_lex", "workers": 4, "stage_budget": _SB},
                   {"variant": "cpsat_lex", "workers": 1, "stage_budget": _SB},'''
b = '''        "cases": [{"variant": "cpsat_lex", "workers": 4, "stage_budget": _SB,
                    "hint": "runs/competitive/CS-20260911T071520-D2026/scouts/Q2-R51/solution_actions.json"},
                   {"variant": "cpsat_lex", "workers": 1, "stage_budget": _SB,
                    "hint": "runs/competitive/CS-20260911T071520-D2026/scouts/Q2-R51/solution_actions.json"},'''
assert a in s
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)

p2 = "code/prod/run_prod.py"
s2 = io.open(p2, encoding="utf-8").read()
s2 = s2.replace('RUN = os.environ.get("DSH_RUN", "FULL-D2026-PROD-B")', 'RUN = os.environ.get("DSH_RUN", "FULL-D2026-PROD-C")')
io.open(p2, "w", encoding="utf-8").write(s2)
py_compile.compile(p2, doraise=True)
print("hint cases + run-C wired")
