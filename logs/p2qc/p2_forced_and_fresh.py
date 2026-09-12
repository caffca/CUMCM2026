# -*- coding: utf-8 -*-
"""P2-11：FORCED 边（恒冲突⇒必撤一端）独立复核 + 生成文档新鲜度（stale doc）检查。"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

DFM, DTM, DGM = P.DF_MAX, P.DT_MAX, P.DG_MAX


def opts_of(p, allow_dg):
    o = [("id", 0)]
    for d in range(-DFM, DFM + 1):
        if d and 0 <= p["f0"] + d and p["f1"] + d <= P.B_MAX:
            o.append(("df", d))
    for d in range(-DTM, DTM + 1):
        if d:
            q = P.shift(p, dt=d)
            ss = P.slot_list(q)
            if min(s for s, e in ss) >= 0 and max(e for s, e in ss) <= P.T_MAX:
                o.append(("dt", d))
    if allow_dg:
        for d in range(-DGM, DGM + 1):
            if d:
                q = P.shift(p, dg=d)
                if q["g"] >= 1:
                    ss = P.slot_list(q)
                    if min(s for s, e in ss) >= 0 and max(e for s, e in ss) <= P.T_MAX:
                        o.append(("dg", d))
    return o


def cells(p, kind, v):
    q = P.shift(p, df=v if kind == "df" else 0, dt=v if kind == "dt" else 0, dg=v if kind == "dg" else 0)
    return frozenset((t, f) for (s, e) in P.slot_list(q) for t in range(s, e) for f in range(q["f0"], q["f1"]))


def main():
    plans = P.load_plans()
    out = {"check": "FORCED 边 + 文档新鲜度"}
    for tag, allow_dg in (("Q2", False), ("Q4", True)):
        auth = P.rj(os.path.join("results", f"{tag}_solution.json"))
        masks = {}
        o_all = {}
        for p in plans:
            oo = opts_of(p, allow_dg and p["cls"] == "C")   # R6：仅 C 类可调间隔
            o_all[p["id"]] = oo
            masks[p["id"]] = [cells(p, k, v) for k, v in oo]
        ids = sorted(o_all)
        # 只对并集相交的对做全组合检查
        unions = {i: set().union(*masks[i]) for i in ids}
        checked = 0
        forced = []
        always_free = 0
        for x in range(len(ids)):
            a = ids[x]
            for y in range(x + 1, len(ids)):
                b = ids[y]
                if not (unions[a] & unions[b]):
                    continue
                checked += 1
                ok_found = False
                for ma in masks[a]:
                    for mb in masks[b]:
                        if not (ma & mb):
                            ok_found = True
                            break
                    if ok_found:
                        break
                if ok_found:
                    always_free += 1
                else:
                    forced.append([a, b])
        out[tag] = {"pairs_with_union_overlap_mine": checked, "forced_edges_mine": len(forced),
                    "forced_edges_auth": auth.get("forced_edges"),
                    "forced_examples": forced[:8],
                    "match": len(forced) == (auth.get("forced_edges") or 0)}

    # 文档/生成器新鲜度
    root = P.ROOT
    def mt(rel):
        p = os.path.join(root, rel)
        return os.path.getmtime(p) if os.path.exists(p) else None
    rep = mt(os.path.join("reports", "RESULTS_REPORT.md"))
    gen = mt(os.path.join("code", "prod", "make_report.py"))
    out["freshness"] = {"RESULTS_REPORT.md_mtime": rep, "make_report.py_mtime": gen,
                        "report_stale_vs_generator": bool(rep and gen and gen > rep)}
    txt = open(os.path.join(root, "reports", "RESULTS_REPORT.md"), encoding="utf-8").read()
    out["stale_strings_found"] = {s: (s in txt) for s in
                                  ["权威解（workers=1 确定性）", "w8=", "视界截断 dg 选项=369"]}
    # 权威 results 绑定的 VALIDATION_PLAN 指纹是否与磁盘一致
    vp_hashed = []
    for fn in sorted(os.listdir(os.path.join(root, "results"))):
        if not fn.endswith(".json"):
            continue
        d = json.load(open(os.path.join(root, "results", fn), encoding="utf-8"))
        ih = (d.get("_meta") or {}).get("input_hashes") or {}
        if "reports/VALIDATION_PLAN.json" in ih:
            actual = hashlib.sha256(open(os.path.join(root, "reports", "VALIDATION_PLAN.json"), "rb").read()).hexdigest()
            vp_hashed.append((fn, ih["reports/VALIDATION_PLAN.json"] == actual))
    import time as _t
    vp_mt = os.stat(os.path.join(root, "reports", "VALIDATION_PLAN.json")).st_mtime
    vp = json.load(open(os.path.join(root, "reports", "VALIDATION_PLAN.json"), encoding="utf-8"))
    newest_result = max(os.stat(os.path.join(root, "results", f)).st_mtime
                        for f in os.listdir(os.path.join(root, "results")) if f.endswith(".json"))
    out["validation_plan_binding"] = {
        "files_binding_plan": len(vp_hashed),
        "files_with_matching_hash": sum(1 for _, ok in vp_hashed if ok),
        "plan_revision": vp.get("plan_revision"),
        "plan_frozen_at": vp.get("frozen_at"),
        "plan_frozen_before_production_runs_claim": vp.get("frozen_before_production_runs"),
        "plan_mtime": _t.strftime("%F %T", _t.localtime(vp_mt)),
        "newest_result_mtime": _t.strftime("%F %T", _t.localtime(newest_result)),
        "plan_actually_written_after_results": vp_mt > newest_result,
    }
    out["verdict"] = P.verdict(out["Q2"]["match"] and out["Q4"]["match"]
                               and not out["freshness"]["report_stale_vs_generator"]
                               and out["validation_plan_binding"]["files_with_matching_hash"]
                               == out["validation_plan_binding"]["files_binding_plan"]
                               and not out["validation_plan_binding"]["plan_actually_written_after_results"])
    P.wr("p2_forced_and_fresh.json", out)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
