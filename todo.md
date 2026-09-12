# 待办事项（阶段顺序来源 workflow_spec.yaml，v7 预设；每阶段完成后 stage_close 收口）

- [x] 1. intake（0intake-assets）— ASSET_REGISTRY v3 gate 通过（tx=SC-AA89E515427C，0 冲突，DATASET_SNAPSHOT 已建）
- [x] 2. brainstorm（tx=SC-A71EA16E7E60）— 48 路线 5 scout 生成→12 Top-K 侦察（Q1 三实现逐字节一致 297 对；Q2-R51 [6,121,1996,663] 证书 [2,6] 开放；Q3-R11 **N*=139 三腿可证**；Q4-R11 锚定 [6,121,1996,663]）→ 4 独立评审（含 TF-1 锚定重算、R22 reject）→ IDEA v2/v3 契约；idea_gate 0/0、candidate_coverage PASS、P1-01 PASS；ADJUDICATION(R1-8)+TOURNAMENT_PROTOCOL+canonical_evaluator(SHA 8c4db98f) 冻结
- [x] 3. analysis（tx=SC-6797B89785F1）— ANALYSIS_MODELING_REPORT.md + 文献 L1-L8（verify_refs 于 6verity 执行）
- [x] 4. methodology_review（tx=SC-DF553EF5396C）— 7 审计 PASS、**FINAL_MODEL_SPEC v4 PASS**（Q1 analytical/Q2-Q4 optimization，formulation_sha 四问绑定）、FIGURE_REQUIREMENTS 10 图、REVIEW_ROUTER 官方构建 PASS、attack_questions 5 条
- [x] 5. validation_plan（tx=SC-D85F20C330E3）— VALIDATION_PLAN v2 rev2：27 条（21 must）全 criterion 机器判据冻结；生产前修订：复现判据=第一级(撤销数)一致
- [~] 6. coding_visual — **run-E 全链 PIPELINE-OK**：19/19 分片+聚合+注册表 15 件+result1-4.xlsx+verify_all 14 文档 PASS+RESULTS_REPORT+10 草图。权威数字：Q1=297（三实现零差）、Q2=[6,121,1996,661]（LB5 gap1 未闭合→区间表述）、Q3=Φ140（gap_cert=0 该基座认证最优）、Q4=[6,118,1894,661]（一级无收益/二级 adj121→118 有收益、截断 369 留痕）。进行中：P1/P2 QC 子代理 → leakage 门 → 收口
- [ ] 7. result_review（9result-review）— RESULT_INTERPRETATION.json
- [ ] 8. paper_plan（10paper-plan）— PAPER_PLAN.json（claims-evidence matrix）
- [ ] 9. editorial_plan（13editorial-plan）— FIGURE_PLAN/FigureSpec v3/Hero 评估
- [ ] 10. schematic（4drawio）— 技术路线图/流程图（TikZ 渲染）或合法 skipped
- [ ] 11. figure_editorial（14figure-editorial）— 正式图 + figure_manifest.json
- [ ] 12. writing（5writing）— paper/main.tex（LaTeX zh/cumcm 模板，数值全部来自 results 溯源）
- [ ] 13. compile_package（11compile-package）— main.pdf + COMPILE_REPORT
- [ ] 14. final_review（12final-review）— 三席盲评 + REVIEW_CLOSURE
- [ ] 15. verification（6verity）— 终验 + 提交包（论文 PDF、result1-4.xlsx、支撑材料 zip、AI 详情）

## 即时事项

- [x] 环境：ortools(cp-sat) 安装于 envlibs/；运行需 PYTHONPATH=envlibs
- [ ] submission/：result1/2/3/4.xlsx 最终落位 + 支撑材料打包 + AI工具使用详情.pdf
