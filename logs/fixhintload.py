# -*- coding: utf-8 -*-
import io, py_compile
p = "code/prod/q2v_cpsat.py"
s = io.open(p, encoding="utf-8").read()
a = '''        hs = _json.load(open(hp, encoding="utf-8"))
        hs = hs.get("result", hs)
        hint_acts = hs.get("actions") or {}'''
b = '''        hs = _json.load(open(hp, encoding="utf-8"))
        hs = hs.get("result", hs)
        ha = hs.get("actions")
        if not isinstance(ha, dict):
            ha = {k: v for k, v in hs.items() if isinstance(v, dict) and (set(v) <= {"revoke", "df", "dt", "dg"})}
        hint_acts = ha or {}'''
assert a in s, "hint loader anchor"
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("hint loader accepts raw actions map")
