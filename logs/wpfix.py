# -*- coding: utf-8 -*-
import io, py_compile

p = "logs/wp_build_req.py"
s = io.open(p, encoding="utf-8").read()
a = '"constraint_id": "CC-Q2Q4-ANCHOR", "question_ids": ["Q2", "Q4"]'
b = '"constraint_id": "CC-Q2Q4-ANCHOR", "question_ids": ["Q4", "Q2"]'
assert a in s
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("cqids reordered")

p = "code/prod/make_degeneracy_triangle.py"
s = io.open(p, encoding="utf-8").read()
a = '"artifact": "degeneracy_triangle", "diagnostic": True,'
assert a in s and '"question_ids": ["Q2", "Q3", "Q4"]' not in s
s = s.replace(a, a + '\n        "question_ids": ["Q2", "Q3", "Q4"],')
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("triangle += question_ids")
