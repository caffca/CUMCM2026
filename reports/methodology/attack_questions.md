# 攻击式评委问题清单（自动生成草稿，人工复核后答复）

- 共 14 条；每条须在正文或附录可回答，否则记为 open issue。（6verity Step 10 逐条答复）
- 生成时间：2026-09-11T21:05:30+08:00；依据：methodology/leakage/figure_story 门禁与 reports/methodology/*.json。

1. **[necessity]** 模型「ANALYTIC-RETIME-R22」被拒的依据是什么？删除后结论/性能/解释是否变化？
   - 触发：necessity: ANALYTIC-RETIME-R22 Rejected
2. **[summary]** 方法学检查提示（优化退化证据不完整：问题 ['Q2', 'Q3', 'Q4'] 的 objective_only/constraint_only/full 含 null/pla…）：正文口径是否需要修正？
   - 触发：methodology: degeneracy
3. **[summary]** 方法学检查提示（未发现『最佳时点/精确决定』类强结论词…）：正文口径是否需要修正？
   - 触发：methodology: conclusion
4. **[figure]** 每张主 Figure 的 main_message 是否在对应正文段落被明确支持？是否存在图与正文结论冲突？
   - 触发：default
5. **[summary]** 摘要在 30 秒内能否传达『发现问题→最终答案』？每问模型缩写是否超过 2 个？
   - 触发：default
6. **[data]** 时界取 643 的依据？附件样例若给出 621 类数值，为何不沿用？答错会不会整体平移一切？
   - 触发：DATASET_SNAPSHOT 陈旧字段 erratum（D-HORIZON-001）：621 为 last_slot_end_max 公式笔误，三实现独立复算 643
7. **[model]** 冲突判定为何用半开区间 [t0,t1)、[f0,f1)？边界相接算不算冲突？若改用闭区间结果差多少？
   - 触发：Q1 边界用例表（boundary_cases）+ 531/532 界探针
8. **[model]** Q3『最大加装数』依赖 Q2 权威解基座；换一个 Q2 可行解，Φ 会变吗？论文如何诚实限定？
   - 触发：侦察基座敏感性（134/136/139 alt bases）→ 正文写明『在问题二交付方案下』口径与附录敏感性表
9. **[stats]** 数据是单一确定实例，无任何随机性：你们的『压力测试/统计口径』是否误导评委？
   - 触发：植入冲突测试为构造性诊断（±4% 措辞限制），不做任何统计推断声称
10. **[opt]** Q2 四级词典序里第 2-4 层证书未闭合时，凭什么叫『最优消解』？
    - 触发：gap_revoke/ladder 未闭合 → 措辞门（未闭合禁『最优/显著』，只称『达成值+证书区间』）
11. **[opt]** G* 图 1693 条潜在边、270626 个禁配组，与 297 个实测冲突什么关系？为何不直接用 297 对建约束？
    - 触发：全势边图口径说明：297 是消解前实测；调整占用会制造新冲突，故约束必须覆盖全部潜在相交对
12. **[code]** 求解用了侦察解作提示（hint），是否把未验证数字接进了权威链？
    - 触发：EV/D-HINT-001：hint 仅定搜索起点；incumbent 重算+独立 checker 第二实现全量复验；hint_source 留痕
13. **[result]** result3 只有三列（序号/频带/使用时段），你们如何表达 12 次重复占用与 T_MAX 截断？模板歧义怎么办？
    - 触发：ADJUDICATION R5 主口径（基座冻结解释）+ 附录模板口径说明
14. **[result]** Q4 允许 g' 后视界必然截断部分周期，99/1530 类『被禁动作数』怎么来的、影响多大？
    - 触发：dg_options_dropped_by_horizon 字段与正文局限性小节