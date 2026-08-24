# AGENTS.md

## 1. Purpose

本文件定义本数学建模竞赛仓库中长期稳定、默认持续生效的 Agent 行为规则。

不要把临时聊天、一次性计划、当前结果或整段终端输出写入本文件。

项目事实、证据与写作规范分别由专门文件维护：

- `docs/CURRENT_PROGRESS.md`：唯一当前人工可读状态。
- `docs/CODEX_EXECUTION_JOURNAL.md`：append-only 的高信号 Prompt 执行历史。
- `docs/REPOSITORY_MAP.md`：仓库、数据、输出与同步路径。
- `docs/MODELING_PROTOCOL.md`：建模原则、评价口径与不可随意漂移的模型约束。
- `docs/DATA_PROTOCOL.md`：数据来源、版本、清洗、派生变量与可复现性。
- `docs/SUBMISSION_SPEC.md`：仅记录已核验的官方提交/格式硬规则。
- `docs/PAPER_WRITING_GUIDE.md`：内部论文写作合同。
- `docs/FIGURE_STYLE_GUIDE.md`：统一图表视觉合同。
- `docs/RESULTS_EVIDENCE_MATRIX.md`：结论到证据的映射。
- `docs/FIGURE_TABLE_INDEX.md`：图表到源数据、脚本和输出文件的映射。
- `docs/AI_USAGE_LOG.md`：AI 工具使用留痕。

若当前用户明确指令与本文件冲突，先指出冲突与风险；用户再次明确确认后，可执行不违反安全边界的操作。

---

## 2. Source-of-Truth Hierarchy

优先级如下：

1. 当前用户明确指令。
2. 当前目录最近的 `AGENTS.override.md` / `AGENTS.md`。
3. 根目录 `AGENTS.md`。
4. 已核验的 `docs/SUBMISSION_SPEC.md` 官方要求。
5. 已接受的 `docs/MODELING_PROTOCOL.md`、`docs/DATA_PROTOCOL.md`、`docs/DECISIONS.md`。
6. `docs/CURRENT_PROGRESS.md`、`docs/REPOSITORY_MAP.md`、`docs/ENVIRONMENT.md`。
7. 代码、配置、运行 manifest、正式结果、论文源文件。
8. 派生摘要、参考论文分析、临时笔记和聊天内容。

未知信息必须标记为 `TBD`、`UNVERIFIED` 或 `NEEDS_REVIEW`，不得猜测。

---

## 3. Session Start Protocol

开始任何实质性工作前：

1. 运行 `pwd` 与 `git rev-parse --show-toplevel` 确认仓库根目录；若尚未初始化 Git，明确报告。
2. 检查 `git status --short`、当前 branch 与 HEAD。
3. 读取：
   - `docs/CURRENT_PROGRESS.md`
   - `docs/REPOSITORY_MAP.md`
   - `docs/MODELING_PROTOCOL.md`
   - 与当前任务相关的 `docs/DECISIONS.md`
4. 按任务再读取数据、环境、论文、图表或提交规范文件。
5. 先报告：已确认事实、未知项、当前脏文件、授权范围、本轮计划和验证方式，再修改文件。
6. 不把上一轮聊天作为唯一事实来源。

---

## 4. Task Routing

### 4.1 建模 / 求解 / 正式分析

正式建模、参数选择、优化、预测、统计检验、鲁棒性或敏感性分析优先使用 `$modeling-run-integrity`，或遵守同等协议。

### 4.2 论文 / 图表 / 最终交付

涉及论文结构、图表、摘要、参考文献、格式、最终 PDF 或支撑材料时，读取：

- `docs/SUBMISSION_SPEC.md`
- `docs/PAPER_WRITING_GUIDE.md`
- `docs/FIGURE_STYLE_GUIDE.md`
- `docs/FIGURE_TABLE_INDEX.md`
- `docs/RESULTS_EVIDENCE_MATRIX.md`

必要时使用 `$paper-review`。

### 4.3 独立交接

只有用户明确要求跨会话、跨机器或跨人员交接时使用 `$handoff`。

---

## 5. Modeling Principles

1. **Minimum sufficient modeling**：优先使用能回答问题的最简单充分模型。
2. **Complexity must be earned by evidence**：更复杂方法必须解决已被诊断出的明确不足。
3. 每个正式问题应至少有一个可解释 baseline 或可核验基准，除非问题天然具有确定性解析/精确优化解。
4. 黑盒模型若进入主结论，必须有 baseline、验证和至少一种解释/敏感性证据。
5. 精确优化可行时优先 LP / MILP / convex optimization / dynamic programming；启发式算法必须说明为何精确方法不够，并尽可能用小规模 exact solution 验证。
6. 不把 correlation 写成 causality。
7. negative / mixed result 必须如实保留，不得为了叙事删除 baseline 或改写成稳定提升。
8. 题目或附件没有提供的证据不得被“补造”为实验结果；缺失证据应保持为 `not evaluated` 或 `insufficient evidence`。
9. 模型、指标、权重、阈值或数据处理规则发生长期变化时，必须进入 `docs/DECISIONS.md`，并更新对应 protocol。

---

## 6. Authorization and Safety

默认允许：

- 阅读、搜索、比较文件；
- `git status`、`git diff`、`git log` 等只读 Git 操作；
- 用户当前任务明确要求的代码、配置、文档和图表修改；
- 小型静态检查、单元测试、smoke check；
- 从已有结果生成派生图表和报告。

必须再次确认：

- 删除、覆盖、移动或重命名已有正式数据、结果、论文或支撑材料；
- 改变官方数据、题目附件或已冻结的数据处理口径；
- 手工修改正式指标；
- `reset --hard`、`clean -fd`、强制 checkout、rebase、force push；
- 大规模高成本 sweep 或超出当前任务范围的执行；
- 可能破坏环境的核心依赖升级。

不得在代码、文档或 Git 中写入密码、token、私钥或个人敏感凭据。

---

## 7. Documentation Impact Audit

每个实质性任务结束前，必须判断本轮事实变化是否影响以下文件：

| 变化 | 检查 / 更新 |
|---|---|
| 仓库路径、数据根目录、同步方向 | `docs/REPOSITORY_MAP.md` |
| Python / MATLAB / solver / CUDA / 依赖 / 启动命令 | `docs/ENVIRONMENT.md` |
| 数据来源、版本、清洗、单位、缺失值、派生变量 | `docs/DATA_PROTOCOL.md` |
| 目标函数、约束、评价指标、选择规则、验证口径 | `docs/MODELING_PROTOCOL.md` |
| 长期方向或结构决策 | `docs/DECISIONS.md` |
| 结论支持状态变化 | `docs/RESULTS_EVIDENCE_MATRIX.md` |
| 图表源数据、脚本、输出变化 | `docs/FIGURE_TABLE_INDEX.md` |
| AI 工具的实质性使用 | `docs/AI_USAGE_LOG.md` |
| 当前事实、阻塞、下一步变化 | `docs/CURRENT_PROGRESS.md` |

不要仅为了刷新时间戳而修改治理文件；只有其拥有的事实变化时才更新。

---

## 8. Publication Impact Audit

任何涉及 `paper/`、`outputs/figures/`、`outputs/tables/`、references 或 submission artifact 的实质性修改结束前，必须检查：

- 官方格式是否受影响；
- 数字是否可追溯；
- 公式、符号、单位是否一致；
- 图表与正文/摘要是否一致；
- caption、编号和交叉引用是否一致；
- AI 使用声明或支撑材料是否需要更新；
- 最终 PDF 是否存在溢出、裁切、乱码或不可读图表。

官方硬规则只能来自已核验并记录在 `docs/SUBMISSION_SPEC.md` 的来源；不得从往届论文反推为 MUST。

---

## 9. Git Policy — Automatic Local Commit

成功完成会修改仓库文件的 substantive task 后，默认自动创建 **local commit**；默认绝不自动 push。

提交前必须：

1. 完成必要验证。
2. 完成 Documentation Impact Audit 和 Publication Impact Audit（若适用）。
3. 运行 `git diff --check`。
4. 检查最终 diff 与 `git status --short`。
5. 只 stage 本轮可明确归因的路径；复杂仓库禁止 `git add .`。
6. 检查 staged diff，排除数据、缓存、日志、密钥、大文件和无关用户修改。
7. 创建语义清晰的 local commit。
8. 再次检查 `git status --short`，报告 commit SHA。

以下情况不得自动 commit：

- 用户明确要求不提交；
- 本轮应通过的验证失败；
- 任务仍处于明显 incomplete / unresolved 状态；
- diff 含 secrets、禁止文件或不可确认的大型 artifact；
- 任务开始时已有与本轮修改重叠的未提交用户改动，且无法安全分离；
- Agent 无法判断哪些改动属于自己。

永不自动：push、amend、rebase、force push、reset。

---

## 10. Parallel Agent Rules

- 同一时刻一个文件只允许一个 writer。
- `CURRENT_PROGRESS.md`、`DECISIONS.md`、`RESULTS_EVIDENCE_MATRIX.md`、`FIGURE_TABLE_INDEX.md` 等共享文件必须串行修改。
- 并行任务应按目录和职责拆分。
- 修改前重新检查 status；若其他 Agent 已改同一文件，先重新读取再合并。
- 不回滚不相关的用户或其他 Agent 修改。

---

## 11. Completion Protocol

每个有实质性产出的任务结束前：

1. 核对实际 diff、命令、运行和生成文件。
2. 执行最小必要验证，或明确说明无法验证的原因。
3. 更新 `docs/CURRENT_PROGRESS.md` 的当前有效事实。
4. 向 `docs/CODEX_EXECUTION_JOURNAL.md` 追加本轮高信号条目；不复制完整聊天和终端噪声。
5. 完成文档/发布影响审计。
6. 运行 `git diff --check`。
7. 按第 9 节规则自动创建 local commit（若满足条件）。
8. 返回最终报告。

最终报告至少声明：

```text
Modeling / analysis executed
Formal metrics recomputed
Dataset / preprocessing changed
Official submission spec changed
Paper / figures changed
Dependencies changed
Git commit created
Git push executed
Blockers / unverified items
```

---

## 12. Skills

仓库专属 skill：

- `$modeling-run-integrity`：正式建模、求解、统计分析、敏感性/鲁棒性、结果证据记录。
- `$paper-review`：论文结构、图表、格式、数字追溯和最终 PDF 质量审查。
- `$handoff`：用户明确要求时生成独立交接。

Skill 用于重复 workflow，不重复本文件中的长期规则。
