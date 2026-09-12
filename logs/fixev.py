# -*- coding: utf-8 -*-
"""vp rev5：evidence_files 工件路径修正（仅指向已登记 results/*.json；判据/阈值/路由零改动）。"""
import io, json, py_compile, datetime

p = "code/vp_build.py"
s = io.open(p, encoding="utf-8").read()
pairs = [
 ('["results/Q1_detect.json", "code/q1_detect.py"]', '["results/Q1_detect.json", "results/Q1_verify.json"]'),
 ('["results/Q1_stats.json", "submission/result1.xlsx"]', '["results/Q1_stats.json", "results/Q1_detect.json"]'),
 ('["results/Q1_stats.json"], keys=["boundary_cases_failed"]', '["results/Q1_stats.json", "results/Q1_detect.json"], keys=["boundary_cases_failed"]'),
 ('["results/Q1_stats.json"], keys=["stress_min_recall"]', '["results/Q1_stats.json", "results/Q1_detect.json"], keys=["stress_min_recall"]'),
 ('"results/Q2_solution.json", "code/check_q2.py"', '"results/Q2_solution.json", "results/Q2_check.json"'),
 ('"results/Q3_solution.json", "code/check_q3.py"', '"results/Q3_solution.json", "results/Q3_check.json"'),
 ('"results/Q3_solution.json", "submission/result3.xlsx"', '"results/Q3_solution.json", "results/Q3_submission_check.json"'),
 ('"results/Q4_solution.json", "code/check_q4.py"', '"results/Q4_solution.json", "results/Q4_check.json"'),
 ('"results/Q4_table1.json", "submission/result4.xlsx"', '"results/Q4_solution.json", "results/Q4_table1.json"'),
 ('["results/Q2_table1.json"]', '["results/Q2_solution.json", "results/Q2_table1.json"]'),
 ('"plan_revision": 4', '"plan_revision": 5'),
]
n = 0
for a, b in pairs:
    c = s.count(a)
    if c:
        s = s.replace(a, b); n += c
    else:
        print("MISS:", a[:70])
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("replacements:", n)

# failure_events 追加 EV-CRIT-002（证据路径修正，判据不变）
ev = json.load(io.open("reports/methodology/failure_events.json", encoding="utf-8"))
ids = {e["event_id"] for e in ev["events"]}
if "EV-CRIT-002" not in ids:
    ev["events"].append({
        "event_id": "EV-CRIT-002", "type": "criterion_invalid", "stage": "result_review",
        "validation_ids": ["V-Q1-02", "V-Q1-03", "V-Q1-04", "V-Q1-06", "V-Q2-02", "V-Q2-07",
                            "V-Q3-01", "V-Q3-05", "V-Q4-01", "V-Q4-06"],
        "description": ("VALIDATION_PLAN rev4 的 evidence_files 混入了未登记工件（code/*.py、submission/*.xlsx），"
                        "validation_evaluator 全局判 ERROR（27/27）。修正=登记面词汇：evidence 一律指向 RESULT_REGISTRY "
                        "中的 results/*.json；xlsx/code 一致性语义已由 Q*_stats/table1 中的对称差字段承载。判据、阈值、"
                        "路由与 success_rule 文本零改动。"),
        "evidence": ["reports/VALIDATION_EVAL.json（27 ERROR 根因）"],
        "resolution": "VALIDATION_PLAN plan_revision=5（rev5），重跑 evaluator。",
        "recorded_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
    json.dump(ev, io.open("reports/methodology/failure_events.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("EV-CRIT-002 logged")
