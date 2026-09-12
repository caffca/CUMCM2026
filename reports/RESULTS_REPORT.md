# 计算结果（D 题：时频冲突检测与消解）

生成：2026-09-12T13:34:23+08:00 · 权威生产运行 `FULL-D2026-PROD-H` · verify_all: PASS

## 运行环境与预算口径
- Python 3.14 + OR-Tools CP-SAT 9.15（F:\dsh_envlibs\mathmodel）；CPU 4 核；分片执行器 sharded_run v2（full 预算、聚合 19/19）。
- 任务超时按问登记：Q1 3600s / Q2 1700s / Q3 1500s / Q4 1700s；执行器单次窗口 deadline 1800s（分波续跑）。
- 层级预算（Q2/Q4）：L1 撤销 800s → 证书阶梯 250s → L2 调整 300s → L3 优先级 100s → L4 幅度 50s。
- 冻结件：canonical_evaluator SHA 8c4db98f…；ADJUDICATION R1-R8（T_MAX=643、半开区间、词典序四级、Q3 主口径）。

## 问题一结果
- 冲突对 **297**（AB21 / AC66 / BC181 / BB10 / CC19，AA=0）；涉及计划 148/150（11175 对全查）。
- 三独立实现（区间算术/位图+倒排/同余闭式）对称差=0；与官方口径 evaluator 对称差=0；边界用例失败=0。
- 植入压力测试：有效注入 124 次、最低召回 0.7177（构造性诊断证据，措辞限定量级）。
- result1.xlsx 与权威边集对称差 = 0（提交后复算）。

## 问题二结果
- 权威解（verified-best：各配置跑中词典序最优且经独立 checker 第二实现全量重算验证）元组 **(撤销 6，调整 121，优先级损失 1996，幅度 661)**，来源跑 workers=4；scalar=6012119960661。
- 复现披露：workers=1 单跑得 [21, 99, 1905, 573]（第一级与 workers=4 不一致，属搜索进程差异，作诊断记录）；workers=4 得 [6, 121, 1996, 661]；权威解本身经第二实现逐约束重验：残留冲突=0、合规违例=0、元组一致=1。
- 撤销层证书：LB=5，达成=6，gap=1（未闭合：论文写『撤销数介于 LB 与达成值之间』，禁称整体最优）。
- 侦察解仅作搜索提示（hint_source=solution_actions.json；全部数值生产重算）。
- 表1：{'A': {'kept': 5, 'adjusted': 15, 'revoked': 0}, 'B': {'kept': 4, 'adjusted': 30, 'revoked': 6}, 'C': {'kept': 14, 'adjusted': 76, 'revoked': 0}}（闭合差=0）；GRASP 对照撤销中位=50。

## 问题三结果
- 在问题二权威解基座上可加装 **Φ=136** 台 C 类计划（result3 行数=136，行差=0）。
- 三腿：候选集双实现差=0（枚举 2124 个）；CP-SAT 模型A OPTIMAL（对照模型B OPTIMAL/136）；LP 上界=1063.0；CP 整数上界=136.0；相位×块初等界=334（口径不同勿混引）。
- gap_certified=0.0 ⇒ **该基座下 Φ 为可证明最大值**。
- 基座绑定：base_tuple=[6, 121, 1996, 661] == 权威 Q2（flag=1）；零冲突复验=0。

## 问题四结果
- 权威解 **(6, 119, 1994, 659)**（verified-best；第二实现元组一致=1）。
- 植入 Q2 锚可行=1（锚元组=[6, 121, 1996, 661]）；撤销层相对 Q2 增益=0（撤销下界所限，无增益为诚实结论）；低层级改善：调整 121→119、优先级损失 1996→1994。
- checker：违例=0、残差=0；表1：{'A': {'kept': 5, 'adjusted': 15, 'revoked': 0}, 'B': {'kept': 4, 'adjusted': 30, 'revoked': 6}, 'C': {'kept': 16, 'adjusted': 74, 'revoked': 0}}（闭合差=0）；扩展域中 dg 候选动作被禁 369 项（分解：非正间隔 270 项 + 末周期越出 643 时域 99 项；分解经独立对抗终检按 plans+cells 语义全量重算吻合，留痕 logs/p2qc/）。

## 约束与一致性校验
全 PASS
- 权威结果件的 _meta 绑定 model_spec/formulation SHA、run、聚合、coverage；诊断/support 件登记 payload/meta 哈希（authority=false）。
- 侦察链（runs/competitive/**）与旧 run（C/D/E）产物不进入任何权威引用。

## 可复现运行方式
```
python code/prod/run_prod.py all          # 权威 run: FULL-D2026-PROD-H
python code/prod/write_results.py --run-id FULL-D2026-PROD-H
python code/prod/make_xlsx.py && python code/prod/submission_checks.py
python code/prod/make_q3_sensitivity.py
python code/verify_all.py && python code/prod/make_report.py && python code/prod/make_figures.py
```