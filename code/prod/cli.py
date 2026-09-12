# -*- coding: utf-8 -*-
"""prod 共享 CLI 管线（仅参数/落盘管道与环境引导，不含任何算法逻辑——算法独立性在各 variant 文件内）。"""
import argparse, json, os, sys, time

# 求解器环境引导：ortools 安装于工作区外 envlibs（见 decision D-ENV-003）
_ENVLIBS = os.environ.get("DSH_ENVLIBS", r"F:\dsh_envlibs\mathmodel")
if os.path.isdir(_ENVLIBS) and _ENVLIBS not in sys.path:
    sys.path.append(_ENVLIBS)


def std_args(desc):
    ap = argparse.ArgumentParser(desc)
    ap.add_argument("--run-id", default="adhoc")
    ap.add_argument("--stage", default="coding_visual")
    ap.add_argument("--seed", default="N/A")
    ap.add_argument("--scenario", default="main")
    ap.add_argument("--parameter", default="{}")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--budget-class", default="full")
    a = ap.parse_args()
    return a, json.loads(a.parameter)


class Timer:
    def __init__(self): self.t0 = time.time()
    def el(self): return round(time.time() - self.t0, 3)


def emit(outdir, result, metrics):
    os.makedirs(outdir, exist_ok=True)
    json.dump(result, open(os.path.join(outdir, "payload.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(metrics, open(os.path.join(outdir, "execution_metrics.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def load_plans_local():
    """每个 variant 独立的最小 CSV 读取（不共享算法模块）。"""
    import io
    rows = io.open("data/canonical_plans.csv", encoding="utf-8").read().strip().splitlines()
    plans = []
    for ln in rows[1:]:
        c = ln.split(",")
        plans.append(dict(id=c[0], cls=c[0][0], f0=int(c[2]), f1=int(c[3]),
                          t0=int(c[4]), t1=int(c[5]), g=int(c[6]), n=int(c[7]),
                          d=int(c[5]) - int(c[4])))
    return plans


def resolve_base(token, run_id, want_variant="cpsat_lex", want_workers=None, qprefix="q2"):
    """@TOKEN 基座解析：在 runs/fresh/<run_id>/tasks/<qprefix>-*/…/payload.json 中
    找 variant（和 workers）匹配的 task payload；也可直接给文件路径。
    want_workers=None 时按 objective_tuple 词典序取最优（并列优先 workers=1 的确定性跑）。"""
    import glob
    token = str(token or "")
    if token.startswith("@"):
        root = os.path.join("runs", "fresh", run_id, "tasks")
        cands = []
        for tf in sorted(glob.glob(os.path.join(root, qprefix + "-*", "attempts", "*", "payload.json"))):
            try:
                import json as _j
                d = _j.load(open(tf, encoding="utf-8"))
                if d.get("variant") == want_variant and (want_workers in (None, "main") or d.get("workers") == want_workers):
                    if d.get("objective_tuple"):
                        cands.append((tuple(d["objective_tuple"]) + (0 if d.get("workers") == 1 else 1,), tf, d))
                    else:
                        cands.append(((10**9,), tf, d))
            except Exception:
                continue
        if want_workers == "main":
            # verified_best：词典序最优 objective_tuple（并列优先 workers=1）；所有候选都过独立 checker
            pool = sorted(cands, key=lambda t: (tuple(t[2].get("objective_tuple") or [10**9]),
                                                0 if t[2].get("workers") == 1 else 1))
            return pool[0][1], "shard:" + pool[0][1]
        if not cands:
            raise SystemExit(f"resolve_base: no {qprefix} {want_variant} payload under {root}")
        cands.sort()
        return cands[0][1], "shard:" + cands[0][1]
    return token, "file:" + token
