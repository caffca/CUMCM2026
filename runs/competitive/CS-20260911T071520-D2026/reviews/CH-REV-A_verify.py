# -*- coding: utf-8 -*-
"""CH-REV-A 独立复核（只读）。
1) Q1：双独立实现重算 297 真值边集；核对三候选 solution 文件 SHA / symdiff=0 声明。
2) Q2：对 R51/R32/R41(3seeds) 独立重算 合规 + 全量残留冲突 + 四级目标元组；
   抽样 20 计划对用第二实现（纯区间法）复算冲突（攻击 evaluation_unfair/bound_invalid）。
3) Q2-R51 star_edges.json：对全部 11175 对独立重算「动作组合级冲突表」，
   与磁盘 G* 做双向精确比对（配对集合 + 每对组合索引集合），并核对 297 原边 ⊆ G*。
4) 用冻结 canonical_evaluator 原样复跑（stdout，不落盘），核对磁盘 eval.json 未被篡改。
5) 621/643、distinct/multiplicity 口径出现位置扫描。
只写 reviews/ 下的报告文本；不改动任何被审文件。
"""
import hashlib
import io
import json
import os
import random
import re
import subprocess
import sys
import time
from itertools import combinations

ROOT = r"F:\2026 数模\D题重跑\D题\runs\competitive\CS-20260911T071520-D2026"
WS = os.path.abspath(os.path.join(ROOT, "..", "..", ".."))
T_MAX = 643
B_MAX = 100
DF_LIM, DT_LIM = 10, 5
PRIO = {"A": 100, "B": 10, "C": 1}
OUT = []


def log(s=""):
    OUT.append(str(s))


def J(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


# ---------------- 数据（独立来源：common_input 紧凑表） ----------------
ci = json.loads(io.open(os.path.join(ROOT, "common_input.json"), encoding="utf-8").read())
compact = {r[0]: r for r in ci["plans_table_compact"]}
plans = {}
for pid, r in compact.items():
    plans[pid] = dict(id=pid, cls=pid[0], f0=r[1], f1=r[2], t0=r[3], t1=r[4],
                      g=r[5], n=r[6], d=r[4] - r[3])
assert len(plans) == 150

# 与 CSV（evaluator 数据源）交叉核对
csv = os.path.join(WS, "data", "canonical_plans.csv")
csv_txt = io.open(csv, encoding="utf-8").read().splitlines()
csv_bad = 0
for line in csv_txt[1:]:
    a = line.split(",")
    p = plans[a[0]]
    if [int(a[2]), int(a[3]), int(a[4]), int(a[5]), int(a[6]), int(a[7])] != \
       [p["f0"], p["f1"], p["t0"], p["t1"], p["g"], p["n"]]:
        csv_bad += 1
log("data: common_input.compact vs canonical_plans.csv mismatches = %d" % csv_bad)

IDS = sorted(plans)


def slots(p, dt=0):
    P = p["g"] + p["d"]
    return [(p["t0"] + dt + k * P, p["t0"] + dt + k * P + p["d"]) for k in range(p["n"])]


def band_overlap(a, b):
    return min(a["f1"], b["f1"]) - max(a["f0"], b["f0"]) > 0


def mask_int(p, df=0, dt=0):
    f0, f1 = p["f0"] + df, p["f1"] + df
    if f0 < 0 or f1 > B_MAX:
        return None
    m = 0
    for (s, e) in slots(p, dt):
        if s < 0 or e > T_MAX:
            return None
        for t in range(s, e):
            base = t * B_MAX
            m |= ((1 << (f1 - f0)) - 1) << (base + f0)
    return m


# ---------------- Q1 真值：实现 M1（位图）与 M2（合并区间两指针） ----------------
t0_ = time.time()
bm = {i: mask_int(plans[i]) for i in IDS}
E_m1 = set()
for i, j in combinations(IDS, 2):
    if band_overlap(plans[i], plans[j]) and (bm[i] & bm[j]):
        E_m1.add((i, j))


def merged(p):
    iv = sorted(slots(p))
    out = []
    for s, e in iv:
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def sweep_hit(la, lb):
    x = y = 0
    while x < len(la) and y < len(lb):
        if max(la[x][0], lb[y][0]) < min(la[x][1], lb[y][1]):
            return True
        if la[x][1] <= lb[y][1]:
            x += 1
        else:
            y += 1
    return False


MG = {i: merged(plans[i]) for i in IDS}
E_m2 = set()
for i, j in combinations(IDS, 2):
    if band_overlap(plans[i], plans[j]) and sweep_hit(MG[i], MG[j]):
        E_m2.add((i, j))
strata = {}
for i, j in E_m1:
    k = "".join(sorted([plans[i]["cls"], plans[j]["cls"]]))
    strata[k] = strata.get(k, 0) + 1
touched = set()
for i, j in E_m1:
    touched.add(i)
    touched.add(j)
log("Q1 truth: |E_M1|=%d |E_M2|=%d symdiff(M1,M2)=%d strata=%s touched=%d  (%.1fs)"
    % (len(E_m1), len(E_m2), len(E_m1 ^ E_m2), J(strata), len(touched), time.time() - t0_))

# ---------------- Q1 三候选：SHA + symdiff ----------------
log("\n== Q1 candidates ==")
q1_files = {"Q1-R21": "scouts/Q1-R21/solution_q1_r21.json",
            "Q1-R52": "scouts/Q1-R52/solution_q1_r52.json",
            "Q1-R41": "scouts/Q1-R41/solution_q1_r41.json"}
q1_sets = {}
for idea, rel in q1_files.items():
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    sha = hashlib.sha256(io.open(p, "rb").read()).hexdigest()
    res = json.loads(io.open(os.path.join(ROOT, "scouts", idea, "result.json"), encoding="utf-8").read())
    sol = json.loads(io.open(p, encoding="utf-8").read())
    S = set(tuple(sorted(x)) for x in sol)
    q1_sets[idea] = S
    dup = len(sol) - len([tuple(x) for x in sol])
    log("%s: disk_sha=%s claimed_sha=%s sha_match=%s n_rows=%d n_unique=%d "
        "symdiff_vs_indep_truth=%d vs_eval_counts(truth=%d submitted=%d missing=%d spurious=%d)"
        % (idea, sha[:16] + "...", (res.get("solution_sha256") or "")[:16] + "...",
           sha == res.get("solution_sha256"), len(sol), len(S), len(S ^ E_m1),
           res["evaluator_counts"]["truth"], res["evaluator_counts"]["submitted"],
           res["evaluator_counts"]["missing"], res["evaluator_counts"]["spurious"]))
log("Q1 pairwise file equality: R21==R52 %s ; R21==R41 %s" %
    (q1_sets["Q1-R21"] == q1_sets["Q1-R52"], q1_sets["Q1-R21"] == q1_sets["Q1-R41"]))

# ---------------- Q2 独立复算 ----------------
log("\n== Q2 independent feasibility/objective ==")


def indep_eval_q2(sol_path):
    sol = json.loads(io.open(sol_path, encoding="utf-8").read())
    viol = []
    for pid, act in sol.items():
        if pid not in plans:
            viol.append("unknown_plan:%s" % pid)
            continue
        keys = [k for k, v in act.items() if v not in (None, False, 0)]
        if len(keys) != 1:
            viol.append("bad_shape:%s:%s" % (pid, J(act)))
            continue
        k = keys[0]
        if k not in ("df", "dt", "revoke"):
            viol.append("bad_key:%s:%s" % (pid, k))
            continue
        if k == "df" and (abs(int(act["df"])) > DF_LIM or int(act["df"]) == 0):
            viol.append("df_range:%s:%s" % (pid, act["df"]))
        if k == "dt" and (abs(int(act["dt"])) > DT_LIM or int(act["dt"]) == 0):
            viol.append("dt_range:%s:%s" % (pid, act["dt"]))
    masks = {}
    for pid in plans:
        act = sol.get(pid, {})
        if act.get("revoke"):
            continue
        df = int(act.get("df", 0))
        dt = int(act.get("dt", 0))
        m = mask_int(plans[pid], df, dt)
        if m is None:
            viol.append("out_of_resource:%s" % pid)
            continue
        masks[pid] = m
    residual = 0
    ks = sorted(masks)
    res_pairs = []
    for x in range(len(ks)):
        i = ks[x]
        for y in range(x + 1, len(ks)):
            j = ks[y]
            if band_overlap(plans[i], plans[j]) and (masks[i] & masks[j]):
                residual += 1
                res_pairs.append((i, j))
    rev = sum(1 for a in sol.values() if a.get("revoke"))
    adj = ploss = mag = 0
    for pid, act in sol.items():
        if not act.get("revoke"):
            ks2 = [k for k in ("df", "dt") if act.get(k)]
            if ks2:
                adj += 1
                ploss += PRIO[plans[pid]["cls"]]
                mag += sum(abs(int(act[k])) for k in ks2)
        else:
            ploss += PRIO[plans[pid]["cls"]] * 2
    tup = [rev, adj, ploss, mag]
    return tup, viol, residual, res_pairs, masks, ks


def _merge_pairs(iv):
    out = []
    for s, e in sorted(iv):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


Q2_FILES = {"Q2-R51": ["scouts/Q2-R51/solution_actions.json"],
            "Q2-R32": ["scouts/Q2-R32/solution_actions.json"],
            "Q2-R41": ["scouts/Q2-R41/solution_actions_seed11.json",
                       "scouts/Q2-R41/solution_actions_seed29.json",
                       "scouts/Q2-R41/solution_actions_seed47.json"]}
for idea, rels in Q2_FILES.items():
    for idx, rel in enumerate(rels):
        tag = ["eval.json", "eval_seed11.json", "eval_seed29.json", "eval_seed47.json"]
        if idea == "Q2-R41":
            evrel = "scouts/Q2-R41/eval_seed%s.json" % rel.split("seed")[-1].split(".")[0]
        else:
            evrel = "scouts/%s/eval.json" % idea
        ev = json.loads(io.open(os.path.join(ROOT, evrel.replace("/", os.sep)), encoding="utf-8").read())
        tup, viol, residual, res_pairs, masks, ks = indep_eval_q2(os.path.join(ROOT, rel.replace("/", os.sep)))
        rng = random.Random(20260911)
        # 20-pair second-implementation recheck (interval-only, incl. revoked plans)
        sol = json.loads(io.open(os.path.join(ROOT, rel.replace("/", os.sep)), encoding="utf-8").read())
        bad = 0
        checked = []
        tried = 0
        while tried < 20:
            i, j = rng.choice(IDS), rng.choice(IDS)
            if (i, j) in checked or i == j:
                continue
            if i > j:
                i, j = j, i
            tried += 1

            def eff(pid):
                a = sol.get(pid, {})
                if a.get("revoke"):
                    return None
                df, dt = int(a.get("df", 0)), int(a.get("dt", 0))
                return (df, dt)

            ei, ej = eff(i), eff(j)
            if ei is None or ej is None:
                hit_iv = False
            else:
                pi, pj = plans[i], plans[j]
                bi = (pi["f0"] + ei[0], pi["f1"] + ei[0])
                bj = (pj["f0"] + ej[0], pj["f1"] + ej[0])
                if min(bi[1], bj[1]) - max(bi[0], bj[0]) <= 0:
                    hit_iv = False
                else:
                    hit_iv = sweep_hit(_merge_pairs(slots(pi, ei[1])), _merge_pairs(slots(pj, ej[1])))
            mi = masks.get(i, 0)
            mj = masks.get(j, 0)
            hit_m = bool(mi & mj)
            checked.append((i, j))
            if hit_iv != hit_m:
                bad += 1
        sha = hashlib.sha256(io.open(os.path.join(ROOT, rel.replace("/", os.sep)), "rb").read()).hexdigest()
        res = json.loads(io.open(os.path.join(ROOT, "scouts", idea, "result.json"), encoding="utf-8").read())
        rel_tag = rel.split("/")[-1]
        if idea == "Q2-R41" and "seed11" not in rel:
            claimed_sha = None   # 仅 seed11 在 result.json 有 solution_sha256 声明位
        else:
            claimed_sha = res.get("solution_sha256")
        log("%s [%s]: indep_tuple=%s eval_tuple=%s match=%s | my_violations=%s | residual_pairs(full-recount)=%d | "
            "20-pair-interval-recheck mismatches=%d | disk_sha=%s claimed_sha_match=%s"
            % (idea, rel_tag, J(tup), J(ev["objective"]), J(tup) == J(ev["objective"]),
               J(viol[:5]) if viol else "[]", residual, bad, sha[:16] + "...",
               (sha == claimed_sha) if claimed_sha else "n/a(per-seed)"))

# ---------------- Star edges 双向精确复核 ----------------
log("\n== Q2-R51 star_edges.json full independent recount ==")
raw = json.loads(io.open(os.path.join(ROOT, "scouts/Q2-R51/star_edges.json"), encoding="utf-8").read())
star = {tuple(k.split("|")): set(map(tuple, v)) for k, v in raw["edges"].items()}


def enumerate_actions(p):
    acts = []
    if mask_int(p, 0, 0) is not None:
        acts.append(("keep", 0, 0))
    for v in list(range(-DF_LIM, 0)) + list(range(1, DF_LIM + 1)):
        if mask_int(p, df=v) is not None:
            acts.append(("df", v, 0))
    for v in list(range(-DT_LIM, 0)) + list(range(1, DT_LIM + 1)):
        if mask_int(p, dt=v) is not None:
            acts.append(("dt", 0, v))
    acts.append(("revoke", 0, 0))
    return acts


t0_ = time.time()
ACTS = {i: enumerate_actions(plans[i]) for i in IDS}
AMASK = {}
for i in IDS:
    for ai, (k, df, dt) in enumerate(ACTS[i]):
        if k != "revoke":
            AMASK[(i, ai)] = mask_int(plans[i], df, dt)
log("action table: total=%d min=%d max=%d ident_all=%s  (%.1fs)"
    % (sum(len(ACTS[i]) for i in IDS), min(len(ACTS[i]) for i in IDS),
       max(len(ACTS[i]) for i in IDS), all(ACTS[i][0][0] == "keep" for i in IDS), time.time() - t0_))

# 我的完整组合重算（组合数学法，不依赖掩码）
def conflict_combos(i, j):
    pi, pj = plans[i], plans[j]
    lo = pj["f0"] - pi["f1"] + 1
    hi = pj["f1"] - pi["f0"] - 1
    if lo > hi:
        return set()
    di, dj = pi["d"], pj["d"]
    Pi, Pj = pi["g"] + di, pj["g"] + dj
    tset = set()
    for k in range(pi["n"]):
        A = pi["t0"] + k * Pi
        for l in range(pj["n"]):
            c = pj["t0"] + l * Pj - A
            v0, v1 = max(-10, c - di + 1), min(10, c + dj - 1)
            for v in range(v0, v1 + 1):
                tset.add(v)
    if not tset:
        return set()
    Ai = [(ai, a) for ai, a in enumerate(ACTS[i]) if a[0] != "revoke"]
    Aj = [(aj, a) for aj, a in enumerate(ACTS[j]) if a[0] != "revoke"]
    out = set()
    for ai, a in Ai:
        for aj, b in Aj:
            if lo <= a[1] - b[1] <= hi and (a[2] - b[2]) in tset:
                out.add((ai, aj))
    return out


t0_ = time.time()
my_edges = {}
for i, j in combinations(IDS, 2):
    cc = conflict_combos(i, j)
    if cc:
        my_edges[(i, j)] = cc
star_keys = set(star)
my_keys = set(my_edges)
pair_only_in_star = star_keys - my_keys
pair_only_in_mine = my_keys - star_keys
combo_mismatch = [(k, len(star[k] ^ my_edges[k])) for k in (star_keys & my_keys) if star[k] != my_edges[k]]
base297 = E_m1
base_covered = base297 <= star_keys
log("recount: my_edges=%d star_edges=%d only_in_star=%d only_in_mine=%d combo_set_mismatch_pairs=%d  (%.1fs)"
    % (len(my_edges), len(star), len(pair_only_in_star), len(pair_only_in_mine), len(combo_mismatch), time.time() - t0_))
log("base297 subset of star_edges: %s ; total combos mine=%d disk=%d"
    % (base_covered, sum(len(v) for v in my_edges.values()), raw["stats"]["infeasible_combos"]))

# 掩码暴力抽查：300 个 star 对 + 200 个非 star 对（用位与逐组合复核组合数学法）
t0_ = time.time()
rng = random.Random(987)
bad_mask = 0
sk = list(star_keys)
for (i, j) in rng.sample(sk, 300):
    Ai = [ai for ai, a in enumerate(ACTS[i]) if a[0] != "revoke"]
    Aj = [aj for aj, a in enumerate(ACTS[j]) if a[0] != "revoke"]
    brute = set()
    for ai in Ai:
        mi = AMASK[(i, ai)]
        for aj in Aj:
            if mi & AMASK[(j, aj)]:
                brute.add((ai, aj))
    if brute != star[(i, j)]:
        bad_mask += 1
non_star_all = [p for p in combinations(IDS, 2) if p not in star_keys]
for (i, j) in rng.sample(non_star_all, 200):
    Ai = [ai for ai, a in enumerate(ACTS[i]) if a[0] != "revoke"]
    Aj = [aj for aj, a in enumerate(ACTS[j]) if a[0] != "revoke"]
    for ai in Ai:
        mi = AMASK[(i, ai)]
        for aj in Aj:
            if mi & AMASK[(j, aj)]:
                bad_mask += 1
                break
log("mask-brute recheck: mismatches=%d (300 star pairs exact + 200 non-star pairs must be empty)  (%.1fs)"
    % (bad_mask, time.time() - t0_))

# 三份 star_edges.json 副本一致性
log("\ncopies sha:")
for rel in ["scouts/Q2-R51/star_edges.json", "scouts/Q2-R51/code/star_edges.json",
            "scouts/Q2-R32/code/star_edges.json", "scouts/Q2-R41/code/star_edges.json"]:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    if os.path.isfile(p):
        log("  %s  %s" % (hashlib.sha256(io.open(p, "rb").read()).hexdigest()[:16] + "...", rel))
    else:
        log("  MISSING  %s" % rel)

# ---------------- 冻结 evaluator 原样复跑（不落盘） ----------------
log("\n== canonical evaluator re-run (stdout only) ==")
for idea, rels in [("Q1-R21", ["scouts/Q1-R21/solution_q1_r21.json"]),
                   ("Q1-R52", ["scouts/Q1-R52/solution_q1_r52.json"]),
                   ("Q1-R41", ["scouts/Q1-R41/solution_q1_r41.json"]),
                   ("Q2-R51", ["scouts/Q2-R51/solution_actions.json"]),
                   ("Q2-R32", ["scouts/Q2-R32/solution_actions.json"]),
                   ("Q2-R41", ["scouts/Q2-R41/solution_actions_seed11.json",
                               "scouts/Q2-R41/solution_actions_seed29.json",
                               "scouts/Q2-R41/solution_actions_seed47.json"])]:
    for rel in rels:
        q = "Q1" if idea.startswith("Q1") else "Q2"
        cp = subprocess.run([sys.executable, os.path.join(ROOT, "canonical_evaluator.py"),
                             "--question", q, "--solution", os.path.join(ROOT, rel.replace("/", os.sep))],
                            capture_output=True, text=True, encoding="utf-8")
        try:
            out = json.loads(cp.stdout)
            log("%s [%s]: feasible=%s objective=%s n_viol=%s" %
                (idea, rel.split("/")[-1], out.get("feasible"), J(out.get("objective")),
                 out.get("n_violations", out.get("counts"))))
        except Exception:
            log("%s [%s]: PARSER FAIL exit=%s out=%s" % (idea, rel, cp.returncode, cp.stdout[:200]))

# ---------------- 口径扫描 621/643、14698/16680 ----------------
log("\n== unit-basis scan (621 / 643 / 14698 / 16680) in candidate artifacts ==")
pat = re.compile(r"621|643|14698|16680")
for idea in ["Q1-R21", "Q1-R52", "Q1-R41", "Q2-R51", "Q2-R41", "Q2-R32"]:
    hits = {}
    d = os.path.join(ROOT, "scouts", idea)
    for fn in os.listdir(d):
        if fn.endswith((".json", ".md", ".txt")):
            try:
                txt = io.open(os.path.join(d, fn), encoding="utf-8").read()
            except Exception:
                continue
            for m in set(pat.findall(txt)):
                hits.setdefault(m, []).append(fn)
    log("%s: %s" % (idea, J({k: sorted(v)[:6] for k, v in hits.items()})))

io.open(os.path.join(ROOT, "reviews", "CH-REV-A_verify_report.txt"), "w", encoding="utf-8").write("\n".join(OUT))
print("\n".join(OUT)[:3000])
print("... report written: reviews/CH-REV-A_verify_report.txt")
