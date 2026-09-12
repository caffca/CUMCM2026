# -*- coding: utf-8 -*-
import io, json, datetime
d = json.load(io.open("state/decision_log.json", encoding="utf-8"))
d["decisions"].append({
    "id": "D-P1-CLOSE", "stage": "coding_visual",
    "decision": ("P1 最小结果门审计（独立子代理，57/57 哈希复算+8/8 字节直传验证+四表 xlsx 全量复算）判『有条件可收口』。"
                 "处置：①③输入冻结漂移 → 以 rev6 VP 新建 run-F 全链重跑为唯一权威（run-E 降为修订前证据）；"
                 "②RESULTS_REPORT 三处 FAIL（workers=1 误标/复现 run-id/timeout 口径）→ make_report v2 全部动态读取修复；"
                 "④措辞门（Q2 gap=1、Q4 未闭合禁称最优；Q3 Φ=140 可称该基座认证最优，ub 口径分标）写入报告与写作纪律；"
                 "verify_all 升级 v2（注册表驱动清单、_meta 绑定/输入 sha 漂移校验、base_tuple==Q2 权威对账、"
                 "Q4_check↔solution 交叉、xlsx openpyxl 直接复算、gap/LB 自洽），堵住 run-D 型回归缺口 G1/G2/G4/G5/G7/G8/G9/G13。"),
    "reason": "P1 报告 d573ac98：数值/权威链/提交件三项证据充分；漂移与门禁缺口按建议闭合",
    "recorded_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
json.dump(d, io.open("state/decision_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("logged")
