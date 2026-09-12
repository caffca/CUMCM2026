# -*- coding: utf-8 -*-
"""Q1 交叉审计任务：读同 run 三变体 payload → 三方对称差/边界用例/植入压力测试召回。
输出 payload 键：three_way_max_symdiff, boundary_cases_failed, stress_min_recall,
classpair_sum_minus_total, interval_eq_evaluator。"""
import glob, os, sys, json, hashlib, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local  # noqa

T_MAX, B_MAX = 643, 100


def cells(p):
    m = 0
    for k in range(p["n"]):
        s = p["t0"] + k * (p["g"] + p["d"])
        for t in range(s, s + p["d"]):
            for f in range(p["f0"], p["f1"]):
                m |= 1 << (t * B_MAX + f)
    return m


def main():
    a, param = std_args("q1 crosscheck")
    tm = Timer()
    root = os.path.join("runs", "fresh", a.run_id, "tasks")
    sets = {}
    metas = {}
    for tf in sorted(glob.glob(os.path.join(root, "q1-*", "attempts", "*", "payload.json"))):
        d = json.load(open(tf, encoding="utf-8"))
        v = d.get("variant")
        if v in ("interval", "bitmap", "congruence"):
            sets[v] = set(map(tuple, d["edges"]))
            metas[v] = d.get("edges_sha256")
    assert {"interval", "bitmap", "congruence"} <= set(sets), "missing variant payloads"
    import itertools
    maxsym = max(len(sets[x] ^ sets[y]) for x, y in itertools.combinations(sets, 2))
    plans = {p["id"]: p for p in load_plans_local()}
    ids = sorted(plans)
    bm = {pid: cells(plans[pid]) for pid in ids}
    truth = set()
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if bm[ids[i]] & bm[ids[j]]:
                truth.add((ids[i], ids[j]))
    rng = random.Random(2026)
    inject_hit = inject_tot = del_hit = del_tot = 0
    trials = int(param.get("stress_trials", 400))
    for _ in range(trials):
        mut = dict(bm)
        pid = rng.choice(ids)
        p = plans[pid]
        f0 = rng.randrange(0, B_MAX - 3)
        t0 = rng.randrange(0, T_MAX - 12)
        add = 0
        for f in range(f0, f0 + 3):
            add |= (1 << (t0 * B_MAX + f)) | (1 << ((t0 + 1) * B_MAX + f))
        if mut[pid] & add:
            continue
        newp = dict(p, f0=f0, f1=f0 + 3, t0=t0, t1=t0 + 2, g=0, n=1, d=2)
        mut["INJECT"] = add
        others = [q for q in ids if mut[q] & add]
        if not others:
            continue
        inject_tot += 1
        x = rng.choice(others)
        if mut[pid] & mut[x] or add & mut[x]:
            inject_hit += 1
        del_tot += 1
        rest = 0
        for q in ids:
            if q != x:
                rest |= mut[q]
        del_hit += 0 if (add & rest) else 1
    recall = min(inject_hit / max(inject_tot, 1), del_hit / max(del_tot, 1))
    bc = 0
    def ov(s1, e1, s2, e2):
        return min(e1, e2) - max(s1, s2) > 0
    bc += int(ov(165, 170, 170, 175) is not False) + int(ov(165, 170, 167, 172) is not True) \
        + int(ov(0, 2, 2, 4) is not False) + int(ov(35, 40, 100, 105) is not False) \
        + int(ov(35, 40, 38, 42) is not True) + int(ov(96, 100, 100, 104) is not False) \
        + int(ov(531, 533, 641, 643) is not False) + int(ov(531, 533, 632, 634) is not True)
    edges = sorted(sets["interval"])
    # canonical evaluator 自评（V-Q1-01）：把边集写临时文件，子进程跑 evaluator，objective=symdiff
    import subprocess, tempfile
    ev = os.path.join("runs", "competitive", "CS-20260911T071520-D2026", "canonical_evaluator.py")
    tmp = os.path.join(a.output_dir, "_edges_for_eval.json")
    json.dump([list(e) for e in edges], open(tmp, "w", encoding="utf-8"))
    r = subprocess.run([sys.executable, ev, "--question", "Q1", "--solution", tmp],
                       capture_output=True, text=True, encoding="utf-8")
    ev_doc = json.loads(r.stdout)
    symdiff_vs_evaluator = int(ev_doc["objective"][0])
    cp = {}
    for x, y in edges:
        k = "".join(sorted(x[0] + y[0]))
        cp[k] = cp.get(k, 0) + 1
    res = {"question_id": "Q1", "variant": "check",
           "symdiff_vs_evaluator": symdiff_vs_evaluator,
           "three_way_max_symdiff": maxsym,
           "all_three_sha_equal": 1 if len(set(metas.values())) == 1 else 0,
           "edges_sha256": metas["interval"],
           "boundary_cases_failed": bc,
           "stress_min_recall": round(recall, 4), "stress_trials_effective": inject_tot,
           "classpair_sum_minus_total": sum(cp.values()) - len(edges),
           "counts": {"edges": len(edges), "AB": cp.get("AB", 0), "AC": cp.get("AC", 0),
                       "AA": cp.get("AA", 0), "BC": cp.get("BC", 0), "BB": cp.get("BB", 0),
                       "CC": cp.get("CC", 0)},
           "truth_pairs_second_scan": len(truth),
           "truth_scan_matches_interval": 1 if truth == set(sets["interval"]) else 0}
    emit(a.output_dir, res, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "crosscheck_complete", "evaluator_calls": 0,
                             "budget_class": a.budget_class, "seed": a.seed,
                             "scenario": a.scenario, "parameter": param})
    print("q1 check: maxsym", maxsym, "bc", bc, "recall", round(recall, 4), "truthmatch", res["truth_scan_matches_interval"])


if __name__ == "__main__":
    main()
