# -*- coding: utf-8 -*-
"""Manager merge 预处理器（确定性）：解析各 child route fragment，
校验 JSON/字段完整性/idea_id 命名段/fingerprint 去重，输出合并总表（磁盘重算 SHA）。"""
import hashlib, io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = "runs/competitive/CS-20260911T071520-D2026"
routes_dir = os.path.join(ROOT, "routes")

def sha(p): return hashlib.sha256(io.open(p, "rb").read()).hexdigest()

REQUIRED = ["idea_id_suggested", "question_id", "tier", "method_family", "problem_reformulation",
            "model", "solver", "bound_plan", "scout_plan", "required_assumptions",
            "failure_conditions", "implementation_risk"]
all_routes = {}
files = sorted(f for f in os.listdir(routes_dir) if f.endswith(".route.json"))
for f in files:
    p = os.path.join(routes_dir, f)
    doc = json.load(io.open(p, encoding="utf-8"))
    cid = doc.get("child_run_id")
    miss = []
    for r in doc.get("routes", []):
        bad = [k for k in REQUIRED if k not in r]
        sp = r.get("scout_plan") or {}
        if not sp.get("metrics"):
            bad.append("scout_plan.metrics")
        fit = (r.get("solver") or {}).get("fit_reason", "")
        if bad or len(fit) < 20:
            miss.append((r.get("idea_id_suggested"), bad or ["fit_reason_thin"]))
        all_routes[r["idea_id_suggested"]] = dict(child=cid, q=r.get("question_id"),
            tier=r.get("tier"), family=r.get("method_family"),
            reform=r.get("problem_reformulation", "")[:80],
            solver=(r.get("solver") or {}).get("algorithm", ""),
            budget=(r.get("solver") or {}).get("budget_type", ""),
            fingerprint=hashlib.sha256(json.dumps(
                {k: r.get(k) for k in ["question_id", "method_family", "problem_reformulation",
                 "model", "transformations", "solver", "bound_plan"]},
                ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12],
            src=f)
    print(f"{f} (child={cid}): routes={len(doc.get('routes', []))} sha={sha(p)[:12]} 缺陷={miss if miss else '无'}")

fps = {}
for k, v in all_routes.items():
    fps.setdefault(v["fingerprint"], []).append(k)
dups = {k: v for k, v in fps.items() if len(v) > 1}
by_q = {}
for k, v in all_routes.items():
    by_q.setdefault(v["q"], []).append((k, v["tier"], v["family"], v["child"]))
print("\n== 每问候选（%d 条路线, %d 问）==" % (len(all_routes), len(by_q)))
for q in sorted(by_q):
    print(f"-- {q}: {len(by_q[q])}")
    for (k, t, fam, ch) in sorted(by_q[q]):
        print(f"   {k:9s} {t:22s} {fam:24s} {ch}")
print("\n重复指纹（改名复制嫌疑）:", dups if dups else "无")
io.open(os.path.join(ROOT, "merge_manifest.json"), "w", encoding="utf-8").write(
    json.dumps({f: sha(os.path.join(routes_dir, f)) for f in files}, ensure_ascii=False, indent=1))
print("merge_manifest.json 已写")
