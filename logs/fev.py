# -*- coding: utf-8 -*-
"""①failure_events（EV-CRIT-001 criterion_invalid 正式记录）。"""
import io, json, datetime
ev = [{
    "event_id": "EV-CRIT-001", "type": "criterion_invalid", "stage": "coding_visual",
    "validation_ids": ["V-Q2-05", "V-Q4-05"],
    "description": ("原判据 repro_first_layer_match==1 把『CP-SAT 不同 worker 数的进程级收敛差异』当作『解不可复现』，"
                    "并把权威解绑到弱配置（w1 rev=20）丢弃强配置（w4 rev=6）——概念操作化错误。"
                    "可复现性正确语义=权威解经独立第二实现全量重算一致（解级验证），非搜索路径逐位相同（进程级巧合）。"),
    "evidence": ["results/Q2_solution.json w1_tuple=[20,103,1916,597] vs w4_tuple=[6,121,1996,661]",
                 "runs/fresh/FULL-D2026-PROD-C/tasks/Q2-Q2-R51-main-N-A-p0|p1/attempts/001"],
    "resolution": ("VALIDATION_PLAN rev4：判据改 tuple_matches_second_impl==1；权威解规则=verified_best"
                   "（checker 验证过的最优元组，w1/w4 全记录）；交叉差异降级为诊断字段。"),
    "recorded_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "note": "修正发生于 validation_evaluator 正式 verdict 之前（coding 期内），判据语义纠错非放宽：阈值不变（=1），换的是被测概念的操作化。"}]
doc = {"schema_version": 1, "events": ev}
if __import__("os").path.exists("reports/methodology/failure_events.json"):
    old = json.load(io.open("reports/methodology/failure_events.json", encoding="utf-8"))
    ids = {e["event_id"] for e in old.get("events", [])}
    doc["events"] = old.get("events", []) + [e for e in ev if e["event_id"] not in ids]
json.dump(doc, io.open("reports/methodology/failure_events.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("failure_events ok")
