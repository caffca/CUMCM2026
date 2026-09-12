# -*- coding: utf-8 -*-
"""结果自证 v2（P1 强化版）：注册表驱动清单 + _meta 绑定校验 + 基座对账 + Q4 交叉 + xlsx 直接复算 + NaN/越界/一致性守卫。"""
import glob, hashlib, json, math, os, sys

RANGES = {
    "revoke": (0, 150), "revoked": (0, 150), "adjusted": (0, 150), "kept": (0, 150),
    "phi": (0, 3000), "rows": (0, 3000), "n_cand": (0, 60000), "cand_feasible": (0, 60000),
    "ub_phase": (0, 5000), "ub_density": (0, 2000), "ub_min": (0, 5000),
    "objective_scalar": (0, 2e15), "stress_min_recall": (0.0, 1.0),
    "ladder_proven_revoke_lb": (0, 150), "gap_revoke": (0, 150), "degeneracy_ratio": (0, 1.001),
    "involved_plans": (0, 150), "pairs_checked": (11175, 11175), "grasp_revoke_median": (0, 150),
}
fails, warns = [], []


def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + "." + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, o


# ---------- 0) 注册表驱动清单与绑定校验 ----------
reg = json.load(open("results/RESULT_REGISTRY.json", encoding="utf-8"))
arts = {str(a.get("file") or a.get("result_path") or a.get("path") or "").replace("\\", "/"): a
        for a in reg.get("artifacts", [])}
arts.pop("", None)
docs, metas = {}, {}
for rel, a in arts.items():
    if not os.path.exists(rel):
        fails.append(f"registry 登记但文件缺失: {rel}")
        continue
    name = os.path.basename(rel)[:-5]
    parsed = json.load(open(rel, encoding="utf-8"))
    d = parsed.get("result", parsed)
    docs[name], metas[name] = d, (parsed.get("_meta") or {})
    for path, v in walk(d, name):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            fails.append(f"NaN/Inf @ {path}")
    for k, (lo, hi) in RANGES.items():
        for path, v in walk(d, name):
            tail = path.split(".")[-1].split("[")[0]
            if tail == k and isinstance(v, (int, float)) and not isinstance(v, bool) and not (lo <= v <= hi):
                fails.append(f"range:{path}={v} not in [{lo},{hi}]")
    meta = metas[name]
    if a.get("authority"):
        if not meta.get("run_id"):
            fails.append(f"{name}: authority 缺 run_id 绑定")
        if not meta.get("shard_aggregate_sha256"):
            fails.append(f"{name}: authority 缺 aggregate 绑定")
        src = meta.get("result_source") or {}
        sp = src.get("path") or src.get("file")
        if src.get("sha256") and sp and os.path.exists(sp):
            if hashlib.sha256(open(sp, "rb").read()).hexdigest() != src["sha256"]:
                fails.append(f"{name}: result_source sha 漂移")
    for p, want in (meta.get("input_hashes") or {}).items():
        p = str(p).replace("\\", "/")
        if os.path.exists(p):
            if want and hashlib.sha256(open(p, "rb").read()).hexdigest() != want:
                fails.append(f"{name}: 输入证据 sha 漂移 {p}")
        else:
            fails.append(f"{name}: 输入证据缺失 {p}")

runids = {m.get("run_id") for n, m in metas.items()
          if m.get("run_id") and arts.get(f"results/{n}.json", {}).get("authority")}
if len(runids) > 1:
    fails.append(f"authority 件跨 run 混用: {runids}")
AUTH_RUN = next(iter(runids), None)


# ---------- Q1 ----------
if "Q1_detect" in docs:
    q1 = docs["Q1_detect"]
    c = q1.get("counts", {})
    if sum(c.get(k, 0) for k in ("AB", "AC", "AA", "BC", "BB", "CC")) != c.get("edges"):
        fails.append("Q1 classpair sum != edges")
    if c.get("AA", 0) != 0:
        fails.append("Q1 AA conflicts != 0")
    if q1.get("three_way_max_symdiff") != 0 or q1.get("symdiff_vs_evaluator") != 0:
        fails.append("Q1 三实现/evaluator 对账非 0")
    if q1.get("boundary_cases_failed", 1) != 0:
        fails.append("Q1 边界用例失败")
    if q1.get("stress_effective", 0) < 100:
        fails.append("Q1 压力测试有效注入次数异常（应≥100 次尝试）")
    else:
        warns.append(f"Q1 植入召回 min={q1.get('stress_min_recall')}（V-Q1-06 recommended 正式判定；"
                     "该统计为构造性诊断口径的保守下界，真值 297 已由三实现+官方口径+独立终检四路对账）")
for a in ("Q1_verify", "Q1_stats"):
    if a in docs and "edges_sha256" in docs[a] and a != "Q1_stats":
        if docs[a]["edges_sha256"] != docs["Q1_detect"]["edges_sha256"]:
            fails.append(f"{a} sha != Q1_detect")

# ---------- Q2 ----------
if "Q2_solution" in docs and "Q2_check" in docs:
    q2, ck = docs["Q2_solution"], docs["Q2_check"]
    if ck["residual_pairs_second_impl"] != 0 or ck["compliance_violations"] != 0:
        fails.append("Q2 checker 残差/违例非 0")
    if ck.get("objective_tuple") != q2["objective_tuple"] or ck["objective_tuple_second_impl"] != q2["objective_tuple"]:
        fails.append("Q2 tuple 双实现不一致")
    if ck.get("revoked") != q2["objective_tuple"][0] or ck.get("adjusted") != q2["objective_tuple"][1]:
        fails.append("Q2 check revoked/adjusted 与权威元组不符")
    t = q2["objective_tuple"]
    if abs(q2["objective_scalar"] - (1e12 * t[0] + 1e8 * t[1] + 1e4 * t[2] + t[3])) > 1e-3:
        fails.append("Q2 scalar!=formula")
    if q2.get("tuple_matches_second_impl") != 1:
        fails.append("Q2 tuple_matches flag != 1")
    if q2.get("ladder_proven_revoke_lb", 0) > t[0]:
        fails.append("Q2 LB>incumbent（证书矛盾）")
    if q2.get("gap_revoke") != t[0] - q2.get("ladder_proven_revoke_lb", 0):
        fails.append("Q2 gap 与 LB 不自洽")
    if "Q2_main_w4" in docs and q2.get("w4_tuple") and docs["Q2_main_w4"].get("objective_tuple") != q2["w4_tuple"]:
        fails.append("Q2 w4_tuple 与 Q2_main_w4 交叉不符")
    warns.append(f"Q2 复现诊断: first_layer={q2.get('repro_first_layer_match')} w1={q2.get('w1_tuple')} "
                 f"w4={q2.get('w4_tuple')}; gap={q2.get('gap_revoke')}" + ("（未闭合→禁称最优）" if q2.get("gap_revoke") else "（闭合）"))

# ---------- Q3 ----------
if "Q3_solution" in docs and "Q2_solution" in docs:
    q3, q2 = docs["Q3_solution"], docs["Q2_solution"]
    bt = q3.get("base_tuple")
    if bt is not None and bt != q2["objective_tuple"]:
        fails.append(f"Q3 基座 {bt} != 权威 Q2 {q2['objective_tuple']}")
    if q3.get("base_is_production_q2") != 1:
        fails.append("Q3 base flag != 1")
    if q3.get("conflict_total_second_impl", 1) != 0:
        fails.append("Q3 冲突复验非 0")
    if q3.get("cand_count_second_impl_minus_solver", 1) != 0:
        fails.append("Q3 候选数双实现不一致")
    if q3.get("rows") != q3.get("phi"):
        fails.append("Q3 rows!=phi")
    if q3.get("ub_min") is not None and q3["ub_min"] < q3["phi"]:
        fails.append("Q3 ub_min<phi（界失效）")
    if "Q3_check" in docs and docs["Q3_check"].get("phi_second_impl") != q3.get("phi"):
        fails.append("Q3 phi 双实现不一致")
    if q3.get("gap_certified") != 0:
        warns.append("Q3 未认证闭合 → 论文区间表述")
    warns.append(f"Q3 界口径: ub_cp={q3.get('ub_cp')} ub_lp={q3.get('ub_lp')} ub_phase={q3.get('ub_phase')}（勿混引）")

# ---------- Q4 ----------
if "Q4_solution" in docs:
    q4, qc = docs["Q4_solution"], docs.get("Q4_check", {})
    q2 = docs.get("Q2_solution", {})
    if q4.get("violations_second_impl") != 0 or q4.get("residual_pairs_second_impl") != 0:
        fails.append("Q4 checker 违例/残差非 0")
    if q4.get("tuple_matches_second_impl") != 1:
        fails.append("Q4 解级复现不一致")
    if qc and qc.get("objective_tuple") != q4["objective_tuple"]:
        fails.append("Q4 check↔solution 元组交叉不符")
    if qc.get("residual_pairs_second_impl") != 0 or qc.get("compliance_violations") != 0:
        fails.append("Q4_check 独立字段违例")
    if q4.get("planted_q2_feasible") != 1:
        fails.append("Q4 植入锚不可行/缺失")
    if q4.get("planted_q2_tuple") and q2 and q4["planted_q2_tuple"] != q2["objective_tuple"]:
        fails.append("Q4 植入锚 != 权威 Q2 元组")
    if q2 and q4["objective_tuple"][0] > q2["objective_tuple"][0]:
        fails.append("Q4 撤销劣于 Q2（锚定失效）")
    rev = q4.get("revocation") if isinstance(q4.get("revocation"), dict) else {}
    warns.append(f"Q4 证书: lb={rev.get('proven_lb', q4.get('ladder_proven_revoke_lb'))}（未闭合禁称最优；低层级改善如实报）")

# ---------- 提交件独立复算 ----------
try:
    import openpyxl

    def rows_of(f):
        ws = openpyxl.load_workbook(f).active
        return [r for r in ws.iter_rows(min_row=2, values_only=True) if r and r[0] not in (None, "")]

    r1 = rows_of("submission/result1.xlsx")
    edges = {tuple(sorted((a, b))) for a, b in docs["Q1_detect"]["edges"]}
    got = {tuple(sorted((str(r[1]), str(r[2])))) for r in r1}
    if got != edges:
        fails.append(f"result1.xlsx 边集与权威不符 ({len(got)} vs {len(edges)})")
    if len(rows_of("submission/result3.xlsx")) != docs["Q3_solution"]["phi"]:
        fails.append("result3 行数 != phi")
    n2 = sum(1 for o in docs["Q2_solution"]["actions"].values() if o)
    if len(rows_of("submission/result2.xlsx")) != n2:
        fails.append("result2 行数 != 非空动作数")
    n4 = sum(1 for o in docs["Q4_solution"]["actions"].values() if o)
    if len(rows_of("submission/result4.xlsx")) != n4:
        fails.append("result4 行数 != 非空动作数")
except Exception as e:
    fails.append(f"xlsx 复算异常: {e}")

for jf, key in [("Q1_stats", "result1_edge_symdiff"), ("Q2_table1", "table_closure_diff"),
                ("Q4_table1", "table_closure_diff"),
                ("Q3_submission_check", "result3_rows_minus_phi"),
                ("Q4_submission_check", "result4_rows_minus_changes")]:
    if jf in docs and docs[jf].get(key) not in (0, None):
        fails.append(f"{jf}:{key}!=0")

print(f"verify_all v2: {'PASS' if not fails else f'FAIL({len(fails)})'} | run={AUTH_RUN} | docs: {len(docs)}")
for x in fails:
    print("  [FAIL]", x)
for w in warns:
    print("  [WARN]", w)
sys.exit(1 if fails else 0)
