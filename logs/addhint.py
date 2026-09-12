# -*- coding: utf-8 -*-
"""Q2 变体加入 hint 支持（侦察 incumbent 仅作搜索提示——所有权威数字由生产链路重算复核）。"""
import io

p = "code/prod/q2v_cpsat.py"
s = io.open(p, encoding="utf-8").read()

a = """    plans = load_plans_local()
    ids = sorted(plans)"""
if a not in s:
    a = """    plans = load_plans_local()
    idx = {p["id"]: i for i, p in enumerate(plans)}"""
assert a in s, "anchor not found"

hint_code = '''    hint_acts = {}
    if param.get("hint"):
        import os as _os, json as _json
        from cli import resolve_base as _rb
        hp = param["hint"]
        if not _os.path.exists(hp):
            hp2, _ = _rb(hp, a.run_id, want_variant="cpsat_lex", want_workers="main", qprefix="q2")
            hp = hp2
        hs = _json.load(open(hp, encoding="utf-8"))
        hs = hs.get("result", hs)
        hint_acts = hs.get("actions") or {}
        hint_src = param["hint"]
    else:
        hint_src = None
'''
# 插入位置：plans 载入之后
s = s.replace(a, a + "\n" + hint_code, 1)

# make_model 内加 AddHint（在 exactly-one 后、返回前）
b = """        if extra_rev_cap is not None:
            m.Add(R <= extra_rev_cap)
        return m, X, (R, A, PL, MG)"""
assert b in s
c = """        if extra_rev_cap is not None:
            m.Add(R <= extra_rev_cap)
        if hint_acts:
            for pid, o in hint_acts.items():
                if pid not in X:
                    continue
                key = ("rv", 0) if o.get("revoke") else next(((k, int(v)) for k, v in o.items()), ("id", 0))
                if key in opts[pid]:
                    m.AddHint(X[pid][opts[pid].index(key)], 1)
        return m, X, (R, A, PL, MG)"""
s = s.replace(b, c, 1)

# 记录 hint 出处到 payload
d = """    res = {"question_id": "Q2", "variant": "cpsat_lex", "workers": workers,"""
assert d in s
s = s.replace(d, """    res = {"question_id": "Q2", "variant": "cpsat_lex", "workers": workers,
           "hint_source": hint_src, "hint_role": "search_hint_only_all_figures_recomputed",""")
io.open(p, "w", encoding="utf-8").write(s)
import py_compile
py_compile.compile(p, doraise=True)
print("q2v hint support OK")
