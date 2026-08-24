# AGENTS.md

本文件只保留比赛期间长期有效、能帮助 Agent 快速推进建模的规则。

## 1. 普通开始

新窗口通常只需：

1. 确认 repo root。
2. 运行 `git status --short`。
3. 读取 `docs/CURRENT_PROGRESS.md`。
4. 根据任务需要读取相关代码、数据、论文或环境文档。
5. 直接开始工作。

`REPOSITORY_MAP.md`、`ENVIRONMENT.md`、`DATA_PROTOCOL.md`、`DECISIONS.md`、
论文文档和其他治理文件均按需读取，不要求每轮全部打开。普通任务不需要
先输出完整的 confirmed facts / unknowns / authorization / validation 报告；
复杂任务用几句说明路线即可。

## 2. Contest Start Fast Path

当用户提供：

```text
选定题目 + 完整题面 + 全部附件
```

即视为正式进入比赛。Agent 可以直接：

- 读取和解析全部题面、附件与数据；
- 做数据清洗、EDA、baseline、数学建模和普通求解；
- 进行参数实验、统计分析、必要的敏感性/稳健性分析和绘图；
- 修改源码、创建结果文件、整理 `outputs/qX/`；
- 修改论文源文件并推进下一问；
- 安装普通轻量 Python 科学计算依赖。

不需要为上述每一步重新申请。只有以下情况需要再次确认：

- 删除或覆盖重要原始数据、正式结果或论文；
- destructive Git 操作；
- 大规模 GPU 训练或显著高成本 sweep；
- 付费 API；
- 大范围、可能破坏环境的 CUDA / PyTorch / 核心依赖修改；
- 明显改变用户已确认的题意或整体建模方向。

## 3. 两种工作模式

### explore

默认模式，服务于快速判断路线是否值得继续。包括 EDA、清洗试验、baseline、
候选模型、参数试验、临时图和失败尝试。

基本流程：

```text
理解问题 → 检查必要数据 → 建 baseline/candidate → 实际运行
→ 看结果 → 诊断主要问题 → 继续或换路线
```

探索不创建 RUN ID、manifest、文件 hash、evidence matrix 或 execution journal。
可以使用 `tmp/` 或普通 working output；无价值试验可以被后续试验替代。

### milestone

当某一问得到基本满意、某个模型成为当前主模型、结果准备进入论文、正式图表
准备保留、重要建模决策确定，或一问基本完成时，升级为 milestone。

轻量归档放在：

```text
outputs/q1/
outputs/q2/
...
```

每个问题按实际需要创建目录。`summary.md` 只记录问题、采用模型、核心假设、
关键输入、关键结果、选择理由、主要验证、对应代码/图表和仍存在的问题。
不复制完整终端日志，不为普通结果计算 hash，不建立庞大 manifest。

## 4. 建模原则

- Minimum sufficient modeling：先用能回答问题的最简单充分模型。
- Complexity must be earned by evidence：复杂度必须解决已诊断的明确不足。
- 先建立可解释 baseline；只有证据支持时才升级模型。
- 黑盒模型进入主结论时，说明 baseline、数据评估方式和至少一种合适解释。
- 优先使用与结构匹配的精确优化方法；启发式方法说明必要性和解质量。
- negative / mixed result 如实保留，不为叙事删除失败方案。
- 不把 correlation 写成 causality，不补造题目或附件没有提供的证据。

验证只针对可能改变结论的风险：预测题重泛化误差，优化题重约束和解质量，
评价题重权重/参数敏感性，机制题重核心假设。不机械完成固定的全套检查表。

## 5. 数据与结果

- `data/raw/` 默认只读，不手工覆盖原始附件。
- `data/processed/` 由脚本生成，关键单位转换和清洗操作要能解释。
- 重要结果应有清晰路径、稳定文件名、生成脚本和关键参数。
- 论文重要数字应能回到 `outputs/qX/` 的正式结果和对应脚本。
- 不创建假 run、假 metrics、虚构数据或无法解释的占位结论。

## 6. 论文与图表

论文按逐问闭环推进：建模思路 → 模型 → 求解 → 必要验证 → 结果 → 小结。
遵守 `docs/PAPER_WRITING_GUIDE.md` 和 `docs/FIGURE_STYLE_GUIDE.md` 的内部约定。
正式图表优先使用稳定文件名和可重复脚本；图必须服务于明确结论。

当届官方格式、页数、匿名、AI 使用和支撑材料要求未由用户提供前，不预设
任何官方 MUST。最终提交检查在用户明确要求且材料到位后再进行。

## 7. 重要决定

`docs/DECISIONS.md` 只记录会影响后续多问或整篇论文的 durable decision，例如：
最终选择题目、统一评价指标、核心假设、主模型切换、放弃重要路线或统一单位。
不要记录调一个参数、换颜色、改函数名等局部操作。

## 8. 安全边界

默认允许读取、搜索、比较文件，修改本任务范围内的源码/文档/结果，并做小型
静态检查和 smoke check。不得写入密码、token、私钥或个人敏感凭据。

删除、覆盖或移动用户数据、题目附件、正式结果和论文前必须再次确认。禁止
`reset --hard`、`clean -fd`、强制 checkout、rebase、force push；永不自动 push。

## 9. Git

Git 采用 milestone commit，而不是 prompt commit：

1. 普通探索不要求立即提交。
2. milestone 时更新 `CURRENT_PROGRESS.md`，整理 `outputs/qX/summary.md` 和正式资产。
3. 运行相关代码检查、关键输出检查、`git diff --check` 和 `git status --short`。
4. 只显式 stage 本次 milestone 的相关路径，不使用 `git add .`。
5. 创建一个语义清楚的 local commit；不自动 push。

不要为了把新 commit SHA 写回文档而再创建 documentation-only commit。Git history
就是 commit source of truth，文档不人工维护 HEAD SHA。若本轮开始已有无法安全
区分的用户改动，不自动提交。

## 10. 常用文件地图

- `docs/CURRENT_PROGRESS.md`：当前状态板，只在实际进展变化时更新。
- `docs/MODELING_PROTOCOL.md`：轻量建模指南。
- `docs/DATA_PROTOCOL.md`：轻量数据处理约定。
- `docs/DECISIONS.md`：重要长期决定。
- `docs/REPOSITORY_MAP.md`、`docs/ENVIRONMENT.md`：路径和环境的 dormant reference，只有变化或故障时读取。
- `docs/PAPER_WRITING_GUIDE.md`、`docs/FIGURE_STYLE_GUIDE.md`：论文与图表长期资产。
- `outputs/qX/`：问题级 milestone 结果、摘要和正式图表。
- `paper/`：论文源文件；`references/`：参考资料；`tmp/`：可丢弃探索文件。

## 11. Skill routing

- `.agents/skills/modeling-workflow/SKILL.md`：正式比赛中的 `explore` / `milestone` 工作流。
- `.agents/skills/paper-review/SKILL.md`：按 `structure`、`figure`、`final` 模式审查论文。
- `.agents/skills/handoff/SKILL.md`：仅在用户明确要求跨会话、跨机器或跨人员交接时使用。

Skill 用于减少重复劳动，不把比赛流程变成额外审计流程。
