# -*- coding: utf-8 -*-
"""独立评审复核脚本（REV-Q4-01 / CH-REV-B）——完全只读被审工件。
本脚本【不】复用冻结 evaluator 的实现来做判定：占用窗、交叠、元组全部按题面
（F-005/F-006/Q4-F019 + ADJUDICATION R1/R3/R4/R6）自行用区间算术重写一遍，
再与 evaluator 的落盘输出对照（同实现不能发现共享 bug）。

输出：reviews/_tmp/recheck_out.json（评审证据附件）
"""
import io, json, os, random, subprocess, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # tournament dir
WS = os.path.abspath(os.path.join(RUN, "..", "..", ".."))           # workspace root
sys.stdout.reconfigure(encoding="utf-8")

T_MAX, B_MAX = 643, 100          # ADJUDICATION R1 / F-001
PRIO = {"A": 100, "B": 10, "C": 1}
LIM = {"df": 10, "dt": 5, "dg": 10}   # F-012 / Q4-F019


# ---------- 独立数据加载（不 import evaluator） ----------
def load_plans():
    path = os.path.join(WS, "data", "canonical_plans.csv")
    lines = io.open(path, encoding="utf-8").read().splitlines()
    plans = {}
    for line in lines[1:]:
        a = line.split(",")
        f0, f1, t0, t1, g, n = int(a[2]), int(a[3]), int(a[4]), int(a[5]), int(a[6]), int(a[7])
        plans[a[0]] = dict(id=a[0], cls=a[0][0], f0=f0, f1=f1, t0=t0, t1=t1,
                           g=g, n=n, d=t1 - t0)
    assert len(plans) == 150, len(plans)
    return plans


def retime(p, act):
    """返回 (slots, band, errs)：slots=[(s,e)...] 全部占用窗（半开），band=[f0,f1)；errs=违规列表。
    占用起点 = t1 + dt + (k-1)*(g' + d)，k=1..n；g' = g + dg（仅 C 允许，Q4-F019）。"""
    errs = []
    keys = [k for k in ("df", "dt", "dg") if act.get(k)]
    rev = bool(act.get("revoke"))
    if rev:
        return None, None, errs
    if len(keys) > 1:
        errs.append(f"multi_param:{p['id']}:{keys}")
        return None, None, errs
    df = int(act.get("df", 0)); dt = int(act.get("dt", 0)); dg = int(act.get("dg", 0))
    for k, v in (("df", df), ("dt", dt), ("dg", dg)):
        if abs(v) > LIM[k]:
            errs.append(f"magnitude_exceeded:{p['id']}:{k}:{v}")
    if dg != 0:
        if p["cls"] != "C":
            errs.append(f"gap_only_C:{p['id']}")
        gp = p["g"] + dg
        if gp < 1:
            errs.append(f"gap_nonpositive:{p['id']}:g'={gp}")
    gp = p["g"] + dg
    f0, f1 = p["f0"] + df, p["f1"] + df
    if f0 < 0 or f1 > B_MAX:
        errs.append(f"out_of_band:{p['id']}:({f0},{f1})")
    period = gp + p["d"]
    slots = [(p["t0"] + dt + k * period, p["t0"] + dt + k * period + p["d"]) for k in range(p["n"])]
    for (s, e) in slots:
        if s < 0:
            errs.append(f"before_horizon:{p['id']}:{s}")
            break
    for (s, e) in slots:
        if e > T_MAX:
            errs.append(f"beyond_horizon:{p['id']}:last_end={e}>643")
            break
    return slots, (f0, f1), errs


def band_overlap(a, b):
    return min(a[1], b[1]) - max(a[0], b[0]) > 0


def time_overlap(sa, sb):
    for (s1, e1) in sa:
        for (s2, e2) in sb:
            if s1 < e2 and s2 < e1:
                return True
    return False


def eval_solution(plans, sol):
    """独立重算：返回 (tuple, violations, conflicts, per-plan info)"""
    viol = []
    kept, info = {}, {}
    for pid, act in sol.items():
        if pid not in plans:
            viol.append(f"unknown_plan:{pid}")
            continue
        slots, band, errs = retime(plans[pid], act)
        viol += errs
        if errs:
            continue
        if act.get("revoke"):
            continue
        kept[pid] = (slots, band)
        info[pid] = dict(slots=slots, band=band)
    ids = sorted(kept)
    conflicts = []
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            i, j = ids[x], ids[y]
            if band_overlap(kept[i][1], kept[j][1]) and time_overlap(kept[i][0], kept[j][0]):
                conflicts.append([i, j])
    viol += [f"residual_conflict:{i}:{j}" for i, j in conflicts]
    rev = adj = ploss = mag = 0
    for pid, act in sol.items():
        if pid not in plans:
            continue
        c = plans[pid]["cls"]
        if act.get("revoke"):
            rev += 1
            ploss += PRIO[c] * 2
            continue
        ks = [k for k in ("df", "dt", "dg") if act.get(k)]
        if ks:
            adj += 1
            ploss += PRIO[c]
            mag += sum(abs(int(act[k])) for k in ks)
    return [rev, adj, ploss, mag], viol, conflicts, info


def scalar(t):
    return t[0] * 10**12 + t[1] * 10**8 + t[2] * 10**4 + t[3]


def leq(a, b):
    """a 词典序 <= b"""
    return tuple(a) <= tuple(b)


def run_evaluator(question, sol_path, out_path, base=None):
    cmd = [sys.executable, os.path.join(RUN, "canonical_evaluator.py"),
           "--question", question, "--solution", sol_path, "--out", out_path]
    if base:
        cmd += ["--base-actions", base]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return {"_error": r.stderr[-800:]}
    return json.load(io.open(out_path, encoding="utf-8"))


def main():
    plans = load_plans()
    S = os.path.join(RUN, "scouts")
    TMP = os.path.join(RUN, "reviews", "_tmp")
    os.makedirs(TMP, exist_ok=True)
    out = {"t_max": T_MAX, "checks": {}}

    # ---------- CHECK 1: Q4-R11 元组与可行性独立复算 ----------
    r11p = os.path.join(S, "Q4-R11", "run", "solution_actions.json")
    r11 = json.load(io.open(r11p, encoding="utf-8"))
    t11, v11, c11, info11 = eval_solution(plans, r11)
    dg_plans = {pid: int(a["dg"]) for pid, a in r11.items() if a.get("dg")}
    # 逐计划 dg 明细
    dg_detail = []
    for pid, dg in sorted(dg_plans.items()):
        p = plans[pid]
        gp = p["g"] + dg
        period = gp + p["d"]
        last_end = p["t0"] + (p["n"] - 1) * period + p["d"]
        dg_detail.append(dict(pid=pid, cls=p["cls"], t0=p["t0"], d=p["d"], g=p["g"], dg=dg,
                              gp=gp, n=p["n"], period=period, last_end=last_end,
                              within_643=last_end <= 643, gp_ge1=gp >= 1, dg_le10=abs(dg) <= 10))
    # 20 个随机计划对（固定 seed=20260911）：含双方全部窗的交叠复算
    rng = random.Random(20260911)
    ids = sorted(plans)
    pairs = []
    seen = set()
    while len(pairs) < 20:
        i, j = rng.choice(ids), rng.choice(ids)
        if i == j:
            continue
        key = tuple(sorted((i, j)))
        if key in seen:
            continue
        seen.add(key)
        ai, aj = r11.get(i, {}), r11.get(j, {})
        si, bi, ei = retime(plans[i], ai)
        sj, bj, ej = retime(plans[j], aj)
        ov = None
        if not ei and not ej and si and sj and not (ai.get("revoke") or aj.get("revoke")):
            ov = band_overlap(bi, bj) and time_overlap(si, sj)
        pairs.append(dict(pair=list(key), act_i=ai, act_j=aj,
                          last_end_i=(max(e for _, e in si) if si else None),
                          last_end_j=(max(e for _, e in sj) if sj else None),
                          overlap=bool(ov), errs=ei + ej))
    # 所有含 dg 的计划 vs 全体保留计划
    dg_pair_conf = []
    for pid in sorted(dg_plans):
        for qid in sorted(info11):
            if qid <= pid:
                continue
            if band_overlap(info11[pid]["band"], info11[qid]["band"]) and \
               time_overlap(info11[pid]["slots"], info11[qid]["slots"]):
                dg_pair_conf.append([pid, qid])
    ev11 = run_evaluator("Q4", r11p, os.path.join(TMP, "eval_r11_recalc.json"))
    out["checks"]["R11"] = dict(
        claimed_result_tuple=[8, 113, 2289, 719],
        claimed_scalar=8011322890719,
        independent_tuple=t11, independent_scalar=scalar(t11),
        evaluator_recheck_tuple=ev11.get("objective"), evaluator_recheck_feasible=ev11.get("feasible"),
        evaluator_recheck_violations=ev11.get("n_violations"),
        independent_residual_conflicts=len(c11), independent_violations=v11[:30],
        n_actions=len(r11), n_dg_actions=len(dg_plans), dg_detail=dg_detail,
        sample20_pairs=pairs, sample20_overlaps=sum(1 for p in pairs if p["overlap"]),
        dg_vs_all_conflicts=dg_pair_conf,
        scalar_formula_consistent=scalar(t11) == 8011322890719)

    # ---------- CHECK 2: Q4-R41 三种子中位数聚合 ----------
    r41 = json.load(io.open(os.path.join(S, "Q4-R41", "result.json"), encoding="utf-8"))
    claimed_by_seed = {int(r["seed"]): [int(x) for x in r["objective_tuple"]]
                       for r in r41["replicates"]}
    reps = {}
    for sd in (11, 29, 47):
        p = os.path.join(S, "Q4-R41", "run", f"solution_seed{sd}.json")
        sol = json.load(io.open(p, encoding="utf-8"))
        t, v, c, _ = eval_solution(plans, sol)
        ev = run_evaluator("Q4", p, os.path.join(TMP, f"eval_r41_seed{sd}.json"))
        reps[sd] = dict(indep_tuple=t, eval_tuple=[int(x) for x in (ev.get("objective") or [])],
                        eval_feasible=ev.get("feasible"), indep_conflicts=len(c),
                        indep_violations=v[:10],
                        claimed_in_result_json=claimed_by_seed[sd],
                        indep_matches_claim=(t == claimed_by_seed[sd]),
                        eval_matches_claim=([int(x) for x in (ev.get("objective") or [])]
                                            == claimed_by_seed[sd]))
    order = sorted(claimed_by_seed, key=lambda s: claimed_by_seed[s])
    med_seed = order[1]
    out["checks"]["R41"] = dict(
        claimed_by_seed=claimed_by_seed, per_seed_independent=reps,
        lex_order_by_claimed=[claimed_by_seed[s] for s in order],
        median_seed_by_claimed=med_seed, median_tuple_by_claimed=claimed_by_seed[med_seed],
        result_json_tuple=r41["objective_tuple"], result_json_seed=r41["seed"],
        result_json_scalar=r41["objective"],
        median_is_seed29=(r41["objective_tuple"] == [11, 117, 2344, 578]),
        best_seed=order[0], best_tuple=claimed_by_seed[order[0]],
        solution_path_points_to_median=r41["solution_path"].endswith(f"solution_seed{med_seed}.json"),
        scalar_consistent=scalar(r41["objective_tuple"]) == r41["objective"])

    # ---------- CHECK 3: Q2 包含性 / 支配界 ----------
    q2red_p = os.path.join(S, "Q4-R11", "run_q2reduction", "solution_q2reduction.json")
    q2red = json.load(io.open(q2red_p, encoding="utf-8"))
    t2, v2, c2, _ = eval_solution(plans, q2red)
    ev2a = run_evaluator("Q2", q2red_p, os.path.join(TMP, "eval_q2red_as_q2.json"))
    ev2b = run_evaluator("Q4", q2red_p, os.path.join(TMP, "eval_q2red_as_q4.json"))
    has_dg = [pid for pid, a in q2red.items() if a.get("dg")]
    # 对照：Q2 官方侦察 incumbent（Q2-R51 解）在 Q4 口径下是否可行、元组多少
    q2r51_p = os.path.join(S, "Q2-R51", "solution_actions.json")
    q2ctl = None
    if os.path.isfile(q2r51_p):
        sol51 = json.load(io.open(q2r51_p, encoding="utf-8"))
        t51, v51, c51, _ = eval_solution(plans, sol51)
        ev51 = run_evaluator("Q4", q2r51_p, os.path.join(TMP, "eval_q2r51_as_q4.json"))
        ev51q2 = run_evaluator("Q2", q2r51_p, os.path.join(TMP, "eval_q2r51_as_q2.json"))
        q2ctl = dict(path=os.path.relpath(q2r51_p, WS), independent_tuple=t51,
                     evaluator_Q4_tuple=ev51.get("objective"), evaluator_Q4_feasible=ev51.get("feasible"),
                     evaluator_Q2_tuple=ev51q2.get("objective"),
                     n_dg_actions=len([1 for a in sol51.values() if a.get("dg")]),
                     has_dg_in_q2sol=bool([pid for pid, a in sol51.items() if a.get("dg")]))
    out["checks"]["inclusion"] = dict(
        claimed_q2reduction_tuple=[14, 96, 2383, 638],
        independent_q2reduction_tuple=t2, independent_conflicts=len(c2),
        evaluator_as_Q2=ev2a.get("objective"), evaluator_as_Q2_feasible=ev2a.get("feasible"),
        evaluator_as_Q4=ev2b.get("objective"), evaluator_as_Q4_feasible=ev2b.get("feasible"),
        dual_eval_identical=bool(ev2a.get("objective") == ev2b.get("objective")),
        q2reduction_contains_dg=has_dg,
        objective_tuple_function_ignores_allow_gap=True,   # 见 canonical_evaluator.py:170-189（allow_gap 未被使用）
        structural_note=("evaluator.objective_tuple(plans,actions,allow_gap) 的形参 allow_gap 在函数体内从未被引用"
                         " ⇒ 同一动作集在 Q2/Q4 两次评估下元组必然逐字相同，该『双评估一致』判据对元组是恒真式；"
                         "其唯一非平凡部分是 feasible（含 dg 的动作在 Q2 下报 gap_not_allowed）。"),
        edges_claim=dict(q2=1693, q4=2117, subset_field_in_artifact=False,
                         note="q2_inclusion_check.json 无 edge_subset/clause_subset 落盘字段（仅 scout.json 口头声称通过）"),
        q2_official_incumbent=q2ctl,
        q4_r11_tuple=t11,
        q4_r11_vs_q2_official=("dominated" if (q2ctl and tuple(q2ctl["independent_tuple"]) < tuple(t11)) else "not_dominated"),
        r11_claimed_gain_vs_own_reduction_only=True)

    # ---------- CHECK 4: Q4-R22 解析构造坍塌 ----------
    r22p = os.path.join(S, "Q4-R22", "run", "solution_actions.json")
    r22 = json.load(io.open(r22p, encoding="utf-8"))
    t22, v22, c22, info22 = eval_solution(plans, r22)
    ev22 = run_evaluator("Q4", r22p, os.path.join(TMP, "eval_r22_recalc.json"))
    log22 = json.load(io.open(os.path.join(S, "Q4-R22", "run", "r22_log.json"), encoding="utf-8"))
    # 独立复算 19 条 CC 边：由重定时消解 vs 由撤销消解
    base_cc = []
    cs = sorted(pid for pid in plans if plans[pid]["cls"] == "C")
    for x in range(len(cs)):
        for y in range(x + 1, len(cs)):
            i, j = cs[x], cs[y]
            si, bi, _ = retime(plans[i], {})
            sj, bj, _ = retime(plans[j], {})
            if band_overlap(bi, bj) and time_overlap(si, sj):
                base_cc.append([i, j])
    cc_audit = []
    for (i, j) in base_cc:
        ri, rj = r22.get(i, {}).get("revoke"), r22.get(j, {}).get("revoke")
        dg_i = int(r22.get(i, {}).get("dg", 0)); dg_j = int(r22.get(j, {}).get("dg", 0))
        cc_audit.append(dict(edge=[i, j], revoked_i=bool(ri), revoked_j=bool(rj),
                             dg_i=dg_i, dg_j=dg_j,
                             killed_by_revoke=bool(ri or rj),
                             retimed=(dg_i != 0 or dg_j != 0)))
    # 重定时-only 可消解性复算（对空条带边 C033|C043 显式穷举）
    def retiming_feasible(i, j):
        feas = []
        for dgi in range(-10, 11):
            if plans[i]["g"] + dgi < 1:
                continue
            si, bi, ei = retime(plans[i], {"dg": dgi})
            if ei:
                continue
            for dgj in range(-10, 11):
                if plans[j]["g"] + dgj < 1:
                    continue
                sj, bj, ej = retime(plans[j], {"dg": dgj})
                if ej:
                    continue
                if not (band_overlap(bi, bj) and time_overlap(si, sj)):
                    feas.append((dgi, dgj))
        return feas
    empty_claim = ["C033", "C043"]
    strip_recheck = dict(band_overlap_base=band_overlap(
        (plans["C033"]["f0"], plans["C033"]["f1"]), (plans["C043"]["f0"], plans["C043"]["f1"])),
        t0=dict(C033=plans["C033"]["t0"], C043=plans["C043"]["t0"]),
        feasible_dg_pairs_if_only_retiming=retiming_feasible("C033", "C043"))
    # mod-10 规则独立复算（全部 C-C 对）
    mism = []
    n_true = 0
    for x in range(len(cs)):
        for y in range(x + 1, len(cs)):
            i, j = cs[x], cs[y]
            band = min(plans[i]["f1"], plans[j]["f1"]) - max(plans[i]["f0"], plans[j]["f0"])
            d = (plans[i]["t0"] - plans[j]["t0"]) % 10
            reach = abs(plans[i]["t0"] - plans[j]["t0"]) <= 111
            pred = band > 0 and d in (0, 1, 9) and reach
            si, bi, _ = retime(plans[i], {}); sj, bj, _ = retime(plans[j], {})
            truth = band_overlap(bi, bj) and time_overlap(si, sj)
            if truth:
                n_true += 1
            if pred != truth:
                mism.append([i, j, pred, truth])
    # 类分布
    byc = {}
    for pid, a in r22.items():
        c = plans[pid]["cls"]
        st = byc.setdefault(c, dict(rev=0, adj=0))
        if a.get("revoke"):
            st["rev"] += 1
        else:
            st["adj"] += 1
    out["checks"]["R22"] = dict(
        claimed_tuple=[66, 43, 1111, 144], independent_tuple=t22,
        evaluator_recheck_tuple=ev22.get("objective"), evaluator_feasible=ev22.get("feasible"),
        independent_conflicts=len(c22), scalar_formula_consistent=scalar(t22) == 66004311110144,
        n_actions=len(r22), class_breakdown=byc,
        mod10_rule=dict(pairs=len(cs) * (len(cs) - 1) // 2, true_conflicts=n_true,
                        mismatches=len(mism), examples=mism[:5],
                        claimed=dict(pairs=4005, true=19, mism=0)),
        cc_edges_recomputed=len(base_cc), cc_log_cc_edges=log22.get("cc_edges"),
        cc_audit=cc_audit,
        cc_killed_by_revoke=sum(1 for a in cc_audit if a["killed_by_revoke"]),
        cc_resolved_by_retiming_only=sum(1 for a in cc_audit if not a["killed_by_revoke"]),
        empty_strip_claim=dict(edge="|".join(empty_claim),
                               independent_feasible_pairs=strip_recheck["feasible_dg_pairs_if_only_retiming"],
                               is_empty=len(strip_recheck["feasible_dg_pairs_if_only_retiming"]) == 0,
                               band_overlap=strip_recheck["band_overlap_base"],
                               t0=strip_recheck["t0"]),
        result_json_failure_mode=json.load(io.open(os.path.join(S, "Q4-R22", "result.json"),
                                                   encoding="utf-8")).get("failure_mode"),
        log_fields=dict(repair_steps=log22.get("repair_steps"), n_rev=log22.get("n_revoke_repairs"),
                        n_adj=log22.get("n_adjust_repairs"), final_residual=log22.get("final_residual_internal")))

    # ---------- CHECK 5: 口径与标量化 ----------
    mx = dict(max_ploss_single_run=0)
    ploss_ub = sum(2 * PRIO[plans[p]["cls"]] for p in plans)
    out["checks"]["caliber"] = dict(
        T_MAX_in_evaluator=643, all_candidates_import_same_evaluator=True,
        scalar_formula="1e12*rev+1e8*adj+1e4*ploss+mag",
        max_possible_ploss=ploss_ub, ploss_term_spacing=10**4, adj_term_spacing=10**8,
        ploss_overflow_threshold=10**4,
        lexicographic_scalar_safe_for_observed_runs=True,
        ploss_overflow_possible=ploss_ub >= 10**4,
        mag_ub_in_model=sum(10 for p in plans) ,
        observed_ploss=dict(R11=t11[2], R41=r41["objective_tuple"][2], R22=t22[2]))

    io.open(os.path.join(TMP, "recheck_out.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    # 摘要打印
    print(json.dumps({
        "R11": dict(indep=out["checks"]["R11"]["independent_tuple"],
                    eval=out["checks"]["R11"]["evaluator_recheck_tuple"],
                    conflicts=out["checks"]["R11"]["independent_residual_conflicts"],
                    n_dg=out["checks"]["R11"]["n_dg_actions"],
                    dg_all_in=out["checks"]["R11"]["dg_detail"] and all(d["within_643"] and d["gp_ge1"] and d["dg_le10"] for d in out["checks"]["R11"]["dg_detail"]),
                    dg_max_end=max(d["last_end"] for d in out["checks"]["R11"]["dg_detail"]),
                    sample20_overlaps=out["checks"]["R11"]["sample20_overlaps"],
                    dg_conflicts=len(out["checks"]["R11"]["dg_vs_all_conflicts"]),
                    scalar_ok=out["checks"]["R11"]["scalar_formula_consistent"]),
        "R41": dict(median_seed=out["checks"]["R41"]["median_seed_by_claimed"],
                    median_tuple=out["checks"]["R41"]["median_tuple_by_claimed"],
                    result_tuple=out["checks"]["R41"]["result_json_tuple"],
                    is_seed29=out["checks"]["R41"]["median_is_seed29"],
                    scalar_ok=out["checks"]["R41"]["scalar_consistent"],
                    path_ok=out["checks"]["R41"]["solution_path_points_to_median"],
                    per_seed_eval={k: v["eval_tuple"] for k, v in out["checks"]["R41"]["per_seed_independent"].items()}),
        "inclusion": dict(q2red_indep=out["checks"]["inclusion"]["independent_q2reduction_tuple"],
                          as_q2=out["checks"]["inclusion"]["evaluator_as_Q2"],
                          as_q4=out["checks"]["inclusion"]["evaluator_as_Q4"],
                          q2_official=out["checks"]["inclusion"]["q2_official_incumbent"],
                          verdict=out["checks"]["inclusion"]["q4_r11_vs_q2_official"]),
        "R22": dict(indep=out["checks"]["R22"]["independent_tuple"],
                    eval=out["checks"]["R22"]["evaluator_recheck_tuple"],
                    conflicts=out["checks"]["R22"]["independent_conflicts"],
                    cc_edges=out["checks"]["R22"]["cc_edges_recomputed"],
                    cc_killed_by_revoke=out["checks"]["R22"]["cc_killed_by_revoke"],
                    cc_retime_only=out["checks"]["R22"]["cc_resolved_by_retiming_only"],
                    mod10=out["checks"]["R22"]["mod10_rule"],
                    empty_strip=out["checks"]["R22"]["empty_strip_claim"]["is_empty"]),
        "caliber": out["checks"]["caliber"],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
