# Skill: paper-review

## Purpose

对数学建模竞赛论文执行结构、证据、图表、格式和最终 PDF 审查。

## Modes

- `structure`：摘要、章节比例、逐问闭环、重复内容和模型选择。
- `figure`：图表类型、视觉统一、caption、页面成本和可读性。
- `final`：数字、公式、答案、图表和最终 PDF 的整体检查。

按任务读取 `docs/PAPER_WRITING_GUIDE.md`、`docs/FIGURE_STYLE_GUIDE.md`、论文源文件
或最终 PDF；不强制读取 submission、evidence 或全局 provenance 文件。

## Structure Audit

检查：

- 问题重述是否只是重述；
- 问题分析是否解释模型选择；
- 每问能否快速定位模型、求解、验证、答案；
- 是否存在算法堆砌；
- 是否存在过长背景和重复结论；
- 摘要是否给定量结果。

## Result and consistency check

- 摘要、正文、图、表数字一致；
- 重要结果能回到 `outputs/qX/` 和对应脚本；
- negative / mixed result 未被包装；
- 结论没有超出当前证据边界。

## Figure Audit

- 每图目的明确；
- chart type 与数据职责匹配；
- style 一致；
- 图内 title 不重复 caption；
- table+figure 非机械重复；
- 3D / rainbow / radar 等是否真的必要；
- 最终 PDF 100% 缩放可读。

## Final mode

检查：

- 各问答案是否明确；
- 公式、符号、单位和数字是否一致；
- 图表是否可读且服务于结论；
- 摘要是否覆盖全部问题；
- 最终 PDF 是否存在溢出、裁切、乱码或不可读内容。

当用户明确提供当届官方规则并要求格式审查时，再按实际材料补充检查；没有材料时
不猜测官方要求。
