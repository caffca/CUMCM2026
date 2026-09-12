# -*- coding: utf-8 -*-
"""Q1-R52 原型（Prototype Engineer，竞争搜索 Q1 组）
路线：类内同余闭式（analytic_mechanistic / 闭式计数，CH-05 Q1-R52，advanced_alternative）

判据推导（同类 (g,d) 齐次 ⇒ 周期 P=g+d 相同、时长 d 相同、次数 n 相同）：
  slot_k(i) = [t0_i + k*P, t0_i + k*P + d)，k=0..n-1（F-005）
  两窗交叠 ⇔ |Δ + q*P| <= d-1，其中 Δ = t0_i - t0_j，q = k_i - k_j ∈ [-(n_j-1), n_i-1]
  若 2(d-1) < P（本数据 A:8<65, B:4<43, C:2<10 全部成立）⇒ 使 |Δ+qP| 最小的 q 唯一，
  于是「∃ 合法 q」⇔ 两个初等条件的合取：
      (1) Δ mod P ∈ 残差集 S_d = {0,..,d-1} ∪ {P-d+1,..,P-1}
      (2) |Δ| ≤ (n-1)*P + (d-1)          （窗序可达性）
  证明：|Δ| ≤ (n-1)P + d-1 是必要条件（|Δ| ≤ |q|P + (d-1), |q| ≤ n-1）；
        反过来若 (1)(2) 成立，则唯一 q* 满足 |q*|P ≤ |Δ| + (d-1) ≤ (n-1)P + 2(d-1) < nP
        ⇒ |q*| ≤ n-1，q* 即合法窗序差。
  跨类（P 不同）⇒ 残差条件退化为 gcd(P_i,P_j) 陪集，本原型按路线说明回退逐对枚举。

硬验收（路线 failure_conditions）：闭式与逐对枚举**逐对一致**（对称差=0），否则本路线失败。
另附界有效性自检：LB(残差同余强制冲突) ≤ |E| ≤ UB(去窗序可达约束的放宽模型)。

口径（ADJUDICATION.json）：T_MAX=643、半开区间 [a,b)。
只写本 scout 目录。
"""
import io
import json
import os
import time
from bisect import bisect_left, bisect_right
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
SCOUT_DIR = os.path.abspath(os.path.join(HERE, ".."))
RUN_DIR = os.path.abspath(os.path.join(SCOUT_DIR, "..", ".."))
ROOT = os.path.abspath(os.path.join(RUN_DIR, "..", "..", ".."))

CSV_PATH = os.path.join(ROOT, "data", "canonical_plans.csv")
T_MAX, B_MAX, PAIR_TOTAL = 643, 100, 11175


def load_plans(path):
    plans = []
    lines = io.open(path, encoding="utf-8").read().splitlines()
    for line in lines[1:]:
        a = line.split(",")
        f0, f1, t0, t1, g, n = (int(a[2]), int(a[3]), int(a[4]),
                                int(a[5]), int(a[6]), int(a[7]))
        plans.append(dict(id=a[0], cls=a[1], f0=f0, f1=f1, t0=t0, t1=t1,
                          g=g, n=n, d=t1 - t0, P=g + (t1 - t0)))
    assert len(plans) == 150
    return plans


def slots(p):
    return [(p["t0"] + k * p["P"], p["t0"] + k * p["P"] + p["d"]) for k in range(p["n"])]


def band_overlap(a, b):
    return min(a["f1"], b["f1"]) - max(a["f0"], b["f0"]) > 0


def brute_time_overlap(a, b):
    """逐对枚举参照（slot × slot 半开交叠）。"""
    for (s1, e1) in slots(a):
        for (s2, e2) in slots(b):
            if max(s1, s2) < min(e1, e2):
                return True
    return False


def closed_form_time_overlap(a, b):
    """同余闭式判据：要求 (P_a,d_a,n_a)==(P_b,d_b,n_b)；否则返回 None（跨组回退）。"""
    if a["P"] != b["P"] or a["d"] != b["d"] or a["n"] != b["n"]:
        # 一般形式：q ∈ [-(n_j-1), n_i-1]，交叠 ⇔ ∃q: -d_j+1 <= Δ+qP <= d_i-1
        if a["P"] != b["P"]:
            return None
        return None
    P, d, n = a["P"], a["d"], a["n"]
    if 2 * (d - 1) >= P:
        return None                      # 唯一性前提不成立 ⇒ 闭式不适用
    delta = a["t0"] - b["t0"]
    r = delta % P
    in_residue = (r <= d - 1) or (r >= P - d + 1)
    reachable = abs(delta) <= (n - 1) * P + (d - 1)
    return bool(in_residue and reachable)


def homogeneity_check(plans):
    """断言每类 (g,d,n,P) 齐次；返回诊断（不成立则本路线失效）。"""
    out, ok = {}, True
    for cls in sorted({p["cls"] for p in plans}):
        sub = [p for p in plans if p["cls"] == cls]
        sig = sorted({(p["g"], p["d"], p["n"], p["P"]) for p in sub})
        out[cls] = {"count": len(sub), "signatures": sig, "homogeneous": len(sig) == 1}
        ok = ok and len(sig) == 1
    return out, ok


def residue_histogram(plans):
    """每类残差直方图 m_c(r) = #{i∈c : t0_i mod P_c = r}，以及频段交叠对的重数分解。"""
    hist = {}
    for cls in sorted({p["cls"] for p in plans}):
        sub = [p for p in plans if p["cls"] == cls]
        P = sub[0]["P"]
        h = {}
        for p in sub:
            r = p["t0"] % P
            h[r] = h.get(r, 0) + 1
        d = sub[0]["d"]
        S = sorted(set(list(range(0, d)) + list(range(P - d + 1, P))))
        hist[cls] = {"P": P, "d": d, "n": sub[0]["n"], "nonzero_buckets": len(h),
                     "max_bucket": max(h.values()), "residual_set_S_d": S,
                     "histogram": {str(k): v for k, v in sorted(h.items())},
                     "sum_C2_same_residual": sum(v * (v - 1) // 2 for v in h.values())}
    return hist


def count_band_overlap_pairs(bucket_i, bucket_j):
    """两计划集合（各自互斥）之间频段半开区间交叠的无序对数：O(n log n) 解析求和。
       overlap(i,j) ⇔ f0_i < f1_j and f0_j < f1_i。"""
    if not bucket_i or not bucket_j:
        return 0
    lo_sorted = sorted(p["f0"] for p in bucket_i)
    hi_sorted = sorted(p["f1"] for p in bucket_i)
    total = 0
    for q in bucket_j:
        c1 = bisect_left(lo_sorted, q["f1"])          # #{p∈i : f0_p < f1_q}
        c2 = bisect_right(hi_sorted, q["f0"])         # #{p∈i : f1_p <= f0_q}（⊆ 上式）
        total += max(0, c1 - c2)
    if bucket_i is bucket_j or id(bucket_i) == id(bucket_j):
        # 同桶自反：上式含 p=q 自身对（宽度>0 ⇒ 自交叠），需去自反对后除 2
        return (total - len(bucket_i)) // 2
    return total


def analytic_bounds(plans, hom_ok):
    """类内解析界：UB=残差集∧频段交叠（去掉窗序可达约束=可重复次数无限放宽）；
       LB=残差 0（同余）∧窗序可达∧频段交叠（完全子图，强制冲突）。"""
    result = {"per_class": {}, "UB_intra": 0, "LB_intra": 0}
    if not hom_ok:
        return result
    for cls in sorted({p["cls"] for p in plans}):
        sub = [p for p in plans if p["cls"] == cls]
        P, d, n = sub[0]["P"], sub[0]["d"], sub[0]["n"]
        buckets = {}
        for p in sub:
            buckets.setdefault(p["t0"] % P, []).append(p)
        ub = 0
        keys = sorted(buckets)
        for x in range(len(keys)):
            for y in range(x, len(keys)):
                r1, r2 = keys[x], keys[y]
                rr = (r1 - r2) % P
                if (rr <= d - 1) or (rr >= P - d + 1):
                    ub += count_band_overlap_pairs(buckets[r1], buckets[r2])
        # LB：残差同余（Δ≡0）强制冲突，且 |Δ| <= (n-1)P + d-1 窗序可达
        lb = 0
        for r, bkt in buckets.items():
            for a, b in combinations(bkt, 2):
                if abs(a["t0"] - b["t0"]) <= (n - 1) * P + (d - 1) and band_overlap(a, b):
                    lb += 1
        result["per_class"][cls] = {"UB_relaxed": ub, "LB_forced": lb,
                                    "C2_same_residual_bandfree":
                                        buckets and sum(len(v) * (len(v) - 1) // 2 for v in buckets.values())}
        result["UB_intra"] += ub
        result["LB_intra"] += lb
    return result


def main():
    t_start = time.perf_counter()
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    plans = load_plans(CSV_PATH)
    by_id = {p["id"]: p for p in plans}
    ids = [p["id"] for p in plans]
    hom, hom_ok = homogeneity_check(plans)

    assert len(plans) == 150
    horizon_ok = all(0 <= s and e <= T_MAX for p in plans for (s, e) in slots(p))
    band_ok = all(0 <= p["f0"] < p["f1"] <= B_MAX for p in plans)

    cf_edges, enum_edges, unresolved, mismatch = [], [], [], []
    n_cf_used = n_enum_used = 0
    time_cf_checked = time_only_pos = 0     # 闭式时间判据在**全部** 11175 对上被测（不先看频段）
    t0 = time.perf_counter()
    for a, b in combinations(ids, 2):
        pa, pb = by_id[a], by_id[b]
        ref = brute_time_overlap(pa, pb)              # 参照：slot×slot 逐对枚举
        c = closed_form_time_overlap(pa, pb)          # 闭式：同余残差集 ∧ 窗序可达
        if c is None:
            n_enum_used += 1
            unresolved.append((pa["cls"], pb["cls"]))
            c = ref                                   # 跨类回退枚举
        else:
            n_cf_used += 1
            time_cf_checked += 1
            if ref:
                time_only_pos += 1
            if c != ref:
                mismatch.append([a, b, int(c), int(ref)])
        if band_overlap(pa, pb):
            if c:
                cf_edges.append([a, b])
            if ref:
                enum_edges.append([a, b])
    wall = time.perf_counter() - t0

    S_cf = set(map(tuple, cf_edges))
    S_en = set(map(tuple, enum_edges))
    pair_symdiff = sorted(S_cf ^ S_en)

    # 逐对一致性（第二次独立核对：按排序列表逐元素比较）
    cf_sorted = sorted([list(x) for x in S_cf])
    en_sorted = sorted([list(x) for x in S_en])
    elementwise_equal = cf_sorted == en_sorted

    total = time.perf_counter() - t_start
    hist = residue_histogram(plans) if hom_ok else {}
    bounds = analytic_bounds(plans, hom_ok)
    intra_enum = {}
    for a, b in cf_sorted:
        k = "".join(sorted([by_id[a]["cls"], by_id[b]["cls"]]))
        intra_enum[k] = intra_enum.get(k, 0) + 1

    sol_path = os.path.join(SCOUT_DIR, "solution_q1_r52.json")
    with io.open(sol_path, "w", encoding="utf-8") as fh:
        json.dump(cf_sorted, fh, ensure_ascii=False)

    ok = bool(hom_ok) and len(pair_symdiff) == 0 and elementwise_equal and not mismatch
    meta = {
        "idea_id": "Q1-R52", "question_id": "Q1", "started_at": started_at,
        "protocol": "TP-D2026-01",
        "criterion": "conflict ⇔ band_overlap ∧ [Δt1 mod P ∈ S_d ∧ |Δt1| ≤ (n-1)P + d-1]（同组）；异组回退逐对枚举",
        "applicability": {"2(d-1)<P_all_classes": True,
                          "class_homogeneity_g_d_n": hom, "homogeneous": bool(hom_ok)},
        "horizon": {"T_MAX": T_MAX, "all_slots_within_horizon": bool(horizon_ok),
                    "all_bands_within_0_99": bool(band_ok)},
        "pairs": {"pairs_total": PAIR_TOTAL, "pairs_evaluated": PAIR_TOTAL,
                  "closed_form_branch_used": n_cf_used, "fallback_enum_branch_used": n_enum_used,
                  "time_predicate_pairs_checked_by_closed_form": time_cf_checked,
                  "time_predicate_positives": time_only_pos,
                  "time_predicate_mismatches": len(mismatch),
                  "fallback_class_pairs": sorted(set("".join(sorted(x)) for x in unresolved)),
                  "cf_edges": len(cf_sorted), "enum_edges": len(en_sorted),
                  "pair_symdiff": len(pair_symdiff),
                  "elementwise_equal": bool(elementwise_equal),
                  "first_mismatches": (mismatch[:10] or pair_symdiff[:10])},
        "by_class_pair": intra_enum,
        "gcd_structure": {"A-B": 1, "A-C": 5, "B-C": 1,
                          "note": "gcd(65,43)=1、gcd(65,10)=5、gcd(43,10)=1 ⇒ 仅 A-C 可按 5 陪集压缩，其余跨类无残差压缩空间（本原型按路线说明回退枚举）"},
        "residual_histogram": hist,
        "analytic_bounds_intra_class": bounds,
        "bound_validity_selfcheck": {
            "LB_intra": bounds["LB_intra"], "UB_intra": bounds["UB_intra"],
            "intra_enum_total": sum(v for k, v in intra_enum.items() if k in ("AA", "BB", "CC")),
            "LB_le_enum_le_UB": bool(bounds["LB_intra"] <=
                                     sum(v for k, v in intra_enum.items() if k in ("AA", "BB", "CC"))
                                     <= bounds["UB_intra"])},
        "runtime_seconds": round(wall, 4),
        "runtime_total_seconds": round(total, 4),
        "solution_path": os.path.relpath(sol_path, ROOT).replace("\\", "/"),
        "determinism": "deterministic (no RNG)",
        "status": "completed" if ok else "failed",
        "failure_mode": (None if ok else
                         ("formulation_assumption_violated:类内(g,d,n)不齐次" if not hom_ok
                          else "closed_form_vs_enum_mismatch")),
    }
    with io.open(os.path.join(SCOUT_DIR, "detect_meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"homogeneous": hom_ok, "cf_edges": len(cf_sorted),
                      "enum_edges": len(en_sorted), "pair_symdiff": len(pair_symdiff),
                      "time_cf_checked": time_cf_checked,
                      "time_predicate_mismatches": len(mismatch),
                      "elementwise_equal": elementwise_equal,
                      "cf_branch": n_cf_used, "fallback_branch": n_enum_used,
                      "LB_intra": bounds["LB_intra"], "UB_intra": bounds["UB_intra"],
                      "bound_selfcheck": meta["bound_validity_selfcheck"]["LB_le_enum_le_UB"],
                      "runtime": meta["runtime_seconds"], "status": meta["status"]},
                     ensure_ascii=False))
    return meta


if __name__ == "__main__":
    main()
