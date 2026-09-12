# -*- coding: utf-8 -*-
"""Q2 hint 支持（锚定实际文件结构）。"""
import io, py_compile

p = "code/prod/q2v_cpsat.py"
s = io.open(p, encoding="utf-8").read()

a = """    plans = load_plans_local()
    ids, opts, masks, edges = build(plans)
    idx = {pid: i for i, pid in enumerate(ids)}
"""
assert a in s
hint_code = """
    hint_acts, hint_src = {}, None
    if param.get("hint"):
        import os as _os, json as _json
        hint_src = str(param["hint"])
        hp = hint_src
        if not _os.path.exists(hp):
            from cli import resolve_base as _rb
            hp, _ = _rb(hp, a.run_id, want_variant="cpsat_lex", want_workers="main", qprefix="q2")
        hs = _json.load(open(hp, encoding="utf-8"))
        hs = hs.get("result", hs)
        hint_acts = hs.get("actions") or {}
"""
s = s.replace(a, a + hint_code, 1)

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

d = '    res = {"question_id": "Q2", "variant": "cpsat_lex", "workers": workers,'
assert d in s
s = s.replace(d, d + '\n           "hint_source": hint_src, "hint_role": "search_hint_only_all_figures_recomputed",', 1)

io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("q2v hint OK")
