# Codex Prompt — 初始化 2026 高教杯数学建模竞赛仓库

你现在负责从一个已经整理好的数学建模 Agent 仓库模板，初始化一个新的独立项目仓库。

## 输入

模板目录或压缩包：`<TEMPLATE_PATH>`

目标仓库：`<TARGET_REPO_PATH>`

项目暂定名：`CUMCM2026`

如果路径与实际环境不同，先检查并报告，不要自行猜测或覆盖已有仓库。

## 总目标

创建一个面向 2026 高教杯数学建模竞赛的 Agent-first 仓库，使后续题目理解、数据处理、建模、求解、验证、图表、论文、AI 使用留痕和最终提交均具有可恢复、可追溯、可审计的工作流。

本轮是 **repository bootstrap**，不是正式建模任务。

## 必须遵守

1. 不从旧聊天、旧机器学习项目或往届论文猜测当前项目事实。
2. 不把往届获奖论文中的格式写成官方 MUST。
3. 当届官方格式、页数、匿名、AI 使用声明、支撑材料和提交要求，在官方文件未提供前全部保留 `UNVERIFIED`。
4. 不执行训练、正式模型求解、大规模分析或高成本计算。
5. 不下载数据、不安装/升级核心依赖，除非本 prompt 后续明确授权。
6. 不自动 push。
7. 按 `AGENTS.md` 的规则，在 bootstrap 成功且 diff 可安全归因时创建一个 local initial commit。

## 初始化步骤

### A. 安全确认

先执行只读检查：

```bash
pwd
ls
```

检查目标路径是否已存在、是否包含用户文件、是否已经是 Git 仓库。

如果目标路径非空且无法确认可以覆盖，停止并报告，不覆盖。

### B. 建立仓库

如果目标目录安全且不是 Git 仓库：

1. 创建目标目录。
2. 将模板内容复制/解压到目标根目录，不能额外套一层模板目录。
3. 执行：

```bash
git init -b main
```

若当前 Git 版本不支持 `-b main`，采用安全等价流程并记录。

### C. 读取治理规则

读取并遵守：

- `AGENTS.md`
- `README_START_HERE.md`
- `REPOSITORY_OPERATING_GUIDE.md`
- `PROJECT_BOOTSTRAP_CHECKLIST.md`
- `docs/CURRENT_PROGRESS.md`
- `docs/REPOSITORY_MAP.md`
- `docs/ENVIRONMENT.md`
- `docs/MODELING_PROTOCOL.md`
- `docs/DATA_PROTOCOL.md`
- `docs/SUBMISSION_SPEC.md`

### D. 填写只能够从当前机器确认的 bootstrap facts

允许通过安全只读命令确认：

- 当前 OS / shell；
- Python / MATLAB / R / solver 是否存在及版本；
- Git 版本；
- 当前仓库绝对路径；
- WSL / Windows 双路径（只有实际可确认时）；
- remote 是否存在。

只把已确认事实写入：

- `docs/REPOSITORY_MAP.md`
- `docs/ENVIRONMENT.md`
- `docs/CURRENT_PROGRESS.md`
- `PROJECT_BOOTSTRAP_CHECKLIST.md`

无法确认的继续保留 `TBD / UNVERIFIED`。

不要安装缺失软件来“完成模板”。

### E. 创建标准空目录（若模板中未存在）

确保至少存在：

```text
src/
configs/
scripts/
tests/
data/raw/
data/processed/
data/external/
outputs/runs/
outputs/reports/
outputs/figures/
outputs/tables/
paper/
references/
tmp/
.agents/skills/
```

不要在这些目录中生成虚构数据或占位结果。

### F. 检查治理工具

运行：

```bash
python scripts/governance_check.py
```

如果当前 Python 不可用，只报告 blocker，不安装环境。

检查：

```bash
git status --short
git diff --check
```

### G. 初始 local commit

如果：

- 模板复制完整；
- 没有 secrets / 大型数据 / 无关文件；
- governance check 无 hard error；
- bootstrap 修改都可明确归因；

则按 `AGENTS.md` 规则显式 stage 当前模板/治理文件并创建一个 local commit，例如：

```text
chore: bootstrap CUMCM 2026 modeling repository
```

禁止 `git add .`；按职责显式添加路径。

不要 push。

## 本轮不要做的事情

- 不填写具体赛题；
- 不选择模型；
- 不提前生成论文正文；
- 不虚构官方格式；
- 不创建假 run / 假 metrics；
- 不把参考国奖论文复制成我们的模板正文；
- 不删除任何无法确认用途的用户文件。

## 最终报告

完成后报告：

1. 实际目标仓库路径；
2. Git branch / HEAD；
3. 创建或确认的目录；
4. 本轮填写了哪些已验证环境/路径事实；
5. 哪些项目仍为 `TBD / UNVERIFIED`；
6. governance check 结果；
7. local commit SHA（若创建）；
8. Git push 是否执行（应为 no）；
9. 下一步需要用户提供的材料，优先包括：
   - 2026 官方竞赛通知；
   - 官方论文模板/格式文件；
   - AI 使用规定；
   - 比赛开始后官方题目与附件。
