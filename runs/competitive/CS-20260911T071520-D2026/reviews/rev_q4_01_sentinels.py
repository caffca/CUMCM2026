# -*- coding: utf-8 -*-
"""REV-Q4-01 附件脚本 I：负例（sentinel）测试矩阵 —— 冻结 evaluator 对 Q4 间隔规则的拒绝能力。
三候选全部只声称『构造期断言/域生成剔除』，无人测试 checker 能否拒绝非法动作。
本脚本把 6 类非法/边界动作逐一喂给冻结 evaluator（只读），登记其返回方式：
  正常返回 feasible=false（合格拒绝）/ 崩溃（不合格）/ 返回 feasible=true（漏判，最危险）。
输出 reviews/_tmp/recheck_out_I.json
"""
import io, json, os, subprocess, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(RUN, "reviews", "_tmp")
sys.stdout.reconfigure(encoding="utf-8")
EV = os.path.join(RUN, "canonical_evaluator.py")

CASES = [
    ("q4_dg_nonpositive_gap", "Q4", {"C001": {"dg": -8}}, "g'=8-8=0 违反 Q4-F019（应拒绝）"),
    ("q4_dg_over10", "Q4", {"C001": {"dg": 11}}, "|dg|=11 越 10Δt（应拒绝）"),
    ("q4_dg_on_A", "Q4", {"A001": {"dg": 1}}, "A 类调间隔（应拒绝）"),
    ("q4_dg_on_B", "Q4", {"B001": {"dg": -1}}, "B 类调间隔（应拒绝）"),
    ("q4_df_over10", "Q4", {"C001": {"df": 11}}, "|df|=11 越 F-012（应拒绝）"),
    ("q4_dt_over5", "Q4", {"C001": {"dt": 6}}, "|dt|=6 越 F-012（应拒绝）"),
    ("q4_multi_param", "Q4", {"C001": {"df": 1, "dt": 1}}, "一个计划调两参数（应拒绝）"),
    ("q4_df_out_of_band", "Q4", {"A004": {"df": 5}}, "频段越出 [0,100)（应拒绝）"),
    ("q4_dt_beyond_horizon", "Q4", {"C083": {"dt": 3}}, "末窗越 643（应拒绝）"),
    ("q4_dg_positive_last_window", "Q4", {"C083": {"dg": 1}}, "C083 dg=+1 ⇒ 末窗 654>643（应拒绝）"),
    ("q4_unknown_plan", "Q4", {"C999": {"df": 1}}, "未知计划编号（应拒绝）"),
    ("q2_dg_forbidden", "Q2", {"C001": {"dg": 2}}, "Q2 禁调间隔（应拒绝）"),
    ("q4_zero_value_action", "Q4", {"C001": {"df": 0}}, "0 值动作（口径歧义：stats 计调整、objective 不计）"),
    ("q4_empty_action", "Q4", {"C001": {}}, "空动作 dict（应拒绝/忽略）"),
    ("q4_boundary_gp1", "Q4", {"C083": {"dg": -7}}, "边界合法：g'=1，末窗缩短（应通过）"),
    ("q4_boundary_dt_minus5", "Q4", {"A006": {"dt": -5}}, "边界合法：dt=-5（应通过）"),
]

out = {"cases": [], "defects": [], "notes": []}
for name, q, sol, expect in CASES:
    sp = os.path.join(TMP, f"sentinel_{name}.json")
    op = os.path.join(TMP, f"sentinel_{name}.out.json")
    io.open(sp, "w", encoding="utf-8").write(json.dumps(sol, ensure_ascii=False))
    r = subprocess.run([sys.executable, EV, "--question", q, "--solution", sp, "--out", op],
                       capture_output=True, text=True, encoding="utf-8")
    rec = dict(case=name, question=q, action=sol, expectation=expect, exit_code=r.returncode)
    if r.returncode != 0:
        tail = [l.strip() for l in (r.stderr or "").strip().splitlines() if l.strip()][-2:]
        rec.update(outcome="CRASH", stderr_tail=tail)
        out["defects"].append(f"{name}: evaluator 崩溃（exit=1）而非返回 feasible=false — {tail[-1] if tail else ''}")
    else:
        j = json.load(io.open(op, encoding="utf-8"))
        kinds = sorted({v.split(":")[0] for v in j.get("violations", [])})
        rec.update(outcome="returned", feasible=j["feasible"], objective=j["objective"],
                   violation_kinds=kinds, n_violations=j.get("n_violations"))
        if "revoke" not in json.dumps(sol) and j["feasible"] is True:
            out["defects"].append(f"{name}: 非法/零信息动作被判 feasible=true（漏判）")
    out["cases"].append(rec)

# 0 值动作的 stats/objective 口径分叉专项
sp = os.path.join(TMP, "sentinel_zero_probe.json")
io.open(sp, "w", encoding="utf-8").write(json.dumps({"C001": {"df": 0}, "C002": {"df": 1}}))
op = os.path.join(TMP, "sentinel_zero_probe.out.json")
subprocess.run([sys.executable, EV, "--question", "Q4", "--solution", sp, "--out", op],
               capture_output=True, text=True, encoding="utf-8")
z = json.load(io.open(op, encoding="utf-8"))
out["zero_action_probe"] = dict(objective=z["objective"], stats_adjusted=z["stats"]["adjusted"],
                                stats_by_class_C=z["stats"]["by_class"]["C"],
                                divergence=(z["stats"]["adjusted"] != z["objective"][1]))
out["notes"].append(
    "objective_tuple 用 `if act.get(k)` 过滤 0 值（不计入 adjusted），apply_actions/stats 用 "
    "`not in (None, False)`（计入 adjusted）⇒ 同一动作文件在『目标』与『表1 统计』两个口径下 adjusted 不同；"
    "三候选域生成不含 0 值动作，故本次数字不受影响，但 Q4 正式结果若有人手工补 0 值行会造成表1 与元组不一致。")

io.open(os.path.join(TMP, "recheck_out_I.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False, indent=1))
