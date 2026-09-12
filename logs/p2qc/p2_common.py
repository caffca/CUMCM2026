# -*- coding: utf-8 -*-
"""P2 独立验证共用模块（编程对抗终检）。

规则：只依赖标准库；不 import code/prod 下任何模块；不使用位图大整数
（生产实现走 64300-bit 大整数位图，这里走纯解析区间算术，形成方法学上的真独立）。
"""
import csv
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CSV_PATH = os.path.join(ROOT, "data", "canonical_plans.csv")
RESULTS = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "logs", "p2qc")

B_MAX = 100
T_MAX = 643          # 600 + 30 + 12 + 1
DF_MAX = 10
DT_MAX = 5
DG_MAX = 10

# Q3 新装 C 计划模板（题面）：3 频带 x 2 时长 x 12 重复，间隔 8
C_W, C_D, C_N, C_G = 3, 2, 12, 8


def rj(rel):
    return json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))


def load_plans():
    """独立 CSV 读取（csv 模块，非手写 split）。返回按 id 升序的 dict 列表。"""
    plans = []
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            p = {
                "id": row["equipment_id"].strip(),
                "cls": row["cls"].strip(),
                "f0": int(row["f_lo"]),
                "f1": int(row["f_hi"]),
                "t0": int(row["t_first_lo"]),
                "t1": int(row["t_first_hi"]),
                "g": int(row["gap"]),
                "n": int(row["use_count"]),
                "bw_csv": int(row["band_width"]),
                "tw_csv": int(row["time_width"]),
            }
            p["d"] = p["t1"] - p["t0"]
            plans.append(p)
    plans.sort(key=lambda x: x["id"])
    return plans


def data_integrity(plans):
    """CSV 自洽：类别/数量/宽度列与推导值一致，原始值均在合法域内。"""
    bad = []
    counts = {"A": 0, "B": 0, "C": 0}
    for p in plans:
        if p["cls"] != p["id"][0]:
            bad.append(f"{p['id']}: cls 与 id 前缀不符")
        counts[p["cls"]] = counts.get(p["cls"], 0) + 1
        if p["bw_csv"] != p["f1"] - p["f0"]:
            bad.append(f"{p['id']}: band_width {p['bw_csv']} != f1-f0 {p['f1']-p['f0']}")
        if p["tw_csv"] != p["t1"] - p["t0"]:
            bad.append(f"{p['id']}: time_width {p['tw_csv']} != t1-t0 {p['d']}")
        if not (0 <= p["f0"] < p["f1"] <= B_MAX):
            bad.append(f"{p['id']}: 频段越界 [{p['f0']},{p['f1']})")
        if p["t0"] < 0 or p["n"] < 1 or p["g"] < 1:
            bad.append(f"{p['id']}: t0/n/g 非法")
    ids = [p["id"] for p in plans]
    if len(set(ids)) != len(ids):
        bad.append("equipment_id 有重复")
    return counts, bad


def shift(p, df=0, dt=0, dg=0):
    """返回应用单个参数动作后的计划（题面 A4-one-param：一次只动一个参数）。"""
    q = dict(p)
    q["f0"] = p["f0"] + df
    q["f1"] = p["f1"] + df
    q["t0"] = p["t0"] + dt
    q["g"] = p["g"] + dg
    return q


def slot_list(p, limit_check=False):
    """题面公式 slot_k = [t0 + k*(g+d), t0 + k*(g+d) + d)。"""
    out = []
    for k in range(p["n"]):
        s = p["t0"] + k * (p["g"] + p["d"])
        e = s + p["d"]
        out.append((s, e))
    return out


def iv_hit(a, b):
    """半开区间相交判据（解析式，非位图）。"""
    return max(a[0], b[0]) < min(a[1], b[1])


def band_hit(p, q):
    return max(p["f0"], q["f0"]) < min(p["f1"], q["f1"])


def conflict(p, q, reason=False):
    """两计划冲突 <=> 频段相交 且 存在 k,l 使时隙相交。"""
    if not band_hit(p, q):
        return (False, None) if reason else False
    sp, sq = slot_list(p), slot_list(q)
    for i, x in enumerate(sp):
        for j, y in enumerate(sq):
            if iv_hit(x, y):
                return (True, (i, j, x, y)) if reason else True
    return (False, None) if reason else False


def all_conflicts(plans):
    """O(n^2) 逐对枚举。返回 (边集 sorted list of [id_a,id_b]，pairs_checked)。"""
    edges = []
    n = len(plans)
    checked = 0
    for i in range(n):
        for j in range(i + 1, n):
            checked += 1
            if conflict(plans[i], plans[j]):
                a, b = sorted((plans[i]["id"], plans[j]["id"]))
                edges.append([a, b])
    edges.sort()
    return edges, checked


def sha_of_edges(edges):
    """与生产一致的去重指纹口径：sha256(json.dumps(sorted_edges))。"""
    import hashlib
    return hashlib.sha256(json.dumps(edges).encode("utf-8")).hexdigest()


def classpair_counts(edges):
    c = {}
    for a, b in edges:
        c["".join(sorted(a[0] + b[0]))] = c.get("".join(sorted(a[0] + b[0])), 0) + 1
    return c


def horizon_violation(p):
    """返回越出 [0,100)x[0,643) 的原因列表（FMS mask-form：越界非法）。"""
    bad = []
    if p["f0"] < 0 or p["f1"] > B_MAX:
        bad.append(f"band[{p['f0']},{p['f1']})")
    if p["g"] < 1:
        bad.append(f"gap={p['g']}")
    for s, e in slot_list(p):
        if s < 0 or e > T_MAX:
            bad.append(f"slot[{s},{e})")
            break
    return bad


def wr(name, obj):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    return os.path.join(OUT, name)


def verdict(ok):
    return "PASS" if ok else "FAIL"
