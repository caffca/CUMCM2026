# -*- coding: utf-8 -*-
"""P2-9：交付件（submission/result*.xlsx）与权威 results JSON 的一致性独立核对。"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.environ.get("DSH_ENVLIBS", r"F:\dsh_envlibs\mathmodel"))   # 自写环境注入，非复用 cli.py
import p2_common as P  # noqa
import openpyxl  # noqa

SUB = os.path.join(P.ROOT, "submission")


def rows(fn):
    wb = openpyxl.load_workbook(os.path.join(SUB, fn), data_only=True)
    ws = wb.active
    return [[c for c in r] for r in ws.iter_rows(values_only=True)]


def rng_parser(v):
    if v is None:
        return None
    s = str(v).strip()
    m = re.match(r"\[?\s*(\d+)\s*[,，]\s*(\d+)\s*\)?", s)
    return (int(m.group(1)), int(m.group(2))) if m else None


def main():
    plans = P.load_plans()
    pmap = {p["id"]: p for p in plans}
    out = {"check": "交付件一致性"}

    # result1：冲突对
    q1 = P.rj(os.path.join("results", "Q1_detect.json"))
    r1 = rows("result1.xlsx")
    body1 = [r for r in r1[1:] if r and r[0]]
    out["result1_rows"] = len(body1)
    out["result1_edges_auth"] = len(q1["edges"])
    pairs_x = set()
    for r in body1:
        cells = [str(x).strip() for x in r if x is not None]
        ids = [c for c in cells if re.match(r"^[ABC]\d{3}$", c)]
        if len(ids) >= 2:
            pairs_x.add(tuple(sorted(ids[:2])))
    pairs_a = {tuple(sorted(e)) for e in q1["edges"]}
    out["result1_symdiff_vs_auth"] = len(pairs_x ^ pairs_a)
    out["result1_rowparse_ok"] = len(pairs_x) > 0

    # result2：调整后频段/时间 + 撤销标记
    q2 = P.rj(os.path.join("results", "Q2_solution.json"))
    r2 = rows("result2.xlsx")
    body2 = [r for r in r2[1:] if r and r[0]]
    mismatch2, revoked_x = [], []
    seen2 = set()
    for r in body2:
        pid = str(r[0]).strip()
        if not re.match(r"^[ABC]\d{3}$", pid):
            continue
        seen2.add(pid)
        o = q2["actions"].get(pid, {})
        p = pmap[pid]
        if o.get("revoke"):
            revoked_x.append(pid)
            continue
        exp_band = (p["f0"] + int(o.get("df", 0)), p["f1"] + int(o.get("df", 0)))
        exp_t = (p["t0"] + int(o.get("dt", 0)), p["t1"] + int(o.get("dt", 0)))
        got_band = rng_parser(r[1]) if len(r) > 1 else None
        got_t = rng_parser(r[2]) if len(r) > 2 else None
        if got_band and got_band != exp_band:
            mismatch2.append({"id": pid, "field": "band", "xlsx": got_band, "expect": exp_band})
        if got_t and got_t != exp_t:
            mismatch2.append({"id": pid, "field": "time", "xlsx": got_t, "expect": exp_t})
    out["result2_rows"] = len(seen2)
    kept2 = {pid for pid in pmap if not q2["actions"].get(pid)}
    out["result2_missing_ids"] = sorted(set(pmap) - seen2)
    out["result2_missing_are_exactly_kept"] = (set(pmap) - seen2) == kept2
    out["result2_template_requires_all_150"] = False  # 附件2 模板仅表头，无预填行
    out["result2_band_time_mismatch"] = mismatch2[:15]
    out["result2_n_mismatch"] = len(mismatch2)
    out["result2_revoked_mine"] = sorted(revoked_x)
    out["result2_revoked_auth"] = sorted(k for k, v in q2["actions"].items() if v.get("revoke"))

    # result3：新增 C 计划
    q3 = P.rj(os.path.join("results", "Q3_solution.json"))
    r3 = rows("result3.xlsx")
    body3 = [r for r in r3[1:] if r and any(x is not None for x in r)]
    x3 = set()
    for r in body3:
        b = rng_parser(r[1]) if len(r) > 1 else None
        t = rng_parser(r[2]) if len(r) > 2 else None
        if b and t:
            x3.add((b[0], t[0]))
    a3 = {(f0, t0) for f0, t0 in q3["selected"]}
    out["result3_rows"] = len(body3)
    out["result3_phi"] = q3["phi"]
    out["result3_symdiff_vs_auth"] = len(x3 ^ a3)
    out["result3_parse_count"] = len(x3)

    # result4
    q4 = P.rj(os.path.join("results", "Q4_solution.json"))
    r4 = rows("result4.xlsx")
    body4 = [r for r in r4[1:] if r and r[0]]
    mismatch4 = []
    seen4 = set()
    for r in body4:
        pid = str(r[0]).strip()
        if not re.match(r"^[ABC]\d{3}$", pid):
            continue
        seen4.add(pid)
        o = q4["actions"].get(pid, {})
        p = pmap[pid]
        if o.get("revoke"):
            continue
        exp_band = (p["f0"] + int(o.get("df", 0)), p["f1"] + int(o.get("df", 0)))
        exp_t = (p["t0"] + int(o.get("dt", 0)), p["t1"] + int(o.get("dt", 0)))
        exp_g = (rng_parser(r[3])[0] if len(r) > 3 and rng_parser(r[3]) else None)
        gb, gt = (rng_parser(r[1]) if len(r) > 1 else None), (rng_parser(r[2]) if len(r) > 2 else None)
        if gb and gb != exp_band:
            mismatch4.append({"id": pid, "field": "band", "xlsx": gb, "expect": exp_band})
        if gt and gt != exp_t:
            mismatch4.append({"id": pid, "field": "time", "xlsx": gt, "expect": exp_t})
        if exp_g is not None and "dg" in o and exp_g != p["g"] + o["dg"]:
            mismatch4.append({"id": pid, "field": "gap", "xlsx": exp_g, "expect": p["g"] + o["dg"]})
    out["result4_rows"] = len(seen4)
    out["result4_n_mismatch"] = len(mismatch4)
    out["result4_mismatch_sample"] = mismatch4[:15]
    kept4 = {pid for pid in pmap if not q4["actions"].get(pid)}
    out["result4_missing_ids"] = sorted(set(pmap) - seen4)
    out["result4_missing_are_exactly_kept"] = (set(pmap) - seen4) == kept4
    out["note_omission_policy"] = ("result2/result4 只登记被调整或被撤销的计划，未登记'保持不变'者；"
                                  "附件2 模板仅有表头（无预填 150 行），故不构成违规，但评审口径存在歧义风险。")
    out["verdict"] = P.verdict(
        out["result1_symdiff_vs_auth"] == 0 and out["result2_n_mismatch"] == 0
        and out["result2_missing_are_exactly_kept"]
        and out["result3_rows"] == q3["phi"] and out["result3_symdiff_vs_auth"] == 0
        and out["result4_n_mismatch"] == 0 and out["result4_missing_are_exactly_kept"]
    )
    P.wr("p2_xlsx_report.json", out)
    print(json.dumps(out, ensure_ascii=False, indent=1)[:4000])


if __name__ == "__main__":
    main()
