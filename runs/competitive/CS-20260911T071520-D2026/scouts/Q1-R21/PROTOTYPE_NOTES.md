# Q1-R21 原型说明（Prototype Engineer / 竞争搜索 Q1 组）

- 路线来源：`routes/CH-02.route.json` → `idea_id_suggested = Q1-R21`（tier=baseline，method_family=analytic_mechanistic）
- 协议：`TOURNAMENT_PROTOCOL.json`（TP-D2026-01），Q1 组 `unit=symdiff_vs_canonical_truth`，direction=minimize，确定性 ⇒ replicates=1
- 口径：`ADJUDICATION.json` R1（T_MAX=643）/ R7（半开区间 + 全 n 次展开 + 每对至多计一次）

## 方法（最小可运行原型，非正式论文结果）

把冲突检测写成 C(150,2)=11175 个计划对上的闭合布尔谓词求值：
`conflict(i,j) ⇔ band_overlap(i,j) ∧ time_overlap(i,j)`

- `slot_k(i) = [t0_i + k·(g_i+d_i), t0_i + k·(g_i+d_i) + d_i)`，k=0..n-1（F-005，g 为空闲间隔）
- 频段判据：`min(f1_i,f1_j) − max(f0_i,f0_j) > 0`（F-023 半开）
- **实现 A**：逐 (k,m) 时段对枚举（最坏 144 次比较/对，上界 1.61e6 次）
- **实现 B**：每计划时段做半开区间并集压缩 → 两指针扫描相交
- 硬验收：A、B 边集对称差 = 0；半开边界用例全部通过

## 复现

```
python runs/competitive/CS-20260911T071520-D2026/scouts/Q1-R21/code/q1_r21_pairwise.py
python runs/competitive/CS-20260911T071520-D2026/canonical_evaluator.py --question Q1 \
  --solution runs/competitive/CS-20260911T071520-D2026/scouts/Q1-R21/solution_q1_r21.json \
  --out      runs/competitive/CS-20260911T071520-D2026/scouts/Q1-R21/eval.json
python runs/competitive/CS-20260911T071520-D2026/scouts/Q1-R21/code/make_artifacts.py
```

## 结果（详见 `result.json` / `scout.json` / `detect_meta.json`）

| 项 | 值 |
|---|---|
| 冲突对 | 297（AB21 / AC66 / BC181 / BB10 / CC19），涉及 148 个计划 |
| 频段轴候选对 | 1352（其余 9823 对纯频段判据即排除） |
| 实现 A vs B 对称差 | **0** |
| 边界用例 | 5/5 通过（[80,90)vs[90,95) 不冲突、[40,45)vs[45,50) 不冲突、A001 第三次窗 [165,170) 命中、端点相接 [170,175) 不命中） |
| 数据源等价性 | `data/canonical_plans.csv` ≡ `common_input.plans_table_compact`（150/150 字段逐项一致） |
| canonical evaluator | objective=[0]，missing=0，spurious=0，truth=297，submitted=297 |
| 运行时 | 0.0165 s（预算 600 s 的 0.0028%） |
| solution SHA256 | `1a08941b766de6bff77024402d2d26fa641e9a3c7c19a6097678df9fe4c92b20` |

三候选（R21/R52/R41）解文件逐字节同 SHA ⇒ 三种范式在同一 evaluator 下给出同一 297 对边集。
