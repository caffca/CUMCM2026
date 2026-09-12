# -*- coding: utf-8 -*-
import json, io
d = json.load(io.open('state/decision_log.json', encoding='utf-8'))
d['decisions'].extend([
 {'id': 'D-BUDGET-R51', 'stage': 'brainstorm-mathmodel',
  'decision': ('CH-REV-A 对 Q2-R51 预算越界申报的 Manager 裁定=有条件豁免：incumbent 求解 547.3s 在 600s 协议内；'
               '超出的 120.4s 为独立「界证书」进程（r=6 incumbent 未变、不替换解、仅收紧/开放界），属 bound 证据不属搜索预算。'
               '公平性成立（其余候选 incumbent 均 ≤600s 达成，超出部分未改善其 objective）。豁免登记于 IDEA_DECISION；'
               '生产阶段界加强按 D-BUDGET-001 走长预算，不适用侦察预算。'),
  'reason': '评审要求显式裁定不得默认放行；证书与 incumbent 可分离计量（cpsat_report/r51_certificates 分列）'},
 {'id': 'D-R32-REVISE', 'stage': 'brainstorm-mathmodel',
  'decision': ('Q2-R32 verdict=revise 的处置：R32 不作 primary（被 R51 支配），revise 三项中「随机版补测」与「workers=1 复现」'
               '记为豁免（理由：其结论已被定位为负结果证据+热启动源，随机性不影响该定位）；「范式重定位」采纳——IDEA_DECISION 中 '
               'R32 定位改写为『CP-SAT 主导混合范式，连续引导贡献量化为 297→175 的负结果证据』。R32 侦察结果保留为对比证据不作质量基准。'),
  'reason': 'critical 未解决不得选 primary 的规则只约束 winner 选择；R32 非 winner；豁免与重定位均入账可复核'},
 {'id': 'D-PROD-REPRO', 'stage': 'brainstorm-mathmodel',
  'decision': ('评审遗留要求转生产验证：①Q2/Q4 生产 CP-SAT 运行必须做 workers=1 与多 worker 的 incumbent 一致性验证（复现性）；'
               '②撤销层 Σr≤5 判定在生产以 ≥1e4s 级预算或专用下界机制攻闭合，闭合前论文只写区间；'
               '③Q1 论文引用 R41 压力测试须措辞为『随机化召回诊断证据（n≈500，±4%量级）』，R52 类内界称『错误探测界』。转 VALIDATION_PLAN 条目。'),
  'reason': '评审意见闭环管理，minor 不阻断但在生产/写作阶段强制兑现'},
 {'id': 'D-Q3-WIN', 'stage': 'brainstorm-mathmodel',
  'decision': ('Q3 侦察关键结果：Q3-R11 集包装 CP-SAT 双模型 OPTIMAL incumbent=bound=139 + HiGHS LP 分数上界=139.0 + '
               '候选放置 98×532 穷举完备（三路对拍 131254 干扰边 0 失配）⇒ 在 R5 主口径（Q2-R51 基座+模板参数+643 视界）下 '
               'N*=139 可证。R51 初等双计数界 332 合法但松 2.39×，仅作可手核对照。生产阶段将在新 Q2 生产解上重算（基座变化则 N* 变化，需重证）。'),
  'reason': 'Q3 最优性等级证据冻结在 scout 工件（cpsat_r11_report.json/lp_crosscheck_hiGHS.json）'}
])
json.dump(d, io.open('state/decision_log.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('rulings logged:', len(d['decisions']))
