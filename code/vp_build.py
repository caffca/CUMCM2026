# -*- coding: utf-8 -*-
"""VALIDATION_PLAN v2 冻结构建器：claim→证据→criterion（机器判定）。运行=结果出现之前。"""
import hashlib, io, json, datetime, os, sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\6verity\scripts")
import decision_handoff as _dh
_HANDOFF = _dh.load_handoff(Path(".").resolve())
assert _HANDOFF.get("active") and _HANDOFF.get("ok"), _HANDOFF.get("errors")
BINDING = _HANDOFF.get("binding")

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

V = []
def v(vid, claim, q, typ, metric, ok, bad, pri, crit, ev, on_fail="BLOCK：修复实现后重跑；判据不得回改", keys=None, anti=None, on_unknown="BLOCK（UNKNOWN 视同未验证）", on_error="BLOCK（求值异常登记 failure_event）", notes=""):
    c = dict(crit)
    import re as _rx
    for k in ("lhs", "rhs"):
        if isinstance(c.get(k), str):
            c[k] = _rx.sub(r"^results:Q\d_[a-z0-9_]+\.", "results:", c[k])
    if c.get("operator") == "equals":
        c.setdefault("tolerance", 0)
    if c.get("operator") == "threshold_lte" and "rhs" in c:
        c["operator"] = "absolute_improvement_gte"
        c.setdefault("direction", "lower_is_better")
        c.setdefault("threshold", 0)
    if c.get("operator") == "threshold_lte":
        c.pop("rhs", None)
    if c.get("operator") == "threshold_gte":
        c.pop("rhs", None)
    notes = (notes + "；" if notes else "")
    def trans(kind, txt):
        if kind == "fail":
            if any(w in str(txt) for w in ("不阻断", "降级", "删除", "SKIPPED")):
                return {"failure_class": "model_invalid", "resolution_mode": "drop_claim", "return_to": "methodology_review"}
            return {"failure_class": "implementation_error", "resolution_mode": "repair_code", "return_to": "coding_visual"}
        if kind == "unknown":
            return {"failure_class": "missing_evidence", "resolution_mode": "run_missing_evidence", "return_to": "coding_visual"}
        return {"failure_class": "implementation_error", "resolution_mode": "repair_code", "return_to": "coding_visual"}
    human = {"on_fail": on_fail, "on_unknown": on_unknown, "on_error": on_error}
    notes += "机器路由=transition 三元组；人读处置：" + "; ".join(f"{k}={val}" for k, val in human.items())
    V.append({"validation_id": vid, "claim_id": claim, "question_id": q, "type": typ,
              "metric": metric, "success_rule": ok, "failure_rule": bad, "priority": pri,
              "result_keys": keys or [], "evidence_files": ev,
              "evidence_refs": ev, "criterion": c, "anti_claim": anti or "",
              "on_fail": trans("fail", on_fail), "on_unknown": trans("unknown", ""),
              "on_error": trans("error", ""), "notes": notes})

# ---------------- Q1 ----------------
v("V-Q1-01", "Q1-C1", "Q1", "independent_reproduction", "三实现对称差对",
  "主实现(区间算术) vs canonical evaluator 基准 symdiff=0", "symdiff>0 ⇒ 检测实现错误，回 coding 修",
  "must", {"operator": "equals", "lhs": "results:Q1_detect.symdiff_vs_evaluator", "rhs": 0},
  ["results/Q1_detect.json"], keys=["symdiff_vs_evaluator"], anti="三实现共享同一隐蔽 bug（要求 checker 为不 import 主实现的第二代码路径）")
v("V-Q1-02", "Q1-C1", "Q1", "independent_reproduction", "位图/闭式 vs 区间算术",
  "bitmap⊕interval 与 congruence(同组子集)⊕interval 均为空", "任一非空 ⇒ 口径漂移，BLOCK",
  "must", {"operator": "equals", "lhs": "results:Q1_detect.three_way_max_symdiff", "rhs": 0},
  ["results/Q1_detect.json", "results/Q1_verify.json"], keys=["three_way_max_symdiff"])
v("V-Q1-03", "Q1-C1", "Q1", "feasibility", "边界用例",
  "半开相接不判冲突/交叠必判（含 A001 三次窗）≥8 用例全过", "任一失败 ⇒ 判定式错误",
  "must", {"operator": "equals", "lhs": "results:Q1_stats.boundary_cases_failed", "rhs": 0},
  ["results/Q1_stats.json", "results/Q1_detect.json"], keys=["boundary_cases_failed"])
v("V-Q1-04", "Q1-C2", "Q1", "feasibility", "result1 行一致性",
  "submission/result1.xlsx 行集 == results/Q1_detect.json 边集（排序后）", "行数或内容不等 ⇒ 提交工件不忠实",
  "must", {"operator": "equals", "lhs": "results:Q1_stats.result1_edge_symdiff", "rhs": 0},
  ["results/Q1_stats.json", "results/Q1_detect.json"], keys=["result1_edge_symdiff"])
v("V-Q1-05", "Q1-C3", "Q1", "uncertainty", "类对计数闭合",
  "Σ类对 = |E| 且 AA=0（若出现 AA 立即疑口径）", "不等 ⇒ 统计口径错",
  "must", {"operator": "equals", "lhs": "results:Q1_stats.classpair_sum_minus_total", "rhs": 0},
  ["results/Q1_stats.json", "results/Q1_detect.json"], keys=["classpair_sum_minus_total"])
v("V-Q1-06", "Q1-C1", "Q1", "robustness", "植入压力测试召回",
  "注入召回≥0.99 且删除消失率≥0.99（诊断证据，措辞限定 ±4%）", "低于 ⇒ 检测漏报风险未排除",
  "recommended", {"operator": "threshold_gte", "lhs": "results:Q1_stats.stress_min_recall", "threshold": 0.99},
  ["results/Q1_stats.json", "results/Q1_detect.json"], keys=["stress_min_recall"], on_fail="不阻断；论文删除该证据或重做")

# ---------------- Q2 ----------------
v("V-Q2-01", "Q2-C1", "Q2", "feasibility", "零冲突",
  "调整后全计划重跑 Q1 独立检测=0 对（evaluator+第二实现双复验）", "任一>0 ⇒ 方案无效，回 coding",
  "must", {"operator": "equals", "lhs": "results:Q2_solution.residual_pairs_second_impl", "rhs": 0},
  ["results/Q2_solution.json", "results/Q2_check.json"], keys=["residual_pairs_second_impl"],
  anti="checker 与被检实现同源（要求：checker 不得 import 求解代码，独立区间算术）")
v("V-Q2-02", "Q2-C2", "Q2", "feasibility", "合规断言",
  "单参数/幅度≤10,5/次数间隔不变/域[0,100)×[0,643)/撤销语义 全部违例=0",
  "任一违例 ⇒ 违反题面规则", "must",
  {"operator": "equals", "lhs": "results:Q2_solution.compliance_violations", "rhs": 0},
  ["results/Q2_solution.json", "results/Q2_check.json"], keys=["compliance_violations"])
v("V-Q2-03", "Q2-C3", "Q2", "convergence", "撤销数下界证书",
  "阶梯 Σr≤0 INFEASIBLE 已证（LB≥1）且证书工件可复跑",
  "未证任何 LB ⇒ Q2-C3 未满足，撤销层只写『未认证』", "must",
  {"operator": "threshold_gte", "lhs": "results:Q2_solution.ladder_proven_revoke_lb", "threshold": 1},
  ["results/Q2_solution.json"], keys=["ladder_proven_revoke_lb"])
v("V-Q2-04", "Q2-C3", "Q2", "degeneracy", "三角退化",
  "(constraint_only−full)/constraint_only ≥ 0.05（目标不起决定作用则本问塌缩为平凡）",
  "<0.05 ⇒ 词典序目标为装饰，重写问题叙事", "must",
  {"operator": "threshold_gte", "lhs": "results:Q2_solution.degeneracy_ratio", "threshold": 0.05},
  ["results/Q2_solution.json"], keys=["degeneracy_ratio"])
v("V-Q2-05", "Q2-C3", "Q2", "independent_reproduction", "复现性",
  "权威解四级元组经独立 checker 第二实现全量重算逐位一致（rev4/EV-CRIT-001）",
  "不一致 ⇒ 以 workers=1 值为准重出全部下游", "must",
  {"operator": "equals", "lhs": "results:Q2_solution.tuple_matches_second_impl", "rhs": 1},
  ["results/Q2_solution.json"], keys=["tuple_matches_second_impl"], notes="plan_revision=4（EV-CRIT-001 criterion_invalid）：复现判据从 worker 交叉 run 元组一致改为『权威解经独立 checker 第二实现全量重算逐位一致』（解级可复现语义）；w1/w4 交叉差异保留为诊断字段")
v("V-Q2-06", "Q2-C3", "Q2", "baseline_comparison", "优于启发式对照",
  "精确解撤销 ≤ GRASP 三 seed 中位撤销", "大于 ⇒ 求解实现可疑，回查",
  "recommended", {"operator": "absolute_improvement_gte", "lhs": "results:revoke", "rhs": "results:grasp_revoke_median",
                  "threshold": 0, "direction": "lower_is_better"},
  ["results/Q2_solution.json", "results/Q2_solution.json"], keys=["revoke", "grasp_revoke_median"])
v("V-Q2-07", "Q2-C4", "Q2", "feasibility", "表1 闭合",
  "按类 kept+adjusted+revoked=类总数 且 Σ=150 且与 result2 行逐一对应",
  "不等 ⇒ 统计或工件错误", "must",
  {"operator": "equals", "lhs": "results:Q2_table1.table_closure_diff", "rhs": 0},
  ["results/Q2_solution.json", "results/Q2_table1.json"], keys=["table_closure_diff"])
v("V-Q2-08", "Q2-C3", "Q2", "uncertainty", "界闭合（理想）",
  "撤销层 UB=LB（gap_revoke=0 ⇒ 可写『最优』）", "gap>0 ⇒ 论文写区间 [LB,UB]（预期态，不阻断）",
  "recommended", {"operator": "equals", "lhs": "results:Q2_solution.gap_revoke", "rhs": 0},
  ["results/Q2_solution.json"], keys=["gap_revoke"],
  on_fail="降级为区间表述并登记（不阻断）", on_unknown="登记 UNKNOWN 并区间表述")

# ---------------- Q3 ----------------
v("V-Q3-01", "Q3-C1", "Q3", "feasibility", "加装零冲突",
  "新 C 集合 vs 生产 Q2 基座 且 内部 双复验 0 冲突（第二实现 checker）",
  ">0 ⇒ 方案无效", "must",
  {"operator": "equals", "lhs": "results:Q3_solution.conflict_total_second_impl", "rhs": 0},
  ["results/Q3_solution.json", "results/Q3_check.json"], keys=["conflict_total_second_impl"])
v("V-Q3-02", "Q3-C1", "Q3", "independent_reproduction", "候选集完备",
  "第二实现重算候选放置数 == 求解输入候选数", "不等 ⇒ 预筛漏/多候选，最优宣称失效",
  "must", {"operator": "equals", "lhs": "results:Q3_bound.cand_count_second_impl_minus_solver", "rhs": 0},
  ["results/Q3_bound.json"], keys=["cand_count_second_impl_minus_solver"])
v("V-Q3-03", "Q3-C2", "Q3", "convergence", "界链有效",
  "min(UB 各腿) ≥ LB(构造=提交行数)（界合法性自检门，CH-05 警示#3）",
  "UB<LB ⇒ 界代码有 bug，BLOCK", "must",
  {"operator": "threshold_gte", "lhs": "results:Q3_bound.ub_min_minus_lb", "threshold": 0},
  ["results/Q3_bound.json"], keys=["ub_min_minus_lb"])
v("V-Q3-04", "Q3-C2", "Q3", "convergence", "三腿会合（认证态）",
  "CP-SAT OPTIMAL 且 LP=incumbent（gap=0 ⇒ 写『最大=Φ，附可检查上界』）",
  "gap>0 ⇒ 论文写『至少 Φ 至多 UB』并解释松因（预期可能态）", "recommended",
  {"operator": "equals", "lhs": "results:Q3_bound.gap_certified", "rhs": 0},
  ["results/Q3_bound.json"], keys=["gap_certified"],
  on_fail="降级区间表述（不阻断），登记 result_review")
v("V-Q3-05", "Q3-C3", "Q3", "feasibility", "行数闭合",
  "result3.xlsx 新增行数 == Φ == results 计数", "不等 ⇒ 工件不忠实",
  "must", {"operator": "equals", "lhs": "results:Q3_solution.result3_rows_minus_phi", "rhs": 0},
  ["results/Q3_solution.json", "results/Q3_submission_check.json"], keys=["result3_rows_minus_phi"])
v("V-Q3-06", "Q3-C1", "Q3", "independent_reproduction", "基座绑定",
  "results/_meta.model_spec_sha256==当前 FMS 且 base 指向生产 Q2 解（非侦察解）",
  "绑定错位 ⇒ 全部 Q3 结果作废重跑", "must",
  {"operator": "equals", "lhs": "results:Q3_solution.base_is_production_q2", "rhs": 1},
  ["results/Q3_solution.json"], keys=["base_is_production_q2"])
v("V-Q3-07", "Q3-C2", "Q3", "sensitivity", "口径 2B（可重排基座）",
  "备查口径下重跑一遍界与构造，双口径数字并表", "未做 ⇒ 灵敏度缺项（论文降级）",
  "optional", {"operator": "threshold_gte", "lhs": "results:Q3_sensitivity.alt2B_ran", "threshold": 1},
  ["results/Q3_solution.json", "results/Q3_sensitivity.json"], keys=["alt2B_ran"],
  on_fail="论文删除该灵敏度声明（记 SKIPPED）")

# ---------------- Q4 ----------------
v("V-Q4-01", "Q4-C1", "Q4", "feasibility", "零冲突+间隔合规",
  "evaluator Q4 复算 feasible=true；第二实现复验含 g'≥1/|dg|≤10/仅C/单参数 全断言",
  "任一失败 ⇒ 无效", "must",
  {"operator": "equals", "lhs": "results:Q4_solution.violations_second_impl", "rhs": 0},
  ["results/Q4_solution.json", "results/Q4_check.json"], keys=["violations_second_impl"])
v("V-Q4-02", "Q4-C1", "Q4", "feasibility", "热启动可行",
  "生产 Q2 解逐字植入 Q4 域（Q2 动作 ⊆ Q4 动作）复算 feasible（支配界机器化）",
  "植入不可行 ⇒ 域构造 bug", "must",
  {"operator": "equals", "lhs": "results:Q4_solution.planted_q2_feasible", "rhs": 1},
  ["results/Q4_solution.json"], keys=["planted_q2_feasible"])
v("V-Q4-03", "Q4-C2", "Q4", "baseline_comparison", "不劣于 Q2",
  "Φ_4 ≤ Φ_2（同一 evaluator 标量）且各层级不劣（词典序逐位 ≤）",
  "存在更劣层 ⇒ 锚定约束未生效，回查求解", "must",
  {"operator": "absolute_improvement_gte", "lhs": "results:scalar", "rhs": "results:scalar_q2_ref", "threshold": 0, "direction": "lower_is_better"},
  ["results/Q4_solution.json"], keys=["scalar"],
  anti="『不劣于』只是域包含的构造性必然 ⇒ 必须另报严格改善量（见 V-Q4-04），不得把构造必然包装成发现")
v("V-Q4-04", "Q4-C2", "Q4", "sensitivity", "改善量（收益判定）",
  "rev_Q2 − rev_Q4 ≥ 1 ⇒ 间隔自由度有可报收益；=0 ⇒ 如实写『本数据上无撤销收益』并看低层级",
  "非二选一表述 ⇒ 违规", "recommended",
  {"operator": "threshold_gte", "lhs": "results:Q4_solution.revoke_gain_vs_q2", "threshold": 1},
  ["results/Q4_solution.json"], keys=["revoke_gain_vs_q2"],
  on_fail="不阻断；收益叙事改为 0 并转低层级改善对比（如实）")
v("V-Q4-05", "Q4-C1", "Q4", "independent_reproduction", "复现性",
  "Q4 权威解元组经第二实现重算一致（解级复现，rev4/EV-CRIT-001）", "不一致 ⇒ BLOCK", "must",
  {"operator": "equals", "lhs": "results:Q4_solution.tuple_matches_second_impl", "rhs": 1},
  ["results/Q4_solution.json"], keys=["tuple_matches_second_impl"], notes="plan_revision=4 同 Q2 口径（EV-CRIT-001）")
v("V-Q4-06", "Q4-C2", "Q4", "feasibility", "表4 闭合",
  "表1 口径闭合（同 V-Q2-07）+ result4 含调整后间隔列非空",
  "不等 ⇒ 工件错误", "must",
  {"operator": "equals", "lhs": "results:Q4_table1.table_closure_diff", "rhs": 0},
  ["results/Q4_solution.json", "results/Q4_table1.json"], keys=["table_closure_diff"])

plan = {
  "schema_version": 2, "plan_revision": 8, "frozen_at": NOW,
  "problem_id": "D2026", "search_id": "CS-20260911T071520Z-1A9D30",
  "frozen_before_production_runs": True,
  "model_decision_binding": BINDING,
  "evidence_contract": {
    "registry_required": True, "execution_metadata_required": True,
    "decision_binding_required": True, "result_evidence_required": True,
    "independent_reproduction_required": True,
    "independent_reproduction": {"pairs": [
      {"pair_id": "IR-Q1", "question_id": "Q1",
       "primary_file": "results/Q1_detect.json", "reproduction_file": "results/Q1_verify.json",
       "compare_paths": ["counts.edges", "counts.AB", "counts.AC", "counts.BC", "counts.BB", "counts.CC"],
       "tolerance": 0, "evidence_refs": ["code/q1_detect.py", "code/q1_verify.py"]},
      {"pair_id": "IR-Q2", "question_id": "Q2",
       "primary_file": "results/Q2_solution.json", "reproduction_file": "results/Q2_check.json",
       "compare_paths": ["objective_scalar", "residual_pairs", "revoked", "adjusted"],
       "tolerance": 0, "evidence_refs": ["code/q2_solve.py", "code/check_q2.py"]},
      {"pair_id": "IR-Q3", "question_id": "Q3",
       "primary_file": "results/Q3_solution.json", "reproduction_file": "results/Q3_check.json",
       "compare_paths": ["phi", "conflicts_vs_base", "conflicts_internal", "rows"],
       "tolerance": 0, "evidence_refs": ["code/q3_pack.py", "code/check_q3.py"]},
      {"pair_id": "IR-Q4", "question_id": "Q4",
       "primary_file": "results/Q4_solution.json", "reproduction_file": "results/Q4_check.json",
       "compare_paths": ["objective_scalar", "residual_pairs", "violations"],
       "tolerance": 0, "evidence_refs": ["code/q4_solve.py", "code/check_q4.py"]}]}},
  "notes_v7": {
    "rebuild_from": ["结果文件", "_meta 执行 metadata", "输入/输出 SHA", "formulation_sha256 绑定 FMS"],
    "pairs_generator_rule": "reproduction 文件必须由独立代码路径（不 import 主实现）生成"},
  "global_freezes": {
    "T_MAX": 643, "horizon_ruling": "ADJUDICATION R1（621 为 stale 字段）",
    "evaluator_frozen_sha256": sha("runs/competitive/CS-20260911T071520-D2026/canonical_evaluator.py"),
    "fms_path_sha": {"path": "reports/FINAL_MODEL_SPEC.json", "sha256": sha("reports/FINAL_MODEL_SPEC.json")},
    "lex_scalar": "1e12*rev+1e8*adj+1e4*ploss+mag",
    "budget_note": "生产两级预算 D-BUDGET-001：Q2/Q4 ≤7200s 分层长跑；Q3 在 Q2 生产解上重算重证；侦察数值不作 production evidence"},
  "validations": V,
  "discipline": "先冻结后跑：跑结果不改判据；改动须回 methodology_review 记 failure_event。must 全过才进 result_review。"}
io.open("reports/VALIDATION_PLAN.json", "w", encoding="utf-8").write(json.dumps(plan, ensure_ascii=False, indent=1))

md = ["# VALIDATION PLAN（人读版，与 JSON 逐条同判据）", "",
      f"冻结时间：{NOW}（早于任何生产运行）· 依据 FMS v4 + QUESTION_CONTRACT capabilities", "",
      "| id | 问 | 判据（机器） | 级别 | 反宣称 |", "|---|---|---|---|---|"]
for x in V:
    c = x["criterion"]
    md.append(f"| {x['validation_id']} | {x['question_id']} | `{c['operator']}({c['lhs']}" +
              (f",{c.get('rhs') if c.get('rhs') is not None else c.get('threshold')})`" if c.get('rhs') is not None or c.get('threshold') is not None else ")`") +
              f" | {x['priority']} | {x.get('anti_claim','') or '—'} |")
md += ["", "判定纪律：must FAIL/UNKNOWN → result_review BLOCK 并按预注册 failure_class 回退；recommended FAIL → 降级表述登记；optional 跳过记 SKIPPED。"]
io.open("reports/VALIDATION_PLAN.md", "w", encoding="utf-8").write("\n".join(md))
print("VALIDATION_PLAN v2 written:", len(V), "validations; must =", sum(1 for x in V if x["priority"] == "must"))
