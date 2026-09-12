# Q2 figure brief

## fig_q2_policy_tradeoff_stage

- **question**: Q2
- **purpose**: 在同一 `H=643`、同一候选状态和同一零冲突可行域上，展示 T/P/E 三种目标协议的数量级权衡与 A/B/C 类保护差异。
- **supported_claim**: T 当前只提供 `C=6,M=120` 可行前缀；P 的八层词典序已证最优；E 是有界预算探索。三者均由统一检测器复验为 0 冲突。
- **source**: `outputs/q2/plot_data/q2_policy_tradeoff_stage.json`，源表 `outputs/q2/policy_comparison.csv`。
- **unit_and_population**: 150 个用频计划；C/M/P 均按计划计数，位移为整数槽位；频移和时移分别报告。
- **uncertainty**: 无统计抽样区间；T/E 的不确定性来自求解器限时未证明，而非测量误差。
- **required_comparison**: `scenario:T`, `scenario:P`, `scenario:E`。
- **final_width_mm**: 155
- **language**: zh-CN
- **aggregation**: 按政策和类别汇总 keep/adjust/cancel；图中 exact values 仍以 CSV/JSON 为准。
- **forbidden_inference**: 不从柱高推断某一政策在题面严格词典序下更优；P 以 A/B 保护优先为代价增加撤销。
