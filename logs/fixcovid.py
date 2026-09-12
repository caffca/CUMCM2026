# -*- coding: utf-8 -*-
import io, py_compile
p = "code/prod/write_results.py"
s = io.open(p, encoding="utf-8").read()
old = 'cov_contract.get("coverage_plan_id")'
new = '(cov_contract.get("coverage_plan_id") or plan.get("coverage_plan_id"))'
n = s.count(old)
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("cov id fallback patched:", n)
