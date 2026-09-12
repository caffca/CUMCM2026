# 方案 — 2026 年 CUMCM 国赛 D 题《时频冲突检测与消解》

## 赛题概述

特定区域内 3 类（A/B/C）共 150 个用频装备提报用频计划（频段区间、首次时间区间、间隔时长、使用次数），
频域 100 个等宽频段、时域以 Δt 为最小单位。两计划时间区间与频段区间同时交叠即为时频冲突。
四问：

- **问题1**：冲突检测 → result1.xlsx（冲突对逐行）。
- **问题2**：冲突消解（每计划只调一个参数：频段平移≤10Δf 或 时间平移≤5Δt，或撤销；
  优先级 A>B>C，尽量少撤销、少调整、小幅度）→ result2.xlsx + 表1 统计。
- **问题3**：基于问题2 无冲突方案，不限平移幅度、不增加时频资源，最多还能安排多少 C 类装备 → result3.xlsx。
- **问题4**：允许部分 C 类装备调整间隔时长（与原间隔差 ≤10Δt），消解问题1 冲突 → result4.xlsx + 表1 统计。

数据：附件1（150 行：A×20 频段宽10/时长5/间隔60/次数3；B×40 宽15/3/40/4；C×90 宽3/2/8/12）。
模板：附件2 result1–4.xlsx。

## 用户偏好与决策（决策日志同步落盘）

- 排版引擎：**LaTeX**（xelatex/MiKTeX 25.12 已实测；模板 zh/cumcm-latex）。
- 竞赛：CUMCM 国赛（预设固定范围）；语言：中文 zh-CN（固定）。
- HIL：**auto**（用户明示：普通问题自行处理，仅真正 BLOCKER 才问）。
- 子问题数量：4（题面已知）。
- 求解器：**OR-Tools CP-SAT 9.15**（cp314 wheel 安装于 `envlibs/`，运行脚本须设
  `PYTHONPATH=<workspace>\envlibs`；已验证 import 通过）。
- 联网策略：允许检索方法文献/高质量论文（频指配、冲突消解、区间图着色、装箱/累积约束、CP-SAT 建模），
  **禁止**浏览本届赛题现成答案/参赛方案讨论。
- 评奖导向：假设合理性、建模创造性、结果正确性、表述清晰——核心结果必须真实计算、可追溯。

## workflow（来源 workflow_spec.yaml v6，`workflow_spec.py --print` 生成，禁止手写副本）

```text
intake → brainstorm → analysis → methodology_review → validation_plan → coding_visual
→ result_review → paper_plan → editorial_plan → schematic → figure_editorial
→ writing → compile_package → final_review → verification
```

各阶段 skill / inputs / outputs / gate / 依赖 / 失败回退以 `workflow_spec.yaml` 的 `stages` 段为准；
阶段收口一律用 `stage_close.py --stage <id>`（原子事务）。产物所有权表：
`docs/generated/artifact_ownership.md`（预设目录内，同源生成）。

## 阶段产物骨架（目录）

```text
reports/intake/     ASSET_REGISTRY v3（gate: --require-v3）/ ASSET_CONFLICTS / INTAKE_REPORT
reports/contracts/  QUESTION_CONTRACT / PROBLEM_FACTS / IDEA_CANDIDATES / IDEA_DECISION
reports/data/       DATA_PROFILE / DATA_CONTRACT / DATASET_SNAPSHOT
reports/discovery/  PROBLEM_STRUCTURE / EDA_FINDINGS / MODEL_OPPORTUNITIES
reports/methodology/ 方法学审计 7 份；reports/FINAL_MODEL_SPEC.json；reports/FIGURE_REQUIREMENTS.json
reports/VALIDATION_PLAN.json|.md
code/ results/ figures/（*.meta.json 溯源）
reports/RESULT_INTERPRETATION.json
reports/PAPER_PLAN.json|.md
reports/review/ 盲评四类输出
paper/ main.tex + sections/ + generated_values.tex
state/ decision_log.json + RUN_STATE.json
```

## 风险控制

1. **正确性红线**：论文数字 100% 命中 results/*.json（trace_allowlist 登记）；UNTRACED=FAIL。
2. **冲突检测语义唯一化**：先冻结「计划级冲突对」与「时段占用重叠」的判定口径（PROBLEM_FACTS），
   Q1 结果用暴力枚举 + 区间算术双实现对账，防止口径漂移。
3. **消解合法性**：调整方案必须经独立 checker 复验（零冲突 + 每计划至多调一个参数 + 平移幅度/撤销 +
   使用次数/间隔不变），禁止只信求解器。
4. **Q3 口径歧义**（是否允许重排 Q2 方案）：主口径=Q2 方案保持不动、新 C 装备自由落位；
   在假设与灵敏度中讨论另一口径。新 C 装备参数模板沿用附件 C 类（宽3/时长2/间隔8/次数12），显式假设。
5. **规模与时间**：CP-SAT 大模型可能慢——分问独立 tournament、限时求解 + 下界/上界论证；
   每问先出 baseline（可行方案 + 诚实统计），再优化。
6. **合规**：不浏览赛题讨论；AI 使用声明按 2026 试行规定写入论文（参考文献之前）+ 支撑材料
   AI 工具使用详情.pdf；参考文献真实可核实。
