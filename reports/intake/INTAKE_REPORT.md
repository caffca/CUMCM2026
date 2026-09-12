# INTAKE REPORT — 2026 CUMCM D 题《时频冲突检测与消解》

## 1. 资产清点结论（asset_registry.v3，10 项，全部真实 SHA256）

| 资产 | 类型 | authority | 说明 |
|---|---|---|---|
| D题.pdf | problem | primary_official | 题面：4 问 + 附录（附件1/2 说明、平移幅度 10Δf/5Δt、A>B>C 优先级） |
| 附件/附件1.xlsx | data | primary_official | 150 个用频计划（A×20/B×40/C×90） |
| 附件/附件2/result1-4.xlsx | template | primary_official | 四问官方提交模板（列结构已核对，见 §3） |
| cQMeL…​.pdf | format_spec | primary_official | 论文格式规范 2026 修订稿（A4、页边距≥2.5cm、正文≤30页、摘要页起页码、电子版首页=摘要页） |
| FlQt6…​.pdf | rules | primary_official | 参赛规则 2026 修订稿（禁浏览赛题讨论；AI 辅助允许但须声明） |
| Glps6…​.pdf | rules | primary_official | AI 工具使用规定 2026 试行（参考文献前置“AI 工具使用声明”+支撑材料《AI 工具使用详情.pdf》） |
| format2026.doc | format_spec | primary_official | 官方 Word 模板（本项目 engine=latex，仅作格式口径核对，不作编译输入） |
| state/rules_cumcm_2026.json | rules | generated | 规则摘要（已 --update-rules 入 manifest，sha 06331f13…） |

数据快照：`reports/data/DATASET_SNAPSHOT.json`（dataset_id=cumcm2026D-attachment1-plans-150；
raw sha 绑定附件1；cleaned=`reports/data/canonical_plans.csv` 无损规范化 150 行）。

## 2. DGP 速览（供 discovery 复核）

- A 类 20 部：频段宽 10、时长 5、间隔 60、次数 3（时段跨度最大 485→610）
- B 类 40 部：频段宽 15、时长 3、间隔 40、次数 4（跨度至 618）
- C 类 90 部：频段宽 3、时长 2、间隔 8、次数 12（跨度至 621）
- 三类内部参数完全同质（同类同宽/同间隔/同次数）；频段下限 0–96、时间下限 0–531。
- 时域自然视界 = **643Δt**（C083 最晚结束：531+11×(8+2)+2；第 k 次占用起点 t₁+(k-1)(g+d)，与题面 A001 例证一致）。
  【勘误 2026-09-11】本节原记"≈[0,620)"及快照 class_profile.last_slot_end_max=621 系公式漏加 d 的陈旧字段，
  已由双独立实现复算+CH-03 探针三方一致裁定 643（决策 D-HORIZON-001）；脚本已修正，coding 阶段重生成快照。
  频域 100 频段。总占用率粗估 ≈ 26%（结构性空隙大 → Q3 有加装空间）。

## 3. 模板列结构核对（提交合规）

- result1: 序号 | 冲突装备1 | 冲突设备2（每行一对）
- result2: 装备编号 | 调整后频段区间 | 调整后时间区间 | 是否撤销（“是”）
- result3: 新增装备序号 | 频段区间 | 时间区间（隐含间隔 8、次数 12、频段宽 3、时长 2 —— 建模时显式假设）
- result4: 装备编号 | 调整后频段范围 | 调整后时间区间 | 调整后间隔时长 | 是否撤销

## 4. 冲突与缺件

- ASSET_CONFLICTS：**0 HIGH** / 1 MEDIUM / 0 LOW。
- MEDIUM（conflict_id 94a826c79abdaefb，missing_coverage data）：results/ 证据在 intake 时点
  本就不存在，由 coding_visual 阶段补齐后自动消除。**人工确认放行**（登记于决策日志）。
- 缺件登记：submission/result1-4.xlsx、results/*.json、figures/、paper/、AI工具使用详情.pdf
  （见 ASSET_REGISTRY.missing_assets，均为后续阶段产物，不编造）。

## 5. 合规红线（写入后续所有阶段）

1. 不浏览/检索本届赛题任何讨论与现成答案；只检索通用方法文献。
2. 论文数字 100% 可追溯 results/*.json（trace_allowlist 登记例外）。
3. 承诺书/编号专用页不进电子版；正文无身份信息；AI 使用声明按规定原文。
4. 消解/加装方案必须过独立 checker 复验（零冲突、单参数调整、幅度限制、次数与间隔不变）。

## 6. 下一步

进入 brainstorm（profile=standard：discovery 前置 → route/bound scouts → 对抗评审 → IDEA_DECISION）。
求解环境：OR-Tools CP-SAT 9.15 @ `F:\dsh_envlibs\mathmodel`（运行脚本需 PYTHONPATH 指向该目录）。
