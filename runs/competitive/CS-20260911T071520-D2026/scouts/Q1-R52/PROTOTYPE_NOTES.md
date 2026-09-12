# Q1-R52 原型说明（Prototype Engineer / 竞争搜索 Q1 组）

- 路线来源：`routes/CH-05.route.json` → `idea_id_suggested = Q1-R52`（tier=advanced_alternative，method_family=analytic_mechanistic，bound_scout 产物）
- 协议：TP-D2026-01，Q1 `unit=symdiff_vs_canonical_truth`，确定性 ⇒ replicates=1
- 口径：`ADJUDICATION.json` R1（T_MAX=643）/ R7（半开 + 全 n 次展开）

## 方法：类内同余闭式 + 跨类回退枚举

同类 (g,d) 齐次 ⇒ 周期 `P = g+d`、时长 `d`、次数 `n` 都相同（原型内**先断言**该性质）：

```
slot_k(i) = [t0_i + k·P, t0_i + k·P + d)
两窗交叠 ⇔ ∃q=k_i−k_j ∈ [−(n−1), n−1]:  |Δ + q·P| ≤ d−1，  Δ = t0_i − t0_j
若 2(d−1) < P（实测 A:8<65、B:4<43、C:2<10 全成立）⇒ 最近倍数唯一，于是
    时间交叠 ⇔ Δ mod P ∈ S_d = {0,…,d−1} ∪ {P−d+1,…,P−1}   （残差集）
              ∧ |Δ| ≤ (n−1)·P + (d−1)                        （窗序可达）
冲突 ⇔ 频段半开交叠 ∧ 上述两条件
```
必要性：|Δ| ≤ |q|P+(d−1) ≤ (n−1)P+(d−1)。充分性：唯一 q* 满足
|q*|P ≤ |Δ|+(d−1) ≤ (n−1)P+2(d−1) < nP ⇒ |q*| ≤ n−1。∎

跨类（P 不同，gcd(65,43)=1、gcd(65,10)=5、gcd(43,10)=1 ⇒ 仅 A–C 可按 5 陪集压缩）
按路线说明**回退逐对枚举**。

### 与"逐对枚举"的硬验收（路线 failure_conditions）
1. **时间判据逐对一致**：对全部 11175 对（**不先看频段**）中的 4975 个同组对
   （=C(20,2)+C(40,2)+C(90,2)），闭式时间判据 vs slot×slot 枚举 ⇒ 不一致数 **0**。
2. **边集逐对一致**：闭式边集 vs 枚举边集对称差 **0**，且排序后逐元素相等 **true**。

### 界有效性自检（CH-05 在 Q3 踩过的坑，此处设硬门）
- LB（类内残差同余 + 窗序可达 + 频段交叠，可证强制冲突）= **8**（A:0 / B:0 / C:8）
- UB（去掉窗序可达约束 = 次数无限放宽模型，类内残差桶 × 频段一维前缀求和）= **92**（A:1 / B:30 / C:61）
- 类内枚举真值（BB10 + CC19，AA=0）= **29** ⇒ LB ≤ 29 ≤ UB 通过（界松 3.2 倍，只作错误探测）
- 另记：同组 4975 对里闭式时间判据命中 479 对（其中仅 29 对同时满足频段交叠）

## 复现
```
python runs/competitive/CS-20260911T071520-D2026/scouts/Q1-R52/code/q1_r52_closed_form.py
python runs/competitive/CS-20260911T071520-D2026/canonical_evaluator.py --question Q1 \
  --solution runs/competitive/CS-20260911T071520-D2026/scouts/Q1-R52/solution_q1_r52.json \
  --out      runs/competitive/CS-20260911T071520-D2026/scouts/Q1-R52/eval.json
python runs/competitive/CS-20260911T071520-D2026/scouts/Q1-R52/code/make_artifacts.py
```

## 结果

| 项 | 值 |
|---|---|
| 类内 (g,d,n) 齐次性 | A(60,5,3) / B(40,3,4) / C(8,2,12)，P=65/43/10 ⇒ 断言通过 |
| 闭式分支覆盖对数 | 4975（同组）；回退枚举 6200（跨类）；合计 11175 全查 |
| 闭式 vs 枚举 | 时间判据不一致 0；边集对称差 0；逐元素相等 true |
| 冲突对 | 297（AB21/AC66/BC181/BB10/CC19） |
| 残差直方图 | A: P=65 非空桶 16（最大桶 3，Σ C(m,2)=5）；B: P=43 非空桶 30（最大桶 2，Σ C(m,2)=10）；C: P=10 十桶全占（最大桶 17，Σ C(m,2)=428）——与 CH-05 探针一致 |
| canonical evaluator | objective=[0]，missing=0，spurious=0 |
| 运行时 | 0.2802 s |
| solution SHA256 | `1a08941b766de6bff77024402d2d26fa641e9a3c7c19a6097678df9fe4c92b20`（与 R21/R41 逐字节相同） |

## 原型级限制（不隐瞒）
- 闭式收益集中在类内 29/297 对；跨类 268/297 对仍靠枚举 ⇒ 作为"可手算证书 + 界结构"路线成立，作为"替代全枚举的性能"路线不成立。
- 依赖"类内 (g,d,n) 齐次"这一数据经验事实（非题面保证），已在代码内显式断言，若不齐次即 status=failed/failure_mode=formulation_assumption_violated。
