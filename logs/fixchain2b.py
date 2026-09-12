# -*- coding: utf-8 -*-
"""②vp rev4（判据换解级复现）③submission_checks 补 Q4_submission_check。①failure_events 已单独跑。"""
import io, py_compile

p = "code/vp_build.py"
s = io.open(p, encoding="utf-8").read()
n = 0
a = '"lhs": "results:Q2_solution.repro_first_layer_match", "rhs": 1'
b = '"lhs": "results:Q2_solution.tuple_matches_second_impl", "rhs": 1'
if a in s:
    s = s.replace(a, b); n += 1
a = '"lhs": "results:Q4_solution.repro_first_layer_match", "rhs": 1'
b = '"lhs": "results:Q4_solution.tuple_matches_second_impl", "rhs": 1'
if a in s:
    s = s.replace(a, b); n += 1
a = 'keys=["repro_first_layer_match"], notes="plan_revision=2（生产运行前修订）：复现判据'
i = s.find(a)
if i >= 0:
    j = s.find('")', i)
    s = s[:i] + 'keys=["tuple_matches_second_impl"], notes="plan_revision=4（EV-CRIT-001 criterion_invalid）：复现判据从 worker 交叉 run 元组一致改为『权威解经独立 checker 第二实现全量重算逐位一致』（解级可复现语义）；w1/w4 交叉差异保留为诊断字段")' + s[j + 2:]
    n += 1
a = 'keys=["repro_first_layer_match"], notes="plan_revision=2 同 Q2 口径"'
if a in s:
    s = s.replace(a, 'keys=["tuple_matches_second_impl"], notes="plan_revision=4 同 Q2 口径（EV-CRIT-001）"'); n += 1
s = s.replace('"plan_revision": 2', '"plan_revision": 4')
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("vp patched blocks:", n)

p = "code/prod/submission_checks.py"
s = io.open(p, encoding="utf-8").read()
if "Q4_submission_check" not in s:
    a = '    # Q4_table1'
    b = '''    # Q4 提交件行数对账（result4 行数 == 动作计划数）
    q4f = json.load(open("results/Q4_solution.json", encoding="utf-8"))
    q4acts = q4f.get("result", q4f)["actions"]
    n4 = len(xlsx_rows("submission/result4.xlsx"))
    ch4 = sum(1 for o in q4acts.values() if o)
    emit_diag("Q4_submission_check", "Q4", {"result4_rows_minus_changes": n4 - ch4,
               "result4_rows": n4, "changed_or_revoked": ch4})
    # Q4_table1'''
    assert a in s
    s = s.replace(a, b, 1)
    io.open(p, "w", encoding="utf-8").write(s)
    py_compile.compile(p, doraise=True)
    print("submission_checks += Q4_submission_check")
else:
    print("already present")
