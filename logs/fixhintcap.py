# -*- coding: utf-8 -*-
"""cap 探针与 hint 冲突修复（q2v/q4v）：cap_R < hint 撤销数 或 leq 锚冲突时，该探针不注入 hint。"""
import io, py_compile

for p, capvar in [("code/prod/q2v_cpsat.py", "extra_rev_cap"), ("code/prod/q4v_cpsat.py", "cap_R")]:
    s = io.open(p, encoding="utf-8").read()
    if "q2v" in p:
        a = """        if hint_acts:
            for pid, o in hint_acts.items():
                if pid not in X:
                    continue"""
        b = """        _hr = sum(1 for o in hint_acts.values() if o.get("revoke"))
        if hint_acts and (extra_rev_cap is None or extra_rev_cap >= _hr):
            for pid, o in hint_acts.items():
                if pid not in X:
                    continue"""
    else:
        a = """        if hint:
            for pid, kv in hint.items():
                key = tuple(kv)
                if key in opts[pid]:
                    m.AddHint(X[pid][opts[pid].index(key)], 1)"""
        b = """        _hr = sum(1 for o in hint.values() if "revoke" in (o if isinstance(o, dict) else {}))
        _capv = cap_R
        _anch = leq_tuple
        if hint and (_capv is None or _capv >= _hr) and (not _anch or _anch[0] >= _hr):
            for pid, kv in hint.items():
                key = tuple(kv)
                if key in opts[pid]:
                    m.AddHint(X[pid][opts[pid].index(key)], 1)"""
    if a not in s:
        print("MISS", p, "-> inspect")
        for ln in s.splitlines():
            if "hint" in ln or "AddHint" in ln:
                print("   ", ln.strip()[:110])
        continue
    s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8").write(s)
    py_compile.compile(p, doraise=True)
    print("fixed", p)
