# -*- coding: utf-8 -*-
import io, py_compile
p = "code/prod/write_results.py"
s = io.open(p, encoding="utf-8").read()
a = """               "--coverage-json", json.dumps({"coverage_id": (cov_contract.get("coverage_plan_id") or plan.get("coverage_plan_id")),
                                               "plan_path": cov_path.replace("\\\\", "/"),
                                               "observed": observed, "status": "complete"}),
"""
if a not in s:
    # 宽松匹配行块
    lines = s.splitlines()
    keep, skip = [], 0
    for ln in lines:
        if "--coverage-json" in ln:
            skip = 2 if "json.dumps" in ln and "status" not in ln else 1
            # 数到闭合 '),'：找含 '),"status": "complete"}),' 的行
            continue_skip = [ln]
            while "complete\"})" not in continue_skip[-1] and "complete\"})," not in continue_skip[-1]:
                nxt = lines[lines.index(ln) + len(continue_skip):lines.index(ln) + len(continue_skip) + 1]
                if not nxt:
                    break
                continue_skip.append(nxt[0])
            continue
        keep.append(ln)
    s = "\n".join(keep)
else:
    s = s.replace(a, "")
io.open(p, "w", encoding="utf-8").write(s)
try:
    py_compile.compile(p, doraise=True)
    print("coverage-json removed; compile OK")
except Exception as e:
    print("COMPILE FAIL:", e)
