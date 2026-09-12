# -*- coding: utf-8 -*-
"""Q1-R41 原型（Prototype Engineer / D 题竞争搜索 Q1 组）
路线：100×643 时频位图 + 倒排 join + 植入式随机压力测试（simulation，CH-04 Q1-R41）

表示层：每个计划 = 一组「矩形占用块」(f0,f1,s,e)（半开，频段 × 时间），由 F-005 周期展开得到；
冲突判据（F-006 + ADJUDICATION R7）⇔ 存在一个 (band,time) 单元被两个计划同时占用。

阶段A（完全确定性）：
  D1 = 倒排索引 join：cell=(t,f) → 计划列表，同格计划对取并集（主检测器）
  D2 = 位并行 AND：每计划一个 64300-bit 大整数，对全部 C(150,2)=11175 对做 AND（全查）
  D3 = 区间算术 oracle：逐对矩形-矩形双轴交叠判定（表示层与 D1/D2 独立；另附频段窗口剪枝版）
  三法边集对称差必须为 0；另有半开端点/末格边界用例，以及「把 g 当周期」错误口径诊断
  （ADJUDICATION R1 记 237 对，本原型不使用）。

阶段B（植入式随机压力测试，冻结种子集 [11,29,47]，共 1000 次扰动）：
  每次随机注入或删除一个「小占用块」（宽≤3 × 时长≤2 的矩形），随后：
   (a) 植入召回：注入块落在目标计划占用内 ⇒ 该对必须被检出；删除使共占格整体移除 ⇒ 该对必须消失；
   (b) 逐对核验：对被扰动计划的 149 个计划对，用 D3 区间算术给出期望边集，与增量倒排索引
       输出比对 → 同时检验漏检（召回）与伪阳性；
   (c) 全局核验：每 50 轮对全部 11175 对做一次区间算术全查并与倒排 join 比对，对称差必须为 0。
  按种子分别报告召回与 symdiff（replicate_values）。

口径（ADJUDICATION.json）：T_MAX=643、B_MAX=100、半开区间 [a,b)。
本脚本只写本 scout 目录（solution / detect_meta），不写 results/、figures/、paper/。
"""
import io
import json
import os
import random
import time
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
SCOUT_DIR = os.path.abspath(os.path.join(HERE, ".."))
RUN_DIR = os.path.abspath(os.path.join(SCOUT_DIR, "..", ".."))
ROOT = os.path.abspath(os.path.join(RUN_DIR, "..", "..", ".."))

CSV_PATH = os.path.join(ROOT, "data", "canonical_plans.csv")
T_MAX, B_MAX = 643, 100
SEEDS = [11, 29, 47]        # 协议冻结种子集
TRIALS_TOTAL = 1000        # 任务冻结：注入/删除合计 1000 次
GLOBAL_CHECK_EVERY = 50


# ---------------------------------------------------------------- 数据装载
def load_plans(path):
    plans = []
    for line in io.open(path, encoding="utf-8").read().splitlines()[1:]:
        a = line.split(",")
        f0, f1, t0, t1, g, n = (int(a[2]), int(a[3]), int(a[4]),
                                int(a[5]), int(a[6]), int(a[7]))
        d = t1 - t0
        rects = [(f0, f1, t0 + k * (g + d), t0 + k * (g + d) + d) for k in range(n)]
        plans.append(dict(id=a[0], cls=a[1], f0=f0, f1=f1, t0=t0, g=g, n=n, d=d, rects=rects))
    assert len(plans) == 150
    return plans


def cells_of(rects):
    """矩形集合 → 占用单元（distinct，cell = t*100 + f；半开，视界内裁剪）。"""
    out = set()
    for (f0, f1, s, e) in rects:
        lo_f, hi_f = max(0, f0), min(B_MAX, f1)
        if lo_f >= hi_f:
            continue
        for t in range(max(0, s), min(T_MAX, e)):
            base = t * B_MAX
            for f in range(lo_f, hi_f):
                out.add(base + f)
    return out


# ---------------------------------------------------------------- 检测器 D1：倒排 join
def detect_inverted_join(rects_by_plan):
    inv = {}
    for pid, rects in rects_by_plan.items():
        for c in cells_of(rects):
            inv.setdefault(c, []).append(pid)
    edges = set()
    max_share = 1
    for lst in inv.values():
        if len(lst) > 1:
            s = sorted(set(lst))
            max_share = max(max_share, len(s))
            for x in range(len(s)):
                for y in range(x + 1, len(s)):
                    edges.add((s[x], s[y]))
    return edges, len(inv), max_share


class InvIndex:
    """可增删的倒排索引（压力测试用的增量位图/倒排侧检测器）。"""

    def __init__(self, rects_by_plan):
        self.inv = {}
        self.cells = {}
        for pid, rects in rects_by_plan.items():
            self.set_plan(pid, rects)

    def set_plan(self, pid, rects):
        new = cells_of(rects)
        old = self.cells.get(pid, set())
        for c in old - new:
            lst = self.inv[c]
            lst.remove(pid)
            if not lst:
                del self.inv[c]
        for c in new - old:
            self.inv.setdefault(c, []).append(pid)
        self.cells[pid] = new

    def partners(self, pid):
        out = set()
        for c in self.cells.get(pid, ()):
            for q in self.inv[c]:
                if q != pid:
                    out.add(q)
        return out

    def edges(self):
        e = set()
        for lst in self.inv.values():
            if len(lst) > 1:
                s = sorted(lst)
                for x in range(len(s)):
                    for y in range(x + 1, len(s)):
                        e.add((s[x], s[y]))
        return e


# ---------------------------------------------------------------- 检测器 D2：位并行 AND
def detect_bitand_fullscan(rects_by_plan):
    bits = {}
    for pid, rects in rects_by_plan.items():
        b = 0
        for c in cells_of(rects):
            b |= (1 << c)
        bits[pid] = b
    ids = sorted(bits)
    edges, scanned = set(), 0
    for a, b in combinations(ids, 2):
        scanned += 1
        if bits[a] & bits[b]:
            edges.add((a, b))
    return edges, scanned


# ---------------------------------------------------------------- 检测器 D3：区间算术
def rects_hit(ra, rb):
    for (f0a, f1a, s0a, e0a) in ra:
        for (f0b, f1b, s0b, e0b) in rb:
            if min(f1a, f1b) > max(f0a, f0b) and min(e0a, e0b) > max(s0a, s0b):
                return True
    return False


def band_spans(rects_by_plan):
    return {pid: (min(r[0] for r in rs), max(r[1] for r in rs))
            for pid, rs in rects_by_plan.items()}


def band_candidates(spans):
    ids = sorted(spans)
    return [(a, b) for a, b in combinations(ids, 2)
            if min(spans[a][1], spans[b][1]) > max(spans[a][0], spans[b][0])]


def detect_interval_oracle(rects_by_plan, candidate_pairs=None):
    if candidate_pairs is None:
        candidate_pairs = list(combinations(sorted(rects_by_plan), 2))
    edges = set()
    for (a, b) in candidate_pairs:
        if rects_hit(rects_by_plan[a], rects_by_plan[b]):
            edges.add((a, b))
    return edges


# ---------------------------------------------------------------- 矩形代数
def rect_contains_cell(rect, cell):
    f0, f1, s, e = rect
    t, f = divmod(cell, B_MAX)
    return f0 <= f < f1 and s <= t < e


def subtract_block(rects, block):
    """从 rects 挖掉矩形 block=(bf0,bf1,bt0,bt1)（半开）→ 至多 4 个子矩形。"""
    bf0, bf1, bt0, bt1 = block
    out = []
    for (f0, f1, s, e) in rects:
        if f1 <= bf0 or f0 >= bf1 or e <= bt0 or s >= bt1:
            out.append((f0, f1, s, e))
            continue
        if f0 < bf0:
            out.append((f0, bf0, s, e))
        if bf1 < f1:
            out.append((bf1, f1, s, e))
        lo, hi = max(f0, bf0), min(f1, bf1)
        if s < bt0:
            out.append((lo, hi, s, bt0))
        if bt1 < e:
            out.append((lo, hi, bt1, e))
    return [r for r in out if r[0] < r[1] and r[2] < r[3]]


# ---------------------------------------------------------------- 边界用例
def boundary_cases():
    cases = []
    cases.append(("band_[80,90)x[90,95)_no_hit", rects_hit([(80, 90, 0, 5)], [(90, 95, 0, 5)]), False))
    cases.append(("time_[40,45)x[45,50)_no_hit", rects_hit([(10, 20, 40, 45)], [(10, 20, 45, 50)]), False))
    cases.append(("time_[40,45)x[44,50)_hit", rects_hit([(10, 20, 40, 45)], [(10, 20, 44, 50)]), True))
    cases.append(("band_[80,90)x[89,95)_hit", rects_hit([(80, 90, 0, 5)], [(89, 95, 0, 5)]), True))
    cases.append(("last_cell_t642_reachable", (642 * 100 + 10) in cells_of([(10, 11, 642, 643)]), True))
    cases.append(("cell_t643_clipped_away",
                  (643 * 100 + 10) not in cells_of([(10, 11, 642, 645)]), True))
    cases.append(("subtract_block_splits_correctly",
                  set(subtract_block([(0, 3, 10, 12)], (1, 2, 11, 12)))
                  == {(0, 1, 10, 12), (2, 3, 10, 12), (1, 2, 10, 11)}, True))
    cases.append(("empty_intersection_deletes_nothing",
                  subtract_block([(0, 3, 10, 12)], (5, 6, 10, 11)) == [(0, 3, 10, 12)], True))
    return [(n, int(bool(v)), int(x), bool(v) == x) for n, v, x in cases]


# ---------------------------------------------------------------- 阶段B
def local_expected(rects, spans, p, ids):
    """区间算术 oracle 给出与计划 p 相关的全部冲突对（149 对；频段窗口剪枝可证完备）。"""
    out = set()
    rp, sp = rects[p], spans[p]
    for q in ids:
        if q == p:
            continue
        if min(sp[1], spans[q][1]) <= max(sp[0], spans[q][0]):
            continue
        if rects_hit(rp, rects[q]):
            out.add(tuple(sorted((p, q))))
    return out


def stress(plans, rng, budget):
    ids = sorted(plans)
    rects = {i: list(plans[i]["rects"]) for i in ids}
    spans = band_spans(rects)
    idx = InvIndex(rects)
    st = dict(trials=0, injected=0, deleted=0, skipped=0, planted_hit=0, planted_miss=0,
              planted_new_edges=0,
              vanish_ok=0, vanish_fail=0, pair_checks=0, pair_miss=0, pair_fp=0,
              global_checks=0, global_symdiff=0, injected_cells=0, deleted_cells=0,
              deleted_blocks=0)
    for it in range(budget):
        mode = "inject" if it % 2 == 0 else "delete"
        p = ids[rng.randrange(len(ids))]
        acted = False
        if mode == "inject":
            tgt = ids[rng.randrange(len(ids))]
            if tgt != p and rects[tgt]:
                (tf0, tf1, ts, te) = rects[tgt][rng.randrange(len(rects[tgt]))]
                bf1 = min(tf1, tf0 + rng.randint(1, 3))
                bt1 = min(te, ts + rng.randint(1, 2))
                if bf1 > tf0 and bt1 > ts:
                    block = (tf0, bf1, ts, bt1)
                    pre = local_expected(rects, spans, p, ids)
                    rects[p] = rects[p] + [block]
                    spans[p] = (min(spans[p][0], block[0]), max(spans[p][1], block[1]))
                    idx.set_plan(p, rects[p])
                    post = local_expected(rects, spans, p, ids)
                    planted = tuple(sorted((p, tgt)))
                    join_post = {tuple(sorted((p, x))) for x in idx.partners(p)}
                    st["injected"] += 1
                    st["injected_cells"] += (bf1 - tf0) * (bt1 - ts)
                    # 植入真值：注入块整体落在 tgt 的占用内 ⇒ (p,tgt) 必为冲突
                    if planted in post and planted in join_post:
                        st["planted_hit"] += 1
                    else:
                        st["planted_miss"] += 1
                    if planted not in pre:
                        st["planted_new_edges"] += 1
                    acted = True
        if not acted and mode == "delete":
            shared_plans = sorted({pid for lst in idx.inv.values() if len(lst) > 1 for pid in lst})
            for _try in range(30):
                if not shared_plans:
                    break
                p = shared_plans[rng.randrange(len(shared_plans))]
                cand = sorted(idx.partners(p))
                if not cand:
                    continue
                q = cand[rng.randrange(len(cand))]
                if q == p or not rects[p]:
                    continue
                inter = idx.cells[p] & idx.cells.get(q, set())
                if not inter:
                    continue
                # 把共占格按其所属的 p 矩形分组，逐组挖除其外接小矩形
                # （⇒ 该对的全部共占格被清空 ⇒ 植入断言：该对必须消失）
                groups = {}
                for c in sorted(inter):
                    for ri, r in enumerate(rects[p]):
                        if rect_contains_cell(r, c):
                            groups.setdefault(ri, []).append(c)
                            break
                    else:
                        groups = None
                        break
                if not groups:
                    continue
                blocks = []
                for cs in groups.values():
                    blocks.append((min(x % B_MAX for x in cs), max(x % B_MAX for x in cs) + 1,
                                   min(x // B_MAX for x in cs), max(x // B_MAX for x in cs) + 1))
                pre = local_expected(rects, spans, p, ids)
                pre_join = {tuple(sorted((p, x))) for x in idx.partners(p)}
                for blk in blocks:
                    rects[p] = subtract_block(rects[p], blk)
                spans[p] = ((min(r[0] for r in rects[p]), max(r[1] for r in rects[p]))
                            if rects[p] else (0, 0))
                idx.set_plan(p, rects[p])
                post = local_expected(rects, spans, p, ids)
                post_join = {tuple(sorted((p, x))) for x in idx.partners(p)}
                vanish = tuple(sorted((p, q)))
                st["deleted"] += 1
                st["deleted_blocks"] += len(blocks)
                st["deleted_cells"] += len(inter)
                # 植入真值：两计划的全部共占格都被挖掉 ⇒ 该对必须从两实现同时消失
                if vanish in pre and vanish in pre_join \
                        and vanish not in post and vanish not in post_join:
                    st["vanish_ok"] += 1
                else:
                    st["vanish_fail"] += 1
                acted = True
                break
        if not acted:
            st["skipped"] += 1
            continue
        st["trials"] += 1
        # (b) 逐对核验：倒排 join 侧输出 vs 区间算术期望
        got_p = {tuple(sorted((p, q))) for q in idx.partners(p)}
        want_p = local_expected(rects, spans, p, ids)
        st["pair_checks"] += len(want_p | got_p)
        st["pair_miss"] += len(want_p - got_p)
        st["pair_fp"] += len(got_p - want_p)
        # (c) 全局核验
        if (it + 1) % GLOBAL_CHECK_EVERY == 0:
            d1 = idx.edges()
            d3 = detect_interval_oracle(rects, band_candidates(spans))
            st["global_checks"] += 1
            st["global_symdiff"] += len(d1 ^ d3)
    st.pop("last_expect", None)
    return st


# ---------------------------------------------------------------- 主流程
def main():
    t_start = time.perf_counter()
    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    plist = load_plans(CSV_PATH)
    plans = {p["id"]: p for p in plist}
    rects0 = {p: list(v["rects"]) for p, v in plans.items()}
    horizon_ok = all(0 <= s and e <= T_MAX and 0 <= f0 < f1 <= B_MAX
                     for v in plans.values() for (f0, f1, s, e) in v["rects"])

    tA = time.perf_counter()
    E1, distinct_cells, max_share = detect_inverted_join(rects0)
    t_join = time.perf_counter() - tA
    tA = time.perf_counter()
    E2, scanned = detect_bitand_fullscan(rects0)
    t_bit = time.perf_counter() - tA
    tA = time.perf_counter()
    spans0 = band_spans(rects0)
    cands = band_candidates(spans0)
    E3 = detect_interval_oracle(rects0, cands)
    E3_full = detect_interval_oracle(rects0)
    t_or = time.perf_counter() - tA
    sd12, sd13, sd13f = len(E1 ^ E2), len(E1 ^ E3), len(E1 ^ E3_full)
    incidence = sum(len(cells_of(v)) for v in rects0.values())

    bc = boundary_cases()
    bc_fail = [c for c in bc if not c[3]]

    wrong_rects = {pid: [(v["f0"], v["f1"], v["t0"] + k * v["g"], v["t0"] + k * v["g"] + v["d"])
                         for k in range(v["n"])] for pid, v in plans.items()}
    n_wrong = len(detect_interval_oracle(wrong_rects))

    tS = time.perf_counter()
    alloc = [TRIALS_TOTAL // len(SEEDS)] * len(SEEDS)
    alloc[0] += TRIALS_TOTAL - sum(alloc)
    per_seed = {}
    for sd_, nb in zip(SEEDS, alloc):
        per_seed[str(sd_)] = stress(plans, random.Random(sd_), nb)
    t_stress = time.perf_counter() - tS
    agg = {k: sum(s[k] for s in per_seed.values())
           for k in ["trials", "injected", "deleted", "skipped", "planted_hit", "planted_miss",
                     "planted_new_edges",
                     "vanish_ok", "vanish_fail", "pair_checks", "pair_miss", "pair_fp",
                     "global_checks", "global_symdiff", "injected_cells", "deleted_cells",
                     "deleted_blocks"]}
    recall_inj = agg["planted_hit"] / max(1, agg["injected"])
    recall_del = agg["vanish_ok"] / max(1, agg["deleted"])
    stress_pass = (agg["planted_miss"] == 0 and agg["vanish_fail"] == 0
                   and agg["pair_miss"] == 0 and agg["pair_fp"] == 0
                   and agg["global_symdiff"] == 0 and agg["trials"] >= 900)
    phaseA_pass = (sd12 == 0 and sd13 == 0 and sd13f == 0 and len(E1) == 297
                   and not bc_fail and horizon_ok)
    ok = bool(phaseA_pass and stress_pass)

    edges_sorted = sorted([list(x) for x in E1])
    sol_path = os.path.join(SCOUT_DIR, "solution_q1_r41.json")
    with io.open(sol_path, "w", encoding="utf-8") as fh:
        json.dump(edges_sorted, fh, ensure_ascii=False)

    strata = {}
    for a, b in edges_sorted:
        k = "".join(sorted([plans[a]["cls"], plans[b]["cls"]]))
        strata[k] = strata.get(k, 0) + 1
    touched = set()
    for a, b in edges_sorted:
        touched |= {a, b}

    total = time.perf_counter() - t_start
    meta = {
        "idea_id": "Q1-R41", "question_id": "Q1", "started_at": started_at,
        "protocol": "TP-D2026-01",
        "horizon": {"T_MAX": T_MAX, "B_MAX": B_MAX, "half_open": True,
                    "all_cells_within_horizon": bool(horizon_ok),
                    "cells_total": T_MAX * B_MAX, "incidence_sum": incidence,
                    "distinct_cells": distinct_cells, "max_shared_per_cell": max_share,
                    "wrong_g_as_period_pairs_diagnostic": n_wrong},
        "phaseA": {"pairs_total": 11175, "pairs_evaluated_bitand": scanned,
                   "pairs_evaluated_oracle_band_pruned": len(cands),
                   "edges_D1_inverted_join": len(E1), "edges_D2_bitand_fullscan": len(E2),
                   "edges_D3_oracle_pruned": len(E3), "edges_D3_oracle_fullscan": len(E3_full),
                   "symdiff_D1_D2": sd12, "symdiff_D1_D3_pruned": sd13,
                   "symdiff_D1_D3_full": sd13f,
                   "by_class_pair": strata, "plans_touched": len(touched),
                   "runtime_join_s": round(t_join, 4), "runtime_bitand_s": round(t_bit, 4),
                   "runtime_oracle_s": round(t_or, 4)},
        "boundary_cases": bc,
        "boundary_case_failures": [list(map(str, f)) for f in bc_fail],
        "phaseB_stress": {"seed_set": SEEDS, "trials_requested": TRIALS_TOTAL,
                          "trials_completed": agg["trials"], "injections": agg["injected"],
                          "deletions": agg["deleted"], "skipped_setup": agg["skipped"],
                          "injection_recall": round(recall_inj, 6),
                          "deletion_vanish_recall": round(recall_del, 6),
                          "planted_missed": agg["planted_miss"],
                          "vanish_fail": agg["vanish_fail"],
                          "pair_level_checks": agg["pair_checks"],
                          "pair_level_missing": agg["pair_miss"],
                          "pair_level_false_positive": agg["pair_fp"],
                          "global_fullscans": agg["global_checks"],
                          "global_symdiff": agg["global_symdiff"],
                          "cells_injected": agg["injected_cells"],
                          "cells_deleted": agg["deleted_cells"],
                          "runtime_seconds": round(t_stress, 4),
                          "per_seed": {k: {kk: vv for kk, vv in v.items()}
                                       for k, v in per_seed.items()}},
        "conflict_pairs": len(edges_sorted),
        "runtime_seconds": round(t_join + t_bit + t_or + t_stress, 4),
        "runtime_total_seconds": round(total, 4),
        "solution_path": os.path.relpath(sol_path, ROOT).replace("\\", "/"),
        "determinism": "阶段A 无随机；阶段B 使用冻结种子集 [11,29,47]（同码同种子逐位可复现）",
        "seed": "阶段A N/A；阶段B 冻结种子集 [11,29,47]，每种子独立 random.Random(seed)",
        "status": "completed" if ok else "failed",
        "failure_mode": (None if ok else
                         ("phaseA_three_impl_symdiff_nonzero" if not phaseA_pass else
                          "planted_recall_or_precision_failure")),
    }
    with io.open(os.path.join(SCOUT_DIR, "detect_meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"edges": len(E1), "sd_D1_D2": sd12, "sd_D1_D3_pruned": sd13,
                      "sd_D1_D3_full": sd13f, "wrong_period_diag": n_wrong,
                      "by_class_pair": strata, "trials": agg["trials"],
                      "inj": agg["injected"], "del": agg["deleted"], "skip": agg["skipped"],
                      "inj_recall": round(recall_inj, 4), "del_recall": round(recall_del, 4),
                      "pair_miss": agg["pair_miss"], "pair_fp": agg["pair_fp"],
                      "global_symdiff": agg["global_symdiff"],
                      "phaseA_pass": phaseA_pass, "stress_pass": stress_pass,
                      "runtime": meta["runtime_seconds"], "status": meta["status"]},
                     ensure_ascii=False))
    return meta


if __name__ == "__main__":
    main()
