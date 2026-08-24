# Figure Style Guide

Version: v0.1
Status: internal convention, not official competition format

本规范综合两类参考：

1. 高教杯国一等奖样文的竞赛阅读语法：逐问闭环、图表紧跟求解、结果可快速定位。
2. 中青杯国一等奖样文的视觉与证据表达：白底、二维图、统一风格、热图/条形图/误差图服务于具体分析。

官方论文模板若与本规范冲突，以 `SUBMISSION_SPEC.md` 为准。

## 1. Core Principles

- 图必须回答一个明确问题，而不是“丰富版面”。
- 正式数据图必须从源数据和脚本生成，可重复。
- 同一语义对象在不同图中尽量保持同一颜色。
- 二维优先；三维只用于数据本身具有空间三维结构时。
- caption 负责说明图的结论/用途，图内 title 不与 caption 重复。
- 数字、单位、图例、坐标轴必须可读且统一。

## 2. Default Visual Language

建议配色（可在官方模板核验后微调）：

- Primary / main method: `#4C78A8`
- Secondary / alternative: `#7A7A7A`
- Positive / improvement: `#54A24B`
- Warning / degradation / difficult case: `#E45756`
- Optional comparison accent: `#F58518`
- Light grid / neutral: `#D9D9D9`

正式图避免同时使用超过 4 个高辨识度类别色，除非类别本身要求。

## 3. Typography

- 图中文字必须与论文中文/英文字体视觉兼容。
- 轴标签、legend、annotation 在最终 PDF 100% 缩放下可读。
- 不依赖超大图内标题传达含义。
- 数学符号使用一致 notation。

## 4. Preferred Figure Types

### Data diagnosis

- histogram / KDE
- scatter + fitted relation
- correlation heatmap
- missingness / distribution audit
- time series
- spatial plot

### Model / mechanism

- 一张全局 problem-to-model framework 优先
- algorithm diagram 仅在流程真的复杂时使用

### Validation

- observed vs predicted
- residual distribution / residual-vs-feature
- model comparison with uncertainty
- confusion matrix（仅分类且正文分析）
- cross-validation / subject/group variation

### Sensitivity / robustness

- parameter → objective/performance curve
- scenario comparison
- uncertainty / error bars
- perturbation heatmap

### Decision / optimization

- Pareto frontier
- resource allocation
- path / spatial decision map
- scenario ranking

## 5. Discouraged by Default

除非数据职责明确，否则默认避免：

- 3D bar chart
- rainbow palette
- decorative pie chart
- word cloud
- radar chart
- unrelated network graph
- 十几种颜色的折线
- 仅为了展示“AI/深度学习感”的神经网络结构图

## 6. Figure–Table Duplication

同一信息可同时有表和图，但职责必须不同：

```text
Table = exact values
Figure = pattern / comparison / uncertainty / spatial structure
```

若图只是把表机械转成柱状图，删除其中一个。

## 7. Framework Diagram

整篇优先只保留一张总框架图，显示各问题之间的数据和模型依赖。

问题级流程图不得重复“开始→处理→算法→输出→结束”的通用模板。

## 8. Export

- 优先 PDF / SVG / vector-compatible output。
- raster 图至少保证最终 PDF 中清晰，不使用压缩截图替代正式导出。
- 图文件名稳定，例如：`fig_q2_model_comparison.pdf`。
- 正式图必须登记到 `FIGURE_TABLE_INDEX.md`。

## 9. Shared Plotting Layer

Matplotlib 正式图优先导入 `src.visualization.style.apply_competition_style()`。

Agent 不应为每张图随意重新定义 palette、font size、grid 和 line width。

## 10. Figure QA

每张最终图至少检查：

- Purpose clear?
- Source traceable?
- Units correct?
- Color semantics consistent?
- Legend necessary and readable?
- Redundant title removed?
- Caption independent?
- Final PDF readable?
