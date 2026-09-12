# -*- coding: utf-8 -*-
"""rev8 前预检：模拟 evaluator 的三类全局检查，杜绝再触发 run 级重绑。
①evidence_files 登记+question 绑定 ②criterion lhs/rhs 键在合并 docs 中可解析为有限数值
③IR pairs compare_paths 在两文档等值且为有限数值 ④threshold/tolerance 形状。"""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")
vp = json.load(io.open("reports/VALIDATION_PLAN.json", encoding="utf-8"))
reg = json.load(io.open("results/RESULT_REGISTRY.json", encoding="utf-8"))
arts = {}
for a in reg["artifacts"]:
    p = str(a.get("file") or "").replace("\\", "/")
    if p:
        arts[p] = a
docs = {}
for p, a in arts.items():
    name = p[:-5].split("/")[-1]
    d = json.load(io.open(p, encoding="utf-8"))
    docs[name] = (d.get("result", d), a)
qdocs = {}
for name, (d, a) in docs.items():
    for q in (a.get("problem_ids") or [a.get("problem_id")]):
        qdocs.setdefault(q, []).append((name, d))
def dotget(d, path):
    cur = d
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit():
            cur = cur[int(part)]
        else:
            return None
    return cur
problems = []
for v in vp["validations"]:
    q = v["question_id"]; vid = v["validation_id"]
    for e in v.get("evidence_files", []):
        e = e.replace("\\", "/")
        if e not in arts:
            problems.append(f"{vid}: evidence 未登记 {e}")
        else:
            pa = arts[e]
            eqs = pa.get("problem_ids") or [pa.get("problem_id")]
            if q not in eqs:
                problems.append(f"{vid}: evidence 跨问 {e} bound={eqs}")
    auth = [e for e in v.get("evidence_files", []) if arts.get(e.replace("\\", "/"), {}).get("authority")]
    if not auth:
        problems.append(f"{vid}: 无 authority evidence")
    c = v.get("criterion") or {}
    merged = {}
    for name, d in qdocs.get(q, []):
        for k, val in d.items():
            merged.setdefault(k, val)
    for side in ("lhs", "rhs"):
        ref = c.get(side)
        if isinstance(ref, str) and ref.startswith("results:"):
            key = ref[len("results:"):]
            val = merged.get(key)
            if val is None:
                problems.append(f"{vid}: {side} 键 {key} 不在 Q{q[-1]} 合并 docs")
            elif not (isinstance(val, (int, float)) and not isinstance(val, bool)):
                problems.append(f"{vid}: {side} 键 {key} 非数值（{type(val).__name__}）")
ir = vp.get("evidence_contract", {}).get("independent_reproduction", {}).get("pairs", [])
for pr in ir:
    pdoc = docs.get(pr["primary_file"].replace("results/", "")[:-5], (None,))[0]
    rdoc = docs.get(pr["reproduction_file"].replace("results/", "")[:-5], (None,))[0]
    if pdoc is None or rdoc is None:
        problems.append(f"IR {pr['pair_id']}: 文档缺失"); continue
    for path in pr.get("compare_paths", []):
        a = dotget(pdoc, path.strip("/")); b = dotget(rdoc, path.strip("/"))
        oknum = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
        if not oknum(a) or not oknum(b):
            problems.append(f"IR {pr['pair_id']}: {path} 非数值（{type(a).__name__}/{type(b).__name__}）")
        elif a != b:
            problems.append(f"IR {pr['pair_id']}: {path} 不等 {a}!={b}")
print("binding:", vp.get("model_decision_binding") is not None, "| problems:", len(problems))
for x in problems:
    print("  -", x)
