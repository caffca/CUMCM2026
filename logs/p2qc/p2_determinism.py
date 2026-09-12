# -*- coding: utf-8 -*-
"""P2-12：确定性/顺序敏感性实测。

同一份生产实现，在两个不同 PYTHONHASHSEED 下各跑一次（输出写到 logs/p2qc/_rerun/，
不触碰任何权威件），比较边集 sha 是否逐位一致；
另跑一次 P2 自己的解析实现，确认与生产实现在任意哈希种子下等价。
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.join(P.ROOT, "code", "prod")


def run_variant(script, outdir, seed):
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = str(seed)
    env["OMP_NUM_THREADS"] = "1"
    env["DSH_ENVLIBS"] = os.environ.get("DSH_ENVLIBS", r"F:\dsh_envlibs\mathmodel")
    log = os.path.join(outdir, "run.log")
    os.makedirs(outdir, exist_ok=True)
    with open(log, "w", encoding="utf-8") as lg:
        p = subprocess.run([sys.executable, os.path.join(PROD, script),
                            "--output-dir", outdir, "--seed", str(seed),
                            "--scenario", "main", "--parameter", "{}"],
                           cwd=P.ROOT, env=env, stdout=lg, stderr=subprocess.STDOUT)
    return p.returncode


def main():
    os.environ["PYTHONHASHSEED"] = "0"      # 让本进程（含 json.dumps/我们的实现）也确定
    roots = os.path.join(HERE, "_rerun")
    out = {"check": "顺序敏感性（PYTHONHASHSEED）实测", "variants": {}}
    for script, key in (("q1v_interval.py", "interval"), ("q1v_bitmap.py", "bitmap"), ("q1v_congruence.py", "congruence")):
        recs = []
        for seed in (0, 1, 12345):
            od = os.path.join(roots, key, f"s{seed}")
            try:
                rc = run_variant(script, od, seed)
            except Exception as ex:                       # 沙箱不允许捕获子进程 stdio 时给出明确说明
                rc = f"SPAWN_ERROR:{type(ex).__name__}:{ex}"
            pf = os.path.join(od, "payload.json")
            sha = edges = None
            if os.path.exists(pf):
                d = json.load(open(pf, encoding="utf-8"))
                d = d.get("result", d)
                edges = d.get("edges")
                sha = d.get("edges_sha256") or P.sha_of_edges([list(e) for e in sorted(map(list, edges or []))])
            recs.append({"seed": seed, "rc": rc, "n_edges": len(edges or []), "sha": sha})
        out["variants"][key] = recs
        out["variants"][key + "_all_seeds_equal"] = len({r["sha"] for r in recs if r["sha"]}) == 1 and all(r["sha"] for r in recs)
    # 与 P2 解析实现对照
    plans = P.load_plans()
    mine, _ = P.all_conflicts(plans)
    out["p2_analytic_sha"] = P.sha_of_edges(mine)
    out["p2_analytic_n"] = len(mine)
    out["matches_all_prod_variants"] = all(
        out["variants"][k][-1]["sha"] == out["p2_analytic_sha"] for k in ("interval", "bitmap", "congruence")
        if out["variants"][k][-1]["sha"])
    out["verdict"] = P.verdict(all(out["variants"][k + "_all_seeds_equal"] for k in ("interval", "bitmap", "congruence"))
                               and out["p2_analytic_n"] == 297)
    P.wr("p2_determinism.json", out)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
