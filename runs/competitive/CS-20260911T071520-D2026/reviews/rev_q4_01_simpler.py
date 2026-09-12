# -*- coding: utf-8 -*-
"""REV-Q4-01 附件脚本 K：把「更简基线 B2b」固化并交冻结 evaluator 复核。
B2b = 无任何解析构造 / 无 CP-SAT / 无 SA 的 60 行贪心：
  每轮取字典序最小残余边 → 端点按 (类权低者优先, 度大者优先) → 尝试该端点全部单参数动作
  中『残余边数严格下降』的最小者；无下降者则撤销优先端点。
目的：给 R22 的「撤销 66 是构造结构性极限」归因一个可机检的反例。
"""
import io, json, os, subprocess, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(RUN, "scouts", "Q4-R11", "code"))
import q4common as Q                                        # noqa: E402
sys.stdout.reconfigure(encoding="utf-8")
TMP = os.path.join(RUN, "reviews", "_tmp")
plans = Q.CE.load_plans()
d4 = Q.build_domains(plans, allow_gap=True)


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


def edges_of(ms):
    ids = sorted(ms)
    return {(ids[x], ids[y]) for x in range(len(ids)) for y in range(x + 1, len(ids))
            if ms[ids[x]] & ms[ids[y]]}


ms = masks_of({})
E = edges_of(ms)
actions = {}
guard = 0
while E:
    guard += 1
    assert guard < 3000
    d = {}
    for (i, j) in E:
        d[i] = d.get(i, 0) + 1
        d[j] = d.get(j, 0) + 1
    i, j = min(E)
    ends = sorted({i, j}, key=lambda k: (Q.PRIO[plans[k]["cls"]], -d.get(k, 0), k))
    moved = False
    for pid in ends:
        best = None
        for opt in d4[pid]:
            if opt["kind"] in ("none", "revoke") or not opt["act"]:
                continue
            trial = dict(actions)
            trial[pid] = opt["act"]
            m2 = masks_of(trial)
            if m2 is None:
                continue
            ne = edges_of(m2)
            if len(ne) < len(E) and best is None:
                best = (ne, opt["act"])
        if best:
            actions[pid] = best[1]
            E = best[0]
            moved = True
            break
    if not moved:
        p = ends[0]
        actions[p] = {"revoke": True}
        E = {(a, b) for (a, b) in E if a != p and b != p}

path = os.path.join(TMP, "B2b_greedy_solution.json")
io.open(path, "w", encoding="utf-8").write(json.dumps(actions, ensure_ascii=False, indent=1))
outp = os.path.join(TMP, "B2b_eval.json")
r = subprocess.run([sys.executable, os.path.join(RUN, "canonical_evaluator.py"), "--question", "Q4",
                    "--solution", path, "--out", outp], capture_output=True, text=True, encoding="utf-8")
ev = json.load(io.open(outp, encoding="utf-8"))
res = dict(exit=r.returncode, feasible=ev["feasible"], tuple=ev["objective"],
           n_violations=ev["n_violations"], stats=ev["stats"],
           independent_residual=len(edges_of(masks_of(actions))),
           vs_R22_lexicographically_better=tuple(ev["objective"]) < (66, 43, 1111, 144),
           rounds=guard)
io.open(os.path.join(TMP, "recheck_out_K.json"), "w", encoding="utf-8").write(
    json.dumps(res, ensure_ascii=False, indent=1))
print(json.dumps(res, ensure_ascii=False, indent=1))
