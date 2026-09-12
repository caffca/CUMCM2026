# -*- coding: utf-8 -*-
import io, py_compile
p = "code/prod/run_prod.py"
s = io.open(p, encoding="utf-8").read()
a = """    waves = list(WAVES) if mode == "all" else [mode]
    for w in waves:"""
b = """    if mode == "aggregate":
        waves = []
    else:
        waves = list(WAVES) if mode == "all" else [mode]
    for w in waves:"""
assert a in s
s = s.replace(a, b)
a2 = """    if mode != "aggregate":
        print("waves done; run 'python code/prod/run_prod.py aggregate' after full completion", flush=True)
        sys.exit(0)
    # 聚合（仅在显式 aggregate 模式）"""
b2 = """    # 聚合（aggregate 模式或 all 完成后）"""
assert a2 in s
s = s.replace(a2, b2)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("run_prod aggregate fixed")
