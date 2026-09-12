# CUMCM2026 D 题 Q4：允许 C 类改变间隔后的冲突消解

## 1. 问题定位与输入边界

Q4 要求在 Q1 原始 150 个用频计划上重新消解冲突。与 Q2 相比，Q4 只额外放宽
C 类计划的一个参数：相邻两次使用的间隔时长可以调整，且满足

$$
|g_i'-g_i|\le 10\Delta t.
$$

本地离散化取 \(\Delta t=1\)，所以 \(g_i'\) 为整数。Q4 不应把 Q2 的某一份排程
直接当成固定背景；Q2 的状态可以作为 Q4 候选集合的子集，但所有 150 个计划要在
同一个 Q4 可行域中重新选择状态。

本文沿用前面各问的固定资源域

$$
\mathcal R=[0,100)\times[0,643),
$$

其中频率和时间均为整数槽，区间为半开区间。643 是附件 1 全部周期使用窗的最晚
结束时刻；它是由数据得到的建模口径，不是题面明示的常数。因此本问的结果必须
绑定 \(H=643\)，若官方规划期另有规定则需整体重算。

## 2. 单个计划的状态空间

原始计划 \(i\) 记为

$$
\Pi_i=(k_i,[f_i,f_i+w_i),[s_i,s_i+d_i),g_i,n_i),
$$

其中 \(w_i=f_i^{\rm R}-f_i^{\rm L}\)、\(d_i=t_i^{\rm R}-t_i^{\rm L}\)，第 \(r\)
次使用窗口为

$$
I_{ir}=[s_i+r(d_i+g_i),\ s_i+r(d_i+g_i)+d_i),
\quad r=0,\ldots,n_i-1.
$$

每台计划从以下互斥状态中恰选一个：

1. **keep**：所有参数不变；
2. **frequency**：仅改变频段，\(f_i\mapsto f_i+\delta_i^f\)，
   \(\delta_i^f\in\{-10,\ldots,10\}\setminus\{0\}\)，且平移后仍在 `[0,100)`；
3. **time**：仅改变首次使用时间，\(s_i\mapsto s_i+\delta_i^t\)，
   \(\delta_i^t\in\{-5,\ldots,5\}\setminus\{0\}\)，且所有重复窗仍在 `[0,H)`；
4. **gap**：仅 C 类允许，\(g_i\mapsto g_i+\delta_i^g\)，
   \(\delta_i^g\in\{-10,\ldots,10\}\setminus\{0\}\)，并要求
   \(g_i+\delta_i^g\ge0\) 以及最后一个使用窗不越过 \(H\)；
5. **cancel**：撤销该计划，不产生使用窗。

Q4 中 A、B 类没有 gap 状态；Q2 的使用次数和间隔固定则对应于把
\(\delta_i^g\) 恒置为 0。一个状态不能同时含有频移、时移和 gap 移位，故严格落实
“一个用频计划只能调整其中一个参数或撤销”。

附件 1 的 C 类原始间隔为 8，所以 gap 候选在未受边界限制时为
\(g_i'\in\{0,1,\ldots,18\}\)；靠近时间右端的状态还要删除越界候选。对每个状态
显式展开全部 \(n_i\) 个周期窗，而不是只检查首次窗口。

## 3. 冲突判定与整数模型

两个非撤销状态发生冲突，当且仅当存在某一对周期窗口同时满足频率区间正长度交叠
和时间区间正长度交叠。端点相接不算冲突。实现上为每个状态预计算整数资源单元
占用集合 \(U_{iq}\)，其中 \(q=(f,t)\)；状态级冲突边也由同一周期判交器生成。

对状态 \(q\) 定义二元变量 \(x_{iq}\)。模型约束为

$$
\sum_{q\in Q_i}x_{iq}=1,\qquad x_{iq}\in\{0,1\},
$$

以及每个时频资源单元的 at-most-one 约束

$$
\sum_{(i,q):\ (f,t)\in U_{iq}}x_{iq}\le1,
\qquad (f,t)\in\mathcal R.
$$

在整数端点和半开区间语义下，两个矩形正长度相交当且仅当共享至少一个整数资源
单元。因此资源单元团约束与逐状态冲突边约束等价；后者保留为审计参考。最后再
把选中的 150 个状态送入统一周期检测器，复验全部窗口和计划对。

## 4. 目标协议

题面没有给出“撤销 1 个”和“调整 1 个”之间的数值交换率，因此不直接编造加权和。
正式 T 口径按题面自然顺序采用逐层词典序

$$
\operatorname{lexmin}(C,M,P_A,C_A,P_B,C_B,S_{\rm sum},S_{\max}),
$$

其中

$$
C=\sum_i c_i,\quad M=\sum_i a_i,\quad
P_k=C_k+M_k,
$$

表示总撤销、总调整以及 A/B/C 类受扰计划数；\(S_{\rm sum}\) 为整数位移指标

$$
S_i=|\delta_i^f|+2|\delta_i^t|+|\delta_i^g|,
\qquad S_{\rm sum}=\sum_iS_i,
\qquad S_{\max}=\max_iS_i.
$$

系数 2 仅用于使时间位移按其允许范围 5 与频移/gap 的范围 10 归一化，不能解释为
题面给出的经济权重。每层求解后把整数最优值作为等式固定，再进入下一层。

## 5. 模型选择与实现

Q4 复用 Q2 已审计的“有限状态—全局兼容—逐层目标”骨架，只替换候选生成器：

- 状态数由 Q2 的 4,582 增加到 6,103，新增 1,521 个 C 类 gap 状态；
- 状态冲突审计边为 444,561 条，资源单元团为 53,679 个；
- 从 6,103 个状态中抽取 1,000 条边与统一周期检测器逐窗比对，位集结果无不一致；
- 全量审计中 444,561 条跨计划状态边与团约束诱导的 444,561 个候选对逐一相等，
  `cell_edge_equivalence.json` 的 missing/extra 均为 0；
- Q2 的 4,582 个状态全部被 Q4 状态集合包含，说明 Q4 的可行域确实是 Q2 候选域的
  扩展，而不是悄悄改变频移、时移或撤销规则。

直接二维 `NoOverlap2D` 作为几何表达较直观，但在全实例预处理和限时证明上不如资源
单元团模型稳定；黑盒元启发式也无法给出可复核的全局上界。因此 CP-SAT 团模型承担
求解，完整状态边和统一检测器承担独立审计。

## 6. 实算结果

当前主文件来自以下有界运行：先固定已找到的 \(C=6,M=115\) 前缀，再在保护 A 类
层搜索 60 s，并保留该层得到的可行排程。求解层记录如下。

| 层 | 状态 | 目标值 | best bound | 解释 |
|---|---|---:|---:|---|
| C | FIXED | 6 | 6 | 输入前缀，不代表 Q4 全局 C 已证 |
| M | FIXED | 115 | 115 | 条件前缀，不代表 Q4 全局 M 已证 |
| P_A | FEASIBLE | 14 | 3 | 限时可行 incumbent，尚未闭合 |

当前排程指标为：

| 类别 | 保持 | 调整 | 撤销 | 受扰 \(P_k\) |
|---|---:|---:|---:|---:|
| A | 6 | 13 | 1 | 14 |
| B | 2 | 33 | 5 | 38 |
| C | 21 | 69 | 0 | 69 |
| 合计 | 29 | 115 | 6 | 121 |

调整动作细分为频移 83、时移 22、gap 调整 10；另有 29 个 keep 和 6 个 cancel。
位移绝对值和分别为

$$
\sum|\delta^f|=589,\qquad
\sum|\delta^t|=78,\qquad
\sum|\delta^g|=61,
$$

对应 \(S_{\rm sum}=806\)、\(S_{\max}=10\)。10 个 gap 计划的调整后间隔为
13、0、0、3、14、0、4、6、15、0（对应 C001、C005、C007、C023、C029、C046、
C055、C056、C059、C079），用于说明 gap 状态确实被写入 result4，而非仅在模型中
计数。

为区分“当前解较好”与“已证明最优”，保留同一模型的运行矩阵：

| 运行 | 时间预算 | 返回结果 | 证据含义 |
|---|---:|---|---|
| 全量 T 首层 C | 180 s | `FEASIBLE`, C=6, best bound=1 | 找到可行值，首层未闭合 |
| T，预算 C≤5 | 180 s | `UNKNOWN` | 未得到不可行证书 |
| 固定 C=6 求 M | 120/240 s | M=115, best bound=81 | 找到更低调整数，M 未闭合 |
| 固定 C=6,M=115 求 P_A | 60/180 s | P_A=14, 下界 3/4 | incumbent 可重复，保护层未闭合 |

## 7. 统一复验与证据边界

`result4.xlsx` 读回后包含 121 条变更记录，撤销 6 条；
`scripts/validate_d_q4_result.py` 将其与原始计划和 `selected_T.json` 逐行对照，报告
121/121 行匹配、0 个字段差异；完整 `selected_T.json` 包含全部 150 个计划。统一
验证器展开 1,277 个使用窗，得到：

| 检查项 | 结果 |
|---|---:|
| 计划数 | 150 |
| 使用窗数 | 1,277 |
| 计划对冲突数 | 0 |
| 边界违规数 | 0 |
| 快速状态冲突数 | 0 |
| canonical validation | `True` |
| 核心单元测试 | 17/17 通过 |

这里的零冲突是可行性证据。最优性证据必须另看每一层的状态和上下界：

1. Q4 全首层运行在 180 s 内返回 `C=6` 可行解，但没有闭合下界；
2. 单独的 `C≤5` 阈值运行在 180 s 内为 `UNKNOWN`，不能写成不可行；
3. 固定 `C=6,M=115` 后，`P_A=14` 仍为 `FEASIBLE`，下界为 3；
4. 因此 `C=6,M=115,P_A=14` 是当前可复验的条件性 incumbent，
   `proven_optimal=false`，不是 Q4 严格词典序最优向量。

Q4 新增 gap 状态扩大了 Q2 的可行域，所以 Q2 已有的 `C≤5` 不可行证书不能直接
移植为 Q4 的首层证明；这也是本问必须重新求解而不能沿用 Q2 前缀结论的关键逻辑。

## 8. 文件与后续工作

- [result4.xlsx](<C:/Users/l/Desktop/CUMCM2026/outputs/q4/result4.xlsx>)：当前条件性
  incumbent 的模板结果；
- [solver_report.json](<C:/Users/l/Desktop/CUMCM2026/outputs/q4/solver_report.json>)：求解
  层、上下界、状态和验证字段；
- [selected_T.json](<C:/Users/l/Desktop/CUMCM2026/outputs/q4/selected_T.json>)：完整状态；
- [candidate_summary.json](<C:/Users/l/Desktop/CUMCM2026/outputs/q4/candidate_summary.json>)：
  候选与冲突规模；
- [cell_edge_equivalence.json](<C:/Users/l/Desktop/CUMCM2026/outputs/q4/cell_edge_equivalence.json>)：
  状态边与资源单元团全量等价性审计；
- [result4_readback_check.json](<C:/Users/l/Desktop/CUMCM2026/outputs/q4/result4_readback_check.json>)：
  Excel 逐行读回校验；
- [summary.md](<C:/Users/l/Desktop/CUMCM2026/outputs/q4/summary.md>)：机器摘要。

主文件的复现入口（在仓库根目录执行）为：

```text
python scripts/solve_d_q4.py --policy T --horizon 643 --fixed-c 6 --fixed-m 115 \
  --hint outputs/q4/selected_T_fixedC6M115.json --time-limit 60 --workers 16 \
  --seed 20260917 --output outputs/q4/result4.xlsx \
  --summary outputs/q4/summary.md --report outputs/q4/solver_report.json \
  --selected outputs/q4/selected_T.json
python scripts/validate_d_q4_result.py
```

第一条命令中的 `--fixed-c/--fixed-m` 是为了复现实验性条件前缀；若要重新检验 Q4
首层，必须去掉这两个参数并单独保存新的报告，不能把固定前缀运行误当作首层证明。

下一步只做有界、可解释的增强：尝试为 `C≤5` 取得独立不可行证书，或在固定已知
前缀下改善 `M` 与保护层；若没有新证书，论文应保留当前 incumbent、下界和
`UNKNOWN`，不能把搜索时间换成“已证明最优”的措辞。
