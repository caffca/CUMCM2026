# -*- coding: utf-8 -*-
"""rev8 全量预检（对齐 evaluator 语义）：evidence 登记+question 绑定+authority；criterion lhs/rhs dot_get 数值；IR pairs 数值等值。
run-H 落地后跑一次，任何非 MIRROR-PENDING 问题都要在收口前解决。"""
import io, json, math, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\6verity\scripts")
import gate_common as gc

vp = json.load(io.open("reports/VALIDATION_PLAN.json", encoding="utf-8"))
reg = json.load(io.open("results/RESULT_REGISTRY.json", encoding="utf-8"))
arts = {str(a.get("file") or "").replace("\\", "/"): a for a in reg["artifacts"] if a.get("file")}
def load(p):
    d = json.load(io.open(p, encoding="utf-8"))
    return d.get("result", d)
docs = {p: load(p) for p in arts}
qmerge = {}
for p, a in arts.items():
    for q in (a.get("problem_ids") or [a.get("problem_id")]):
        m = qmerge.setdefault(q, {})
        for k, v in docs[p].items():
            m.setdefault(k, v)
problems, mirror = [], []
for v in vp["validations"]:
    q, vid = v["question_id"], v["validation_id"]
    evs = [str(e).replace("\\", "/") for e in v.get("evidence_files", [])]
    for e in evs:
        if e not in arts:
            problems.append(f"{vid}: evidence 未登记 {e}")
        elif q not in (arts[e].get("problem_ids") or [arts[e].get("problem_id")]):
            problems.append(f"{vid}: evidence 跨问 {e}")
    if not any(arts.get(e, {}).get("authority") for e in evs):
        problems.append(f"{vid}: 无 authority evidence")
    c = v.get("criterion") or {}
    for side in ("lhs", "rhs"):
        ref = c.get(side)
        if isinstance(ref, str) and ref.startswith("results:"):
            key = ref[len("results:"):]
            val = qmerge.get(q, {}).get(key)
            if val is None:
                (mirror if vid in ("V-Q2-05", "V-Q4-05") else problems).append(f"{vid}: {side} 键 {key} 缺失")
            elif not (isinstance(val, (int, float)) and not isinstance(val, bool)):
                problems.append(f"{vid}: {side} 键 {key} 非数值")
for pr in vp["evidence_contract"]["independent_reproduction"]["pairs"]:
    pd, rd = docs.get(pr["primary_file"], {}), docs.get(pr["reproduction_file"], {})
    for path in pr["compare_paths"]:
        a, b = gc.dot_get(pd, path), gc.dot_get(rd, path)
        ok = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))
        if ok(a) and ok(b):
            if a != b:
                problems.append(f"IR {pr['pair_id']}: {path} 不等 {a}!={b}")
        elif a is None or b is None:
            mirror.append(f"IR {pr['pair_id']}: {path} 待 run-H 镜像")
        else:
            problems.append(f"IR {pr['pair_id']}: {path} 非数值")
b = vp.get("model_decision_binding")
import decision_handoff as dh
from pathlib import Path
h = dh.load_handoff(Path(".").resolve())
if b != h.get("binding"):
    problems.append("model_decision_binding != handoff.binding")
print("rev", vp["plan_revision"], "| problems:", len(problems), "| pending-H mirrors:", len(mirror))
for x in problems:
    print("  [X]", x)
for x in mirror:
    print("  [~]", x)
