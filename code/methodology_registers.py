# -*- coding: utf-8 -*-
"""methodology_review 阶段登记件生成器：7 份审计 JSON（确定性组合优化题口径）。"""
import io, json, os, hashlib

os.makedirs("reports/methodology", exist_ok=True)
def W(name, obj): io.open(f"reports/methodology/{name}", "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False, indent=2))

W("data_generating_process.json", {
  "analysis_unit": "用频计划（150 个提报计划；观测对象=计划参数四元组）",
  "repeated_measurement": False,
  "group_id_field": None,
  "within_group_dependence": False,
  "outcome_directly_observed": True,
  "censoring": {"left": False, "interval": False, "right": False, "truncation": False},
  "missingness": False,
  "measurement_error": False,
  "class_imbalance": True,
  "time_dependence": False,
  "notes": ("数据为组委会构造的静态提报（非抽样/非观测实验）：频段区间/时间区间/间隔/次数四参数精确给定，"
            "无观测噪声、无删失、无缺失。类内参数完全同质（A:10/5/60/3，B:15/3/40/4，C:3/2/8/12）——"
            "这是题目设计结构（DGP=确定性栅格铺设+受控冲突植入），非采样巧合；类计数 20/40/90 不均衡属题面设定，"
            "影响仅体现在 Q2 优先级损失的类内分布。占用窗由确定性公式生成（F-005），冲突关系可完全判定。")})

W("statistical_assumptions.json", {
  "ml_or_inference_applicable": False,
  "independence": "not_applicable（无随机抽样；全部计算为确定性判定/优化）",
  "conditional_independence": "not_applicable",
  "homoscedasticity": "not_applicable",
  "distribution": "not_applicable（唯一概率化操作=Q1 植入压力测试与 SA/GRASP 的种子采样，属算法随机性而非统计推断，种子冻结可复现）",
  "censoring_assumption": "not_applicable",
  "missingness_assumption": "none",
  "random_effect_structure": "not_applicable",
  "notes": "全文禁止出现无修饰『相互独立』等统计断言；本模型体系无统计假设对象。算法随机性以 seed 冻结+复现校验管理（见 ml_operation_scope 与 validation plan）。"})

W("censoring_report.json", {
  "classification": "none",
  "candidate_models": [],
  "interpolation_used": False,
  "interpolation_labeled_approximate": False,
  "interval_model_comparison_done": False,
  "decision_impact_reported": False,
  "notes": "不存在事件时间估计问题：全部占用时刻由整数参数精确给定（Δt/Δf 离散化，F-001/F-003）。删失结构=none，豁免声明。"})

W("model_necessity.json", {
  "models": [
    {"id": "Q1-ENUM3", "role": "Primary", "changes_conclusion": True, "improves_performance": True,
     "explains_mechanism": True, "used_in_decision": True,
     "necessity": "完全枚举是 Q1-C1 验收的硬要求；三实现对账（算术/同余闭式/位图）防口径漂移，闭式与位图各自还是 Q2(G*)与Q3(栅格)的输入结构"},
    {"id": "Q2-CSP-GSTAR", "role": "Primary", "changes_conclusion": True, "improves_performance": True,
     "explains_mechanism": True, "used_in_decision": True,
     "necessity": "众数解（逐边贪心修补/只约束原边）被机器证伪：只约束原 297 边的松弛 min Σr=OPTIMAL 0（假象）；G* 全势边+词典序是正确性的必要条件，非装饰"},
    {"id": "Q2-LADDER-CERT", "role": "Primary", "changes_conclusion": True, "improves_performance": False,
     "explains_mechanism": True, "used_in_decision": True,
     "necessity": "Q2-C3 验收要求撤销数下界论证；阶梯 INFEASIBLE 证书是唯一可复核机制（组合界恒 0 已证伪）"},
    {"id": "Q3-SETPACK", "role": "Primary", "changes_conclusion": True, "improves_performance": True,
     "explains_mechanism": True, "used_in_decision": True,
     "necessity": "Q3-C2 要求『最多』论证：候选完备+CP-SAT 双模型+LP 对偶三腿会合是唯一能写『最大=139（该基座下）』的路径；贪心只能给下界"},
    {"id": "Q4-RETIMING-CSP", "role": "Primary", "changes_conclusion": True, "improves_performance": True,
     "explains_mechanism": True, "used_in_decision": True,
     "necessity": "支配界（Q4 域⊇Q2 域）是可证先验：不劣于 Q2 由模型包含构造保证，比实验对比强；扩域 CSP 是收益判定的载体"},
    {"id": "GRASP-SA-BASELINE", "role": "Baseline", "used_in_decision": True,
     "necessity": "Q2-C3 明确要求启发式对照（防精确解实现 bug 与过度自信）；结果区间 [10,28] 也量化了纯启发式的不可靠性"},
    {"id": "PENALTY-FIELD", "role": "Robustness", "used_in_decision": False,
     "necessity": "连续引导的量化负结果（297→175 后修复退化为全量重解）：支撑『问题本质是组合的，连续化不构成独立贡献』的论证；也提供热启动源"},
    {"id": "ELEMENTARY-BOUND-332", "role": "Robustness", "used_in_decision": False,
     "necessity": "相位×块双计数界 332 是论文可手核的初等上界（教学价值+机器界 sanity 哨兵）；不用于最优宣称（认证界=139）"},
    {"id": "ANALYTIC-RETIME-R22", "role": "Rejected", "moved_to_appendix": True,
     "necessity": "作为求解路线被评审 reject（撤销 66 系实现自伤）；其 mod-10 同余引理（4005 对 0 反例）保留为附录机理解释素材"}
  ],
  "content_share": {"primary": 0.65, "baseline": 0.15, "robustness": 0.12, "rejected_in_appendix": 0.08},
  "moved_to_appendix": ["ANALYTIC-RETIME-R22"],
  "notes": "每模型四问审计见 necessity 字段；『它解决了哪个现有方法无法解决的问题』逐条回答。"})

W("ml_operation_scope.json", {
  "operations": [],
  "ml_applicable": False,
  "notes": "确定性优化/枚举题目：无监督学习、无统计估计、无训练/测试划分。算法随机性（SA/GRASP/LNS 的种子）不是 ML 数据流操作，种子集合 [11,29,47] 全程冻结并复现登记；不存在 outer_test 概念（评价由 canonical evaluator 对同一全量输入复算）。"})

W("sample_sizes.json", {
  "groups": [],
  "minimum_group_n": None,
  "ci_width_limit_weeks": None,
  "note": ("确定性题目（无观测样本、无置信区间概念）：合法 null 声明。"
           "全量口径登记：|V|=150、|E|=297、|G*|=1693、资源盒 100×643=64300、distinct 占用=14698、"
           "Q3 候选放置=2123、干扰边=62071——均为总体完全枚举而非样本估计。"
           "Q1 植入压力测试 n=996 属诊断证据（±4% 量级），不支撑任何论文数值结论。")})

print("7 methodology JSONs written")
