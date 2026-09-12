# -*- coding: utf-8 -*-
"""P2-13：表1 对账 + 官方/裁定 evaluator 指纹核对。"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

out = {"check": "表1 + evaluator 指纹"}
plans = P.load_plans()
pmap = {p["id"]: p for p in plans}
WP = {"A": 100, "B": 10, "C": 1}

for tag in ("Q2", "Q4"):
    acts = P.rj(os.path.join("results", f"{tag}_solution.json"))["actions"]
    mine = {"A": {"kept": 0, "adjusted": 0, "revoked": 0}, "B": {"kept": 0, "adjusted": 0, "revoked": 0},
            "C": {"kept": 0, "adjusted": 0, "revoked": 0}}
    for pid in pmap:
        o = acts.get(pid, {})
        c = pmap[pid]["cls"]
        key = "revoked" if o.get("revoke") else ("adjusted" if o else "kept")
        mine[c][key] += 1
    t1 = P.rj(os.path.join("results", f"{tag}_table1.json"))
    out[tag] = {"p2_by_class": mine, "table1_by_class": t1["by_class"],
                "equal": mine == t1["by_class"],
                "closure_diff_auth": t1.get("table_closure_diff"),
                "class_totals_mine": {c: sum(mine[c].values()) for c in mine},
                "grand_total_mine": sum(sum(v.values()) for v in mine.values()),
                "table1_rows_field": t1.get("result2_rows") if tag == "Q2" else t1.get("result4_rows")}

ev = "runs/competitive/CS-20260911T071520-D2026/canonical_evaluator.py"
p = os.path.join(P.ROOT, ev)
rec = "8c4db98fa11845ca5492255e4da6c4b2e92e040ee30556fa9156993c06fcbb32"
out["evaluator"] = {"path": ev, "exists": os.path.exists(p),
                    "sha256_actual": hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None,
                    "sha256_recorded_in_ADJ_and_FMS": rec,
                    "match": os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == rec}
csv_sha = hashlib.sha256(open(os.path.join(P.ROOT, "data", "canonical_plans.csv"), "rb").read()).hexdigest()
fms = P.rj(os.path.join("reports", "FINAL_MODEL_SPEC.json"))
q1p = [x for x in fms["problems"] if x["problem_id"] == "Q1"][0]
rec_csv = None
q2p = [x for x in fms["problems"] if x["problem_id"] == "Q2"][0]
for par in q2p["parameters"]:
    if par["id"] == "E-SET" or str(par.get("source_path", "")).endswith("canonical_plans.csv"):
        rec_csv = par.get("source_sha256")
star = "runs/competitive/CS-20260911T071520-D2026/scouts/Q2-R51/star_edges.json"
sp = os.path.join(P.ROOT, star)
out["csv_binding"] = {"actual": csv_sha, "recorded_in_FMS_E_SET": rec_csv, "match": csv_sha == rec_csv,
                      "note": "FMS 里 N_PLANS 的 source_sha256 指向附件1.xlsx，E-SET 的 source_sha256 指向 CSV"}
se = json.load(open(sp, encoding="utf-8"))
out["star_edges"] = {"count": len(se.get("edges", {})), "stats_field": se.get("stats", {}).get("star_edges"),
                     "auth_gstar_Q2": P.rj(os.path.join("results", "Q2_solution.json"))["gstar_edges"]}
out["verdict"] = P.verdict(out["Q2"]["equal"] and out["Q4"]["equal"] and out["evaluator"]["match"]
                           and out["csv_binding"]["match"] and out["star_edges"]["count"] == out["star_edges"]["auth_gstar_Q2"])
P.wr("p2_tables_evaluator.json", out)
print(json.dumps(out, ensure_ascii=False, indent=1))
