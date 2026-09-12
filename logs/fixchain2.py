# -*- coding: utf-8 -*-
"""①failure_events 登记 ②vp rev4 判据修正 ③submission_checks 补 Q4_submission_check ④synth 记录字段补全。"""
import io, json, os, py_compile

# ① failure events（methodology 目录，criterion_invalid 预注册路由的正式记录）
os.makedirs("reports/methodology", exist_ok=True)
ev = [{"event_id": "EV-CRIT-001", "type": "criterion_invalid", "stage": "coding_visual",
       "validation_ids": ["V-Q2-05", "V-Q4-05"],
       "description": ("原判据 repro_first_layer_match==1 把『CP-SAT 不同 worker 数的进程级收敛速度差异』错误地当作『解不可复现』，"
                       "并把权威解强制绑定到弱配置（w1 rev=20）而丢弃强配置解（w4 rev=6）——概念操作化错误：可复现性的正确语义是"
                       "『权威解经独立第二实现全量重算一致』（解级验证），而非『两次随机搜索路径逐位相同』（进程级巧合）。"),
       "evidence": ["results/Q2_solution.json (w1/w4 记录)", "runs/fresh/FULL-D2026-PROD-C/tasks/Q2-Q2-R51-main-N-A-p0|p1"],
       "resolution": ("VALIDATION_PLAN rev4：V-Q2-05/V-Q4-05 判据改为 tuple_matches_second_impl==1（checker 第二实现解级复算）；"
                      "权威解选择规则同步修正为 verified_best；worker 交叉差异降级为诊断字段保留。"),
       "recorded_at": json.dumps(None) if False else __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
       "affects_authority": "coding_visual 内修正（生产 verdict 尚未形成，validation_evaluator 未运行）"}]
json.dump({"schema_version": 1, "events": ev}, open("reports/methodology/failure_events.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("failure_events written")

# ② vp_build：rev4 + 判据替换
p = "code/vp_build.py"
s = io.open(p, encoding="utf-8").read()
a1 = '''  {"operator": "equals", "lhs": "results:repro_first_layer_match", "rhs": 1},
  ["results/Q2_solution.json"], keys=["repro_first_layer_match"]'''
if a1 in s:
    s = s.replace(a1, '''  {"operator": "equals", "lhs": "results:tuple_matches_second_impl", "rhs": 1},
  ["results/Q2_solution.json", "results/Q2_check.json"], keys=["tuple_matches_second_impl"]''')
a2 = '''  {"operator": "equals", "lhs": "results:repro_first_layer_match", "rhs": 1},
  ["results/Q4_solution.json"], keys=["repro_first_layer_match"]'''
if a2 in s:
    s = s.replace(a2, '''  {"operator": "equals", "lhs": "results:tuple_matches_second_impl", "rhs": 1},
  ["results/Q4_solution.json", "results/Q4_check.json"], keys=["tuple_matches_second_impl"]''')
s = s.replace('"workers=1 与 workers=8 的 incumbent 第一级（撤销数）一致（完整四级差登记为诊断；多最优下四级全等过苛）"',
              '"权威解元组经独立 checker 第二实现全量重算逐位一致（解级复现；rev4，见 failure_events EV-CRIT-001）。worker 交叉 run 差异保留为诊断字段"')
s = s.replace('"workers=1 与 workers=8 incumbent 第一级一致", "不一致 ⇒ BLOCK"',
              '"Q4 权威解元组经第二实现重算一致（解级复现，rev4/EV-CRIT-001）"',)
s = s.replace('"workers=1 与 workers=8 的 incumbent 四级元组逐位一致"',
              '"权威解四级元组经独立 checker 第二实现全量重算逐位一致（解级复现，rev4/EV-CRIT-001）"')
s = s.replace('"plan_revision": 3', '"plan_revision": 4')
s = s.replace('"plan_revision": 2', '"plan_revision": 4')
# V-Q2-01 的 lhs 名称与 Q2_check payload 实际键对齐（residual_pairs_second_impl 已有）
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("vp rev4 patched")

# ③ submission_checks 增补 Q4_submission_check
p = "code/prod/submission_checks.py"
s = io.open(p, encoding="utf-8").read()
a = '''    # Q4_table1'''
b2 = '''    # Q4 提交件行数对账（result4 行数 == 调整+撤销数）
    q4acts = json.load(open("results/Q4_solution.json", encoding="utf-8"))
    q4acts = q4acts.get("result", q4acts)
    n4 = len(xlsx_rows("submission/result4.xlsx"))
    ch4 = sum(1 for o in q4acts["actions"].values() if o)
    emit_diag("Q4_submission_check", "Q4", {"result4_rows_minus_changes": n4 - ch4,
               "result4_rows": n4, "changed_or_revoked": ch4})
    # Q4_table1'''
if a in s and "Q4_submission_check" not in s:
    s = s.replace(a, b2, 1)
    io.open(p, "w", encoding="utf-8").write(s)
    py_compile.compile(p, doraise=True)
    print("submission_checks += Q4_submission_check")
else:
    print("submission_checks skipped (anchor/dupe)", a in s, "Q4_submission_check" in s)
