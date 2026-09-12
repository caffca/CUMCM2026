# -*- coding: utf-8 -*-
import io, py_compile, glob, os

# 1) write_results: attempts/*/payload.json 取最大 attempt
p = "code/prod/write_results.py"
s = io.open(p, encoding="utf-8").read()
a = """    for tid, t in tasks.items():
        d = os.path.join(run_root, "tasks", tid, "attempts", "1")
        pp = os.path.join(d, "payload.json")
        em = os.path.join(d, "execution_metrics.json")
        if not os.path.isfile(pp):
            continue"""
b = """    for tid, t in tasks.items():
        ad = sorted(glob.glob(os.path.join(run_root, "tasks", tid, "attempts", "*")))
        if not ad:
            continue
        d = ad[-1]
        pp = os.path.join(d, "payload.json")
        em = os.path.join(d, "execution_metrics.json")
        if not os.path.isfile(pp):
            continue"""
assert a in s
s = s.replace(a, b)
if "import glob" not in s:
    s = s.replace("import json, os, subprocess, sys", "import glob, json, os, subprocess, sys")
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("write_results attempts glob fixed")

# 2) q_synth variant=synth 标签
p = "code/prod/q_synth.py"
s = io.open(p, encoding="utf-8").read()
n = 0
for a2, b2 in [
    ('"question_id": "Q2", "assembled": True,', '"question_id": "Q2", "variant": "synth", "assembled": True,'),
    ('"question_id": "Q3", "assembled": True, "phi": phi,', '"question_id": "Q3", "variant": "synth", "assembled": True, "phi": phi,'),
    ('"question_id": "Q4", "assembled": True,', '"question_id": "Q4", "variant": "synth", "assembled": True,'),
]:
    if b2 not in s and a2 in s:
        s = s.replace(a2, b2)
        n += 1
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("q_synth tagged:", n)

# 3) synth 匹配改用 assembled 标志（不动 shard payload——哈希链完整优先）
p = "code/prod/write_results.py"
s = io.open(p, encoding="utf-8").read()
a = """        for c in by_var.get(q, []):
            if c["var"] == variant and (workers is None or c["workers"] == workers):
                rec = c"""
b = """        for c in by_var.get(q, []):
            v_ok = (c["var"] == variant) or (variant == "synth" and c.get("assembled"))
            if v_ok and (workers is None or c["workers"] == workers):
                rec = c"""
assert a in s, "pick anchor"
s = s.replace(a, b)
s = s.replace("""            by_var.setdefault(t.get("question_id"), []).append(
                {"task_id": tid, "payload": pp.replace("\\\\", "/"), "metrics": em, "var": pv.get("variant"),
                 "workers": pv.get("workers"), "task": t})""",
              """            by_var.setdefault(t.get("question_id"), []).append(
                {"task_id": tid, "payload": pp.replace("\\\\", "/"), "metrics": em, "var": pv.get("variant"),
                 "workers": pv.get("workers"), "assembled": bool(pv.get("assembled")), "task": t})""")
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("write_results synth matching by assembled flag; payload untouched")

