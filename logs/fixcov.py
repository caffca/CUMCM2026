# -*- coding: utf-8 -*-
import io, py_compile
p = "code/prod/write_results.py"
s = io.open(p, encoding="utf-8").read()
a = """    plan = json.load(open(agg["plan_file"], encoding="utf-8"))
    cov_contract = plan.get("coverage_contract") or {}"""
b = """    plan = json.load(open(agg["plan_file"], encoding="utf-8"))
    cov_contract = plan.get("coverage_policy") or plan.get("coverage_contract") or {}"""
assert a in s
s = s.replace(a, b)
a2 = """    observed = {"cases_complete": [t["coverage_case_id"] for t in agg.get("tasks", []) if t.get("status") == "complete"],
                "total_cases": len(agg.get("tasks", [])), "run_id": a.run_id}"""
b2 = """    observed = {"cases_complete": [t["coverage_case_id"] for t in agg.get("tasks", [])
                                    if t.get("complete") or t.get("state") == "complete"],
                "total_cases": len(agg.get("tasks", [])), "run_id": a.run_id}"""
assert a2 in s
s = s.replace(a2, b2)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("coverage contract/id/cases fixed")
