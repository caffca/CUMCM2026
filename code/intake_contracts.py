# -*- coding: utf-8 -*-
"""brainstorm 读题登记：QUESTION_CONTRACT v2 + PROBLEM_FACTS v1（Manager 产物，非路线）。
来源资产：D题.pdf（primary_official），逐 fact 绑定其 SHA256 与原文 span。
约定：与某一问绑定的 target/constraint 事实用 <Qid>- 前缀 fact_id 并带 affected_question_ids，
使 strategy_matching 的 evidence ref 为 question-local。跨问共享的题面事实用 F- 前缀。"""
import hashlib, io, json

STATEMENT = "D题.pdf"
sha_stmt = hashlib.sha256(open(STATEMENT, "rb").read()).hexdigest()
ASSET_ID = "A-D题.pdf"

def fact(fid, span, raw, norm, unit, typ, qs=None, note=""):
    e = {"fact_id": fid, "source_asset_id": ASSET_ID, "source_sha256": sha_stmt,
         "source_span": span, "raw_text": raw, "normalized_value": norm, "unit": unit,
         "fact_type": typ, "confidence": "high"}
    if qs:
        e["affected_question_ids"] = list(qs)
    if note:
        e["note"] = note
    return e

F = [
 fact("F-001","频域离散化","以固定的频带宽度Δf将系统可提供的有限带宽频率资源离散化为100个宽度相同的频段",100,"频段","parameter",note="频段索引 0..99，区间左闭右开 [a,b)"),
 fact("F-002","频段占用","每一个用频计划可以占用连续的多个频段，并且占用的频段数量保持不变","contiguous_fixed_width",None,"rule",["Q2","Q4"],note="调整（平移）后频段数量（宽度）不变"),
 fact("F-003","时域离散化","用固定的时间长度Δt作为时间资源的基本单位……所占用的时间长度必须是Δt的整数倍","integer_multiples_of_dt",None,"rule",note="所有时间参数为整数（以Δt计）"),
 fact("F-004","计划四参数","每个用频计划包含四个参数：频段区间、首次使用的时间区间、相邻两次使用该频段的间隔时长以及使用次数","4_params",None,"definition"),
 fact("F-005","周期使用规则","间隔时长60表示相隔60Δt的时间再次以相同长度的时间区间占用该频段，即第二次占用……[40Δt+60Δt,45Δt+60Δt)","slot_k=[t1+(k-1)*(g+d), t1+(k-1)*(g+d)+d), k=1..n",None,"definition",note="间隔 g 为两次占用之间的空闲时长；d=时间区间长度。例：A001 首次[35,40),g=60→第二次[100,105),第三次[165,170)"),
 fact("F-006","冲突判定","当两个用频计划的时间区间和频段区间都存在交叠时，则判定它们之间存在时频冲突","pair_conflict=band_overlap AND any_slot_time_overlap",None,"definition",note="时间交叠按全部使用次数占用时段集合判定（半开区间交叠），频段按 [a,b) 半开交叠"),
 fact("F-007","消解定义","通过调整某些用频计划的参数（比如平移频段区间或者时间区间等），甚至撤销某些用频计划，使得消解后的用频计划不存在时频冲突","adjust_or_revoke_to_zero_conflict",None,"rule"),
 fact("F-008","单参数规则","一个用频计划只能调整其中一个参数或撤销","one_param_or_revoke",None,"rule",["Q2","Q4"],note="Q2/Q4 通用；Q4 特别说明允许 C 类调间隔（仍只能调一个）"),
 fact("F-009","常规禁调项","一般不调整使用次数和使用间隔时长","gap_count_frozen_unless_stated",None,"rule",["Q2"],note="使用次数在任何问均不得调整"),
 fact("F-010","优先级","A类优先级最高，B类其次，C类最低，高优先级用频装备的用频计划应尽量保持","A_gt_B_gt_C",None,"rule"),
 fact("F-012","平移幅度上限","规定频段、时间调整的最大平移幅度分别为10Δf、5Δt","df<=10 AND dt<=5",None,"constraint",["Q2","Q4"],note="平移幅度=|新起点-旧起点|；频段/时间各自上限 10/5；Q3 明确解除此限"),
 fact("F-013","数据规模","附件1给出了3类共150个用频装备提报的用频计划",150,"部","parameter",note="A001-A020, B001-B040, C001-C090"),
 fact("F-021","result2模板列","A列装备编号；B列调整后频段范围；C列调整后时间区间；D列是否撤销(是)","4cols",None,"definition",["Q2"]),
 fact("F-022","result4模板列","A装备编号；B频段范围；C时间区间；D间隔时长；E是否撤销","5cols",None,"definition",["Q4"]),
 fact("F-023","频段区间记法","频段区间[80,90)表示占用 [f0+80Δf, f0+90Δf)","half_open_[a,b)",None,"definition"),
 fact("Q1-F014","问题1输出","将结果保存到文件result1.xlsx中（模板文件见附件2），并在论文中给出时频冲突的统计结果","result1.xlsx+stats",None,"target",["Q1"]),
 fact("Q2-F011","目标层级(Q2)","对问题1中检测出的时频冲突进行消解……应尽可能减少撤销；尽量减少被调整数量；高优先级尽量保持；尽量减少调整幅度","lex(revoke,adjusted,priority,magnitude)",None,"target",["Q2"]),
 fact("Q2-F015","问题2输出","将消解方案保存到文件result2.xlsx中……按表1的格式给出时频冲突消解的统计结果","result2.xlsx+Table1",None,"target",["Q2"]),
 fact("Q2-F016","表1格式","表1：类别/保留数量/调整数量/撤销数量（A、B、C三行）","Table1",None,"definition",["Q2","Q4"]),
 fact("Q3-F017","问题3条件","基于问题2无冲突方案，如果不限制频段和时间的平移幅度，在不增加时频资源的前提下，最多还能安排多少C类用频装备","max_addC_unbounded_shift_no_extra_resource",None,"target",["Q3"],note="口径假设：既有计划保持问题2方案不变；不增加时频资源=仍 100频段×同一时间视界；新C沿用附件C模板(宽3/时长2/间隔8/次数12)"),
 fact("Q3-F018","问题3输出","给出相应的用频计划，将结果保存到文件result3.xlsx","result3.xlsx(序号,频段区间,时间区间)",None,"target",["Q3"],note="模板仅3列→间隔8/次数12/宽3/时长2为隐含固定参数"),
 fact("Q4-F019","问题4条件","若允许部分C类用频装备对用频间隔时长进行调整，但要求与原间隔时长的差异不超过10Δt","abs(dg)<=10 AND g_prime>=1","Δt","constraint",["Q4"],note="仅 C 类可调整间隔；|新间隔-原间隔|≤10；间隔为正整数Δt；其余同 Q2"),
 fact("Q4-F011","目标层级(Q4)","允许调整间隔后对问题1冲突消解，仍按题面目标层级链优化","lex(revoke,adjusted,priority,magnitude)",None,"target",["Q4"]),
 fact("Q4-F020","问题4输出","将消解方案保存到文件result4.xlsx中……按表1的格式给出统计结果","result4.xlsx+Table1",None,"target",["Q4"]),
]

pf = {"schema_version": 1, "source_asset": ASSET_ID, "extracted_at": "brainstorm-intake",
      "source_sha256": sha_stmt, "facts": F}

def cap(cid, req, mand, facts, acc, ev):
    return {"capability_id": cid, "requirement": req, "mandatory": mand,
            "source_fact_ids": facts, "acceptance_rule": acc, "required_evidence": ev}

QC = {"schema_version": 2, "problem_id": "D2026", "questions": [
 {"question_id": "Q1", "original_request": "对附件1给出的用频计划进行时频冲突检测，将结果保存到 result1.xlsx，并在论文中给出时频冲突的统计结果。",
  "decision_target": "枚举全部时频冲突计划对", "analysis_unit": "用频计划对 (i,j)", "observation_unit": "计划对×占用时段×频段",
  "special_data_structure": {"kind":"周期矩形占用","note":"每计划=频段窗口 × 周期(gap+d)重复 n 个时间窗"},
  "required_outputs": ["submission/result1.xlsx（每行一对冲突）","论文冲突统计（总数/按类对/热点）"],
  "allowed_information": ["附件1 全部计划参数"], "forbidden_information": ["调整/撤销决策（Q1 只检测）"],
  "evaluation_target": ["冲突对集合完全且无伪"],
  "capabilities": [
    cap("Q1-C1","冲突对枚举完整且精确",True,["F-001","F-005","F-006","F-023"],"暴力逐时段枚举与区间算术双实现一致；独立checker复核",["results/Q1_detect.json","code/q1_detect.py","code/q1_verify.py"]),
    cap("Q1-C2","result1.xlsx 符合模板",True,["Q1-F014","F-021"],"列结构与行数与 result 列表一致",["submission/result1.xlsx"]),
    cap("Q1-C3","论文给出统计结果",True,["Q1-F014"],"统计数字与 results JSON 逐项命中",["results/Q1_stats.json"])]},
 {"question_id": "Q2", "original_request": "对问题1检测出的时频冲突进行消解（调整至多一个参数或撤销），保存 result2.xlsx，按表1给出统计。",
  "decision_target": "每计划动作∈{保持,频段平移,时间平移,撤销}及平移量", "analysis_unit": "用频计划", "observation_unit": "计划×时段×频段",
  "special_data_structure": "冲突图上顶点操作+带幅重嵌入",
  "required_outputs": ["submission/result2.xlsx","论文表1"],
  "allowed_information": ["Q1 冲突对集合"], "forbidden_information": ["调整使用次数","同时调整频段与时间","超出 10Δf/5Δt"],
  "evaluation_target": ["零冲突","目标链 revoke<adjusted<priority<magnitude"],
  "capabilities": [
    cap("Q2-C1","输出方案零冲突",True,["F-006","F-007","Q2-F015"],"对调整后全部计划重跑 Q1 检测器返回 0 对",["results/Q2_solution.json","code/check_q2.py"]),
    cap("Q2-C2","单参数与幅度合规",True,["F-002","F-008","F-009","F-012"],"逐行 checker 断言 |Δf|≤10,|Δt|≤5,次数/间隔不变,频段0..99",["code/check_q2.py"]),
    cap("Q2-C3","目标链优化并给出证据",True,["F-010","Q2-F011"],"CP-SAT 最优性状态 + 撤销数下界论证 + 启发式对照",["results/Q2_solution.json","runs/competitive"]),
    cap("Q2-C4","表1与 result2 一致",True,["Q2-F016","Q2-F015"],"按类聚合与逐行一致",["results/Q2_table1.json"])]},
 {"question_id": "Q3", "original_request": "基于问题2无冲突方案，不限平移幅度、不增加时频资源，最多还能安排多少C类装备？结果存 result3.xlsx。",
  "decision_target": "新增C类计划集合（频段区间+时间区间；间隔8/次数12/宽3/时长2 固定）", "analysis_unit": "新增C计划", "observation_unit": "占用单元(频段×时间格)",
  "special_data_structure": "周期脉冲装箱：3频段×相位×12连续oct",
  "required_outputs": ["submission/result3.xlsx","最大数量论证(构造下界+上界)"],
  "allowed_information": ["Q2 最终方案"], "forbidden_information": ["增加时频资源","改既有计划次数/间隔"],
  "evaluation_target": ["新增C数量最大化","与Q2方案零冲突","新增内部零冲突"],
  "capabilities": [
    cap("Q3-C1","加装方案零冲突",True,["Q3-F017"],"checker 复验(对Q2方案+内部)",["results/Q3_solution.json","code/check_q3.py"]),
    cap("Q3-C2","数量最大化论证",True,["Q3-F017"],"上界可检查,下界=提交行数,报告gap",["results/Q3_bound.json"]),
    cap("Q3-C3","result3 行数=宣称数量且格式合规",True,["Q3-F018"],"行级断言",["submission/result3.xlsx"])]},
 {"question_id": "Q4", "original_request": "允许部分C类调整间隔(≤10Δt)，消解问题1冲突，存 result4.xlsx 并按表1统计。",
  "decision_target": "每计划动作∈{保持,频段平移,时间平移,(仅C)间隔调整,撤销}及幅度", "analysis_unit": "用频计划", "observation_unit": "计划×时段×频段",
  "special_data_structure": "周期结构重定时(retiming)",
  "required_outputs": ["submission/result4.xlsx","论文表1+与Q2对比"],
  "allowed_information": ["Q1 冲突对集合"], "forbidden_information": ["A/B调间隔","C |Δgap|>10或间隔≤0","调次数","多参数同调"],
  "evaluation_target": ["零冲突","同Q2目标链","相对Q2改善证据"],
  "capabilities": [
    cap("Q4-C1","零冲突+合规",True,["F-006","F-008","Q4-F019","Q4-F020"],"checker 全断言(含间隔规则)",["results/Q4_solution.json","code/check_q4.py"]),
    cap("Q4-C2","利用间隔自由度不劣于Q2",True,["Q4-F011"],"同一 canonical 评价函数下对比",["results/Q4_table1.json","results/Q2_table1.json"])]},
]}
io.open("reports/contracts/QUESTION_CONTRACT.json","w",encoding="utf-8").write(json.dumps(QC,ensure_ascii=False,indent=2))
io.open("reports/contracts/PROBLEM_FACTS.json","w",encoding="utf-8").write(json.dumps(pf,ensure_ascii=False,indent=2))
print("wrote QUESTION_CONTRACT.json (4 questions) + PROBLEM_FACTS.json (%d facts)" % len(F))
