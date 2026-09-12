# -*- coding: utf-8 -*-
"""rev8：IR compare_paths 点分路径化 + 纯数值化；变体镜像字段补齐；precheck 对齐 evaluator 语义。"""
import io, py_compile, json

# 1) vp_build IR pairs
p = "code/vp_build.py"
s = io.open(p, encoding="utf-8").read()
subs = [
 ('"compare_paths": ["/counts/edges", "/counts/AB", "/counts/AC", "/counts/BC", "/counts/BB", "/counts/CC", "/edges_sha256"]',
  '"compare_paths": ["counts.edges", "counts.AB", "counts.AC", "counts.BC", "counts.BB", "counts.CC"]'),
 ('"compare_paths": ["/objective_tuple", "/residual_pairs", "/revoked", "/adjusted"]',
  '"compare_paths": ["objective_scalar", "residual_pairs", "revoked", "adjusted"]'),
 ('"compare_paths": ["/phi", "/conflicts_vs_base", "/conflicts_internal", "/rows"]',
  '"compare_paths": ["phi", "conflicts_vs_base", "conflicts_internal", "rows"]'),
 ('"compare_paths": ["/objective_tuple", "/residual_pairs", "/violations"]',
  '"compare_paths": ["objective_scalar", "residual_pairs", "violations"]'),
 ('"plan_revision": 7', '"plan_revision": 8'),
]
n = 0
for a, b in subs:
    if a in s:
        s = s.replace(a, b); n += 1
    else:
        print("MISS vp:", a[:60])
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("vp IR patched:", n)

# 2) 变体镜像字段
p = "code/prod/check_q2.py"
s = io.open(p, encoding="utf-8").read()
a = '"objective_tuple": tuple_chk, "revoked": rev, "adjusted": adj, "residual_pairs": residual,'
if a in s and '"objective_scalar"' not in s:
    s = s.replace(a, a + ' "objective_scalar": scalar,')
    io.open(p, "w", encoding="utf-8").write(s)
    py_compile.compile(p, doraise=True)
    print("check_q2 +objective_scalar")
else:
    print("check_q2 skip/absent anchor", a in s)

p = "code/prod/q4v_check.py"
s = io.open(p, encoding="utf-8").read()
a = '"objective_tuple_second_impl": tup2, "objective_tuple": tup2,'
if a in s and '"objective_scalar"' not in s:
    s = s.replace(a, a + ' "objective_scalar": 10**12 * tup2[0] + 10**8 * tup2[1] + 10**4 * tup2[2] + tup2[3],')
    io.open(p, "w", encoding="utf-8").write(s)
    py_compile.compile(p, doraise=True)
    print("q4v_check +objective_scalar")
else:
    print("q4v_check skip", a in s)

p = "code/prod/q_synth.py"
s = io.open(p, encoding="utf-8").read()
a1 = '"revoke": main_["objective_tuple"][0],'
if a1 in s and '"revoked": main_' not in s:
    s = s.replace(a1, a1 + '\n                    "revoked": main_["objective_tuple"][0], "adjusted": main_["objective_tuple"][1],')
    io.open(p, "w", encoding="utf-8").write(s)
    py_compile.compile(p, doraise=True)
    print("q_synth Q2 +revoked/adjusted mirrors")
else:
    print("q_synth skip", a1 in s)
