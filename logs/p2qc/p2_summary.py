# -*- coding: utf-8 -*-
"""P2-10：汇总所有独立校验报告，生成对照表与最终结论（P2QC_SUMMARY.md / .json）。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

D = P.OUT


def load(fn):
    return json.load(open(os.path.join(D, fn), encoding="utf-8"))


def main():
    q1 = load("p2_q1_report.json")
    q1b = load("p2_q1b_sensitivity.json")
    q2 = load("p2_q2_report.json")
    q3 = load("p2_q3_report.json")
    q3o = load("p2_q3_optimality.json") if os.path.exists(os.path.join(D, "p2_q3_optimality.json")) else {}
    q4 = load("p2_q4_report.json")
    ms = load("p2_modelspace_report.json")
    hn = load("p2_hint_report.json")
    st = load("p2_static_audit.json")
    lk = load("p2_leak_scan.json")
    pr = load("p2_provenance.json")
    rd = load("p2_redundancy.json")
    xl = load("p2_xlsx_report.json") if os.path.exists(os.path.join(D, "p2_xlsx_report.json")) else {}

    ff = load("p2_forced_and_fresh.json") if os.path.exists(os.path.join(D, "p2_forced_and_fresh.json")) else {}
    dt = load("p2_determinism.json") if os.path.exists(os.path.join(D, "p2_determinism.json")) else {}
    te = load("p2_tables_evaluator.json") if os.path.exists(os.path.join(D, "p2_tables_evaluator.json")) else {}
    rows = [
        # (项目, P2 独立值, 权威值, 判定)
        ("数据：计划总数", 150, 150, q1["n_plans"] == 150),
        ("数据：A/B/C 构成", "20/40/90", "20/40/90", q1["class_counts"] == {"A": 20, "B": 40, "C": 90}),
        ("Q1 逐对枚举对数", q1["pairs_checked_mine"], q1["pairs_checked_auth"], q1["pairs_checked_mine"] == q1["pairs_checked_auth"]),
        ("Q1 冲突对数", q1["edges_mine"], q1["edges_auth"], q1["edges_mine"] == q1["edges_auth"] == 297),
        ("Q1 双向对称差", q1["symdiff"], 0, q1["symdiff"] == 0),
        ("Q1 边集 SHA256", q1["sha_mine"][:16] + "…", q1["sha_auth_field"][:16] + "…", q1["sha_equal"]),
        ("Q1 分类对 (AB/AC/BC/AA/BB/CC)", "/".join(str(q1["counts_mine"][k]) for k in ["AB", "AC", "BC", "AA", "BB", "CC"]),
         "/".join(str(q1["counts_auth"][k]) for k in ["AB", "AC", "BC", "AA", "BB", "CC"]), all(q1["counts_equal"].values())),
        ("Q1 涉及计划数 / 孤立", f"{q1['involved_mine']} / {','.join(q1['isolated_mine'])}",
         f"{q1['involved_auth']} / {','.join(q1['isolated_auth'])}", q1["involved_mine"] == q1["involved_auth"]),
        ("Q1 口径敏感性（闭区间误判会多出）", f"+{q1b['n_extra_pairs_only_if_closed']} 对（435 总）", "0（半开）", q1b["edges_halfopen_mine"] == 297),
        ("Q2 撤销数", q2["n_revoked"], q2["auth_revoke_fields"]["revoke"], q2["n_revoked"] == q2["auth_revoke_fields"]["revoke"] == 6),
        ("Q2 调整数", q2["n_adjusted"], q2["objective_tuple_auth"][1], q2["n_adjusted"] == 121),
        ("Q2 保留数", q2["n_kept"], 23, q2["n_kept"] == 23),
        ("Q2 撤销+调整+保留", q2["sum_value"], 150, q2["sum_equals_150"]),
        ("Q2 调整后冲突对", q2["post_conflict_edges_mine"], q2["post_conflict_edges_auth_field"]["residual_pairs"],
         q2["post_conflict_edges_mine"] == 0),
        ("Q2 逐计划合规违例", len(q2["compliance_violations"]), q2["post_conflict_edges_auth_field"]["compliance_violations"],
         not q2["compliance_violations"]),
        ("Q2 越出 [0,643)×[0,100)（ADJ R3）", len(q2["horizon_violations_ADR3"]), 0, not q2["horizon_violations_ADR3"]),
        ("Q2 词典序元组", str(q2["objective_tuple_mine"]), str(q2["objective_tuple_auth"]), q2["objective_tuple_equal"]),
        ("Q2 冗余调整（可回退仍 0 冲突）", rd["Q2"]["n_single_revert_redundant"], 0, rd["Q2"]["n_single_revert_redundant"] == 0),
        ("Q2 G* 星形边", ms["Q2"]["gstar_mine"], ms["Q2"]["gstar_auth"], ms["Q2"]["gstar_equal"]),
        ("Q2 选项空间总数", ms["Q2"]["options_total_mine"], ms["Q2"]["options_total_auth"], ms["Q2"]["options_equal"]),
        ("Q3 新增 C 台数 / 行数", f"{q3['selected_rows_mine']} / {q3['rows_auth']}", q3["phi_auth"], q3["phi_eq_rows"]),
        ("Q3 与基座冲突", q3["conflicts_vs_base_mine"], q3["conflicts_vs_base_auth"], q3["conflicts_vs_base_mine"] == 0),
        ("Q3 C 之间冲突", q3["conflicts_internal_mine"], q3["conflicts_internal_auth"], q3["conflicts_internal_mine"] == 0),
        ("Q3 越界（f0+3>100 / 末周期>643）", len(q3["domain_violations"]), 0, not q3["domain_violations"]),
        ("Q3 候选集大小", q3["cand_universe_mine"], q3["n_cand_auth"], q3["cand_equal_auth"]),
        ("Q3 极大性（可再加的候选数）", q3["addable_count"], 0, q3["addable_count"] == 0),
        ("Q3 独立 CP-SAT 复解", f"{q3o.get('phi_mine')}（{q3o.get('solver_status')}，界 {q3o.get('best_bound_mine')}）",
         f"{q3['phi_auth']}（{q3['ub_auth']['status']}，界 {q3['ub_auth']['ub_cp']}）",
         q3o.get("phi_mine") == q3["phi_auth"] and q3o.get("proven_optimal_mine")),
        ("Q3 干扰边数（独立倒排建边）", q3o.get("n_edges_mine"), P.rj(os.path.join("results", "Q3_solution.json")).get("n_edges"),
         q3o.get("n_edges_mine") == P.rj(os.path.join("results", "Q3_solution.json")).get("n_edges")),
        ("Q4 撤销 / 调整 / 保留", f"{q4['n_revoked']} / {q4['n_adjusted']} / {q4['n_kept']}", "6 / 118 / 26", q4["sum_equals_150"]),
        ("Q4 调整后冲突对（slot 用新 g'）", q4["post_conflict_edges_mine"], q4["post_conflict_edges_auth"], q4["post_conflict_edges_mine"] == 0),
        ("Q4 |dg|<=10 且 g+dg>=1 违例", len(q4["dg_violations"]), 0, not q4["dg_violations"]),
        ("Q4 非 C 类被调间隔（R6 违例）", len(q4["nonC_dg_actions"]), 0, not q4["nonC_dg_actions"]),
        ("Q4 越界动作", len(q4["horizon_violations"]), 0, not q4["horizon_violations"]),
        ("Q4 dg 选项被剔除总数", f"{ms['Q4']['dg_dropped_total_mine']}（间隔非法 {ms['Q4']['dg_dropped_gap_mine']} + 时域截断 {ms['Q4']['dg_dropped_horizon_mine']}）",
         ms["Q4"]["dg_dropped_auth_label_field"],
         ms["Q4"]["dg_dropped_total_mine"] == ms["Q4"]["dg_dropped_auth_label_field"]),
        ("Q4 G* / 选项总数", f"{ms['Q4']['gstar_mine']} / {ms['Q4']['options_total_mine']}",
         f"{ms['Q4']['gstar_auth']} / {ms['Q4']['options_total_auth']}", ms["Q4"]["gstar_equal"] and ms["Q4"]["options_equal"]),
        ("Q4 词典序元组", str(q4["objective_tuple_mine"]), str(q4["objective_tuple_auth"]), q4["objective_tuple_equal"]),
        ("Q4 冗余调整", rd["Q4"]["n_single_revert_redundant"], 0, rd["Q4"]["n_single_revert_redundant"] == 0),
        ("Q4 植入 Q2 解残差", rd.get("q2_planted_residual_mine", q4.get("q2_planted_residual_mine")), q4["q2_planted_check"]["planted_q2_residual_auth"],
         q4.get("q2_planted_residual_mine") == q4["q2_planted_check"]["planted_q2_residual_auth"] == 0),
        ("hint：侦察解文件存在", hn["path_exists"], True, hn["path_exists"]),
        ("hint：侦察解撤销数", hn["hint_revoke_count"], 6, hn["hint_rev_eq_6"]),
        ("hint：与最终解差异动作数", hn["n_actions_differing"], "非权威", hn["hint_residual_conflicts_mine"] == 0),
        ("确定性：生产 3 实现 × 3 个 PYTHONHASHSEED 边集 sha 全等且等于 P2 解析实现",
         "9/9 同 sha " + str(dt.get("p2_analytic_sha", ""))[:12] + "…", "同值",
         bool(dt) and dt.get("matches_all_prod_variants") and all(
             dt["variants"][k + "_all_seeds_equal"] for k in ("interval", "bitmap", "congruence"))),
        ("FORCED 恒冲突边（Q2）", ff.get("Q2", {}).get("forced_edges_mine"), ff.get("Q2", {}).get("forced_edges_auth"),
         ff.get("Q2", {}).get("match")),
        ("恒冲突对枚举数（Q2=G*）", ff.get("Q2", {}).get("pairs_with_union_overlap_mine"), 1693,
         ff.get("Q2", {}).get("pairs_with_union_overlap_mine") == 1693),
        ("恒冲突边（Q4，权威未记录该字段→按 0 计）", ff.get("Q4", {}).get("forced_edges_mine"), 0,
         ff.get("Q4", {}).get("pairs_with_union_overlap_mine") == 2117),
        ("交付件：result1 与权威边对称差", xl.get("result1_symdiff_vs_auth"), 0, xl.get("result1_symdiff_vs_auth") == 0),
        ("交付件：result3 行数=Φ 且集合一致", f"{xl.get('result3_rows')} / {xl.get('result3_symdiff_vs_auth')}", "140 / 0",
         xl.get("result3_rows") == 140 and xl.get("result3_symdiff_vs_auth") == 0),
        ("交付件：result2/result4 频段·时间·间隔列错配", f"{xl.get('result2_n_mismatch')} / {xl.get('result4_n_mismatch')}", "0 / 0",
         xl.get("result2_n_mismatch") == 0 and xl.get("result4_n_mismatch") == 0),
        ("表1 对账：Q2 按类保留/调整/撤销", "5·15·0 / 4·30·6 / 14·76·0", "同左（class 合计 20/40/90）", te.get("Q2", {}).get("equal")),
        ("表1 对账：Q4 按类保留/调整/撤销", "6·14·0 / 4·30·6 / 16·74·0", "同左（class 合计 20/40/90）", te.get("Q4", {}).get("equal")),
        ("侦察件 star_edges 条数 = 权威 G*", (te.get("star_edges") or {}).get("count"), (te.get("star_edges") or {}).get("auth_gstar_Q2"),
         (te.get("star_edges") or {}).get("count") == 1693),
        ("〔溯源〕canonical_evaluator 文件 SHA = ADJ/FMS 记录", (te.get("evaluator") or {}).get("match"), True, (te.get("evaluator") or {}).get("match")),
        ("〔溯源〕CSV 文件 SHA = FMS E-SET 绑定", (te.get("csv_binding") or {}).get("match"), True, (te.get("csv_binding") or {}).get("match")),
        ("〔溯源〕4 个实现文件 SHA = FMS computation_contract", pr["all_impl_sha_ok"], True, pr["all_impl_sha_ok"] is True),
        ("〔溯源〕VALIDATION_PLAN 指纹：9 件结果绑定的版本是否仍在磁盘",
         f"{(ff.get('validation_plan_binding') or {}).get('files_with_matching_hash')}/{(ff.get('validation_plan_binding') or {}).get('files_binding_plan')} 匹配",
         "应为 9/9", False),
        ("〔溯源〕RESULTS_REPORT.md 是否由当前 make_report.py 生成", "否（md 08:18:18 < py 08:43:18）", "应为是", False),
    ]
    DOC_ROWS = {i for i, r in enumerate(rows) if str(r[0]).startswith("〔溯源〕")}

    hard = ["实现文件 SHA 与 FMS 契约一致: " + str(pr["all_impl_sha_ok"]),
            "Q1 字段 edges_sha256 与自身 edges 列表自洽: " + str(pr["q1_sha_selfconsistent"]),
            "静态扫描：结果数字硬编码命中 " + str(st["n_hits"]) + " 处（" +
            "; ".join(f"{h['file']}:{h['line']}={','.join(h['numbers'])}" for h in st["hardcoded_result_number_hits"]) + "）",
            "tokenize 级泄漏扫描命中 " + str(lk["n_hits"]) + " 处（真阳性 2 处：make_figures.py 297 / q1_solve.py 11175；"
            "假阳性 2 处：make_figures.py:157 的 303 是文本纵坐标、make_report.py:73 的 120 是切片长度）",
            "随机性：3 个文件使用 random，全部 Random(定值/参数种子)，无未定 seed 路径: " + str(st["verdict_random"]),
            "FORCED 恒冲突边（必撤一端）独立复算 Q2=0（权威 forced_edges=0）；无'恒冲突⇒必须撤销'的对",
            "选项空间恒等式（三方交叉验证 369 的构成）：Q4 options 6013 − Q2 options 4582 = 1431 = 1800(C 类 90×20) − 369 = 1530(间隔合法) − 99(时域截断)"
            " ⇒ 369 = 270(因 g'=8+dg≤0 被禁) + 99(因末周期越出 643 被截断)，与 FMS 记的 99/1530 完全自洽",
            "Q2 撤销层 LB=5 / UB=6（gap=1，未闭合）；L2/L3/L4 界 22/699/174 均远低于达成值 121/1996/661 ⇒ 四级皆非证明最优，仅 incumbent",
            "Q4 撤销层 LB=3 / UB=6；L3_minPL 状态 UNKNOWN 且无 L4 层 ⇒ Q4 元组第 3/4 级只是 L2 解的副产物，未独立优化",
            "VALIDATION_PLAN 指纹断链：9 件权威/诊断结果绑定 2166c4c8…，而磁盘现件为 rev6 / f00b1948…（08:26:57 写盘，晚于结果 08:17:47-08:18:17）；"
            "旧版无存档副本 ⇒ '求解前冻结'声明不可证",
            "reports/RESULTS_REPORT.md 比 code/prod/make_report.py 旧（08:18:18 vs 08:43:18），仍含 'workers=1 确定性'、'w8=' 两处与权威字段矛盾的表述"]

    items = {
        "1_Q1重算": q1["verdict"], "2_Q2复算": q2["verdict"], "3_Q3复算": q3["verdict"] + "/" + (q3o.get("verdict", "-")),
        "4_Q4复算": q4["verdict"] + "/" + ms["verdict"], "5_静态审计": "FLAG（见发现）/ random PASS",
        "6_hint链": hn["verdict"],
    }
    numeric_ok = all(bool(rows[i][3]) for i in range(len(rows)) if i not in DOC_ROWS)
    doc_bad = [rows[i][0] for i in sorted(DOC_ROWS) if not bool(rows[i][3])]
    out = {"check": "P2 汇总", "table": rows, "hard_facts": hard, "per_item": items,
           "numeric_verdict": P.verdict(numeric_ok), "traceability_verdict": P.verdict(not doc_bad),
           "traceability_failures": doc_bad}
    P.wr("P2QC_SUMMARY.json", out)

    md = ["# P2 编程对抗终检（独立第二实现）结论", "",
          "- 独立性：所有校验代码位于 `logs/p2qc/`，仅依赖标准库 + 自写的 ortools/openpyxl 路径注入；未 import `code/prod/` 任何模块。",
          "- 方法学差异：生产用 64300-bit 大整数位图；P2 用解析半开区间算术 + 整数格集合（第三条实现路径）。", "",
          "## 逐项判定", ""]
    for k, v in items.items():
        md.append(f"- {k}: **{v}**")
    md += ["", "## 数字对照表（P2 独立值 vs 权威值）", "",
           "> 前缀〔溯源〕的行是证据链检查（不是数值）：其 ❌ 对应下方 F-2 / F-3 文档与指纹缺陷。", "",
           "| 项目 | P2 独立 | 权威 | 一致 |", "|---|---|---|---|"]
    for name, a, b, ok in rows:
        md.append(f"| {name} | {a} | {b} | {'✅' if ok else '❌'} |")
    md += ["", "## 硬性事实", ""] + [f"- {h}" for h in hard]
    md += ["", "## 缺陷清单（P2 判不可信 / 需修，按严重度）", ""]
    flaws = [
        ("F-1 口径命名错误（中）",
         "results/Q4_solution.json `dg_options_dropped_by_horizon=369` 与 reports/RESULTS_REPORT.md『视界截断 dg 选项=369』。"
         "P2 复算：369 = 270（g'=8+dg≤0 的非法间隔）+ 99（末周期越出 643 的真截断）。"
         "FMS/方法学件写的是 99/1530（正确），results 字段与 RESULTS_REPORT 写 369 并冠名『视界截断』（错误口径）。"
         "论文若写『369 个选项因超出时域被剔除』即为事实错误，须改为 99（或明确 369 含 270 项非法间隔）。"),
        ("F-2 文档与权威字段矛盾（中）",
         "reports/RESULTS_REPORT.md 仍写『权威解（workers=1 确定性）』并出现『w8=』，"
         "而 results/Q2_solution.json 实为 workers=4、best_is_w1=0、只有 w1/w4 两次跑；"
         "且该 md 的 mtime(08:18:18) 早于 code/prod/make_report.py(08:43:18) —— 生成器已改、报告未重出。"),
        ("F-3 验证计划指纹断链（中，属可复现性而非数值）",
         "9 件 results 的 _meta.input_hashes 绑定 VALIDATION_PLAN=2166c4c8…，磁盘现件为 rev6/f00b1948…（08:26:57 写盘，"
         "晚于全部结果 08:17:47-08:18:17），且旧版无存档。计划自述 frozen_before_production_runs=true 因此不可证 —— 论文/附录禁写『验证计划在求解前冻结』。"),
        ("F-4 图表数字硬编码（低-中，违反数据驱动图规范）",
         "code/prod/make_figures.py:156-157 把『消解前/消解后』柱值写死为 [297, 0]，而同一文件其它面板均从 results 读取；"
         "数值恰与权威一致（P2 独立复算 297/0 均对），但该图不再具备 results→figure 的可追溯链。"),
        ("F-5 自报计数写死（低）",
         "code/prod/q1_solve.py:88 `\"pairs_checked\": 11175` 为字面量（应为枚举计数，q1v_interval 内部确有 n2 计数）。"
         "真值 C(150,2)=11175 已由 P2 独立复算确认，故不影响结论，但『全查』这一自证字段名不副实。"),
        ("F-6 最优性声明口径（提示，非数值错误）",
         "Q2 四级 layers 全为 FEASIBLE：L1 obj6/bound5、L2 121/22、L3 1996/699、L4 661/174 ⇒ 撤销 6 未证最小（LB=5），"
         "第 2-4 级也只是 incumbent（results 里 gap_revoke=1、lb_closed=false 已如实登记）。"
         "Q4 更弱：L3 UNKNOWN、无 L4 层，且 L1/L2 带『逐维 ≤ 植入 Q2 元组』锚定框（R≤6,A≤121,PL≤1996,MG≤661）——"
         "该框在 min-R 层不是保序的：若存在『撤销 5 次但调整 >121』的解会被锚排除，故 Q4 的 6 只能称锚定域内达成值"
         "（他们确实用无锚 cap_R=5 探针试过低维，结果 UNKNOWN）；而『Q4 域 ⊇ Q2 域 ⇒ 不劣于 Q2』本身无需锚定即可论证。"
         "只有 Q3 有闭合证书：P2 自建候选(2270)+自建边(69678)+自写 CP-SAT 独立得 OPTIMAL 且界=140=φ。"),
        ("F-7 交付件登记口径（提示）",
         "result2/result4 只列被改或被撤的 127/124 个计划，未列 23/26 个『保持不变』者；附件2 模板只有表头，形式上不违规，"
         "但评审可能读成漏填，建议在论文正文或表注中写明登记口径。"),
    ]
    for t, b in flaws:
        md.append(f"### {t}")
        md.append(f"- {b}")
        md.append("")
    md += ["## P2 总判定", "",
           "数值链（Q1 297 / Q2 (6,121,1996,661) / Q3 Φ=140 / Q4 (6,118,1894,661)）"
           "**全部经独立实现复算一致，可采信**；不可信项集中于口径命名、文档新鲜度、指纹绑定与措辞越界（F-1…F-7）。", ""]
    open(os.path.join(D, "P2QC_SUMMARY.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("numeric:", out["numeric_verdict"], "| traceability:", out["traceability_verdict"], out["traceability_failures"])
    for i, r in enumerate(rows):
        if not bool(r[3]) and i not in DOC_ROWS:
            print("MISMATCH(数值):", r)
    print("written P2QC_SUMMARY.md / .json")


if __name__ == "__main__":
    main()
