# Paper Writing Guide

Version: v0.1
Status: internal production contract

本文件不是官方格式说明。官方硬规则只写入 `SUBMISSION_SPEC.md`。

## 1. Core Writing Spine

整篇论文遵循：

> Problem → Model → Evidence → Interpretation → Decision

模型可以复杂，但叙事必须朴素。任何新增方法都要解释它解决了什么明确问题。

## 2. Default Structure

除官方模板另有要求外：

```text
Title
Abstract
Keywords
1 Problem Restatement
2 Problem Analysis
3 Assumptions and Symbols
4 Data Processing
5 Model Establishment and Solution
  5.1 Problem 1
  5.2 Problem 2
  ...
6 Model Evaluation and Extension
References
Appendix / Supporting Material
```

每一问优先：

```text
建模思路
→ 变量/参数
→ 数学模型
→ 求解方法
→ 必要验证
→ 最终结果
→ 小结
```

## 3. Abstract

摘要必须能够作为一页 executive summary 独立评审整篇论文。

每一问回答：

- 解决什么；
- 使用什么核心模型；
- 最关键定量结果是什么；
- 结论是什么。

禁止：

- 堆算法名；
- 长推导；
- “显著提升/鲁棒性良好”等无证据形容词；
- 把 mixed/negative result 改写成 success；
- 无必要地列程序文件名。

## 4. Problem Restatement vs Analysis

### 重述

回答“题目要求什么”，保留输入、输出、硬约束和问与问的依赖。

### 分析

回答“为什么这样建模”，说明数学对象、难点、模型选择理由和前后问题关系。

两节不得重复完整复述同一内容。

## 5. Assumptions and Symbols

- 假设必须具体、必要、可审计。
- 核心符号首次出现时定义。
- 单位统一。
- 只出现一次的局部变量不必塞进总符号表。

## 6. Equations

公式用于表达核心关系、状态变量、目标、约束、评价指标和必要算法更新。

不要把代码逐行翻译成公式以制造“数学密度”。

每个重要公式后应解释：

- 物理/业务含义；
- 变量和单位；
- 为什么适用于当前问题。

## 7. Model Complexity

遵循：

```text
simple baseline
→ diagnosed limitation
→ stronger model
```

而不是：

```text
advanced model
→ result
```

## 8. Results

结果段优先：

```text
Observation
→ Evidence
→ Interpretation
→ Boundary
```

模型不超过 baseline 时如实写明，并解释其边界或局部价值。

## 9. Validation

验证必须对应明确风险，不追求“全家桶”。

例如：

- baseline：证明复杂模型是否必要；
- CV / holdout：证明泛化；
- residual：证明结构遗漏；
- sensitivity：证明关键参数不脆弱；
- exact small-scale：验证启发式；
- scenario：证明决策在不同情景下如何变化。

## 10. Figures and Tables

遵守 `FIGURE_STYLE_GUIDE.md` 和 `FIGURE_TABLE_INDEX.md`。

同一结果的表和图若共存，必须分别承担 exact values 与 pattern/uncertainty 等不同职责。

## 11. Model Evaluation

优点只写正文已有证据支持的能力。

不足优先写：

- 建模近似；
- 数据限制；
- 评价边界；
- 参数敏感性；
- 未覆盖场景；
- 外推风险。

避免模板句：

> 模型简单高效、准确可靠、推广性强。

除非正文已有直接证据。

## 12. Title

标题反映“最强且被支持的贡献”，不以最复杂但失败/混合的方法包装整篇工作。

## 13. References

优先：

1. 题目领域权威来源；
2. 模型/算法经典或原始文献；
3. 官方数据/标准；
4. 高质量同行评审资料。

AI 工具引用/声明只按当届官方规则执行。

## 14. Appendix / Supporting Material

正文只保留理解模型必需的伪代码/核心逻辑。

若只展示节选代码，明确标记为“核心代码 / illustrative excerpt”。

提交要求需要完整源码时，支撑材料中的源码必须可运行并与论文结果对应。

## 15. Final Paper Gates

```text
P0 Structure Complete
P1 Numerical Provenance Passed
P2 Modeling Consistency Passed
P3 Figure/Table QA Passed
P4 Official Format Compliance Passed
P5 Independent Reviewer Audit Passed
P6 Final PDF Visual Inspection Passed
```
