# -*- coding: utf-8 -*-
"""REV-Q4-01 附件脚本 E：势边表 / 禁元组表的【完备性】独立审计。

风险点（CH-05 警示#2a）：若边表只覆盖原始冲突对或漏掉某些 (选项_i, 选项_j) 对，
CP-SAT 会给出"看起来零冲突"的假可行解。本脚本不用候选的 build_edges，
自己用区间算术重算全部 150 计划 × 全部选项的占用位图，然后：
  (1) 对全部 C(150,2)=11175 个计划对：判定"是否存在一对非撤销选项相交"⇒ 应入边表；
  (2) 对已入边表的每一对：逐选项对判定相交 ⇒ 应入禁元组表；
  (3) 与候选 build_edges 的输出做双向集合差（漏边 = 假可行风险；多边 = 只损失效率）。
"""
import io, json, os, sys, time

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS = os.path.abspath(os.path.join(RUN, "..", "..", ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(RUN, "scouts", "Q4-R11", "code"))
import q4common as Q                                        # noqa: E402
sys.stdout.reconfigure(encoding="utf-8")

T_MAX, B_MAX = 643, 100


def my_mask(p, df=0, dt=0, dg=0):
    """独立实现（区间算术 → 位图），不经过 evaluator.mask_of。越界 → None。"""
    gp = p["g"] + dg
    if gp < 1:
        return None
    f0, f1 = p["f0"] + df, p["f1"] + df
    if f0 < 0 or f1 > B_MAX:
        return None
    period = gp + p["d"]
    m = 0
    for k in range(p["n"]):
        s = p["t0"] + dt + k * period
        e = s + p["d"]
        if s < 0 or e > T_MAX:
            return None
        for t in range(s, e):
            base = t * B_MAX
            for f in range(f0, f1):
                m |= 1 << (base + f)
    return m


plans = Q.CE.load_plans()
d4 = Q.build_domains(plans, allow_gap=True)
edges_c, forb_c = Q.build_edges(plans, d4)          # 候选的边表（仅作对照，不做判定依据）
t0 = time.time()

# 独立位图 + 与候选位图的一致性核对（同一选项索引）
mismatch = []
MY = {}
for pid, opts in d4.items():
    arr = []
    for o, opt in enumerate(opts):
        if opt["kind"] == "revoke":
            mm = 0
        elif opt["kind"] == "none":
            mm = my_mask(plans[pid])
        else:
            mm = my_mask(plans[pid], **({opt["kind"]: opt["v"]}))
        if (mm or 0) != (opt["mask"] or 0):
            mismatch.append([pid, o, opt["kind"], opt["v"], (mm or 0) == (opt["mask"] or 0)])
        arr.append(mm)
    MY[pid] = arr
out = {"option_mask_recount_mismatches": len(mismatch), "examples": mismatch[:5]}

ids = sorted(d4)
mine_edges, mine_forb = set(), {}
for x in range(len(ids)):
    i = ids[x]
    for y in range(x + 1, len(ids)):
        j = ids[y]
        mi, mj = MY[i], MY[j]
        f = {}
        anyp = False
        for o1 in range(len(mi)):
            a = mi[o1]
            if not a:
                continue
            for o2 in range(len(mj)):
                b = mj[o2]
                if not b:
                    continue
                if a & b:
                    f.setdefault(o1, set()).add(o2)
                    anyp = True
        if anyp:
            mine_edges.add((i, j))
            mine_forb[(i, j)] = f
cand_edges = set(map(tuple, edges_c))
missing_edges = sorted(mine_edges - cand_edges)          # 候选漏掉的边 → 假可行风险
extra_edges = sorted(cand_edges - mine_edges)
# 禁元组对差异（只在共有边上比较）
missing_pairs = 0
extra_pairs = 0
ex = []
for e in sorted(mine_edges & cand_edges):
    f_c = forb_c[e][0]
    for o1, o2s in mine_forb[e].items():
        for o2 in o2s:
            if o2 not in f_c.get(o1, ()):
                missing_pairs += 1
                if len(ex) < 5:
                    ex.append([list(e), o1, o2])
    for o1, o2s in f_c.items():
        for o2 in o2s:
            if o2 not in mine_forb[e].get(o1, set()):
                extra_pairs += 1
out["E_edge_table_audit"] = dict(
    mine_edges=len(mine_edges), candidate_edges=len(cand_edges),
    missing_edges=len(missing_edges), missing_examples=[list(m) for m in missing_edges[:10]],
    extra_edges=len(extra_edges), extra_examples=[list(m) for m in extra_edges[:10]],
    forbidden_pair_missing_in_candidate=missing_pairs,
    forbidden_pair_extra_in_candidate=extra_pairs, pair_examples=ex,
    elapsed_seconds=round(time.time() - t0, 1),
    verdict_zero_missing=(len(missing_edges) == 0 and missing_pairs == 0))

# ---------- 同一审计对 Q2 退化域做一遍（包含性证据的独立版） ----------
d2 = Q.build_domains(plans, allow_gap=False)
MY2 = {}
for pid, opts in d2.items():
    arr = []
    for opt in opts:
        if opt["kind"] == "revoke":
            arr.append(0)
        elif opt["kind"] == "none":
            arr.append(my_mask(plans[pid]))
        else:
            arr.append(my_mask(plans[pid], **({opt["kind"]: opt["v"]})))
    MY2[pid] = arr
e2c, _ = Q.build_edges(plans, d2)
mine2 = set()
ids2 = sorted(d2)
for x in range(len(ids2)):
    i = ids2[x]
    for y in range(x + 1, len(ids2)):
        j = ids2[y]
        mi, mj = MY2[i], MY2[j]
        if any((mi[a] and mj[b] and (mi[a] & mj[b])) for a in range(len(mi)) for b in range(len(mj))):
            mine2.add((i, j))
out["E_q2_edge_audit"] = dict(mine=len(mine2), candidate=len(set(map(tuple, e2c))),
                              subset_of_q4=set(map(tuple, e2c)).issubset(cand_edges),
                              mine2_subset_of_mine4=mine2.issubset(mine_edges),
                              mine_q2_count=sorted(mine2).__len__(),
                              mine_q4_count=len(mine_edges))
io.open(os.path.join(RUN, "reviews", "_tmp", "recheck_out_E.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1, default=str))
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
