# -*- coding: utf-8 -*-
"""Manager 探索性复核（非正式结果，runs 级）：两套独立实现交叉验证 Q1 冲突对语义。
实现A：逐计划对×逐时段对区间交叠；实现B：位图占用集合求交。
两者必须一致才允许 common_input 的参考事实成立。"""
import csv, io, json, sys
sys.stdout.reconfigure(encoding="utf-8")

plans = []
with io.open("data/canonical_plans.csv", encoding="utf-8") as f:
    rd = csv.DictReader(f)
    for r in rd:
        plans.append(dict(id=r["equipment_id"], f=(int(r["f_lo"]), int(r["f_hi"])),
                          t=(int(r["t_first_lo"]), int(r["t_first_hi"])),
                          g=int(r["gap"]), n=int(r["use_count"]),
                          d=int(r["time_width"])))
N = len(plans)

# ---- 实现 A：区间算术 ----
def slots_a(p):
    return [(p["t"][0] + k * (p["g"] + p["d"]), p["t"][0] + k * (p["g"] + p["d"]) + p["d"]) for k in range(p["n"])]
confA = set()
for i in range(N):
    for j in range(i + 1, N):
        a, b = plans[i], plans[j]
        if min(a["f"][1], b["f"][1]) - max(a["f"][0], b["f"][0]) > 0:
            sa, sb = slots_a(a), slots_a(b)
            if any(min(x[1], y[1]) - max(x[0], y[0]) > 0 for x in sa for y in sb):
                confA.add((i, j))

# ---- 实现 B：位图（频段×时间格占用集合）----
TMAX = max(p["t"][0] + (p["n"] - 1) * (p["g"] + p["d"]) + p["d"] for p in plans)
masks = []
for p in plans:
    m = set()
    for k in range(p["n"]):
        t0 = p["t"][0] + k * (p["g"] + p["d"])
        for t in range(t0, t0 + p["d"]):
            for fb in range(p["f"][0], p["f"][1]):
                m.add(t * 100 + fb)
    masks.append(m)
confB = set()
for i in range(N):
    for j in range(i + 1, N):
        if not masks[i].isdisjoint(masks[j]):
            confB.add((i, j))

print("A pairs:", len(confA), "B pairs:", len(confB), "diff:", len(confA ^ confB))
by_cp = {}
for (i, j) in confA:
    key = "".join(sorted(plans[i]["id"][0] + plans[j]["id"][0]))
    by_cp[key] = by_cp.get(key, 0) + 1
print("by_class_pair:", json.dumps(by_cp, sort_keys=True))
involved = set()
for (i, j) in confA:
    involved |= {i, j}
print("plans_involved:", len(involved), "/ 150")
# 每计划冲突度分布（供建模参考）
deg = {i: 0 for i in range(N)}
for (i, j) in confA:
    deg[i] += 1
    deg[j] += 1
import statistics
ds = sorted(deg.values(), reverse=True)
top = sorted(((deg[i], plans[i]["id"]) for i in range(N)), reverse=True)[:12]
print("degree: max=%d median=%.1f isolated=%d top=%s" % (ds[0], statistics.median(ds), sum(1 for v in ds if v == 0), top))
