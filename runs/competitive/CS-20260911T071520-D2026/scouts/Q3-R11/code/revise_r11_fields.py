# -*- coding: utf-8 -*-
"""Q3-R11 字段自洽修订（评审闭环追加任务）：
finalize 表头曾按“三候选统一记录 R51 初等界”把 upper_bound 写成 332，与本候选自身的
认证界（CP-SAT OPTIMAL bound=139 + HiGHS LP=139.0）矛盾。修订为：
  upper_bound=139（认证界）、relative_gap=0.0、lower_bound=139、
  elementary_bound=332（R51 初等界，仅作可手核对照，不再充当本候选 UB 字段）、
  certified_optimal 处加内联 scope 限定（Manager 提供的基座敏感性文字）。"""
import json
import os
import io

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../scouts/Q3-R11
SCOPE = ("scope: frozen base=Q2-R51 scout solution (tuple [6,121,1996,663]); "
         "基座敏感性 R32→134/R41→136 见评审 CH-REV-A base_sensitivity")

# ---- result.json ----
p = os.path.join(D, "result.json")
r = json.load(io.open(p, encoding="utf-8"))
r["objective_tuple"] = [139, 139]                     # [count, certified UB]
r["upper_bound_certified"] = 139
r["elementary_bound"] = 332
r["elementary_bound_source"] = "Q3-R51 相位×块双计数（仅作可手核对照，不是本候选认证界）"
r["certified_optimal"] = {"value": True, "scope": SCOPE}
r["optimality_evidence"] = ("CP-SAT OPTIMAL (A/B 双模型 incumbent=bound=139) + HiGHS LP 界 139.0 独立复证；" + SCOPE)
r["revision_note"] = "评审闭环修订 v2：upper_bound 由 332（finalize 表头统一值）改为自身认证界 139，gap=0.0，332 移入 elementary_bound 对照字段"
json.dump(r, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- scout.json ----
p = os.path.join(D, "scout.json")
s = json.load(io.open(p, encoding="utf-8"))
s["upper_bound"] = 139
s["upper_bound_source"] = "本候选认证界：CP-SAT A/B 双模型 OPTIMAL best_bound=139 + HiGHS LP 松弛界=139.0（不同求解器族复证）"
s["elementary_bound"] = 332
s["elementary_bound_source"] = "Q3-R51 相位×块双计数界（UB=min(332,密度界676)）；仅作可手核对照，非本候选上界字段"
s["lower_bound"] = 139
s["relative_gap"] = 0.0
s["certified_optimal"] = {"value": True, "scope": SCOPE}
s["revision_note"] = "评审闭环修订 v2：原 finalize 表头把 upper_bound 统一写成 R51 初等界 332，与自身认证矛盾；现以认证界 139 为准（gap=0），332 保留为 elementary_bound 对照"
json.dump(s, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(json.dumps({
    "result": {k: r[k] for k in ("objective", "objective_tuple", "upper_bound_certified", "elementary_bound")},
    "scout": {k: s[k] for k in ("lower_bound", "upper_bound", "elementary_bound", "relative_gap")},
}, ensure_ascii=False, indent=1))
