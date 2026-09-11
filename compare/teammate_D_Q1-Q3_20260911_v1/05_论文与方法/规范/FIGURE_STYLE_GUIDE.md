# Figure Style Guide

Version: v0.3 (2026-09-11 scientific figure system)
Status: internal convention, not official competition format

本规范综合两类参考：

1. 高教杯国一等奖样文的竞赛阅读语法：逐问闭环、图表紧跟求解、结果可快速定位。
2. 中青杯国一等奖样文的视觉与证据表达：白底、二维图、统一风格、热图/条形图/误差图服务于具体分析。

这是内部视觉约定；用户提供官方模板后再按实际模板调整。

## 1. Core Principles

- 图必须回答一个明确问题，而不是“丰富版面”。
- 正式数据图必须从源数据和脚本生成，可重复。
- 同一语义对象在不同图中尽量保持同一颜色。
- 二维优先；三维只用于数据本身具有空间三维结构时。
- caption 负责说明图的结论/用途，图内 title 不与 caption 重复。
- 数字、单位、图例、坐标轴必须可读且统一。

## 2. Default Visual Language

当前正式草稿采用根目录 `VISUAL_STYLE_PROFILE.toml`，所有问题级图优先复用
`src.visualization.style.PALETTE`：

- Primary / main method: `#3B6686`
- Secondary / baseline: `#8195A3`
- Adjust / improvement state: `#2A8278`
- Revoke / warning state: `#B95C50`
- Comparison accent: `#C17B3A`
- Keep / neutral state: `#9AABB5`
- Light grid / neutral: `#D9E1E5`

正式图避免同时使用超过 4 个高辨识度类别色，除非类别本身要求。
该色板参考可访问性与低饱和科研图表原则，不是 Nature、Science 或 CUMCM 官方色板。

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

- 默认 PDF/SVG 矢量 + PNG 实际预览；SVG 保留文本元素，PDF 使用嵌入 TrueType，另输出灰度 PNG 做 QA。
- raster 图至少保证最终 PDF 中清晰，不使用压缩截图替代正式导出。
- 图文件名稳定，例如：`fig_q2_model_comparison.pdf`。
- 正式图在对应问题的 `outputs/qX/summary.md` 中注明用途、脚本和来源。

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

## 11. Frozen figure execution

重要图使用 8–12 行 brief：figure_id、question、purpose、supported_claim、source、
unit_and_population、uncertainty、required_comparison、final_width_mm、language、
forbidden_inference；有聚合时补 aggregation。探索图不强制 brief。

Builder 保留 `outputs/qX/results.*`、`plot_data/<figure_id>.*`、`figure_briefs.md`，并负责
可复现 plotting script、可读正式 `figures/` 及其论文嵌入；冻结小型绘图输入可显式加入
milestone，完整 raw data 无需入 Git。Review Lane 只在 `review/*` 中拥有可选精修版本，
其纯绘图脚本可放 `scripts/figures/`，PDF/PNG 可放 `outputs/figures/`。
忽略文件只能从明确只读且身份可核实的冻结导出读取，缺失 BLOCKED；变化 STALE。
在现有 summary 记录 base_sha、来源身份、用途、版本和实际检查，不另建实验 registry。

`apply_competition_style()` 保持无参兼容。默认 155×90mm，也可传 width_mm/height_mm；
75/155mm、9–10.5pt 是内部常用规格，最终按用户模板调整。导出保持真实画布尺寸，
不以 tight 裁切后再猜插入宽度。字体按 Noto Sans SC → Microsoft YaHei → SimHei →
SimSun 的实际覆盖选择；缺字失败，不静默翻译。数学排版可用 Matplotlib mathtext。
baseline/main/reference/warning 使用固定颜色并搭配方形/圆形/三角/叉及线型。

最小可运行示例：`tests/figures/fixture.json`，四类结构为模型比较、网格敏感性、
预测与已有残差、依赖框架，均为 SYNTHETIC TEST。CLI 只消费输入，不拟合、平滑、
插值、再聚合或新增区间。区间由源提供，图注必须明确 SD/SE/CI/情景范围/none；
候选网格最好不等于全局最优，可行/不可行需明确。不得用生成式图像制造数值证据。

```powershell
.\.venv\Scripts\python.exe scripts/figures/render_figure.py --source <FROZEN_JSON> --sha256 <INPUT_SHA256> --brief <BRIEF_JSON> --output-dir <ISOLATED_FIGURES_DIR> --base-sha <FULL_MILESTONE_SHA>
```

CLI 验证输入身份和图形数据，不自动证明 source 属于指定 commit。调用它的 Builder 或
Review Root 在自己的授权工作区核对 `git rev-parse HEAD`、输入及允许输出路径，执行前后
核对 tracked/untracked 和重要 ignored 输入。单图单 writer；共享 style 由集成者修改。
当前 designer 只读回退，由调用它的 root 执行，不将 workspace-write 当文件白名单。

正确性 → PNG 像素 → 中文 PDF 实际页面依次验收。未看像素标
NOT_VISUALLY_VERIFIED；机器 PASS 不等于人工确认。图注简述对象/口径、图元/区间、
观察和边界。通常最多两版、一轮正常修订，达到正确可读即停。
R0/非关键 R1 不打断 Builder；涉及核心数值/单位/结论的错误显眼交 Human 裁决。

### 数值输入与比较对象（pilot小修）

数值图默认拒绝NaN/Inf、空数组及形状不一致。敏感性线图的y缺测仅在冻结源和brief
同时声明 `missing_data_policy: gap` 且brief有 `missing_data_note` 时允许，保留断线，
不补零、不插值；无穷值、全缺测和x缺测仍拒绝。其他图型遇缺测先返回Builder。
`required_comparison` 使用对象ID列表，如 `["series:baseline", "series:main"]` 或
`["reference:identity", "reference:zero"]`；确实不需要时明确 `none`。原来的自由文字
应转换为这些明确对象，不能只靠字段非空通过；绘制前和实际创建对象后都检查。
`supported_claim`成员检查仅保证与Builder批准文字一致，不自动证明科学命题；
解释仍需对照数据及人工科学核验，不建设自然语言证明引擎。
