# Skill: modeling-run-integrity

## Purpose

用于正式建模、求解、预测、统计分析、参数选择、敏感性/鲁棒性和结果审计。

它负责把“跑出一个结果”升级为“可追溯的建模证据”。

## Start

1. 读取 `AGENTS.md`、`CURRENT_PROGRESS`、`MODELING_PROTOCOL`、`DATA_PROTOCOL` 和相关 decision。
2. 明确问题编号、研究/决策问题、baseline/reference、输入数据、目标、约束、评价指标和成功/停止标准。
3. 创建唯一 `RUN-YYYYMMDD-NNN_<short-name>`。
4. 基于 `docs/templates/MODELING_RUN_MANIFEST.yaml` 写入 manifest。
5. 在首次不可轻易重建的写入前，向 execution journal 追加 OPEN/checkpoint。

## Integrity Checks

按任务选择：

- input path / hash / version correct；
- units and preprocessing consistent；
- no test/group leakage；
- selection and preprocessing fitted only on allowed data；
- baseline protocol matched；
- output directory new / no overwrite；
- random seed / solver / parameters recorded；
- exact vs heuristic distinction clear；
- negative / mixed result preserved。

## During Run

保存实际命令、解析后的配置、异常和输出路径。

失败不静默删除。

## After Run

记录：

- status；
- primary metrics / objective；
- baseline delta；
- validation；
- sensitivity / robustness；
- anomalies；
- conclusion；
- affected Result IDs；
- go / no-go / rerun decision。

然后更新：

- `CURRENT_PROGRESS.md`
- `RESULTS_EVIDENCE_MATRIX.md`（若结论状态变化）
- `FIGURE_TABLE_INDEX.md`（若正式图表变化）

不得为了更好看的故事修改正式结果文件。
