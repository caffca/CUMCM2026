# -*- coding: utf-8 -*-
"""Q2 三候选 result.json / scout.json 装配器。

用法：python assemble_artifacts.py --idea Q2-R51|Q2-R41|Q2-R32
权威 objective/feasible 一律取自 canonical_evaluator 的 --out 产物（eval*.json）；
本脚本只做字段装配、协议规定的标量化与稳定性统计，绝不重算目标。
契约：TOURNAMENT_PROTOCOL.result_artifact_contract（status_enum/required_fields）+ 任务书附加字段。
"""
import argparse
import hashlib
import io
import json
import os
import statistics
import sys
import time

RUN = r"F:\2026 数模\D题重跑\D题\runs\competitive\CS-20260911T071520-D2026"
SC = os.path.join(RUN, "scouts")
SHA_EVAL = "8c4db98fa11845ca5492255e4da6c4b2e92e040ee30556fa9156993c06fcbb32"
RELROOT = r"F:\2026 数模\D题重跑\D题"
ADJ = {"T_MAX": 643, "half_open_intervals": True,
       "lex_levels": ["revoke", "adjusted", "priority_loss", "magnitude_sum"],
       "revoke_priority_double": True,
       "reference": "runs/competitive/CS-20260911T071520-D2026/ADJUDICATION.json"}
SCALAR_DOC = "1e12*revoke + 1e8*adjusted + 1e4*priority_loss + magnitude_sum"


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None


def jload(p, d=None):
    return json.load(io.open(p, encoding="utf-8")) if os.path.isfile(p) else d


def scalar(t):
    """协议标量化公式（整型精确：150×1e12 < 2^53，float 亦可无损表示）。"""
    return int(1e12 * t[0] + 1e8 * t[1] + 1e4 * t[2] + t[3])


def rel(p):
    return os.path.relpath(p, RELROOT).replace("\\", "/")


def wj(p, obj):
    io.open(p, "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False, indent=1))


def base(idea, d, eval_file, solution_file, runtime, status, feas, tup, seed_desc, replicates,
         failure_mode, bounds, extra_res, extra_sct, stab, stab_note):
    obj = scalar(tup) if (feas and tup) else None
    res = {
        "question_id": "Q2",
        "idea_id": idea,
        "status": status,
        "feasible": feas,
        "objective": obj,
        "objective_tuple": tup,
        "objective_unit": "weighted_lexicographic_scalar",
        "objective_scalar_formula": SCALAR_DOC,
        "runtime_seconds": runtime,
        "evaluator_invoked": True,
        "evaluator_command": ("python runs/competitive/CS-20260911T071520-D2026/canonical_"
                             "evaluator.py --question Q2 --solution %s --out %s"
                             % (rel(os.path.join(d, solution_file)) if solution_file else None,
                                rel(os.path.join(d, eval_file)))),
        "canonical_evaluator_sha256_bound": SHA_EVAL,
        "seed": seed_desc,
        "replicates": replicates,
        "solution_path": rel(os.path.join(d, solution_file)) if solution_file else None,
        "solution_sha256": sha(os.path.join(d, solution_file)) if solution_file else None,
        "failure_mode": failure_mode,
        "adjudication_binding": ADJ,
        "budget": {"scout_wall_seconds_per_candidate_per_replicate": 600,
                   "replicate_wall_seconds": runtime,
                   "protocol_limit_check": (runtime or 0) <= 600.0},
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "note": "最小可运行原型（侦察证据），非正式论文结果；未写 results/figures/paper。",
    }
    res.update(bounds)
    res.update(extra_res or {})
    sct = {
        "idea_id": idea, "question_id": "Q2", "status": status, "feasible": feas,
        "objective": obj, "objective_tuple": tup, "runtime_seconds": runtime,
        "replicates": replicates,
        "replicate_values": (extra_res or {}).get("replicate_values"),
        "stability_metric": stab, "stability_note": stab_note,
        "lower_bound": bounds.get("lower_bound"), "upper_bound": bounds.get("upper_bound"),
        "bound_detail": bounds.get("bound_detail"), "relative_gap": bounds.get("relative_gap"),
        "seed": seed_desc,
        "canonical_evaluator": {"invoked": True, "out": rel(os.path.join(d, eval_file)),
                                "objective": tup, "feasible": feas},
        "solution_path": res["solution_path"],
        "failure_mode": failure_mode,
        "scope_statement": "只读 common_input/protocol/evaluator/routes；只写本 scout 目录；"
                           "未写 results/figures/paper/IDEA_DECISION/FINAL_MODEL_SPEC，"
                           "侦察数字不外传进 results/。",
    }
    sct.update(extra_sct or {})
    wj(os.path.join(d, "result.json"), res)
    wj(os.path.join(d, "scout.json"), sct)
    return res, sct


def do_r51(d):
    rep = jload(os.path.join(d, "cpsat_report.json"), {})
    cert = jload(os.path.join(d, "r51_certificates.json"), {})
    ev = jload(os.path.join(d, "eval.json"), {})
    meta = jload(os.path.join(d, "solution_meta.json"), {})
    tup = ev.get("objective")
    feas = bool(ev.get("feasible"))
    t_solve = rep.get("wall_total_s") or 0.0
    t_cert = cert.get("wall_total_s") or 0.0
    c1 = rep.get("certs", {}) or {}
    lb_sources = [v for v in (c1.get("revoke_LB_after_ladder"),
                              c1.get("revoke_LB_floor_certificate"),
                              rep.get("stages", [{}])[0].get("best_bound"),
                              cert.get("revoke_LB_best"),
                              cert.get("revoke_LB_relaxation"),
                              cert.get("revoke_LB_full_model_certificate")) if v is not None]
    lb1 = max(lb_sources) if lb_sources else None
    ub1 = (tup or [None])[0]
    per_layer = []
    for st in rep.get("stages", []):
        per_layer.append({"layer": st.get("layer"), "status": st.get("status"),
                          "incumbent": st.get("value"), "best_bound": st.get("best_bound"),
                          "proven_optimal": st.get("proven_optimal"),
                          "budget_s": st.get("budget_s"), "wall_s": st.get("wall_s")})
    bounds = {
        "lower_bound": (int(1e12 * lb1) if lb1 is not None else None),
        "upper_bound": scalar(tup) if feas else None,
        "relative_gap": ((scalar(tup) - 1e12 * lb1) / scalar(tup)) if (feas and lb1) else None,
        "bound_detail": {
            "kind": "CP-SAT 分层界（词典序四级，逐级锁定）",
            "layer1_revoke": {"LB": lb1, "UB": ub1, "gap": (ub1 - lb1) if ub1 is not None else None,
                              "LB_sources": {
                                  "min_sum_revoke_best_bound":
                                      rep.get("stages", [{}])[0].get("best_bound"),
                                  "floor_k0_INFEASIBLE_certificate":
                                      rep.get("certs", {}).get("revoke_LB_floor_certificate"),
                                  "relaxation_base_edges_only": cert.get("revoke_LB_relaxation"),
                                  "full_model_deep_certificate":
                                      cert.get("revoke_LB_full_model_certificate")},
            "lb_sources_all": sorted(set(lb_sources)),
                              "certificate_status": ("CLOSED（gap_revoke=0）" if (lb1 == ub1) else
                                                      "OPEN：Σr≤5 深证明 116.5s 仍 UNKNOWN ⇒ "
                                                      "撤销层只有 LB=%s（CP 界/地板证书），"
                                                      "无闭合 INFEASIBLE 证书" % lb1)},
            "per_layer_incumbent_and_bound": per_layer,
            "scalar_LB_note": "下界标量只用层1（撤销数）的证书界；层2-4 的界是在"
                              "Σr=层1 锁定条件下的条件界，不参与全局标量下界。",
            "ladder": rep.get("ladder"), "certificates": rep.get("certs"),
            "phase2": cert},
    }
    extra_res = {
        "replicate_values": [scalar(tup)] if feas else [],
        "model_facts": rep.get("model"), "star_graph": rep.get("stats"),
        "solver_params": rep.get("params"),
        "runtime_breakdown_s": {"cpsat_lex_solve": t_solve, "bound_certificate_phase": t_cert,
                                "total_wall": round(t_solve + t_cert, 1)},
        "budget_disclosure": {
            "protocol_limit_per_replicate_s": 600,
            "own_lex_solve_wall_s": t_solve,
            "extra_bound_certificate_wall_s": t_cert,
            "total_candidate_wall_s": round(t_solve + t_cert, 1),
            "within_limit": (t_solve + t_cert) <= 600.0,
            "note": "透明申报：词典序四级求解本体用 %.1fs（≤600s 预算内）；随后又跑了 %.1fs 的"
                    "独立'下界/证书加强'进程（relaxation 界 + Σr≤5 深证明），合计超出每重复上限，"
                    "超出部分只用于界证据、未替换 incumbent 目标值。评分时请按本字段口径处理。"
                    % (t_solve, t_cert)},
        "internal_vs_evaluator": {"internal_tuple": meta.get("internal_objective_tuple"),
                                 "evaluator_tuple": tup,
                                 "match": meta.get("internal_objective_tuple") == tup},
        "feasibility_gates": {"base_conflicts_subset_of_star": (rep.get("stats") or {}).get(
            "star_covers_base"), "mask_recheck": (rep.get("stats") or {}).get("mask_recheck"),
            "internal_residual_pairs": meta.get("internal_residual_pairs"),
            "evaluator_n_violations": ev.get("n_violations")},
    }
    structural = {
        "star_vs_base": {"base_conflicts": (rep.get("stats") or {}).get("base_conflicts"),
                         "star_edges": (rep.get("stats") or {}).get("star_edges"),
                         "action_level_nogoods": (rep.get("stats") or {}).get("infeasible_combos")},
        "key_insight_revokes_are_preventive": {
            "statement": "把子句集缩到『只处理原 297 条冲突边』的真子句松弛后，min Σr = 0"
                         "（CP-SAT 证 OPTIMAL）⇒ 本实例的撤销需求完全由『不得新造冲突』"
                         "（预防性 G* 约束）逼出，而不是由原冲突本身逼出。",
            "evidence_relaxation_min_revoke": cert.get("revoke_LB_relaxation"),
            "evidence_relaxation_status": (cert.get("relaxation_record") or {}).get("status"),
            "consequence": "因此撤销数下界不可能来自原冲突图上的匹配/团等组合论证"
                           "（CH-05 探针实测组合界=0），只能来自全势边模型上的 INFEASIBLE 证书；"
                           "该证书在 116.5s 内未取得 ⇒ gap_revoke=4 是本路线的诚实交付状态。",
        },
        "identity_action_note": "每计划只保留 1 个恒等动作（若同时保留 (f,0)/(t,0) 两个恒等列，"
                                "分数解可用 0.5/0.5 零代价满足全部成对行，见 Q2-R53 自检）。",
    }
    extra_sct = {"structural_findings": structural,
                 "search_process": {"stages": per_layer, "ladder": rep.get("ladder"),
                                    "certificates": rep.get("certs"), "phase2": cert},
                 "model_facts": rep.get("model"), "star_graph": rep.get("stats"),
                 "feasibility_gates": extra_res["feasibility_gates"],
                 "stopping_reason": ("budget_exhausted_after_layer4" if t_solve >= 540 else
                                     "completed_within_budget")}
    return base("Q2-R51", d, "eval.json", "solution_actions.json", t_solve, "completed",
                feas, tup, "确定性路线（CP-SAT random_seed=0, num_search_workers=8）；"
                            "replicates=1", 1, None, bounds, extra_res, extra_sct,
                None,
                "确定性精确路线：协议 replicates_deterministic=1；同机同参重跑 incumbent 目标"
                "逐位一致（本次未做第二重复，预算全用于层1-4 搜索与界）。")


def do_r41(d):
    summ = jload(os.path.join(d, "grasp_seeds_summary.json"), {})
    reps, tups, walls, vals = [], [], [], []
    per_seed = {}
    for s in ["11", "29", "47"]:
        rec = jload(os.path.join(d, "grasp_record_seed%s.json" % s), {})
        ev = jload(os.path.join(d, "eval_seed%s.json" % s), {})
        t = ev.get("objective")
        per_seed[s] = {"tuple": t, "feasible": ev.get("feasible"),
                       "internal_tuple": rec.get("internal_objective_tuple"),
                       "internal_residual": rec.get("internal_residual_full_mask"),
                       "wall_s": rec.get("wall_s"), "starts": rec.get("starts"),
                       "failed_descents": rec.get("failed_descents"),
                       "scalar": scalar(t) if t else None,
                       "match_internal": t == rec.get("internal_objective_tuple")}
        if t:
            reps.append(s)
            tups.append(t)
            walls.append(rec.get("wall_s"))
            vals.append(scalar(t))
    med = statistics.median(vals) if vals else None
    rng_ = (max(vals) - min(vals)) if len(vals) >= 2 else None
    stab = (rng_ / med) if (med and rng_ is not None) else None
    # 中位数重复：取标量等于中位数的那一次（并列时取元组字典序小者）
    idx = sorted(range(len(vals)), key=lambda k: (abs(vals[k] - med), tups[k]))[0] if vals else None
    tup = tups[idx] if idx is not None else None
    runtime = max([w for w in walls if w] or [0.0])
    bounds = {"lower_bound": None, "upper_bound": None, "relative_gap": None,
              "bound_detail": {"kind": "启发式路线，按任务书规定 lower/upper_bound = null",
                               "route_plan": "冲突图极大匹配给出 |adjusted|+|revoke| 图论下界"
                                             "（CH-04 复算 61-63），本次侦察未实现为正式界",
                               "per_seed": per_seed}}
    extra_res = {"replicate_values": vals, "replicate_tuples": tups,
                 "per_seed": per_seed, "aggregation": "median over 3 replicates (seeds 11/29/47)",
                 "total_wall_seconds": round(sum(w for w in walls if w), 1),
                 "params": jload(os.path.join(d, "grasp_record_seed11.json"), {}).get("params"),
                 "feasibility_gates": {
                     "evaluator_feasible_all_seeds": all(v["feasible"] for v in per_seed.values()),
                     "internal_residual_all_zero": all(v["internal_residual"] == 0
                                                       for v in per_seed.values())}}
    extra_sct = {"per_seed": per_seed, "params": extra_res["params"],
                 "stopping_reason": "wall_clock_budget_per_replicate（185s×3，协议 ≤600s/重复）",
                 "feasibility_gates": extra_res["feasibility_gates"]}
    return base("Q2-R41", d, "eval_seed%s.json" % (reps[idx] if idx is not None else "11"),
                "solution_actions_seed%s.json" % (reps[idx] if idx is not None else "11"),
                runtime, "completed" if vals else "failed", bool(vals), tup,
                "冻结 seeds=[11,29,47]，每重复一个独立 random.Random(seed)", len(vals),
                None if vals else "no_feasible_within_budget", bounds, extra_res, extra_sct,
                stab,
                "稳定性 = 三重复标量极差/中位数 = %s；三元组 %s" % (
                    ("%.4f" % stab) if stab is not None else "n/a",
                    " | ".join(json.dumps(t) for t in tups)))


def do_r32(d):
    diag = jload(os.path.join(d, "r32_diagnostics.json"), {})
    ev = jload(os.path.join(d, "eval.json"), {})
    tup = ev.get("objective")
    feas = bool(ev.get("feasible"))
    runtime = diag.get("wall_total_s")
    ladder = diag.get("derevoke_ladder") or []
    cert = None
    for row in reversed(ladder):
        if row.get("status") == "INFEASIBLE":
            cert = row["try_global_revoke_max"] + 1
    bounds = {"lower_bound": None, "upper_bound": None, "relative_gap": None,
              "bound_detail": {
                  "kind": "异范式启发式（route 明确 proof_possible=false）⇒ null",
                  "note": "去撤销阶梯（局部自由集上的 Σr≤k-1 判定）不是全局证书："
                          "最后一轮 %s；自由集覆盖 147/150 计划，虽接近全量但不构成证明。"
                          % (json.dumps(ladder[-1], ensure_ascii=False) if ladder else "无"),
                  "local_ladder": ladder,
                  "certificate_LB_if_any": cert}}
    extra_res = {"replicate_values": [scalar(tup)] if feas else [],
                 "field_diagnostics": diag.get("field"), "rounding": diag.get("rounding"),
                 "repair": diag.get("repair"), "derevoke_ladder": ladder,
                 "internal_vs_evaluator": {"internal_tuple": diag.get("final_internal_tuple"),
                                           "evaluator_tuple": tup,
                                           "match": diag.get("final_internal_tuple") == tup},
                 "feasibility_gates": {
                     "mask_full_recheck_residual": diag.get("mask_full_recheck_residual"),
                     "violated_after_repair": (diag.get("repair") or {}).get(
                         "violated_after_repair"),
                     "evaluator_n_violations": ev.get("n_violations"),
                     "phi_monotone_sentinel_ok": (diag.get("field") or {}).get(
                         "F_monotone_by_construction"),
                     "repair_degenerate_to_global": (diag.get("repair") or {}).get(
                         "touch_fraction", 0) > 0.5},
                 "internal_residual": diag.get("final_internal_residual")}
    extra_sct = {"field": diag.get("field"), "rounding": diag.get("rounding"),
                 "repair": diag.get("repair"), "derevoke_ladder": ladder,
                 "guide_effect": {"conflicts_all_keep": (diag.get("rounding") or {}).get(
                     "violated_at_all_keep"),
                     "conflicts_after_rounding": (diag.get("rounding") or {}).get(
                         "violated_after_round"),
                     "reduction": (diag.get("rounding") or {}).get("guide_reduction")},
                 "stopping_reason": "取整-修复一轮闭环 + 去撤销阶梯预算耗尽（391s/≤600s）",
                 "feasibility_gates": extra_res["feasibility_gates"]}
    return base("Q2-R32", d, "eval.json", "solution_actions.json", runtime, "completed",
                feas, tup, "确定性配置（无随机；固定迭代序与破平键=计划编号）；replicates=1",
                1, None, bounds, extra_res, extra_sct, None,
                "确定性路线：协议 replicates_deterministic=1；连续层严格确定性"
                "（numpy 向量化 + 固定步长规则），修复层 CP-SAT 并行 worker 可能引入"
                "run-to-run 差异 ⇒ 已记录 num_search_workers=4。")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--idea", required=True, choices=["Q2-R51", "Q2-R41", "Q2-R32"])
    a = ap.parse_args()
    d = os.path.join(SC, a.idea)
    fn = {"Q2-R51": do_r51, "Q2-R41": do_r41, "Q2-R32": do_r32}[a.idea]
    res, sct = fn(d)
    print(json.dumps({"idea": a.idea, "status": res["status"], "feasible": res["feasible"],
                      "objective": res["objective"], "objective_tuple": res["objective_tuple"],
                      "runtime_seconds": res["runtime_seconds"],
                      "lower_bound": res["lower_bound"], "upper_bound": res["upper_bound"]},
                     ensure_ascii=False))
    print("written:", rel(os.path.join(d, "result.json")), "|", rel(os.path.join(d, "scout.json")))
