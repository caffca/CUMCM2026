# -*- coding: utf-8 -*-
import io, re, py_compile
p = "code/prod/write_results.py"
s = io.open(p, encoding="utf-8").read()
s2 = re.sub(r'\n\s*"--coverage-json", json\.dumps\(\{"coverage_id":.*?"status": "complete"\}\),', "", s, flags=re.S)
assert s2 != s, "pattern not found"
io.open(p, "w", encoding="utf-8").write(s2)
py_compile.compile(p, doraise=True)
print("coverage-json flag removed")
