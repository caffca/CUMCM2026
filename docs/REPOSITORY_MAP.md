# Repository and Storage Map

Last updated: 2026-08-24

## Repository Identity

- Project name: CUMCM2026 (暂定)
- Canonical repository: `E:\CUMCM2026`
- Canonical branch: main
- Remote URL: none configured (verified 2026-08-24)
- Local working copy: `E:\CUMCM2026`
- WSL path, if any: `/mnt/e/CUMCM2026` (verified accessible)
- Remote machine / mirror, if any: none configured

## Directory Responsibilities

| Path | Responsibility | Write policy |
|---|---|---|
| `src/` | 可复用源码 | 受控修改 |
| `scripts/` | 可复现实用脚本 | 受控修改 |
| `configs/` | 人工维护配置 | 显式修改 |
| `data/raw/` | 官方原始附件/原始数据 | 默认只读 |
| `data/processed/` | 处理后的数据 | 脚本生成，不覆盖旧版本 |
| `outputs/runs/` | 正式建模/分析 run 证据 | append-only |
| `outputs/reports/` | 汇总报告 | 从正式输出生成 |
| `outputs/figures/` | 正式图件 | 从源数据+脚本生成 |
| `outputs/tables/` | 正式表格 | 从源数据+脚本生成 |
| `paper/` | 最终论文源文件 | 按官方模板受控修改 |
| `docs/` | 治理、协议、状态、证据索引 | 按 ownership 维护 |
| `references/` | 参考资料 | 非 source-of-truth |
| `tmp/` | 临时文件 | 可丢弃 |

## Canonical Paths

- Official problem statement: TBD
- Official attachments: TBD
- Raw data root: `E:\CUMCM2026\data\raw`
- Processed data root: `E:\CUMCM2026\data\processed`
- Main source entry: TBD
- Main run output root: `outputs/runs/`
- Main report root: `outputs/reports/`
- Main paper source: TBD
- Final PDF: TBD
- Supporting-material root: TBD

## Synchronization Rules

- Canonical edit direction: TBD
- Allowed overwrite direction: TBD
- Hash verification required for: official attachments, final data manifests, final submission artifacts
- Directories that must remain local: environments, caches, large raw data unless explicitly synchronized
