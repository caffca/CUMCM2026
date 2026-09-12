# -*- coding: utf-8 -*-
import io, py_compile
p = "code/prod/pipeline_tail.py"
s = io.open(p, encoding="utf-8").read()
a = '    ("verify", [sys.executable, "code/verify_all.py"]),'
b = ('    ("sensitivity", [sys.executable, "code/prod/make_q3_sensitivity.py"]),\n'
     '    ("verify", [sys.executable, "code/verify_all.py"]),')
if "make_q3_sensitivity" not in s:
    assert a in s
    s = s.replace(a, b, 1)
    io.open(p, "w", encoding="utf-8").write(s)
    py_compile.compile(p, doraise=True)
    print("tail += sensitivity")
else:
    print("already")
