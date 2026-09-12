# -*- coding: utf-8 -*-
"""Q2 生产求解器：带撤销色多选择 CSP（G* 全势边表格子句）+ 词典序四级逐级锁定 + 撤销阶梯证书。
独立实现（全新代码，仅按 FMS 契约），位图为大整数。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local  # noqa
os.environ.setdefault("OMP_NUM_THREADS", "1")
from ortools.sat.python import cp_model  # noqa

T_MAX, B_MAX, DFM, DTM = 643, 100, 10, 5
WP = {"A": 100, "B": 10, "C": 1}


def cells(p, df=0, dt=0):
    m = 0
    for k in range(p["n"]):
        s = p["t0"] + dt + k * (p["g"] + p["d"])
        if s < 0 or s + p["d"] > T_MAX:
            return None
        for t in range(s, s + p["d"]):
            row = t * B_MAX
            for f in range(p["f0"] + df, p["f1"] + df):
                if f < 0 or f >= B_MAX:
                    return None
                m |= 1 << (row + f)
    return m


def build(plans):
    opts, masks = {}, {}
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
        o.append(("rv", 0)); ms.append(0)
        opts[p["id"]] = o; masks[p["id"]] = ms
    union = {}
    for pid in opts:
        u = 0
        for m in masks[pid]:
            u |= m
        union[pid] = u
    ids = sorted(opts)
    edges = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            if not (union[a] & union[b]):
                continue
            bad = []
            for x, mx in enumerate(masks[a]):
                for y, my in enumerate(masks[b]):
                    if mx & my:
                        bad.append((x, y))
            if len(bad) == len(opts[a]) * len(opts[b]):
                edges.append((a, b, "FORCED"))   # 恒冲突：必撤一端
            elif bad:
                edges.append((a, b, bad))
    return ids, opts, masks, edges


def main():
    a, param = std_args("q2 cpsat")
    tm = Timer()
    workers = int(param.get("workers", 4))
    tb = param.get("stage_budget", {})
    BUD = {"l1": tb.get("l1", 900), "ladder": tb.get("ladder", 300),
           "l2": tb.get("l2", 600), "l3": tb.get("l3", 300), "l4": tb.get("l4", 300)}
    plans = load_plans_local()
    ids, opts, masks, edges = build(plans)
    idx = {pid: i for i, pid in enumerate(ids)}

    hint_acts, hint_src = {}, None
    if param.get("hint"):
        import os as _os, json as _json
        hint_src = str(param["hint"])
        hp = hint_src
        if not _os.path.exists(hp):
            from cli import resolve_base as _rb
            hp, _ = _rb(hp, a.run_id, want_variant="cpsat_lex", want_workers="main", qprefix="q2")
        hs = _json.load(open(hp, encoding="utf-8"))
        hs = hs.get("result", hs)
        ha = hs.get("actions")
        if not isinstance(ha, dict):
            ha = {k: v for k, v in hs.items() if isinstance(v, dict) and (set(v) <= {"revoke", "df", "dt", "dg"})}
        hint_acts = ha or {}

    def make_model(extra_rev_cap=None):
        m = cp_model.CpModel()
        X = {pid: [m.NewBoolVar(f"x{pid}_{k}") for k in range(len(opts[pid]))] for pid in ids}
        for pid in ids:
            m.AddExactlyOne(X[pid])
        n_forced = 0
        for (pi, pj, bad) in edges:
            if bad == "FORCED":
                ri = opts[pi].index(("rv", 0)); rj = opts[pj].index(("rv", 0))
                m.AddImplication(X[pi][ri].Not(), X[pj][rj])
                n_forced += 1
            else:
                for (x, y) in bad:
                    m.AddBoolOr([X[pi][x].Not(), X[pj][y].Not()])
        rv = {pid: X[pid][opts[pid].index(("rv", 0))] for pid in ids}
        # adj_i = 1 当且仅当选择了 df/dt（非恒等且非撤销）
        adjv = {pid: sum(X[pid][k] for k in range(len(opts[pid]))
                         if opts[pid][k][0] in ("df", "dt")) for pid in ids}
        R = m.NewIntVar(0, len(ids), "R")
        m.Add(R == sum(rv.values()))
        A = m.NewIntVar(0, len(ids), "A")
        m.Add(A == sum(adjv.values()))
        PL = m.NewIntVar(0, 4 * len(ids) * 200, "PL")
        m.Add(PL == sum(WP[pid[0]] * (2 * rv[pid] + adjv[pid]) for pid in ids))
        MG = m.NewIntVar(0, 20 * len(ids), "MG")
        m.Add(MG == sum(sum(abs(opts[pid][k][1]) * X[pid][k] for k in range(len(opts[pid]))
                            if opts[pid][k][0] in ("df", "dt")) for pid in ids))
        if extra_rev_cap is not None:
            m.Add(R <= extra_rev_cap)
        _hr = sum(1 for o in hint_acts.values() if o.get("revoke"))
        if hint_acts and (extra_rev_cap is None or extra_rev_cap >= _hr):
            for pid, o in hint_acts.items():
                if pid not in X:
                    continue
                key = ("rv", 0) if o.get("revoke") else next(((k, int(v)) for k, v in o.items()), ("id", 0))
                if key in opts[pid]:
                    m.AddHint(X[pid][opts[pid].index(key)], 1)
        return m, X, (R, A, PL, MG)

    log, layers = [], {}

    def run(tag, locks, minimize, cap_R=None, limit=300, hint=None):
        """locks: dict of layer vars to pin (R/A/PL); minimize: 'R'|'A'|'PL'|'MG'; cap_R: Σr<=k probe."""
        m, X, (R, A, PL, MG) = make_model(extra_rev_cap=cap_R)
        var = {"R": R, "A": A, "PL": PL, "MG": MG}
        for k, v in (locks or {}).items():
            m.Add(var[k] == v)
        if hint:
            for pid, kv in hint.items():
                key = tuple(kv)
                if key in opts[pid]:
                    m.AddHint(X[pid][opts[pid].index(key)], 1)
        if minimize is not None:
            m.Minimize(var[minimize])
        sv = cp_model.CpSolver()
        sv.parameters.max_time_in_seconds = float(limit)
        sv.parameters.num_search_workers = workers
        st = sv.Solve(m)
        name = sv.StatusName(st)
        rec = {"layer": tag, "status": name, "locks": {k: v for k, v in (locks or {}).items()},
               "min": minimize, "cap_R": cap_R, "wall_cum": round(tm.el(), 1)}
        sel = None
        if name in ("OPTIMAL", "FEASIBLE"):
            rec.update({"objective": sv.ObjectiveValue(),
                        "best_bound": sv.BestObjectiveBound(),
                        "solution_tuple": [sv.Value(R), sv.Value(A), sv.Value(PL), sv.Value(MG)]})
            sel = {}
            for pid in ids:
                for k, xv in enumerate(X[pid]):
                    if sv.Value(xv):
                        sel[pid] = list(opts[pid][k])
        log.append(rec)
        return name, sel, rec

    # L1：min Σr
    st1, sel1, rec1 = run("L1_minR", None, "R", limit=BUD["l1"])
    incumbent = sel1
    rev_star = rec1.get("solution_tuple", [None, 0, 0, 0])[0] if sel1 else None
    # 证书与下降阶梯：CP 传播界 + Σr≤0 INFEASIBLE + 可行 cap 下降搜索
    cert = []
    lb = 0
    if rec1.get("best_bound") is not None:
        lb = int(rec1["best_bound"])
        cert.append({"cap": None, "source": "cpsat_bound_L1", "status": st1, "lb": lb})
    st0, _, _ = run("ladder_Rle0", None, None, cap_R=0, limit=BUD["ladder"])
    cert.append({"cap": 0, "status": st0, "source": "infeasibility_probe"})
    lb = max(lb, 1 if st0 == "INFEASIBLE" else 0)
    closed = (rev_star is not None and rev_star == lb)
    budget_left = lambda: tm.el() < BUD["l1"] + BUD["ladder"]
    cap = (rev_star - 1) if rev_star is not None else None
    while cap is not None and cap >= lb and budget_left() and not closed:
        stc, selc, rec2 = run(f"ladder_Rle{cap}", None, "R", cap_R=cap,
                              limit=min(60, BUD["l1"] + BUD["ladder"] - tm.el()),
                              hint=incumbent)
        if stc == "INFEASIBLE":
            cert.append({"cap": cap, "status": stc, "source": "infeasibility_probe"})
            lb = max(lb, cap + 1)
            break
        if selc:
            cert.append({"cap": cap, "status": stc, "source": "feasible_better",
                          "found_rev": rec2["solution_tuple"][0]})
            incumbent = selc
            rev_star = rec2["solution_tuple"][0]
            if rec2.get("best_bound") is not None:
                lb = max(lb, int(rec2["best_bound"]))
            cap = rev_star - 1
            closed = rev_star == lb
            continue
        cert.append({"cap": cap, "status": stc, "source": "probe_timeout"})
        break
    final_sel = incumbent
    if rev_star is not None:
        closed = rev_star == lb
        st2, sel2, rec2 = run("L2_minA", {"R": rev_star}, "A", limit=BUD["l2"])
        if sel2:
            final_sel = sel2
        adj_star = rec2.get("solution_tuple", [rev_star, None, None, None])[1] if sel2 else None
        if adj_star is not None:
            st3, sel3, rec3 = run("L3_minPL", {"R": rev_star, "A": adj_star}, "PL", limit=BUD["l3"])
            if sel3:
                final_sel = sel3
            pl_star = rec3.get("solution_tuple", [None, None, None, None])[2] if sel3 else None
            if pl_star is not None:
                st4, sel4, rec4 = run("L4_minMG", {"R": rev_star, "A": adj_star, "PL": pl_star},
                                      "MG", limit=BUD["l4"])
                if sel4:
                    final_sel = sel4
    actions = {}
    for pid, (kind, v) in ((p, tuple(o)) for p, o in (final_sel or {}).items()):
        if kind == "rv":
            actions[pid] = {"revoke": True}
        elif kind != "id":
            actions[pid] = {kind: v}
    if not final_sel:
        raise SystemExit("FAIL-CLOSED: no incumbent (L1 empty) — refusing empty authoritative payload")

    def tup(acts):
        rev = adj = pl = mg = 0
        for pid, o in acts.items():
            c = pid[0]
            if o.get("revoke"):
                rev += 1; pl += 2 * WP[c]
            elif o:
                adj += 1; pl += WP[c]
                mg += sum(abs(int(vv)) for vv in o.values())
        return [rev, adj, pl, mg]
    # 独立重算 tuple（不依赖模型变量）
    t_final = tup(actions)
    scalar = 10**12 * t_final[0] + 10**8 * t_final[1] + 10**4 * t_final[2] + t_final[3]
    res = {"question_id": "Q2", "variant": "cpsat_lex", "workers": workers,
           "hint_source": hint_src, "hint_role": "search_hint_only_all_figures_recomputed",
           "gstar_edges": len(edges), "forced_edges": sum(1 for e in edges if e[2] == "FORCED"),
           "options_total": sum(len(v) for v in opts.values()),
           "actions": actions, "objective_tuple": t_final, "objective_scalar": scalar,
           "revocation": {"upper_incumbent": t_final[0], "proven_lb": lb, "lb_closed": closed,
                           "certificates": cert, "ladder_log": log},
           "layers": log}
    emit(a.output_dir, res, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "stages_complete_or_budget", "evaluator_calls": len(log),
                             "budget_class": a.budget_class, "seed": a.seed,
                             "scenario": a.scenario, "parameter": param})


if __name__ == "__main__":
    main()
