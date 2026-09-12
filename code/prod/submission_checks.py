# -*- coding: utf-8 -*-
"""提交件一致性诊断：xlsx↔results 对账 → 诊断结果文件（经 result_writer --diagnostic 登记）。
用法：python code/prod/submission_checks.py（在 make_xlsx 之后运行）"""
import json, os, subprocess, sys

WRITER = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts\result_writer.py"
os.makedirs("runs/checks", exist_ok=True)


def R(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("result", d)


def emit_diag(name, qid, payload):
    tmp = f"runs/checks/{name}.json"
    json.dump(payload, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    out = f"results/{name}.json"
    cmd = [sys.executable, WRITER, "--workspace", ".", "--payload", tmp, "--output", out,
           "--problem-id", qid, "--role", "support", "--diagnostic",
           "--generator", "code/prod/submission_checks.py",
           "--input-file", "data/canonical_plans.csv"]
    if os.path.exists(out):
        cmd.append("--replace")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(("OK  " if r.returncode == 0 else "FAIL") + f" {out}", (r.stdout or "")[-160:] if r.returncode else "")
    if r.returncode:
        print(r.stderr[-500:])


def xlsx_rows(path, col_id=1):
    import openpyxl
    ws = openpyxl.load_workbook(path).active
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r and r[col_id - 1] not in (None, ""):
            rows.append(r)
    return rows


def main():
    q1 = R("results/Q1_detect.json")
    # Q1_verify：独立位图实现视图（从 per_variant 拆分，generator 记 q1v_bitmap）
    emit_diag("Q1_verify", "Q1", {**q1["per_variant"]["bitmap"],
               "counts_agree_with_primary": 1 if q1["per_variant"]["bitmap"]["edges_sha256"] == q1["edges_sha256"] else 0,
               "derived_from": "results/Q1_detect.json:per_variant.bitmap"})
    # Q1_stats：result1.xlsx 对账
    rows = xlsx_rows("submission/result1.xlsx")
    got = set()
    for r in rows:
        a, b = str(r[1]), str(r[2])
        got.add(tuple(sorted((a, b))))
    truth = set(tuple(sorted(e)) for e in q1["edges"])
    emit_diag("Q1_stats", "Q1", {"result1_edge_symdiff": len(got ^ truth),
               "result1_rows": len(rows), "boundary_cases_failed": q1["boundary_cases_failed"],
               "classpair_sum_minus_total": q1["classpair_sum_minus_total"],
               "stress_min_recall": q1["stress_min_recall"], "involved_plans": q1["involved_plans"],
               "isolated_plans": q1["isolated_plans"], "counts": q1["counts"]})
    # Q2_table1
    q2 = R("results/Q2_solution.json")
    ck = R("results/Q2_check.json")
    rows2 = xlsx_rows("submission/result2.xlsx")
    byc = ck["by_class"]
    closure = 0
    for c, tot in (("A", 20), ("B", 40), ("C", 90)):
        st = byc[c]
        closure += abs(st["kept"] + st["adjusted"] + st["revoked"] - tot)
    n_change = len(rows2)
    closure += abs(n_change - (byc["A"]["adjusted"] + byc["B"]["adjusted"] + byc["C"]["adjusted"]
                               + byc["A"]["revoked"] + byc["B"]["revoked"] + byc["C"]["revoked"]))
    emit_diag("Q2_table1", "Q2", {"by_class": byc, "table_closure_diff": closure,
               "result2_rows": n_change, "objective_tuple": q2["objective_tuple"]})
    # Q3 submission
    q3 = R("results/Q3_solution.json")
    rows3 = xlsx_rows("submission/result3.xlsx")
    emit_diag("Q3_submission_check", "Q3", {"result3_rows_minus_phi": len(rows3) - q3["phi"],
               "rows": len(rows3), "phi": q3["phi"]})
    # Q4 提交件行数对账（result4 行数 == 动作计划数）
    q4f = json.load(open("results/Q4_solution.json", encoding="utf-8"))
    q4acts = q4f.get("result", q4f)["actions"]
    n4 = len(xlsx_rows("submission/result4.xlsx"))
    ch4 = sum(1 for o in q4acts.values() if o)
    emit_diag("Q4_submission_check", "Q4", {"result4_rows_minus_changes": n4 - ch4,
               "result4_rows": n4, "changed_or_revoked": ch4})
    # Q4_table1
    q4 = R("results/Q4_solution.json")
    ck4 = R("results/Q4_check.json")
    rows4 = xlsx_rows("submission/result4.xlsx")
    byc4 = ck4["by_class"]
    closure4 = 0
    for c, tot in (("A", 20), ("B", 40), ("C", 90)):
        st = byc4[c]
        closure4 += abs(st["kept"] + st["adjusted"] + st["revoked"] - tot)
    n_change4 = len(rows4)
    closure4 += abs(n_change4 - sum(byc4[c]["adjusted"] + byc4[c]["revoked"] for c in "ABC"))
    emit_diag("Q4_table1", "Q4", {"by_class": byc4, "table_closure_diff": closure4,
               "result4_rows": n_change4, "objective_tuple": q4["objective_tuple"]})


if __name__ == "__main__":
    main()
