# -*- coding: utf-8 -*-
"""methodology 阶段：从 FIGURE_REQUIREMENTS 生成 figures/figure_manifest.json 草案（story 齐备）。"""
import io, json, os
req = json.load(io.open("reports/FIGURE_REQUIREMENTS.json", encoding="utf-8"))
os.makedirs("figures", exist_ok=True)
man = []
UNI = {
 "fig-q1-grid-conflict": "冲突热点的空间位置（其余 Q1 图只给计数/分布）",
 "fig-q1-degree-dist": "稀疏性画像（max=8）⇒ Q2 精确可行域规模的直接依据",
 "fig-q1-classpairs": "冲突来源的类别归因（BC 主导 ⇒ B 带与 C 周期为设计矛盾）",
 "fig-q2-hero-lex": "四级目标各自的 LB-UB 区间（表1 与 ladder 图均不含层级区间）",
 "fig-q2-table1": "按类保留/调整/撤销的官方口径读数（对应论文表1）",
 "fig-q2-ladder": "Σr≤k 可满足性序列（证书链独有）",
 "fig-q3-utilization": "加装后资源栅格全貌（放置位置级信息）",
 "fig-q3-bound-meet": "三腿上界会合与初等界的松紧对比（认证逻辑独有）",
 "fig-q4-vs-q2": "两问四级元组差（间隔自由度收益的呈现位）",
 "fig-q4-dg-dist": "dg 分布与视界截断效应（重定时机理解释独有）"}
PRI = {"hero": 1, "primary": 2, "secondary": 3}
for f in req["figures"]:
    man.append({
        "id": f["id"], "question_id": f["question_id"], "kind": f["kind"],
        "role": "hero" if f.get("priority") == "hero" else f.get("priority", "secondary"),
        "visual_priority": "primary" if f.get("priority") in ("hero", "primary") else "secondary",
        "unique_information": UNI.get(f["id"], "本图独有信息见 main_message"),
        "story": {"main_message": f["main_message"], "claim_bind": f.get("claim_bind", [])},
        "caption": f.get("caption_draft", ""), "panels": f.get("panels", []),
        "data_source": f.get("data_source", ""),
        "status": "proposed", "artifact": None, "meta": None,
        "renderer": "matplotlib", "provenance": {"source_results": [f.get("data_source", "")]},
    })
io.open("figures/figure_manifest.json", "w", encoding="utf-8").write(json.dumps(man, ensure_ascii=False, indent=1))
print("figure_manifest draft:", len(man), "entries (hero:",
      sum(1 for x in man if x["role"] == "hero"), ")")
