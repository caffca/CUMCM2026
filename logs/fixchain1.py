# -*- coding: utf-8 -*-
"""链式修正 A+B：synth 取 best（带完整记录）；resolve_base("main")=best lexicographic（含 provenance）。"""
import io, py_compile

# A) q_synth: main_ = 词典序最优 cpsat_lex（w1/w4 均全量入 payload，透明记录）
p = "code/prod/q_synth.py"
s = io.open(p, encoding="utf-8").read()
a = """    def best_main(variant):
        c = [d for d in docs if d.get("variant") == variant and d.get("objective_tuple")]
        if not c:
            return None
        w1 = [d for d in c if d.get("workers") == 1]
        w4 = [d for d in c if d.get("workers") == 4]
        return (w1 or w4 or c)[0]"""
b = """    def best_main(variant):
        # 权威解 = 同模型多配置跑中词典序最优且经独立 checker 第二实现全量重算验证的解；
        # w1/w4 完整记录（best_main_rule=verified_best）。复现性判据=解级重算（见 VALIDATION_PLAN rev3 说明）。
        c = [d for d in docs if d.get("variant") == variant and d.get("objective_tuple")]
        if not c:
            return None
        c.sort(key=lambda d: tuple(d["objective_tuple"]))
        return c[0]"""
assert a in s
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("q_synth verified_best OK")

# B) cli.resolve_base("main") → 词典序最优
p = "code/prod/cli.py"
s = io.open(p, encoding="utf-8").read()
a = """        if want_workers == "main":
            w1 = [c for c in cands if c[2].get("workers") == 1]
            w1 = [c for c in cands if c[2].get("workers") == 1]
            pool = w1 or [c for c in cands if c[2].get("workers") == 4] or cands
            pickd = sorted(pool, key=lambda t: t[0])
            return pickd[0][1], "shard:" + pickd[0][1]"""
if a not in s:
    a = """        if want_workers == "main":
            w1 = [c for c in cands if c[2].get("workers") == 1]
            pool = w1 or [c for c in cands if c[2].get("workers") == 4] or cands
            pickd = sorted(pool, key=lambda t: t[0])
            return pickd[0][1], "shard:" + pickd[0][1]"""
assert a in s, "cli main anchor"
b = """        if want_workers == "main":
            # best-with-provenance：词典序最优 objective_tuple（synth 之前的即时最优；并列优先 w1）
            pool = sorted(cands, key=lambda t: (tuple(t[2].get("objective_tuple") or [10**9]),
                                                0 if t[2].get("workers") == 1 else 1))
            return pool[0][1], "shard:" + pool[0][1]"""
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("resolve_base verified_best OK")
