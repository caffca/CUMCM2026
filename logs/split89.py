# -*- coding: utf-8 -*-
import io, py_compile
p = "code/prod/run_prod.py"
s = io.open(p, encoding="utf-8").read()
a = '    "8": [("Q4", 2), ("Q4", 3)],'
b = '    "8": [("Q4", 2)],\n    "9": [("Q4", 3)],'
assert a in s, "wave8 anchor"
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("wave split 8/9 done")
