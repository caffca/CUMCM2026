# -*- coding: utf-8 -*-
"""run-F 前自检：每条 validation 的 evidence_files 必须 ①在 RESULT_REGISTRY 登记 ②至少一条 authority。
用现有 results/ 的登记面模拟 run-F 的登记面（同名文件同 role/authority）。"""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")
vp = json.load(io.open("reports/VALIDATION_PLAN.json", encoding="utf-8"))
reg = json.load(io.open("results/RESULT_REGISTRY.json", encoding="utf-8"))
art = {}
for a in reg["artifacts"]:
    p = a.get("result_path") or a.get("path") or a.get("file") or (a.get("outputs") or [None])[0]
    if p:
        art[str(p).replace("\\", "/")] = bool(a.get("authority"))
print("registry paths:", sorted(art))
bad = []
for v in vp["validations"]:
    evs = [str(e).replace("\\", "/") for e in (v.get("evidence_files") or [])]
    miss = [e for e in evs if e not in art]
    auth = [e for e in evs if art.get(e)]
    if miss or not auth:
        bad.append((v["validation_id"], "unregistered:" + str(miss), "authority" if auth else "NO-AUTHORITY"))
for b in bad:
    print("BAD", *b)
print("selfcheck:", "CLEAN" if not bad else f"{len(bad)} problems")
