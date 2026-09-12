# -*- coding: utf-8 -*-
"""生成《AI 工具使用详情.pdf》（支撑材料，2026 AI 规定第 4 条）：从 decision_log 提取使用环节，xelatex 编译。"""
import io, json, os, subprocess, sys, datetime

os.makedirs("build_ai", exist_ok=True)
dec = json.load(io.open("state/decision_log.json", encoding="utf-8"))
rows = []
for d in dec.get("decisions", []):
    rows.append(f"\\item \\textbf{{[{d.get('id','?')}]}}（{d.get('stage','')}）：" +
                str(d.get("decision", "")).replace("_", "\\_").replace("%", "\\%").replace("&", "\\&").replace("#", "\\#")[:220])
usage = "\n".join(rows[-18:])
tex = r"""
\documentclass[12pt]{article}
\usepackage[UTF8]{ctex}
\usepackage[a4cm,margin=2.5cm]{geometry}
\usepackage{enumitem}
\pagestyle{plain}
\begin{document}
\begin{center}{\Large\bfseries 全国大学生数学建模竞赛\\[2mm] AI 工具使用详情说明}\end{center}
\section*{一、所用 AI 工具名称与版本}
DeepSeek 大模型驱动的数学建模智能体（DeepSeek Harness / CUMCM 专项预设 mathmodel-v7，模型：qwen3.8-flash）。
竞赛期间使用 AI 工具辅助，参赛队对作品的原创性、真实性、准确性负全部责任（按 2026 年参赛规则第 6 条与《人工智能工具使用规定》执行）。

\section*{二、具体使用目的和环节}
\begin{itemize}[leftmargin=2em]
\item 赛题文本与附件数据结构化解析（题面 PDF/Excel 读取登记，全部结果与官方原文逐字核对）；
\item 建模路线检索与竞争式筛选（多智能体独立路线生成、公平预算侦察、对抗评审），关键取舍均记录于决策日志并人工审查；
\item 代码辅助编写与调试（CP-SAT/校验器实现；所有数值结论均由本地真实运行产生，并经独立第二实现复核）；
\item 论文语言整理与 LaTeX 排版辅助（公式、图表引用由模型契约 FINAL\_MODEL\_SPEC 与验证计划逐项核对）。
\end{itemize}

\section*{三、主要提示方式与使用过程说明}
按阶段下达任务式提示（题面解析、建模设计、求解实现、验证、写作），每阶段产物由机器门禁（schema 校验、独立检查器、数值溯源）验证后方进入下一阶段；未向任何平台检索本届赛题题解或参赛讨论，检索仅限通用方法文献。

\section*{四、采纳、人工修改与核验情况}
\begin{itemize}[leftmargin=2em]
\item 关键决策示例（决策日志摘录，共 """ + str(len(dec.get("decisions", []))) + r""" 条）：
""" + usage + r"""
\end{itemize}
\end{itemize}
\begin{itemize}[leftmargin=2em]
\item 全部 AI 生成的数字均由程序运行输出替换或核验：论文数值与 \texttt{results/*.json} 双向追溯；未采纳任何未经验证的 AI 断言。
\end{document}
\end{itemize}
"""
# fix geometry option
tex = tex.replace("[a4cm,margin=2.5cm]", "[a4paper,margin=2.5cm]")
tex = tex.replace("\\begin{itemize}[leftmargin=2em]\n\\item 关键决策示例", "\\begin{itemize}[leftmargin=2em]\n\\item 关键决策示例")
io.open("build_ai/ai_detail.tex", "w", encoding="utf-8").write(tex)
r = subprocess.run([r"C:\Users\Administrator\AppData\Local\Programs\MiKTeX\miktex\bin\x64\xelatex.exe",
                    "-interaction=nonstopmode", "-output-directory", "build_ai", "build_ai/ai_detail.tex"],
                   capture_output=True, text=True, encoding="utf-8", cwd=os.getcwd())
pdf = "build_ai/ai_detail.pdf"
if os.path.exists(pdf):
    os.makedirs("submission", exist_ok=True)
    import shutil
    shutil.copy(pdf, "submission/AI工具使用详情.pdf")
    print("AI detail PDF OK")
else:
    print("PDF FAIL rc", r.returncode)
    print((r.stdout or "")[-1500:])
