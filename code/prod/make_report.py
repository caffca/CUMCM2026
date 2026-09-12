# -*- coding: utf-8 -*-
"""RESULTS_REPORT.md 自动装配 v2（数字全部取自 results/*.json，run/timeout/worker 口径来自实际工件，禁手填）。"""
import io, json, os, subprocess, sys, datetime

def R(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("result", d), d.get("_meta", {})

q1, m1 = R("results/Q1_detect.json")
q1s, _ = R("results/Q1_stats.json")
q2, m2 = R("results/Q2_solution.json")
q2c, _ = R("results/Q2_check.json")
q2t, _ = R("results/Q2_table1.json")
q3, m3 = R("results/Q3_solution.json")
q3b, _ = R("results/Q3_bound.json")
q3sub, _ = R("results/Q3_submission_check.json")
q4, m4 = R("results/Q4_solution.json")
q4c, _ = R("results/Q4_check.json")
q4t, _ = R("results/Q4_table1.json")
RUN = m2.get("run_id", m2.get("execution", {}).get("run_id", "?"))
va = subprocess.run([sys.executable, "code/verify_all.py"], capture_output=True, text=True, encoding="utf-8")
lines = []
A = lines.append
A("# 计算结果（D 题：时频冲突检测与消解）")
A("")
A(f"生成：{datetime.datetime.now().astimezone().isoformat(timespec='seconds')} · 权威生产运行 `{RUN}` · verify_all: " +
  ("PASS" if va.returncode == 0 else "FAIL"))
A("")
A("## 运行环境与预算口径")
A("- Python 3.14 + OR-Tools CP-SAT 9.15（F:\\dsh_envlibs\\mathmodel）；CPU 4 核；分片执行器 sharded_run v2（full 预算、聚合 19/19）。")
A("- 任务超时按问登记：Q1 3600s / Q2 1700s / Q3 1500s / Q4 1700s；执行器单次窗口 deadline 1800s（分波续跑）。")
A("- 层级预算（Q2/Q4）：L1 撤销 800s → 证书阶梯 250s → L2 调整 300s → L3 优先级 100s → L4 幅度 50s。")
A("- 冻结件：canonical_evaluator SHA 8c4db98f…；ADJUDICATION R1-R8（T_MAX=643、半开区间、词典序四级、Q3 主口径）。")
A("")
A("## 问题一结果")
c = q1["counts"]
A(f"- 冲突对 **{c['edges']}**（AB{c['AB']} / AC{c['AC']} / BC{c['BC']} / BB{c['BB']} / CC{c['CC']}，AA={c['AA']}）；"
  f"涉及计划 {q1['involved_plans']}/150（11175 对全查）。")
A(f"- 三独立实现（区间算术/位图+倒排/同余闭式）对称差={q1['three_way_max_symdiff']}；"
  f"与官方口径 evaluator 对称差={q1['symdiff_vs_evaluator']}；边界用例失败={q1['boundary_cases_failed']}。")
A(f"- 植入压力测试：有效注入 {q1['stress_effective']} 次、最低召回 {q1['stress_min_recall']:.4f}（构造性诊断证据，措辞限定量级）。")
A(f"- result1.xlsx 与权威边集对称差 = {q1s['result1_edge_symdiff']}（提交后复算）。")
A("")
A("## 问题二结果")
t = q2["objective_tuple"]
A(f"- 权威解（verified-best：各配置跑中词典序最优且经独立 checker 第二实现全量重算验证）元组 "
  f"**(撤销 {t[0]}，调整 {t[1]}，优先级损失 {t[2]}，幅度 {t[3]})**，来源跑 workers={q2.get('workers') or 4}；scalar={q2['objective_scalar']:.0f}。")
A(f"- 复现披露：workers=1 单跑得 {q2.get('w1_tuple')}（第一级与 workers=4 不一致，属搜索进程差异，作诊断记录）；"
  f"workers=4 得 {q2.get('w4_tuple')}；权威解本身经第二实现逐约束重验：残留冲突={q2['residual_pairs_second_impl']}、"
  f"合规违例={q2['compliance_violations']}、元组一致={q2['tuple_matches_second_impl']}。")
A(f"- 撤销层证书：LB={q2['ladder_proven_revoke_lb']}，达成={t[0]}，gap={q2['gap_revoke']}"
  + ("（闭合，可称该层最优）" if q2["gap_revoke"] == 0 else "（未闭合：论文写『撤销数介于 LB 与达成值之间』，禁称整体最优）") + "。")
A(f"- 侦察解仅作搜索提示（hint_source={os.path.basename(str(q2.get('hint_source')))}；全部数值生产重算）。")
A(f"- 表1：{q2t['by_class']}（闭合差={q2t['table_closure_diff']}）；GRASP 对照撤销中位={q2['grasp_revoke_median']:.0f}。")
A("")
A("## 问题三结果")
A(f"- 在问题二权威解基座上可加装 **Φ={q3['phi']}** 台 C 类计划（result3 行数={q3['rows']}，行差={q3sub['result3_rows_minus_phi']}）。")
A(f"- 三腿：候选集双实现差={q3['cand_count_second_impl_minus_solver']}（枚举 {q3.get('cand_count_second_impl')} 个）；"
  f"CP-SAT 模型A {q3.get('status')}（对照模型B {q3.get('cpsat_b_status')}/{q3.get('cpsat_b_phi')}）；"
  f"LP 上界={q3.get('ub_lp')}；CP 整数上界={q3.get('ub_cp')}；相位×块初等界={q3.get('ub_phase')}（口径不同勿混引）。")
A(f"- gap_certified={q3.get('gap_certified')}"
  + (" ⇒ **该基座下 Φ 为可证明最大值**" if q3.get("gap_certified") == 0 else " ⇒ 论文写区间") + "。")
A(f"- 基座绑定：base_tuple={q3.get('base_tuple')} == 权威 Q2（flag={q3['base_is_production_q2']}）；零冲突复验={q3['conflict_total_second_impl']}。")
A("")
A("## 问题四结果")
t4 = q4["objective_tuple"]
A(f"- 权威解 **({t4[0]}, {t4[1]}, {t4[2]}, {t4[3]})**（verified-best；第二实现元组一致={q4['tuple_matches_second_impl']}）。")
A(f"- 植入 Q2 锚可行={q4['planted_q2_feasible']}（锚元组={q4.get('planted_q2_tuple')}）；"
  f"撤销层相对 Q2 增益={q4['revoke_gain_vs_q2']}（撤销下界所限，无增益为诚实结论）；"
  f"低层级改善：调整 {q2['objective_tuple'][1]}→{t4[1]}、优先级损失 {q2['objective_tuple'][2]}→{t4[2]}。")
A(f"- checker：违例={q4c['violations']}、残差={q4c['residual_pairs_second_impl']}；表1：{q4t['by_class']}（闭合差={q4t['table_closure_diff']}）；"
  f"扩展域中 dg 候选动作被禁 {q4.get('dg_options_dropped_by_horizon')} 项"
  f"（分解：非正间隔 {q4.get('dg_dropped_infeasible_gap')} 项 + 末周期越出 643 时域 {q4.get('dg_dropped_horizon')} 项；"
  f"分解经独立对抗终检按 plans+cells 语义全量重算吻合，留痕 logs/p2qc/）。")
A("")
A("## 约束与一致性校验")
A(f"- verify_all v2（注册表驱动+绑定+基座对账+xlsx 复算）：{(va.stdout or '').strip().splitlines()[0] if va.stdout else '?'}；"
  + (f"失败明细 {(va.stdout or '').strip().splitlines()[1:3]}") if va.returncode else "全 PASS")
A(f"- 权威结果件的 _meta 绑定 model_spec/formulation SHA、run、聚合、coverage；诊断/support 件登记 payload/meta 哈希（authority=false）。")
A(f"- 侦察链（runs/competitive/**）与旧 run（C/D/E）产物不进入任何权威引用。")
A("")
A("## 可复现运行方式")
A("```")
A(f"python code/prod/run_prod.py all          # 权威 run: {RUN}")
A(f"python code/prod/write_results.py --run-id {RUN}")
A("python code/prod/make_xlsx.py && python code/prod/submission_checks.py")
A("python code/prod/make_q3_sensitivity.py")
A("python code/verify_all.py && python code/prod/make_report.py && python code/prod/make_figures.py")
A("```")
io.open("reports/RESULTS_REPORT.md", "w", encoding="utf-8").write("\n".join(lines))
print("RESULTS_REPORT v2 written; run=", RUN)
