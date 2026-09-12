# -*- coding: utf-8 -*-
import io, py_compile
p = "logs/wp_build_req.py"
s = io.open(p, encoding="utf-8").read()
a = """    "remaining_budget": {
        "source_ref": ref(AGG), "derivation": "deadline_minus_elapsed_seconds",
        "value_path": "execution_policy.deadline_seconds",
        "used_value_path": "aggregation.total_elapsed_seconds", "unit": "hours",
    },"""
b = """    "remaining_budget": {
        "source_ref": ref("results/compute_budget.json"),
        "value_path": "remaining_budget_hours", "unit": "hours",
    },"""
assert a in s
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("budget source switched")
