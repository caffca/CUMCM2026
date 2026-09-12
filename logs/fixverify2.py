# -*- coding: utf-8 -*-
import io, py_compile
p = "code/verify_all.py"
s = io.open(p, encoding="utf-8").read()
a = """    if q4.get("planted_q2_feasible") != 1:"""
b = """    if q4.get("tuple_matches_second_impl") != 1:
        fails.append("Q4 解级复现（第二实现重算）不一致")
    if q4.get("planted_q2_feasible") != 1:"""
assert a in s
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("Q4 tuple assert added")
