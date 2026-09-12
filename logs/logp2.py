# -*- coding: utf-8 -*-
import io, json, datetime
d = json.load(io.open("state/decision_log.json", encoding="utf-8"))
d["decisions"].append({
    "id": "D-P2-CLOSE", "stage": "coding_visual",
    "decision": ("P2 独立对抗终检（第三实现路径：解析半开区间+整数格集合，自写 CP-SAT 独立认证 Q3 OPTIMAL=140；"
                 "全链独立重算 Q1-Q4 数字全对、hint 链确认非抄录、随机源全带定种子）判『数值链可信』。7 项发现处置："
                 "F-1 dg 369=270(间隔非法)+99(时域截断) → 报告措辞改分解表述并引 logs/p2qc 留痕；"
                 "F-2 报告陈旧 → make_report v2 已修（run-F 尾部自动重出）；"
                 "F-3 计划-结果指纹时序 → run-F 以 rev6 计划重跑后自证（结果晚于当前计划）；论文仍统一用『验证计划先于本轮生产运行冻结』的事实表述，不写泛化『预注册』；"
                 "F-4 图表面板硬编码 → make_figures 改读 Q1_detect.counts.edges/Q2 residual 字段；"
                 "F-5 q1_solve pairs_checked 字面量 → 值正确（C(150,2)=11175 已独立确认）但分派器被 plan 绑定，run-F 期间禁改；列入下一轮代码卫生清理，不影响任何论文数字；"
                 "F-6 措辞边界 → Q2/Q4 全部『达成值+证书区间』表述，Q4 撤销 6 注明锚定域内达成；唯 Q3 可称『该基座下可证明最大（独立实现认证）』，且方案不唯一（P2 最优解交集 139/140 简并证据）；"
                 "F-7 result2/4 登记口径 → 表注/正文写明『仅登记被调整或被撤销计划，不变者不列』。"),
    "reason": "P2 报告 eda74c6c + logs/p2qc/P2QC_SUMMARY.md",
    "recorded_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
json.dump(d, io.open("state/decision_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("P2 disposition logged")
