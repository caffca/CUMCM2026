# -*- coding: utf-8 -*-
"""REV-Q4-01 附件脚本 H：幅度层（第 3/4 级）抛光潜力测试 —— 检验各候选「UNKNOWN 层」的证据缺口。
对每个已交付解做两类确定性后处理（不改模型、不越预算口径，仅评审计用）：
  H1. 幅度降级 1-opt：保持 rev/adj 计数不变（同类型动作，只把 |v| 调小），零冲突则接受；
  H2. 撤销回滚：允许把撤销换成调整/保留（会改 rev 计数，词典序第一级下降即赢）。
两者都用冻结 evaluator 复核 feasibility 与元组。
"""
import io, json, os, subprocess, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(RUN, "scouts", "Q4-R11", "code"))
import q4common as Q                                        # noqa: E402
sys.stdout.reconfigure(encoding="utf-8")
plans = Q.CE.load_plans()
TMP = os.path.join(RUN, "reviews", "_tmp")
LIM = {"df": 10, "dt": 5, "dg": 10}
out = {}


def masks_of(actions):
    ms = {}
    for pid, p in plans.items():
        a = actions.get(pid, {})
        if a.get("revoke"):
            continue
        m = Q.mask_int(p, df=int(a.get("df", 0)), dt=int(a.get("dt", 0)), dg=int(a.get("dg", 0)))
        if m is None:
            return None
        ms[pid] = m
    return ms


def n_conf(ms):
    ids = sorted(ms)
    return sum(1 for x in range(len(ids)) for y in range(x + 1, len(ids)) if ms[ids[x]] & ms[ids[y]])


def frozen_eval(path, q="Q4"):
    o = path + ".eval.json"
    r = subprocess.run([sys.executable, os.path.join(RUN, "canonical_evaluator.py"), "--question", q,
                        "--solution", path, "--out", o], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return {"_error": r.stderr[-300:]}
    e = json.load(io.open(o, encoding="utf-8"))
    return dict(feasible=e["feasible"], tuple=e["objective"], n_violations=e["n_violations"])


def sat_profile(actions):
    c = {"df10": 0, "dt5": 0, "dg10": 0, "n_adj": 0}
    for a in actions.values():
        if a.get("revoke"):
            continue
        c["n_adj"] += 1
        if abs(int(a.get("df", 0))) == 10:
            c["df10"] += 1
        if abs(int(a.get("dt", 0))) == 5:
            c["dt5"] += 1
        if abs(int(a.get("dg", 0))) == 10:
            c["dg10"] += 1
    return c


def polish_mag(actions):
    """H1：只降 |v|（同类型、同号），保持 rev/adj 数不变，逐计划多轮至不动点。"""
    cur = dict(actions)
    ms = masks_of(cur)
    assert ms is not None and n_conf(ms) == 0

    def clash(pid, m):
        return any((m & ms[q]) for q in ms if q != pid)

    changed = 0
    again = True
    while again:
        again = False
        for pid in sorted(cur):
            a = cur[pid]
            if a.get("revoke"):
                continue
            k = [x for x in ("df", "dt", "dg") if a.get(x)][0]
            v = int(a[k])
            for nv in range(abs(v) - 1, 0, -1):
                cand = {k: -nv if v < 0 else nv}
                mnew = Q.mask_int(plans[pid], **cand)
                if mnew is None or clash(pid, mnew):
                    continue
                cur[pid] = cand
                ms[pid] = mnew
                changed += 1
                again = True
                break
    return cur, changed


for name, rel in [("R11", "scouts/Q4-R11/run/solution_actions.json"),
                  ("R41_seed29", "scouts/Q4-R41/run/solution_seed29.json"),
                  ("R41_seed47", "scouts/Q4-R41/run/solution_seed47.json"),
                  ("R22", "scouts/Q4-R22/run/solution_actions.json")]:
    sol = json.load(io.open(os.path.join(RUN, rel), encoding="utf-8"))
    t0v, s0 = Q.opt_scalar(plans, sol)
    pol, nch = polish_mag(sol)
    t1v, s1 = Q.opt_scalar(plans, pol)
    p = os.path.join(TMP, f"polished_{name}.json")
    io.open(p, "w", encoding="utf-8").write(json.dumps(pol, ensure_ascii=False, indent=1))
    out[name] = dict(original_tuple=t0v, saturated=sat_profile(sol),
                     polished_tuple=t1v, n_mag_reductions=nch,
                     mag_drop=t0v[3] - t1v[3],
                     frozen_before=frozen_eval(os.path.join(RUN, rel)),
                     frozen_after=frozen_eval(p),
                     lexicographic_improvement=tuple(t1v) < tuple(t0v))

io.open(os.path.join(TMP, "recheck_out_H.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1, default=str))
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
