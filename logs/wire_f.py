# -*- coding: utf-8 -*-
"""run-F 正确接线 + pipeline 增 sensitivity 步 + 校验分派器未被改动（不破坏 plan 绑定）。"""
import io, hashlib, py_compile, os

for f in ("code/prod/run_prod.py", "code/prod/pipeline.py"):
    s = io.open(f, encoding="utf-8").read()
    s2 = s.replace("FULL-D2026-PROD-E", "FULL-D2026-PROD-F")
    with io.open(f, "w", encoding="utf-8") as fh:
        fh.write(s2)
    py_compile.compile(f, doraise=True)
    print("wired", f, "F" if "PROD-F" in s2 else "??")

# pipeline 增 make_q3_sensitivity 步（在 submission_checks 之后、verify 之前）
p = "code/prod/pipeline.py"
s = io.open(p, encoding="utf-8").read()
a = '    ("verify", [sys.executable, "code/verify_all.py"]),'
b = ('    ("sensitivity", [sys.executable, "code/prod/make_q3_sensitivity.py"]),\n'
     '    ("verify", [sys.executable, "code/verify_all.py"]),')
if a in s and "make_q3_sensitivity" not in s:
    s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8").write(s)
    py_compile.compile(p, doraise=True)
    print("pipeline sensitivity step added")

# 校验：分派器 sha 未被本轮编辑改动（确保 plan 仍绑定当前分派器）
for q in ("q1_solve.py", "q2_solve.py", "q3_solve.py", "q4_solve.py"):
    print(q, hashlib.sha256(open("code/prod/" + q, "rb").read()).hexdigest()[:16])
print("plan exists:", os.path.exists("reports/execution/SHARD_PLAN.json"))
