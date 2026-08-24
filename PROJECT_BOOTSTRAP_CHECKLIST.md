# Project Bootstrap Checklist

仅用于新仓库初始化。完成后保留为初始化记录，不作为日常任务列表。

## A. Repository

- [x] 项目暂定名称已记录为 `CUMCM2026`；正式竞赛名称仍为 `TBD / UNVERIFIED`。
- [x] `git init -b main` 已完成。
- [x] canonical branch 已确认为 `main`。
- [x] remote 已检查；当前未配置 remote。
- [x] `docs/REPOSITORY_MAP.md` 已填写已确认的真实路径。
- [x] `.gitignore` 已检查。

## B. Competition / Submission

- [ ] 当届官方竞赛通知已取得（UNVERIFIED）。
- [ ] 官方论文格式/模板已取得（UNVERIFIED）。
- [ ] AI 工具使用规定已取得（UNVERIFIED）。
- [ ] 支撑材料要求已取得（UNVERIFIED）。
- [ ] 所有硬规则已写入 `docs/SUBMISSION_SPEC.md`，并记录来源与核验日期（UNVERIFIED）。
- [x] 未从往届论文推断任何 MUST 规则。

## C. Environment

- [x] Python 3.12.6 已确认；MATLAB、R/Rscript 和已检查的 solver CLI 未找到。
- [ ] 环境激活命令已验证；当前未发现已激活的项目环境。
- [ ] 关键依赖和版本已完整记录；Matplotlib 导入已确认失败，其他依赖仍为 TBD。
- [ ] 最小 smoke check 已验证；可视化 style smoke check 因 Matplotlib 缺失未通过。

## D. Data

- [x] 官方附件预留位置已创建为 `data/raw/`；实际附件尚未取得。
- [ ] 原始附件只读策略已确认。
- [ ] 外部数据是否允许已根据当届规则确认。
- [ ] 数据 hash / manifest 方案已建立。
- [ ] 单位、缺失值、异常值和派生变量策略已初步记录。

## E. Modeling

- [ ] `MODELING_PROTOCOL` 已填写第一版具体研究问题/目标/约束（题目尚未提供）。
- [ ] baseline 原则已确认。
- [ ] validation / sensitivity / robustness 的最低要求已确认。
- [ ] 正式结果输出目录已确认。

## F. Paper / Figures

- [ ] 官方论文源模板已放入 `paper/` 或明确链接/路径。
- [ ] `FIGURE_STYLE_GUIDE` 已与官方模板兼容。
- [ ] plotting style 模块可导入（当前因 Matplotlib 缺失未通过）。
- [ ] figure/table provenance 流程已确认。

## G. Agent / Governance

- [x] `AGENTS.md` 已读取并无冲突。
- [ ] `$modeling-run-integrity` 可用。
- [ ] `$paper-review` 可用。
- [ ] `scripts/governance_check.py` 运行通过。
- [x] 自动 local commit 策略已接受并按本轮指令执行。
- [ ] 初始 template/bootstrap commit 已创建。
