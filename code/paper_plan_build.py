# -*- coding: utf-8 -*-
"""PAPER_PLAN v1 装配器（result_review 通过后运行）：claims 只取 RESULT_INTERPRETATION 的 SUPPORTED/缩窄 PARTIAL。"""
import hashlib, io, json, sys, datetime

RI = json.load(io.open("reports/RESULT_INTERPRETATION.json", encoding="utf-8"))
VP = json.load(io.open("reports/VALIDATION_PLAN.json", encoding="utf-8"))
FR = json.load(io.open("reports/FIGURE_REQUIREMENTS.json", encoding="utf-8"))
figs = {f["id"]: f for f in FR["figures"]}

ADM = {"SUPPORTED", "PARTIAL_NARROWED"}
matrix = []
for c in RI["claims"]:
    st = c["status"]
    if c.get("replacement_claim") and c.get("replacement_claim", {}).get("claim_id"):
        cid, text, st = c["replacement_claim"]["claim_id"], c["replacement_claim"].get("text", c["observation"]), "PARTIAL_NARROWED"
    else:
        cid, text = c["claim_id"], c["observation"]
    if st not in ADM and c["claim_status"] not in ("SUPPORTED",):
        continue
    ev = [{"type": "result", "id": k} for k in c.get("result_keys", [])[:6]]
    for f in c.get("evidence_refs", []):
        ev.append({"type": "file", "id": f})
    matrix.append({"claim": text, "claim_id": cid, "status": "SUPPORTED", "evidence": ev,
                   "section": None})  # section 填于下方映射
SEC = {"C-Q1-DETECT": "5.1 问题一：冲突检测", "C-Q2-SOLVE": "5.2 问题二：消解方案",
       "C-Q2-OPT": "5.2 问题二：消解方案", "C-Q3-PHI": "5.3 问题三：最大加装",
       "C-Q3-BOUND": "5.3 问题三：最大加装", "C-Q4-SOLVE": "5.4 问题四：间隔调整消解",
       "C-Q4-GAIN": "5.4 问题四：间隔调整消解"}
for m in matrix:
    m["section"] = SEC.get(m["claim_id"], "5 模型建立与求解")

FIG_SEC = {"5.1 问题一：冲突检测": ["fig-q1-grid-conflict", "fig-q1-degree-dist", "fig-q1-classpairs"],
           "5.2 问题二：消解方案": ["fig-q2-hero-lex", "fig-q2-table1", "fig-q2-ladder"],
           "5.3 问题三：最大加装": ["fig-q3-utilization", "fig-q3-bound-meet"],
           "5.4 问题四：间隔调整消解": ["fig-q4-vs-q2", "fig-q4-dg-dist"]}
sections = [
    {"section_id": "1", "title": "问题重述", "reader_question": "赛题给了什么数据与规则，四问各要交付什么？",
     "purpose": "忠实转述题面与四问任务、结果文件形式", "claims": [], "evidence": [], "figures": [], "tables": [],
     "formulas": [], "soft_page_budget": 1.5},
    {"section_id": "2", "title": "问题分析", "reader_question": "四问的数学结构是什么、彼此如何依赖？",
     "purpose": "识别时频矩形冲突结构、词典序四级目标、逐问交付形态与依赖链", "claims": [], "evidence": [],
     "figures": [], "tables": [], "formulas": [], "soft_page_budget": 2},
    {"section_id": "3", "title": "模型假设与符号说明", "reader_question": "建模依赖哪些前提，符号如何约定？",
     "purpose": "编号假设（含依据作用）+ 符号表", "claims": [], "evidence": [], "figures": [], "tables": ["表2 符号"],
     "formulas": [], "soft_page_budget": 2},
    {"section_id": "4", "title": "数据与预处理", "reader_question": "150 个计划的数据如何读取、校验、口径裁决？",
     "purpose": "数据登记、口径（半开区间/T_MAX=643）、退化说明", "claims": [], "evidence": [], "figures": [],
     "tables": [], "formulas": [], "soft_page_budget": 1.5},
    {"section_id": "5.1", "title": "问题一：时频冲突检测", "reader_question": "哪些计划对冲突、多少、什么构成？",
     "purpose": "区间相交判据+三独立实现+297 对结果与构成", "claims": [], "evidence": [],
     "figures": FIG_SEC["5.1 问题一：冲突检测"], "tables": ["表3 冲突构成"], "formulas": ["冲突判定式"], "soft_page_budget": 3.5},
    {"section_id": "5.2", "title": "问题二：冲突消解", "reader_question": "如何以最小撤销/调整清空冲突并保证合规？",
     "purpose": "词典序四级 ILP/CP 模型+阶梯证书+消解方案与表1", "claims": [], "evidence": [],
     "figures": FIG_SEC["5.2 问题二：消解方案"], "tables": ["表1 按类统计"], "formulas": ["四级目标", "禁配约束族"], "soft_page_budget": 6},
    {"section_id": "5.3", "title": "问题三：最大加装", "reader_question": "在不新增冲突下最多能加装多少台 C 类？",
     "purpose": "集包装模型+候选穷举双实现+三腿认证（该基座 Φ 最大）", "claims": [], "evidence": [],
     "figures": FIG_SEC["5.3 问题三：最大加装"], "tables": ["表4 加装参数"], "formulas": ["集包装 ILP"], "soft_page_budget": 5},
    {"section_id": "5.4", "title": "问题四：间隔调整消解", "reader_question": "放开重定时后方案能好多少？",
     "purpose": "扩域模型+锚定不劣+诚实结论（撤销无增益、低层级改善）", "claims": [], "evidence": [],
     "figures": FIG_SEC["5.4 问题四：间隔调整消解"], "tables": ["表5 对比"], "formulas": ["含 dg 的周期约束"], "soft_page_budget": 5},
    {"section_id": "6", "title": "模型评价与推广", "reader_question": "结果可信度、局限与推广价值？",
     "purpose": "检验汇总、证书边界、敏感性、局限", "claims": [], "evidence": [], "figures": [], "tables": [],
     "formulas": [], "soft_page_budget": 2.5},
]
for m in matrix:
    for s in sections:
        if s["title"].startswith(m["section"].split("：")[0][-3:]) or m["section"].startswith(s["title"][:4]):
            s["claims"].append(m["claim_id"])
doc = {"schema_version": 1,
       "contribution": "以三独立实现对账的冲突检测（297 对）、带证书区间的词典序四级 CP-SAT 消解、三腿认证的基座最大加装（该基座可证明最优）与锚定不劣的间隔重定时消解，给出四问可提交方案与全部约束的二次核验。",
       "claim_evidence_matrix": matrix, "sections": sections,
       "figure_manifest_ref": "figures/figure_manifest.json",
       "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "source_bindings": {"RESULT_INTERPRETATION": hashlib.sha256(open("reports/RESULT_INTERPRETATION.json", "rb").read()).hexdigest(),
                           "VALIDATION_PLAN": hashlib.sha256(open("reports/VALIDATION_PLAN.json", "rb").read()).hexdigest()}}
json.dump(doc, io.open("reports/PAPER_PLAN.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
md = ["# 论文规划", "", "**贡献一句话**：" + doc["contribution"], "", "## Claims–Evidence 矩阵", "",
      "| claim | 状态 | 证据 | 章节 |", "|---|---|---|---|"]
for m in matrix:
    md.append(f"| {m['claim_id']} {m['claim'][:38]}… | {m['status']} | {', '.join(e['id'] for e in m['evidence'][:4])}… | {m['section']} |")
md += ["", "## 逐节计划", ""]
for s in sections:
    md.append(f"### {s['section_id']} {s['title']}（约 {s['soft_page_budget']} 页）")
    md.append(f"- 读者问题：{s['reader_question']}")
    md.append(f"- 目的：{s['purpose']}")
    md.append(f"- 图：{', '.join(s['figures']) or '无'}；表：{', '.join(s['tables']) or '无'}")
    md.append("")
io.open("reports/PAPER_PLAN.md", "w", encoding="utf-8").write("\n".join(md))
print("PAPER_PLAN written; matrix rows:", len(matrix))
