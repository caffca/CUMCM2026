# -*- coding: utf-8 -*-
import json, io
from datetime import datetime
P = "runs/competitive/CS-20260911T071520-D2026/TOURNAMENT_PROTOCOL.json"
d = json.load(io.open(P, encoding="utf-8"))
d["per_question"]["Q4"]["candidate_set"] = ["Q4-R41", "Q4-R11", "Q4-R22"]
d["per_question"]["Q4"]["note"] = ("R41=重定时SA baseline（3seeds）；R11=扩域差分CSP CP-SAT（含 g 选项后全势边重建，"
                                   "注意 C 末窗 11 倍放大与 643 视界）；R22=(t1,g') 禁止条带解析构造（确定性，CH-02 版）。")
d["amendments"] = [{
    "id": "AMD-01", "field": "per_question.Q4.candidate_set[2]",
    "from": "Q4-R52", "to": "Q4-R22",
    "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    "reason": ("装配期（IDEA_CANDIDATES 生成前）发现协议笔误与派工文本不一致：Q4 组 prototype 派工自始指定 CH-02 的 "
               "Q4-R22（解析重定时构造），实际执行与 result.json 均为 R22；R52（CH-05 同范式候选）从未被侦察、"
               "无 result authority，不得进入账本。两候选同属『解析范式』代表，替换不改变 Top-K 多样性政策；"
               "Q4-R52 记入 eliminations（未侦察-同范式被 R22 代表）。本修订如实带时间戳，不追改 frozen_at，"
               "属账本对齐而非事后换将（被选者从未基于结果变化）。"),
    "impact": "无结果影响：Q4 winner（R11）在两种候选集下不变（R52 从未参选）"}]
io.open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2))
print("protocol amended (AMD-01)")
