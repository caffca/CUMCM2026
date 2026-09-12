# -*- coding: utf-8 -*-
import json, io
d = json.load(io.open("state/decision_log.json", encoding="utf-8"))
d["decisions"].append({
 "id": "D-HINT-001", "stage": "coding_visual",
 "decision": ("生产 Q2 cpsat 任务以侦察 incumbent（runs/competitive/.../Q2-R51/solution_actions.json）仅作 AddHint 搜索提示："
              "hint 不进入任何权威数值——incumbent 由生产 CP-SAT 重新求解、生产 evaluator 与独立第二实现 checker 全量重算复验；"
              "payload 登记 hint_source/hint_role=search_hint_only。依据：侦察教训（rev=6 需 hint+深度）；不违反 'scout 数字不入 results' 红线"
              "（该红线禁止复制 scout 数值为权威；此处仅复用解的结构作为起点，数值全部生产重算）。"),
 "reason": "run-B 无 hint 生产 rev=10 显著劣于侦察证明可达的 6；生产质量直接影响 Q3 基座与 Q4 锚定"})
json.dump(d, io.open("state/decision_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("hint decision logged")
