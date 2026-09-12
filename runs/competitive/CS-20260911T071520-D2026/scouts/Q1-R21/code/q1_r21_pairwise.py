# -*- coding: utf-8 -*-
"""Q1-R21 原型（Prototype Engineer，竞争搜索 Q1 组）
路线：逐对区间算术（analytic_mechanistic，CH-02 Q1-R21，baseline）

双实现（Q1-C1 验收规则要求）：
  A = 逐 (k,m) 时段对枚举 + 半开区间交叠判定
  B = 每计划时段做区间并集压缩（半开）后两指针扫描相交
两者输出边集做集合相等断言；另含边界用例与 common_input 等价性核对。

口径（ADJUDICATION.json）：T_MAX=643；区间一律半开 [a,b)；
slot_k = [t1+(k-1)(g+d), t1+(k-1)(g+d)+d)（F-005，g 为空闲间隔）。

本脚本只写本 scout 目录（solution/detect_meta），不写 results/figures/paper。
"""
import io
import json
import os
import time
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))          # .../scouts/Q1-R21/code
SCOUT_DIR = os.path.abspath(os.path.join(HERE, ".."))      # .../scouts/Q1-R21
RUN_DIR = os.path.abspath(os.path.join(SCOUT_DIR, "..", ".."))       # runs/competitive/<search_id>
ROOT = os.path.abspath(os.path.join(RUN_DIR, "..", "..", ".."))      # workspace 根

CSV_PATH = os.path.join(ROOT, "data", "canonical_plans.csv")
COMMON_INPUT = os.path.join(RUN_DIR, "common_input.json")
T_MAX = 643   # 裁定 R1
B_MAX = 100   # 裁定 R1 / F-001
PAIR_TOTAL = 11175   # C(150,2)：全查对数


def load_plans_from_csv(path):
    plans = []
    with io.open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    hdr = lines[0].split(",")
    assert hdr[0] == "equipment_id", hdr
    for line in lines[1:]:
        a = line.split(",")
        pid, cls = a[0], a[1]
        f0, f1, t0, t1, g, n = (int(a[2]), int(a[3]), int(a[4]),
                                int(a[5]), int(a[6]), int(a[7]))
        plans.append(dict(id=pid, cls=cls, f0=f0, f1=f1, t0=t0, t1=t1,
                          g=g, n=n, d=t1 - t0))
    return plans


def crosscheck_common_input(plans):
    """核对 data/canonical_plans.csv 与 common_input.plans_table_compact 等价。"""
    if not os.path.isfile(COMMON_INPUT):
        return {"available": False}
    with io.open(COMMON_INPUT, encoding="utf-8") as fh:
        ci = json.load(fh)
    compact = ci.get("plans_table_compact")
    if not compact:
        return {"available": False}
    cmap = {r[0]: r for r in compact}
    bad = []
    for p in plans:
        r = cmap.get(p["id"])
        if r is None:
            bad.append((p["id"], "missing_in_compact"))
            continue
        # compact 行: [id, f_lo, f_hi, t_first_lo, t_first_hi, gap, use_count]
        if [r[1], r[2], r[3], r[4], r[5], r[6]] != [p["f0"], p["f1"], p["t0"],
                                                   p["t1"], p["g"], p["n"]]:
            bad.append((p["id"], "field_mismatch", r))
    return {"available": True, "rows_compact": len(compact), "rows_csv": len(plans),
            "mismatches": bad[:10], "equivalent": (not bad) and len(compact) == len(plans)}


def slots(p):
    """F-005 全展开：n 个占用时段（半开）。"""
    P = p["g"] + p["d"]
    return [(p["t0"] + k * P, p["t0"] + k * P + p["d"]) for k in range(p["n"])]


def band_overlap(a, b):
    """频段半开区间交叠：min(f1)-max(f0) > 0（F-023）。"""
    return min(a["f1"], b["f1"]) - max(a["f0"], b["f0"]) > 0


def time_overlap_A(a, b):
    """实现 A：逐 (k,m) 时段对枚举。"""
    sa, sb = slots(a), slots(b)
    for (s1, e1) in sa:
        for (s2, e2) in sb:
            if max(s1, s2) < min(e1, e2):   # 半开交叠
                return True
    return False


def merged_union(p):
    """把 n 个半开时段压成不相交的半开区间并集（端点相接可并）。"""
    out = []
    for (s, e) in sorted(slots(p)):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return [(s, e) for s, e in out]


def two_pointer_hit(la, lb):
    """实现 B：两个已排序不相交半开区间列表做两指针扫描。"""
    i = j = 0
    while i < len(la) and j < len(lb):
        s1, e1 = la[i]
        s2, e2 = lb[j]
        if max(s1, s2) < min(e1, e2):
            return True
        if e1 <= e2:
            i += 1
        else:
            j += 1
    return False


def detect():
    plans = load_plans_from_csv(CSV_PATH)
    assert len(plans) == 150, len(plans)
    ids = [p["id"] for p in plans]
    assert len(set(ids)) == 150
    # 视界自检：全部占用应落在 [0,643)
    horizon_ok = all(0 <= s and e <= T_MAX for p in plans for (s, e) in slots(p))
    band_ok = all(0 <= p["f0"] < p["f1"] <= B_MAX for p in plans)

    merged = {p["id"]: merged_union(p) for p in plans}
    by_id = {p["id"]: p for p in plans}

    edges_A, edges_B = [], []
    band_pairs = 0
    t0 = time.perf_counter()
    for a, b in combinations(ids, 2):
        pa, pb = by_id[a], by_id[b]
        if not band_overlap(pa, pb):
            continue
        band_pairs += 1
        if time_overlap_A(pa, pb):
            edges_A.append([a, b])
        if two_pointer_hit(merged[a], merged[b]):
            edges_B.append([a, b])
    wall = time.perf_counter() - t0
    assert len(edges_A) == len(edges_B)
    symdiff = set(map(tuple, edges_A)) ^ set(map(tuple, edges_B))
    return plans, edges_A, edges_B, symdiff, band_pairs, wall, horizon_ok, band_ok


def boundary_cases():
    """半开区间边界用例：端点相接不得计冲突。"""
    cases = []
    mk = lambda f0, f1, t0_, t1_, g, n: dict(id="x", cls="A", f0=f0, f1=f1,
                                             t0=t0_, t1=t1_, g=g, n=n, d=t1_ - t0_)
    p1 = mk(80, 90, 0, 5, 60, 1)
    p2 = mk(90, 95, 0, 5, 60, 1)
    cases.append(("band_[80,90)vs[90,95)", band_overlap(p1, p2), False))
    q1 = mk(10, 20, 40, 45, 60, 1)
    q2 = mk(10, 20, 45, 50, 60, 1)
    cases.append(("time_[40,45)vs[45,50)", time_overlap_A(q1, q2), False))
    cases.append(("time_[40,45)vs[44,50)", time_overlap_A(q1, mk(10, 20, 44, 50, 60, 1)), True))
    r1 = mk(10, 20, 35, 40, 60, 3)      # A001 型：[35,40),[100,105),[165,170)
    r2 = mk(10, 20, 165, 170, 60, 1)
    cases.append(("third_slot_hit_[165,170)", time_overlap_A(r1, r2), True))
    r3 = mk(10, 20, 170, 175, 60, 1)
    cases.append(("third_slot_touch_[170,175)", time_overlap_A(r1, r3), False))
    fails = [c for c in cases if bool(c[1]) != c[2]]
    return [(n, int(bool(v)), int(exp), int(bool(v)) == exp) for n, v, exp in cases], fails


def main():
    t_start = time.perf_counter()
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    eq = crosscheck_common_input(load_plans_from_csv(CSV_PATH))
    plans, A, B, symdiff, band_pairs, wall, horizon_ok, band_ok = detect()
    bc, bc_fails = boundary_cases()

    A_sorted = sorted([list(p) for p in A])
    B_sorted = sorted([list(p) for p in B])

    sol_path = os.path.join(SCOUT_DIR, "solution_q1_r21.json")
    with io.open(sol_path, "w", encoding="utf-8") as fh:
        json.dump(A_sorted, fh, ensure_ascii=False)

    # 按类对分层统计（供 scout.json 与后续对照）
    by_id = {p["id"]: p for p in plans}
    strata = {}
    for a, b in A_sorted:
        key = "".join(sorted([by_id[a]["cls"], by_id[b]["cls"]]))
        strata[key] = strata.get(key, 0) + 1
    touched = set()
    for a, b in A_sorted:
        touched.add(a)
        touched.add(b)

    total = time.perf_counter() - t_start
    meta = {
        "idea_id": "Q1-R21",
        "question_id": "Q1",
        "started_at": started_at,
        "protocol": "TP-D2026-01",
        "horizon": {"T_MAX": T_MAX, "B_MAX": B_MAX, "half_open": True,
                    "all_slots_within_horizon": bool(horizon_ok),
                    "all_bands_within_0_99": bool(band_ok)},
        "data_source": {"csv": os.path.relpath(CSV_PATH, ROOT).replace("\\", "/"),
                        "common_input_equivalence": eq},
        "evaluation": {"pairs_total": PAIR_TOTAL, "pairs_evaluated": PAIR_TOTAL,
                       "band_candidate_pairs": band_pairs,
                       "slot_pair_comparisons_worst_case": 1609200,
                       "impl_A_edges": len(A_sorted), "impl_B_edges": len(B_sorted),
                       "symdiff_AB": len(symdiff),
                       "impl_A_equals_impl_B": bool(len(symdiff) == 0),
                       "impl_A_equals_impl_B_sorted_lists": A_sorted == B_sorted},
        "conflict_pairs": len(A_sorted),
        "by_class_pair": strata,
        "plans_touched": len(touched),
        "boundary_cases": bc,
        "boundary_case_failures": [list(map(str, f)) for f in bc_fails],
        "runtime_seconds": round(wall, 4),
        "runtime_total_seconds": round(total, 4),
        "solution_path": os.path.relpath(sol_path, ROOT).replace("\\", "/"),
        "determinism": "deterministic (no RNG)",
        "status": "completed" if (len(symdiff) == 0 and not bc_fails) else "failed",
        "failure_mode": (None if (len(symdiff) == 0 and not bc_fails)
                         else "internal_inconsistency_impls_or_boundary"),
    }
    with io.open(os.path.join(SCOUT_DIR, "detect_meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"conflict_pairs": meta["conflict_pairs"],
                      "by_class_pair": meta["by_class_pair"],
                      "symdiff_AB": meta["evaluation"]["symdiff_AB"],
                      "band_candidate_pairs": meta["evaluation"]["band_candidate_pairs"],
                      "status": meta["status"],
                      "runtime_seconds": meta["runtime_seconds"],
                      "csv_vs_common_input_equivalent":
                          eq.get("equivalent"),
                      "boundary_failures": len(meta["boundary_case_failures"])},
                     ensure_ascii=False))
    print("symdiff:", len(symdiff), "| boundary fails:", len(bc_fails))
    return meta


if __name__ == "__main__":
    main()
