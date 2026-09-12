# -*- coding: utf-8 -*-
"""从权威 results JSON 填充官方模板 → submission/result1-4.xlsx（唯一出口：数字全部来自 results/）。"""
import json, os, shutil, sys
import openpyxl

TPL = "附件/附件2"
OUT = "submission"


def R(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("result", d)


def band_str(pid, f0, f1, df=0):
    return f"[{f0 + df},{f1 + df})"


def main():
    os.makedirs(OUT, exist_ok=True)
    plans = {}
    import io
    for ln in io.open("data/canonical_plans.csv", encoding="utf-8").read().splitlines()[1:]:
        c = ln.split(",")
        plans[c[0]] = (int(c[2]), int(c[3]), int(c[4]), int(c[5]), int(c[6]))
    q1 = R("results/Q1_detect.json")
    q2 = R("results/Q2_solution.json")
    q3 = R("results/Q3_solution.json")
    q4 = R("results/Q4_solution.json")
    # result1
    wb = openpyxl.load_workbook(os.path.join(TPL, "result1.xlsx"))
    ws = wb.active
    for i, (a, b) in enumerate(q1["edges"], 1):
        ws.cell(row=i + 1, column=1, value=i)
        ws.cell(row=i + 1, column=2, value=a)
        ws.cell(row=i + 1, column=3, value=b)
    wb.save(os.path.join(OUT, "result1.xlsx"))
    # result2 / result4
    def fill(res, fname, gap_col):
        wb = openpyxl.load_workbook(os.path.join(TPL, fname))
        ws = wb.active
        acts = res["actions"]
        r = 2
        for pid, o in acts.items():
            f0, f1, t0, t1, g = plans[pid]
            ws.cell(row=r, column=1, value=pid)
            if o.get("revoke"):
                ws.cell(row=r, column=4 if not gap_col else 5, value="是")
            else:
                if "df" in o:
                    ws.cell(row=r, column=2, value=f"[{f0 + int(o['df'])},{f1 + int(o['df'])})")
                if "dt" in o:
                    ws.cell(row=r, column=3, value=f"[{t0 + int(o['dt'])},{t1 + int(o['dt'])})")
                if gap_col and "dg" in o:
                    ws.cell(row=r, column=4, value=str(g + int(o["dg"])))
            r += 1
        wb.save(os.path.join(OUT, fname))
    fill(q2, "result2.xlsx", False)
    fill(q4, "result4.xlsx", True)
    # result3
    wb = openpyxl.load_workbook(os.path.join(TPL, "result3.xlsx"))
    ws = wb.active
    for i, (f0, t0) in enumerate(q3["selected"], 1):
        ws.cell(row=i + 1, column=1, value=i)
        ws.cell(row=i + 1, column=2, value=f"[{f0},{f0 + 3})")
        ws.cell(row=i + 1, column=3, value=f"[{t0},{t0 + 2})")
    wb.save(os.path.join(OUT, "result3.xlsx"))
    print("xlsx written:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
