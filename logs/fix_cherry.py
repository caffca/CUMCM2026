# -*- coding: utf-8 -*-
"""反 cherry-pick 修补：权威主解=确定性 workers=1（缺失回退 w4），w4 仅第一级印证复现。"""
import io

# 1) cli.resolve_base: "main" mode
p = 'code/prod/cli.py'
s = io.open(p, encoding='utf-8').read()
a = """        if not cands:
            raise SystemExit(f"resolve_base: no {qprefix} {want_variant} payload under {root}")
        cands.sort()
        return cands[0][1], "shard:" + cands[0][1]"""
b = """        if want_workers == "main":
            w1 = [c for c in cands if c[1].split("p0") or (c[2].get("workers") == 1)]
            w1 = [c for c in cands if c[2].get("workers") == 1]
            pool = w1 or [c for c in cands if c[2].get("workers") == 4] or cands
            pickd = sorted(pool, key=lambda t: t[0])
            return pickd[0][1], "shard:" + pickd[0][1]
        if not cands:
            raise SystemExit(f"resolve_base: no {qprefix} {want_variant} payload under {root}")
        cands.sort()
        return cands[0][1], "shard:" + cands[0][1]"""
assert a in s
s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8').write(s)
print('cli patched')

# 2) q_synth: w1 优先权威
p = 'code/prod/q_synth.py'
s = io.open(p, encoding='utf-8').read()
a = """    def best_main(variant):
        c = [d for d in docs if d.get("variant") == variant and d.get("objective_tuple")]
        if not c:
            return None
        c.sort(key=lambda d: (tuple(d["objective_tuple"]), 0 if d.get("workers") == 1 else 1))
        return c[0]"""
b = """    def best_main(variant):
        \"\"\"权威主解=确定性 workers=1（若存在）；否则 workers=4。绝不在 w1/w4 间按目标值挑优（anti cherry-pick）。
        两跑的更优元组仅作为 best_tuple_seen_across_runs 诊断记录。\"\"\"
        c = [d for d in docs if d.get("variant") == variant and d.get("objective_tuple")]
        if not c:
            return None
        w1 = [d for d in c if d.get("workers") == 1]
        w4 = [d for d in c if d.get("workers") == 4]
        return (w1 or w4 or c)[0]"""
assert a in s
s = s.replace(a, b)
a2 = '''                    "repro_first_layer_match": 1 if (w1 and w4 and w1["objective_tuple"][0] == w4["objective_tuple"][0]) else 0,
                    "repro_w1_eq_w8": 1 if (w1 and w4 and w1["objective_tuple"] == w4["objective_tuple"]) else 0,
                    "best_is_w1": 1 if main_ is w1 else 0,
                    "w1_tuple": (w1 or {}).get("objective_tuple"),
                    "w4_tuple": (w4 or {}).get("objective_tuple"),
                    "run_id_ref": a.run_id})'''
b2 = '''                    "repro_first_layer_match": 1 if (w1 and w4 and w1["objective_tuple"][0] == w4["objective_tuple"][0]) else 0,
                    "repro_w1_eq_w8": 1 if (w1 and w4 and w1["objective_tuple"] == w4["objective_tuple"]) else 0,
                    "best_is_w1": 1 if main_ is w1 else 0,
                    "best_tuple_seen_across_runs": (min([d["objective_tuple"] for d in docs if d.get("variant") == "cpsat_lex" and d.get("objective_tuple")]) if any(d.get("variant") == "cpsat_lex" and d.get("objective_tuple") for d in docs) else None),
                    "w1_tuple": (w1 or {}).get("objective_tuple"),
                    "w4_tuple": (w4 or {}).get("objective_tuple"),
                    "run_id_ref": a.run_id})'''
assert a2 in s
s = s.replace(a2, b2)
a3 = '''        q2m = sorted([d for d in q2m if d.get("variant") == "cpsat_lex" and d.get("objective_tuple")],
                     key=lambda d: (tuple(d["objective_tuple"]), 0 if d.get("workers") == 1 else 1))[0]'''
b3 = '''        _c = [d for d in q2m if d.get("variant") == "cpsat_lex" and d.get("objective_tuple")]
        q2m = ([d for d in _c if d.get("workers") == 1] or [d for d in _c if d.get("workers") == 4] or _c)[0]'''
assert a3 in s
s = s.replace(a3, b3)
a4 = '''        q2m = sorted([d for d in q2docs if d.get("variant") == "cpsat_lex" and d.get("objective_tuple")],
                     key=lambda d: (tuple(d["objective_tuple"]), 0 if d.get("workers") == 1 else 1))[0]'''
b4 = '''        _c = [d for d in q2docs if d.get("variant") == "cpsat_lex" and d.get("objective_tuple")]
        q2m = ([d for d in _c if d.get("workers") == 1] or [d for d in _c if d.get("workers") == 4] or _c)[0]'''
assert a4 in s
s = s.replace(a4, b4)
a5 = '''                    "repro_first_layer_match": 1 if (w1 and w4 and w1["objective_tuple"][0] == w4["objective_tuple"][0]) else 0,
                    "repro_w1_eq_w8": 1 if (w1 and w4 and w1["objective_tuple"] == w4["objective_tuple"]) else 0,
                    "best_is_w1": 1 if main_ is w1 else 0,
                    "w1_tuple": (w1 or {}).get("objective_tuple"), "w4_tuple": (w4 or {}).get("objective_tuple"),'''
b5 = '''                    "repro_first_layer_match": 1 if (w1 and w4 and w1["objective_tuple"][0] == w4["objective_tuple"][0]) else 0,
                    "repro_w1_eq_w8": 1 if (w1 and w4 and w1["objective_tuple"] == w4["objective_tuple"]) else 0,
                    "best_is_w1": 1 if main_ is w1 else 0,
                    "best_tuple_seen_across_runs": min([d["objective_tuple"] for d in docs if d.get("variant") == "cpsat_lex" and d.get("objective_tuple")]) if any(d.get("variant") == "cpsat_lex" and d.get("objective_tuple") for d in docs) else None,
                    "w1_tuple": (w1 or {}).get("objective_tuple"), "w4_tuple": (w4 or {}).get("objective_tuple"),'''
assert a5 in s
s = s.replace(a5, b5)
io.open(p, 'w', encoding='utf-8').write(s)
print('q_synth patched')

# 3) check 脚本同步 "main" 解析
for f, old, new in [
    ('check_q2.py', 'want_variant="cpsat_lex", want_workers=None', 'want_variant="cpsat_lex", want_workers="main"'),
    ('q4v_check.py', 'want_variant="cpsat_lex", want_workers=None, qprefix="q4"', 'want_variant="cpsat_lex", want_workers="main", qprefix="q4"'),
    ('q3v_check.py', 'want_variant="cpsat_a", want_workers=None, qprefix="q3"', 'want_variant="cpsat_a", want_workers=None, qprefix="q3"'),
    ('q3v_enum.py', 'want_variant="cpsat_lex", want_workers=None, qprefix="q2"', 'want_variant="cpsat_lex", want_workers="main", qprefix="q2"'),
    ('q3v_bound.py', 'want_variant="cpsat_lex", want_workers=None', 'want_variant="cpsat_lex", want_workers="main"'),
    ('q4v_cpsat.py', 'want_workers=None, qprefix="q2"', 'want_workers="main", qprefix="q2"'),
]:
    p = 'code/prod/' + f
    s = io.open(p, encoding='utf-8').read()
    assert old in s, (f, old)
    s = s.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('ok', f)
print('ALL ANTI-CHERRY-PICK PATCHES APPLIED')
