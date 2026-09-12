# -*- coding: utf-8 -*-
"""rev6：6 处 evidence_files 全部指向已登记 results 件（判据不变），并生成 Q3 敏感性诊断件。"""
import io, py_compile
p = "code/vp_build.py"
s = io.open(p, encoding="utf-8").read()
pairs = [
 # V-Q1-05 纯诊断 → 加权威 Q1_detect（classpair 字段权威件也有）
 ('"must", {"operator": "equals", "lhs": "results:Q1_stats.classpair_sum_minus_total", "rhs": 0},\n   ["results/Q1_stats.json"]',
  '"must", {"operator": "equals", "lhs": "results:Q1_stats.classpair_sum_minus_total", "rhs": 0},\n   ["results/Q1_stats.json", "results/Q1_detect.json"]'),
 # V-Q2-04 去未登记 methodology 路径 → 用权威 Q2_solution（degeneracy_ratio 字段所在）
 ('  ["results/Q2_solution.json", "reports/methodology/optimization_degeneracy.json"]',
  '  ["results/Q2_solution.json"]'),
 # V-Q2-06 未生成的 Q2_baseline → GRASP 中位在 Q2_solution
 ('"results/Q2_baseline.json"', '"results/Q2_solution.json"'),
 # V-Q2-07 纯诊断 → 加权威
 ('["results/Q2_table1.json", "submission/result2.xlsx"]',
  '["results/Q2_solution.json", "results/Q2_table1.json"]'),
 # V-Q3-06 去未登记 FMS 路径
 ('  ["results/Q3_solution.json", "reports/FINAL_MODEL_SPEC.json"]',
  '  ["results/Q3_solution.json", "results/Q2_solution.json"]'),
 # V-Q3-07 optional：证据指向将生成的诊断件（保留该验证，标 optional）
 ('"plan_revision": 5', '"plan_revision": 6'),
]
n = 0
for a, b in pairs:
    if a in s:
        s = s.replace(a, b); n += 1
    else:
        print("MISS:", a[:60])
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("rev6 evidence fixed:", n)
