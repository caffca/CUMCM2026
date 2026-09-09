# paper/

最终论文源文件放置处。

**不要在模板阶段自行生成“仿官方”的论文格式。**

当届官方 Word / LaTeX 模板取得后，再按实际模板决定 `main.tex` / `.docx` 的组织。
论文进入完整初稿后，对最终 PDF 做逐页视觉检查。

当前已有一个明确标注 `SYNTHETIC TEST` 的内部多页链路演练生成器：

```powershell
C:\Users\zyy17\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe paper/build_internal_rehearsal.py --help
```

它用于验证计算结果、正式图、中文正文、表格/公式、PDF 和逐页渲染链路，不是 2026
赛题结果，也不是官方模板。正式比赛时 Builder 仍须根据真实题面生成完整初稿和实际
多页 PDF；Reviewer 只消费冻结版本做独立验收与精修。
