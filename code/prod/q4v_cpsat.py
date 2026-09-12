# -*- coding: utf-8 -*-
"""Q4 生产求解器：Q2 模型扩 C 类重定时选项（dg），Q2 生产解热启动 + 字典序不劣锚定 + 阶梯证书。
独立实现（自含），大整数位图。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local, resolve_base  # noqa
os.environ.setdefault("OMP_NUM_THREADS", "1")
from ortools.sat.python import cp_model  # noqa

T_MAX, B_MAX, DFM, DTM, DGM = 643, 100, 10, 5, 10
WP = {"A": 100, "B": 10, "C": 1}


def cells(p, df=0, dt=0, dg=0, dg_allowed=True):
    if dg and not dg_allowed:
        return None
    g = p["g"] + dg
    if g < 1:
        return None
    m = 0
    for k in range(p["n"]):
        s = p["t0"] + dt + k * (g + p["d"])
        if s < 0 or s + p["d"] > T_MAX:
            return None
        for t in range(s, s + p["d"]):
            row = t * B_MAX
            for f in range(p["f0"] + df, p["f1"] + df):
                if f < 0 or f >= B_MAX:
                    return None
                m |= 1 << (row + f)
    return m


def main():
    a, param = std_args("q4 cpsat")
    tm = Timer()
    workers = int(param.get("workers", 4))
    tb = param.get("stage_budget", {})
    BUD = {"l1": tb.get("l1", 900), "ladder": tb.get("ladder", 300),
           "l2": tb.get("l2", 600), "l3": tb.get("l3", 300), "l4": tb.get("l4", 300)}
    anchor = param.get("anchor", True)
    plans = load_plans_local()
    opts, masks = {}, {}
    dropped = 0
    for p in plans:
        o = [("id", 0)]; ms = [cells(p)]
        for d in range(-DFM, DFM + 1):
            if d:
                m = cells(p, df=d)
                if m is not None:
                    o.append(("df", d)); ms.append(m)
        for d in range(-DTM, DTM + 1):
            if d:
                m = cells(p, dt=d)
                if m is not None:
                    o.append(("dt", d)); ms.append(m)
        if p["cls"] == "C":
            for d in range(-DGM, DGM + 1):
                if d:
                    m = cells(p, dg=d)
                    if m is None:
                        dropped += 1
                    else:
                        o.append(("dg", d)); ms.append(m)
        o.append(("rv", 0)); ms.append(0)
        opts[p["id"]] = o; masks[p["id"]] = ms
    emv = {}
    for pid in opts:
        u = 0
        for m in masks[pid]:
            u |= m
        emv[pid] = u
    ids = sorted(opts)
    bedges = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            x, y = ids[i], ids[j]
            if not (emv[x] & emv[y]):
                continue
            bad = []
            for a_, mx in enumerate(masks[x]):
                for b_, my in enumerate(masks[y]):
                    if mx & my:
                        bad.append((a_, b_))
            if len(bad) == len(opts[x]) * len(opts[y]):
                bedges.append((x, y, "FORCED"))
            elif bad:
                bedges.append((x, y, bad))
    hint_acts = {}
    anchor_tuple = None
    if param.get("q2_solution"):
        from cli import resolve_base
        p2, _src = resolve_base(param["q2_solution"], a.run_id, want_variant="cpsat_lex",
                                 want_workers="main", qprefix="q2")
        s2 = json.load(open(p2, encoding="utf-8"))
        s2 = s2.get("result", s2)
        hint_acts = s2.get("actions") or {}
        anchor_tuple = s2.get("objective_tuple")
        param = dict(param); param["_q2_src"] = _src

    def make(cap_Rp=None, leq=None):
        m = cp_model.CpModel()
        X = {pid: [m.NewBoolVar(f"x{pid}_{k}") for k in range(len(opts[pid]))] for pid in ids}
        for pid in ids:
            m.AddExactlyOne(X[pid])
        for (x, y, bad) in bedges:
            if bad == "FORCED":
                m.AddImplication(X[x][opts[x].index(("rv", 0))].Not(), X[y][opts[y].index(("rv", 0))])
            else:
                for (u, v) in bad:
                    m.AddBoolOr([X[x][u].Not(), X[y][v].Not()])
        rv = {pid: X[pid][opts[pid].index(("rv", 0))] for pid in ids}
        adjv = {pid: sum(X[pid][k] for k in range(len(opts[pid]))
                         if opts[pid][k][0] in ("df", "dt", "dg")) for pid in ids}
        R = m.NewIntVar(0, len(ids), "R"); m.Add(R == sum(rv.values()))
        A = m.NewIntVar(0, len(ids), "A"); m.Add(A == sum(adjv.values()))
        PL = m.NewIntVar(0, 4 * len(ids) * 200, "PL")
        m.Add(PL == sum(WP[pid[0]] * (2 * rv[pid] + adjv[pid]) for pid in ids))
        MG = m.NewIntVar(0, 30 * len(ids), "MG")
        m.Add(MG == sum(sum(abs(opts[pid][k][1]) * X[pid][k] for k in range(len(opts[pid]))
                            if opts[pid][k][0] in ("df", "dt", "dg")) for pid in ids))
        _hrv = sum(1 for o in hint_acts.values() if o.get("revoke"))
        if (cap_Rp is None or cap_Rp >= _hrv) and (leq is None or leq[0] >= _hrv):
            for pid, o in hint_acts.items():
                if pid in X:
                    key = ("rv", 0) if o.get("revoke") else next(((k, int(v)) for k, v in o.items() if k != "revoke"), ("id", 0))
                    if key in opts[pid]:
                        for k, opt in enumerate(opts[pid]):
                            m.AddHint(X[pid][k], 1 if opt == key else 0)
        return m, X, (R, A, PL, MG)

    log, cert = [], []

    def run(tag, locks, minimize, cap_R=None, limit=300, leq_tuple=None):
        m, X, (R, A, PL, MG) = make(cap_R, leq_tuple)
        var = {"R": R, "A": A, "PL": PL, "MG": MG}
        if cap_R is not None:
            m.Add(R <= cap_R)
        for k, v in (locks or {}).items():
            m.Add(var[k] == v)
        if leq_tuple:
            m.Add(R <= leq_tuple[0]); m.Add(A <= leq_tuple[1])
            m.Add(PL <= leq_tuple[2]); m.Add(MG <= leq_tuple[3])
        if minimize:
            m.Minimize(var[minimize])
        sv = cp_model.CpSolver()
        sv.parameters.max_time_in_seconds = float(limit)
        sv.parameters.num_search_workers = workers
        st = sv.Solve(m)
        name = sv.StatusName(st)
        rec = {"layer": tag, "status": name, "min": minimize, "cap_R": cap_R,
               "wall_cum": round(tm.el(), 1)}
        sel = None
        if name in ("OPTIMAL", "FEASIBLE"):
            rec.update({"objective": sv.ObjectiveValue(), "best_bound": sv.BestObjectiveBound(),
                        "solution_tuple": [sv.Value(R), sv.Value(A), sv.Value(PL), sv.Value(MG)]})
            sel = {}
            for pid in ids:
                for k, xv in enumerate(X[pid]):
                    if sv.Value(xv):
                        sel[pid] = list(opts[pid][k])
        log.append(rec)
        return name, sel, rec

    def to_actions(sel):
        acts = {}
        for pid, (kind, v) in ((p, tuple(o)) for p, o in (sel or {}).items()):
            if kind == "rv":
                acts[pid] = {"revoke": True}
            elif kind != "id":
                acts[pid] = {kind: v}
        return acts

    def tup(acts):
        rev = adj = pl = mg = 0
        for pid, o in acts.items():
            c = pid[0]
            if o.get("revoke"):
                rev += 1; pl += 2 * WP[c]
            else:
                ks = [k for k in o if k != "revoke"]
                if ks:
                    adj += 1; pl += WP[c]; mg += sum(abs(int(o[k])) for k in ks)
        return [rev, adj, pl, mg]

    # 锚定不劣（先算）：Q2 生产解植入 Q4 域；四层模型均加逐维 ≤ 锚（植入解自身满足 ⇒ 不致不可行）
    planted = None
    planted_residual = None
    if hint_acts:
        planted = tup(hint_acts)
        pmask = {}
        okp = True
        planted_reject = None
        for pid, o in hint_acts.items():
            if pid not in opts:
                okp = False
                planted_reject = "notinopts:" + pid
                break
            key = ("rv", 0) if o.get("revoke") else next(((k, int(v)) for k, v in o.items()), ("id", 0))
            if key not in opts[pid]:
                okp = False
                planted_reject = f"key:{pid}:{key}"
                break
            pmask[pid] = masks[pid][opts[pid].index(key)]
        if okp:
            pr = 0
            for i in range(len(ids)):
                mi = pmask.get(ids[i])
                if not mi:
                    continue
                for j in range(i + 1, len(ids)):
                    mj = pmask.get(ids[j])
                    if mj and (mi & mj):
                        pr += 1
            planted_residual = pr
        else:
            planted = None
    anch = planted if (anchor and planted) else None
    st1, sel1, rec1 = run("L1_minR", None, "R", limit=BUD["l1"], leq_tuple=anch)
    final_sel = sel1
    rev_star = rec1.get("solution_tuple", [None])[0] if sel1 else None
    lb = int(rec1.get("best_bound") or 0)
    st0, _, _ = run("ladder_Rle0", None, None, cap_R=0, limit=BUD["ladder"])
    cert.append({"cap": 0, "status": st0})
    lb = max(lb, 1 if st0 == "INFEASIBLE" else 0)
    if rev_star is not None and rev_star - 1 > lb:
        stc, selc, rec2 = run("ladder_desc", None, "R", cap_R=rev_star - 1, limit=BUD["ladder"])
        if selc:
            final_sel = selc
            rev_star = rec2["solution_tuple"][0]
            lb = max(lb, int(rec2.get("best_bound") or 0))
        cert.append({"cap": rev_star - 1, "status": stc})
        lb = max(lb, rev_star) if stc == "INFEASIBLE" else lb
    closed = (rev_star == lb)
    if sel1 and rev_star is not None:
        adjlock = rec1.get("solution_tuple", [None, None])[1]
        st2, sel2, rec2 = run("L2_minA", {"R": rev_star}, "A", limit=BUD["l2"], leq_tuple=anch)
        if sel2:
            final_sel = sel2
        adjv = rec2.get("solution_tuple", [None, None, None, None])[1] if sel2 else None
        if adjv is not None:
            st3, sel3, rec3 = run("L3_minPL", {"R": rev_star, "A": adjv}, "PL", limit=BUD["l3"])
            if sel3:
                final_sel = sel3
            plv = rec3.get("solution_tuple", [None, None, None, None])[2] if sel3 else None
            if plv is not None:
                st4, sel4, rec4 = run("L4_minMG", {"R": rev_star, "A": adjv, "PL": plv}, "MG", limit=BUD["l4"])
                if sel4:
                    final_sel = sel4
    acts = to_actions(final_sel)
    if not final_sel:
        raise SystemExit("FAIL-CLOSED: Q4 no incumbent (L1 empty)")
    tf = tup(acts)
    res = {"question_id": "Q4", "variant": "cpsat_lex", "workers": workers,
           "gstar_edges": len(bedges), "options_total": sum(len(v) for v in opts.values()),
           "dg_options_dropped_by_horizon": dropped,
           "actions": acts, "objective_tuple": tf,
           "objective_scalar": 10**12 * tf[0] + 10**8 * tf[1] + 10**4 * tf[2] + tf[3],
           "planted_q2_tuple": planted, "planted_q2_residual": planted_residual,
           "planted_q2_feasible": (1 if (planted is not None and planted_residual == 0) else (0 if planted is not None else None)),
           "planted_reject_reason": planted_reject,
           "revocation": {"upper_incumbent": tf[0], "proven_lb": lb, "lb_closed": closed,
                           "certificates": cert},
           "anchor_requested": anchor, "layers": log}
    emit(a.output_dir, res, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "stages_complete_or_budget", "evaluator_calls": len(log),
                             "budget_class": a.budget_class, "seed": a.seed,
                             "scenario": a.scenario, "parameter": param})


if __name__ == "__main__":
    main()
