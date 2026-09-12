# -*- coding: utf-8 -*-
"""intake 数据快照：附件1.xlsx -> 规范 CSV（cleaned）+ dataset_snapshot.v1 哈希绑定。"""
import hashlib, io, json, os, re, sys
import openpyxl

sys.stdout.reconfigure(encoding="utf-8")
RAW = "附件/附件1.xlsx"
CLEAN = "data/canonical_plans.csv"
OUT = "reports/data/DATASET_SNAPSHOT.json"

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

wb = openpyxl.load_workbook(RAW)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
assert rows[0][0] == "用频装备编号"
pat = re.compile(r"^\[(\d+),(\d+)\)$")
recs = []
for r in rows[1:]:
    if r[0] is None:
        continue
    eq, fb, ft, gap, cnt = r
    m1, m2 = pat.match(fb.strip()), pat.match(ft.strip())
    assert m1 and m2, r
    f1, f2 = int(m1.group(1)), int(m1.group(2))
    t1, t2 = int(m2.group(1)), int(m2.group(2))
    assert 0 <= f1 < f2 <= 100 and t1 < t2 and gap > 0 and cnt > 0, r
    recs.append(dict(equipment_id=eq, cls=eq[0], f_lo=f1, f_hi=f2,
                     t_first_lo=t1, t_first_hi=t2, gap=int(gap), use_count=int(cnt),
                     band_width=f2 - f1, time_width=t2 - t1))

os.makedirs("reports/data", exist_ok=True)
os.makedirs(os.path.dirname(CLEAN) or ".", exist_ok=True)
hdr = ["equipment_id", "cls", "f_lo", "f_hi", "t_first_lo", "t_first_hi", "gap", "use_count", "band_width", "time_width"]
lines = [",".join(hdr)] + [",".join(str(x[k]) for k in hdr) for x in recs]
io.open(CLEAN, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")

by_cls = {}
for x in recs:
    by_cls.setdefault(x["cls"], []).append(x)
profile = {}
for c, xs in sorted(by_cls.items()):
    profile[c] = {
        "n": len(xs),
        "band_width": sorted({x["band_width"] for x in xs}),
        "time_width": sorted({x["time_width"] for x in xs}),
        "gap": sorted({x["gap"] for x in xs}),
        "use_count": sorted({x["use_count"] for x in xs}),
        "f_lo_range": [min(x["f_lo"] for x in xs), max(x["f_lo"] for x in xs)],
        "t_first_lo_range": [min(x["t_first_lo"] for x in xs), max(x["t_first_lo"] for x in xs)],
        "last_slot_end_max": max(x["t_first_lo"] + (x["use_count"] - 1) * (x["gap"] + x["time_width"]) + x["time_width"] for x in xs),
    }

snap = {
    "schema_version": 1,
    "dataset_id": "cumcm2026D-attachment1-plans-150",
    "raw_input_sha256": sha(RAW),
    "cleaned_dataset_sha256": sha(CLEAN),
    "source_file": RAW.replace("\\", "/"),
    "source_sha256": sha(RAW),
    "source_files": [RAW.replace("\\", "/")],
    "source_sha256s": [sha(RAW)],
    "cleaned_file": CLEAN.replace("\\", "/"),
    "created_at": "intake",
    "n_records": len(recs),
    "columns": hdr,
    "class_profile": profile,
    "notes": "cleaned 为无损规范化解析（区间字符串->整数四列），未删除/修改任何记录；profile 供 discovery 复核 DGP。",
}
io.open(OUT, "w", encoding="utf-8").write(json.dumps(snap, ensure_ascii=False, indent=2))
print("records:", len(recs), "cleaned:", CLEAN, "snapshot:", OUT)
print(json.dumps(profile, ensure_ascii=False))
