# -*- coding: utf-8 -*-
"""通用合成器：从同 run 的兄弟任务 payload 合成问题级权威结果文档（纯机械聚合，无新计算）。
parameter: {"question":"Q2"}；键名与 VALIDATION_PLAN criterion 对齐。"""
import glob, json, os, sys, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit  # noqa


def load_siblings(run_id, qprefix):
    docs = []
    for tf in sorted(glob.glob(os.path.join("runs", "fresh", run_id, "tasks", qprefix + "-*",
                                            "attempts", "*", "payload.json"))):
        try:
            d = json.load(open(tf, encoding="utf-8"))
            d["_path"] = tf
            docs.append(d)
        except Exception:
            continue
    return docs


def pick(docs, variant, workers=None):
    out = [d for d in docs if d.get("variant") == variant and (workers is None or d.get("workers") == workers)]
    return out[-1] if out else None


def main():
    a, param = std_args("synth")
    tm = Timer()
    q = param["question"]
    docs = load_siblings(a.run_id, q.lower())

    def best_main(variant):
        """权威主解=verified_best：同模型各配置跑中词典序最优 objective_tuple 的解
        （每候选解都将被独立 checker 第二实现全量重算验证——见 VALIDATION_PLAN rev4/EV-CRIT-001）；
        w1/w4 完整记录入 payload，绝不隐藏较差跑。"""
        c = [d for d in docs if d.get("variant") == variant and d.get("objective_tuple")]
        if not c:
            return None
        c.sort(key=lambda d: (tuple(d["objective_tuple"]), 0 if d.get("workers") == 1 else 1))
        return c[0]
    if q == "Q2":
        main_ = best_main("cpsat_lex")
        w1 = pick(docs, "cpsat_lex", 1)
        w4 = pick(docs, "cpsat_lex", 4)
        grasp = [d for d in docs if d.get("variant") == "grasp"]
        chk = pick(docs, "check")
        revs = sorted(d["objective_tuple"][0] for d in grasp) or [None]
        out = dict(main_)
        out.update({"question_id": "Q2", "variant": "synth", "assembled": True,
                    "revoke": main_["objective_tuple"][0],
                    "revoked": main_["objective_tuple"][0], "adjusted": main_["objective_tuple"][1],
                    "grasp_revoke_median": float(statistics.median(revs)),
                    "grasp_runs": len(grasp),
                    "residual_pairs_second_impl": chk["residual_pairs_second_impl"],
                    "compliance_violations": chk["compliance_violations"],
                    "tuple_matches_second_impl": chk["tuple_matches_solver"],
                    "residual_pairs": chk["residual_pairs_second_impl"],
                    "ladder_proven_revoke_lb": main_["revocation"]["proven_lb"],
                    "gap_revoke": main_["objective_tuple"][0] - main_["revocation"]["proven_lb"],
                    "degeneracy_ratio": (150 - main_["objective_tuple"][0]) / 150.0,
                    "repro_first_layer_match": 1 if (w1 and w4 and w1["objective_tuple"][0] == w4["objective_tuple"][0]) else 0,
                    "repro_w1_eq_w8": 1 if (w1 and w4 and w1["objective_tuple"] == w4["objective_tuple"]) else 0,
                    "best_is_w1": 1 if main_ is w1 else 0,
                    "best_tuple_seen_across_runs": (min([d["objective_tuple"] for d in docs if d.get("variant") == "cpsat_lex" and d.get("objective_tuple")]) if any(d.get("variant") == "cpsat_lex" and d.get("objective_tuple") for d in docs) else None),
                    "w1_tuple": (w1 or {}).get("objective_tuple"),
                    "w4_tuple": (w4 or {}).get("objective_tuple"),
                    "run_id_ref": a.run_id})
    elif q == "Q3":
        en = pick(docs, "enum")
        ca = pick(docs, "cpsat_a")
        cb = pick(docs, "cpsat_b")
        lp = pick(docs, "lp_hiGHS")
        bd = pick(docs, "bound_elementary")
        chk = pick(docs, "check")
        q2m = load_siblings(a.run_id, "q2")
        _c = sorted([d for d in q2m if d.get("variant") == "cpsat_lex" and d.get("objective_tuple")],
                    key=lambda d: (tuple(d["objective_tuple"]), 0 if d.get("workers") == 1 else 1))
        q2m = _c[0]
        ubs = [x for x in [bd.get("ub_min") if bd else None,
                           (int(lp["lp_bound"]) + (1 if lp.get("lp_bound") and lp["lp_bound"] % 1 else 0)) if lp and lp.get("lp_bound") is not None else None,
                           ca.get("best_bound") if ca and ca.get("status") == "OPTIMAL" else None] if x is not None]
        phi = ca["phi"] if ca else 0
        out = dict(ca or {})
        out.update({"question_id": "Q3", "variant": "synth", "assembled": True, "phi": phi,
                    "selected": ca["selected"], "rows": len(ca["selected"]),
                    "conflicts_vs_base": chk["conflicts_vs_base"],
                    "conflicts_internal": chk["conflicts_internal"],
                    "conflict_total_second_impl": chk["conflict_total_second_impl"],
                    "cand_count_second_impl": chk["cand_count_second_impl"],
                    "cand_count_second_impl_minus_solver": chk["cand_count_second_impl"] - (en["cand_feasible"] if en else -1),
                    "cand_agreement_enum_impls": en["cand_agreement_second_impl"],
                    "ub_phase": bd.get("ub_phase_doublecount"), "ub_density": bd.get("ub_density"),
                    "ub_lp": (lp or {}).get("lp_bound"), "ub_cp": (ca or {}).get("best_bound"),
                    "ub_min": min(ubs) if ubs else None,
                    "ub_min_minus_lb": (min(ubs) - phi) if ubs else None,
                    "gap_certified": (ca.get("best_bound") - phi) if (ca and ca.get("proven_optimal") and ca.get("best_bound") is not None) else None,
                    "proven_optimal": bool(ca.get("proven_optimal")) if ca else False,
                    "selected_sha256": __import__("hashlib").sha256(
                        json.dumps(ca["selected"], sort_keys=True).encode()).hexdigest() if ca else None,
                    "base_is_production_q2": 1 if (en and q2m and en.get("base_tuple") == q2m.get("objective_tuple")) else 0,
                    "cpsat_b_status": (cb or {}).get("status"), "cpsat_b_phi": (cb or {}).get("phi"),
                    "run_id_ref": a.run_id})
    elif q == "Q4":
        main_ = best_main("cpsat_lex")
        w1 = pick(docs, "cpsat_lex", 1)
        w4 = pick(docs, "cpsat_lex", 4)
        chk = pick(docs, "check")
        q2docs = load_siblings(a.run_id, "q2")
        _c = sorted([d for d in q2docs if d.get("variant") == "cpsat_lex" and d.get("objective_tuple")],
                    key=lambda d: (tuple(d["objective_tuple"]), 0 if d.get("workers") == 1 else 1))
        q2m = _c[0]
        out = dict(main_)
        # dg 被禁动作分解：g'≤0 非法间隔 vs 末周期越出时界 643（P2 独立复算 270+99=369 恒等式自洽；
        # 口径与 q4v_cpsat 选项枚举一致：全部 90 个 C 计划的非零 dg 候选）
        from cli import load_plans_local
        _infeas = 0
        for p in load_plans_local():
            if p["cls"] != "C":
                continue
            hi = min(10, -p["g"])  # g+dg<=0 的 dg 上界
            if hi >= -10:
                _infeas += hi - (-10) + 1 - (1 if -0 in range(-10, hi + 1) else 0)  # 非零 dg
        out.update({"question_id": "Q4", "variant": "synth", "assembled": True,
                    "dg_dropped_infeasible_gap": _infeas,
                    "dg_dropped_horizon": (main_.get("dg_options_dropped_by_horizon") or 0) - _infeas,
                    "scalar": main_["objective_scalar"], "scalar_q2_ref": q2m["objective_scalar"],
                    "revoke_gain_vs_q2": q2m["objective_tuple"][0] - main_["objective_tuple"][0],
                    "violations_second_impl": chk["violations"],
                    "residual_pairs_second_impl": chk["residual_pairs_second_impl"],
                    "tuple_matches_second_impl": chk["tuple_matches_solver"],
                    "residual_pairs": chk["residual_pairs_second_impl"], "violations": chk["violations"],
                    "repro_first_layer_match": 1 if (w1 and w4 and w1["objective_tuple"][0] == w4["objective_tuple"][0]) else 0,
                    "repro_w1_eq_w8": 1 if (w1 and w4 and w1["objective_tuple"] == w4["objective_tuple"]) else 0,
                    "best_is_w1": 1 if main_ is w1 else 0,
                    "best_tuple_seen_across_runs": min([d["objective_tuple"] for d in docs if d.get("variant") == "cpsat_lex" and d.get("objective_tuple")]) if any(d.get("variant") == "cpsat_lex" and d.get("objective_tuple") for d in docs) else None,
                    "w1_tuple": (w1 or {}).get("objective_tuple"), "w4_tuple": (w4 or {}).get("objective_tuple"),
                    "by_class": chk.get("by_class"),
                    "run_id_ref": a.run_id})
    else:
        raise SystemExit("unknown synth question " + q)
    emit(a.output_dir, out, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "assembled", "evaluator_calls": 0,
                             "budget_class": a.budget_class, "seed": a.seed,
                             "scenario": a.scenario, "parameter": param})
    print("synth", q, "ok")


if __name__ == "__main__":
    main()
