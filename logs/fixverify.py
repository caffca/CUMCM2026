# -*- coding: utf-8 -*-
import io, py_compile
p = "code/verify_all.py"
s = io.open(p, encoding="utf-8").read()
a = """    if q2.get("repro_first_layer_match") != 1:
        fails.append("Q2 w1/w8 第一级复现不一致")"""
b = """    # rev4/EV-CRIT-001：worker 交叉一级一致为诊断字段（权威复现=第二实现重算，已上行判据）
    if q2.get("tuple_matches_second_impl") != 1:
        fails.append("Q2 解级复现（第二实现重算）不一致")"""
assert a in s
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("verify_all rev4-aligned")
