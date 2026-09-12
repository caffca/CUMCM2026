# -*- coding: utf-8 -*-
"""P2-8：动作冗余性/支配性检验 + 各层证书状态口径。

对 Q2/Q4：
 (a) 逐计划"回退为不调"看是否仍 0 冲突（若是，则该调整冗余，adj 可减少）；
 (b) 迭代求不动点（尽量回退），看能否在同等 rev 下得到更小的 adj；
 (c) 打印 layers 的 status/objective/best_bound，区分"证明最优"与"仅 incumbent"。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

WP = {"A": 100, "B": 10, "C": 1}


def build(plans, acts, allow_dg=False):
    out = []
    for pid in sorted({p["id"] for p in plans}):
        o = acts.get(pid, {})
        if o.get("revoke"):
            continue
        out.append(P.shift(pmap[pid], df=int(o.get("df", 0)), dt=int(o.get("dt", 0)),
                           dg=int(o.get("dg", 0)) if allow_dg else 0))
    return out


def tup(acts, pmap):
    rev = adj = pl = mg = 0
    for pid, o in acts.items():
        c = pmap[pid]["cls"]
        if o.get("revoke"):
            rev += 1
            pl += 2 * WP[c]
        elif o:
            adj += 1
            pl += WP[c]
            mg += sum(abs(v) for v in o.values() if isinstance(v, int) and not isinstance(v, bool))
    return [rev, adj, pl, mg]


plans = P.load_plans()
pmap = {p["id"]: p for p in plans}

res = {"check": "冗余性/支配性 + 证书口径"}
for tag, allow_dg in (("Q2", False), ("Q4", True)):
    sol = P.rj(os.path.join("results", f"{tag}_solution.json"))
    acts0 = json.loads(json.dumps(sol["actions"]))
    base = build(plans, acts0, allow_dg)
    e0, _ = P.all_conflicts(base)
    assert len(e0) == 0, f"{tag} 权威解本身不 0 冲突"

    # (a) 单点回退
    singly_redundant = []
    for pid in list(acts0):
        if acts0[pid].get("revoke"):
            continue
        a = dict(acts0)
        del a[pid]
        e, _ = P.all_conflicts(build(plans, a, allow_dg))
        if len(e) == 0:
            singly_redundant.append({"id": pid, "action": acts0[pid]})
    # (b) 不动点回退（贪心：反复删掉可回退者）
    a = dict(acts0)
    dropped = []
    improved = True
    while improved:
        improved = False
        for pid in [k for k, v in a.items() if not v.get("revoke")]:
            t = dict(a)
            del t[pid]
            e, _ = P.all_conflicts(build(plans, t, allow_dg))
            if len(e) == 0:
                a = t
                dropped.append(pid)
                improved = True
                break
    e_fix, _ = P.all_conflicts(build(plans, a, allow_dg))
    # 同时测：单点撤销替换（把某计划改为撤销能否让别的计划不调？）——只做轻量：把 adj 最大的计划试撤
    res[tag] = {
        "auth_tuple": list(sol["objective_tuple"]),
        "mine_tuple": tup(acts0, pmap),
        "single_revert_redundant": singly_redundant,
        "n_single_revert_redundant": len(singly_redundant),
        "fixpoint_reverted_ids": dropped,
        "fixpoint_tuple": tup(a, pmap),
        "fixpoint_conflicts": len(e_fix),
        "fixpoint_dominates_auth": tup(a, pmap) < sol["objective_tuple"],
        "layers": [{"layer": l.get("layer"), "status": l.get("status"), "min": l.get("min"),
                    "cap_R": l.get("cap_R"), "objective": l.get("objective"),
                    "best_bound": l.get("best_bound"), "solution_tuple": l.get("solution_tuple")}
                   for l in sol.get("layers", [])],
        "revocation_cert": {k: v for k, v in sol.get("revocation", {}).items() if k != "ladder_log"},
    }
res["verdict"] = P.verdict(all(res[t]["n_single_revert_redundant"] == 0 and not res[t]["fixpoint_reverted_ids"]
                               for t in ("Q2", "Q4")))
P.wr("p2_redundancy.json", res)
print(json.dumps(res, ensure_ascii=False, indent=1)[:6000])
