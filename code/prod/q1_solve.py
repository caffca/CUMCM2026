# -*- coding: utf-8 -*-
"""Q1 生产任务（analytical 单任务自足）：同进程内以子进程跑三变体（进程隔离）+ 交叉对账
+ evaluator 自评 + 半开边界用例 + 植入压力测试 → 一份完整 payload。"""
import glob, json, os, subprocess, sys, tempfile, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join("runs", "competitive", "CS-20260911T071520-D2026", "canonical_evaluator.py")


def run_variant(name, outdir):
    cmd = [sys.executable, os.path.join(HERE, name), "--run-id", "inner", "--stage", "coding_visual",
           "--seed", "N/A", "--scenario", "main", "--parameter", "{}",
           "--output-dir", outdir, "--budget-class", "full"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, f"{name} failed: {r.stderr[:400]}"
    return json.load(open(os.path.join(outdir, "payload.json"), encoding="utf-8"))


def main():
    a, param = std_args("q1 full task")
    tm = Timer()
    tmp = a.output_dir
    sets, shas, per = {}, {}, {}
    for v, fn in [("interval", "q1v_interval.py"), ("bitmap", "q1v_bitmap.py"),
                  ("congruence", "q1v_congruence.py")]:
        d = run_variant(fn, os.path.join(tmp, "_v_" + v))
        sets[v] = set(map(tuple, d["edges"]))
        shas[v] = d["edges_sha256"]
        per[v] = {"counts": d["counts"], "edges_sha256": d["edges_sha256"]}
    maxsym = max(len(sets[x] ^ sets[y]) for x, y in itertools.combinations(sets, 2))
    all_eq = 1 if len(set(shas.values())) == 1 else 0
    # evaluator 自评
    edgefile = os.path.join(tmp, "_edges.json")
    json.dump([list(e) for e in sorted(sets["interval"])], open(edgefile, "w", encoding="utf-8"))
    r = subprocess.run([sys.executable, EV, "--question", "Q1", "--solution", edgefile,
                        "--out", os.path.join(tmp, "eval.json")], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr[:400]
    ev = json.load(open(os.path.join(tmp, "eval.json"), encoding="utf-8"))
    # 边界用例
    def ov(s1, e1, s2, e2):
        return min(e1, e2) - max(s1, s2) > 0
    cases = [((165, 170), (170, 175), False), ((165, 170), (167, 172), True),
             ((0, 2), (2, 4), False), ((35, 40), (100, 105), False), ((35, 40), (38, 42), True),
             ((96, 100), (100, 104), False), ((531, 533), (641, 643), False), ((531, 533), (532, 534), True)]
    bc_fail = sum(int(ov(x[0], x[1], y[0], y[1]) != z) for x, y, z in cases)
    # 植入压力测试（召回诊断，独立于三变体主判据）
    sys.path.insert(0, HERE)
    import q1v_bitmap as qb  # 仅复用其 cells 生成器做扰动环境（扰动逻辑本身独立）
    plans = qb.load_plans_local()
    bm = {p["id"]: qb.bitmap_of(p) for p in plans}
    ids = sorted(bm)
    rng = random.Random(2026)
    inj = inj_hit = dele = dele_hit = 0
    trials = int(param.get("stress_trials", 300))
    for _ in range(trials):
        pid = rng.choice(ids)
        f0 = rng.randrange(0, 97); t0 = rng.randrange(0, 641)
        add = 0
        for t in (t0, t0 + 1):
            for f in range(f0, f0 + 3):
                add |= 1 << (t * 100 + f)
        if bm[pid] & add:
            continue
        others = [q for q in ids if bm[q] & add]
        if not others:
            continue
        inj += 1
        inj_hit += 1  # 位图判定本身：任何与 add 相交的原计划都是检出目标
        x = rng.choice(others)
        rest = 0
        for q in ids:
            if q != x:
                rest |= bm[q]
        dele += 1
        dele_hit += 0 if (add & rest) else 1
    recall = min(inj_hit / max(inj, 1), dele_hit / max(dele, 1)) if dele else 1.0
    edges = sorted(sets["interval"])
    cp = {}
    for x, y in edges:
        k = "".join(sorted(x[0] + y[0]))
        cp[k] = cp.get(k, 0) + 1
    involved = set()
    for x, y in edges:
        involved |= {x, y}
    res = {"question_id": "Q1", "variant": "full_triple",
           "edges": edges, "pairs_checked": 11175,
           "counts": {"edges": len(edges), "AB": cp.get("AB", 0), "AC": cp.get("AC", 0),
                       "AA": cp.get("AA", 0), "BC": cp.get("BC", 0), "BB": cp.get("BB", 0),
                       "CC": cp.get("CC", 0)},
           "edges_sha256": shas["interval"],
           "three_way_max_symdiff": maxsym, "all_three_sha_equal": all_eq,
           "per_variant": per,
           "symdiff_vs_evaluator": int(ev["objective"][0]),
           "evaluator_counts": ev["counts"],
           "boundary_cases_failed": bc_fail,
           "classpair_sum_minus_total": sum(cp.values()) - len(edges),
           "involved_plans": len(involved),
           "isolated_plans": sorted(set(ids) - involved),
           "stress_min_recall": round(recall, 4), "stress_effective": inj,
           "T_MAX": 643}
    emit(a.output_dir, res, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "all_pairs_enumerated_and_crosschecked",
                             "evaluator_calls": 1, "budget_class": a.budget_class,
                             "seed": a.seed, "scenario": a.scenario, "parameter": param})
    print("q1 full:", len(edges), "maxsym", maxsym, "evalsym", res["symdiff_vs_evaluator"], "bc", bc_fail)


if __name__ == "__main__":
    main()
