#!/usr/bin/env python3
"""Build the verified internal multi-page Chinese rehearsal PDF.

This is an internal synthetic pipeline, not a 2026 official submission template.
"""
from __future__ import annotations

import argparse
import csv
from html import escape
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    XPreformatted,
)


def find_font() -> str:
    candidates = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            pdfmetrics.registerFont(TTFont("ChineseBody", candidate))
            return candidate
    raise FileNotFoundError("No verified Chinese TTF/TTC font found")


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def build(source_root: Path, output: Path) -> dict:
    source_root = source_root.resolve()
    manuscript = json.loads((source_root / "paper/manuscript.json").read_text(encoding="utf-8"))
    results = json.loads((source_root / "outputs/q1/results.json").read_text(encoding="utf-8"))
    table_rows = list(csv.DictReader(
        (source_root / "outputs/q1/results.csv").open(encoding="utf-8", newline="")
    ))
    figure_path = source_root / "outputs/q1/figures/synthetic_cost_comparison.png"
    solve_path = source_root / "scripts/solve.py"
    if not figure_path.is_file() or not solve_path.is_file():
        raise FileNotFoundError("Required frozen figure or solver source missing")

    font_path = find_font()
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "BodyCN", parent=styles["BodyText"], fontName="ChineseBody", fontSize=10,
        leading=16, alignment=TA_JUSTIFY, wordWrap="CJK", spaceAfter=5 * mm,
    )
    small = ParagraphStyle(
        "SmallCN", parent=body, fontSize=8.5, leading=12, spaceAfter=2 * mm,
    )
    title = ParagraphStyle(
        "TitleCN", parent=styles["Title"], fontName="ChineseBody", fontSize=20,
        leading=29, alignment=TA_CENTER, textColor=colors.HexColor("#17365D"),
        spaceAfter=8 * mm,
    )
    subtitle = ParagraphStyle(
        "SubtitleCN", parent=body, fontSize=11, leading=17, alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"), spaceAfter=10 * mm,
    )
    heading = ParagraphStyle(
        "HeadingCN", parent=styles["Heading1"], fontName="ChineseBody", fontSize=14,
        leading=20, textColor=colors.HexColor("#17365D"), spaceBefore=2 * mm,
        spaceAfter=4 * mm,
    )
    subheading = ParagraphStyle(
        "SubheadingCN", parent=heading, fontSize=11.5, leading=17,
        textColor=colors.HexColor("#245B8A"), spaceAfter=3 * mm,
    )
    formula = ParagraphStyle(
        "FormulaCN", parent=body, fontSize=11, leading=18, alignment=TA_CENTER,
        borderColor=colors.HexColor("#B4C7E7"), borderWidth=0.5,
        borderPadding=5, backColor=colors.HexColor("#F5F8FC"),
    )
    caption = ParagraphStyle(
        "CaptionCN", parent=small, fontSize=8.5, leading=12, alignment=TA_CENTER,
        textColor=colors.HexColor("#444444"), spaceBefore=2 * mm,
    )
    code = ParagraphStyle(
        "Code", parent=styles["Code"], fontName="Courier", fontSize=7.4,
        leading=9.4, borderColor=colors.HexColor("#DDDDDD"), borderWidth=0.5,
        borderPadding=5, backColor=colors.HexColor("#FAFAFA"),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=18 * mm, title=manuscript["title"],
        author="CUMCM2026 synthetic rehearsal",
    )

    def decorate(canvas, _doc):
        canvas.saveState()
        width, height = A4
        canvas.setFont("ChineseBody", 7.5)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(20 * mm, height - 11 * mm, "CUMCM2026 内部多页出版链路演练")
        canvas.drawRightString(width - 20 * mm, height - 11 * mm, "SYNTHETIC TEST")
        canvas.drawCentredString(width / 2, 9 * mm, f"第 {canvas.getPageNumber()} 页")
        canvas.setStrokeColor(colors.HexColor("#D9E2F3"))
        canvas.line(20 * mm, height - 13 * mm, width - 20 * mm, height - 13 * mm)
        canvas.restoreState()

    story = [
        Spacer(1, 18 * mm),
        paragraph(manuscript["title"], title),
        paragraph(manuscript["subtitle"], subtitle),
        paragraph("SYNTHETIC TEST / 合成演练，不是2026赛题结果，也不是官方模板", subheading),
        paragraph("摘要", heading),
        paragraph(manuscript["abstract"], body),
        paragraph("关键词：" + "；".join(manuscript["keywords"]), body),
        Spacer(1, 8 * mm),
        paragraph(
            "证据边界：全部数据由本演练脚本生成；所有数值均可由有限整数可行集穷举复核。"
            "本文只验证计算、绘图、写作、PDF和冻结交接链路，不证明任何现实业务结论。",
            small,
        ),
        PageBreak(),
        paragraph("1 问题、数据与模型", heading),
        paragraph(manuscript["problem"], body),
        paragraph("1.1 第一问：有容量约束的整数分配", subheading),
        paragraph(manuscript["q1_method"], body),
        Paragraph(
            "<i>C</i>(x<sub>A</sub>, x<sub>B</sub>) = 4x<sub>A</sub> + "
            "6x<sub>B</sub>, &nbsp; x<sub>A</sub> + x<sub>B</sub> = 12, "
            "&nbsp; 0 &lt;= x<sub>A</sub> &lt;= 8, &nbsp; 0 &lt;= x<sub>B</sub> &lt;= 10. "
            "&nbsp;&nbsp; (1)",
            formula,
        ),
        paragraph(
            f"穷举得到 x_A={results['q1']['x_a']}、x_B={results['q1']['x_b']}，"
            f"最小成本为 {results['q1']['minimum_cost']} 元。表1给出全部可行整数方案；"
            "最优性仅限式(1)定义的有限集合。",
            body,
        ),
        Table(
            [["表 1  可行整数方案（SYNTHETIC）", "", ""],
             ["x_A", "x_B", "成本/元"]]
            + [[row["x_a"], row["x_b"], row["cost"]] for row in table_rows],
            colWidths=[42 * mm, 42 * mm, 42 * mm],
            repeatRows=2,
            style=TableStyle([
                ("SPAN", (0, 0), (-1, 0)),
                ("FONTNAME", (0, 0), (-1, -1), "ChineseBody"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#D9EAF7")),
                ("GRID", (0, 1), (-1, -1), 0.35, colors.HexColor("#AAB7C4")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
            ]),
        ),
        PageBreak(),
        paragraph("2 结果、验证与跨问接口", heading),
        paragraph(
            f"等分基线成本为 {results['q1']['baseline_cost']} 元，模型方案为 "
            f"{results['q1']['minimum_cost']} 元。图1按P-005采用“候选—共同指标—决定”邻接，"
            "对象ID为series:baseline与series:main；无缺测，区间为确定性单点。",
            body,
        ),
        Image(str(figure_path), width=150 * mm, height=88 * mm),
        paragraph(
            "图 1  等分基线与有限整数可行集最优方案的成本比较。"
            "该图支持“在本合成约束下成本较低”，不支持现实外推、统计显著性或一般全局最优。",
            caption,
        ),
        paragraph("2.1 第二问：上游结果进入容量受损情景", subheading),
        paragraph(manuscript["q2_method"], body),
        paragraph(
            f"第二问读取第一问的 x_A={results['q1']['x_a']} 作为起始分配。"
            f"A容量降为 {results['q2']['reduced_capacity_a']} 后，重分配为"
            f"({results['q2']['x_a']}, {results['q2']['x_b']})，成本"
            f"{results['q2']['cost']} 元，较第一问增加 {results['q2']['increment']} 元。"
            "这验证了P-001的具名接口，而不是把两个无关例子拼接为多问。",
            body,
        ),
        paragraph(
            "验证：脚本枚举全部可行整数点，并断言需求守恒、容量约束、成本公式与已知解析边界。"
            "失败或边界：没有随机误差、现实数据与外部效度；因此不报告置信区间或因果效果。",
            body,
        ),
        PageBreak(),
        paragraph("3 结论与可恢复性", heading),
        paragraph(manuscript["conclusion"], body),
        paragraph("测试参考项", subheading),
        paragraph(
            "[1] 本仓库 docs/PAPER_WRITING_GUIDE.md，内部写作约定（非学术引文）。\n"
            "[2] 本演练 scripts/solve.py 与 data/input.csv，合成数据和可复核运算来源。\n"
            "[3] 本演练 outputs/q1/figure_briefs.md，图1的命题、单位和禁止推断。",
            small,
        ),
        paragraph("附录 A 复现入口", subheading),
        XPreformatted(
            "python -X utf8 scripts/solve.py\n"
            "python -X utf8 scripts/figures/render_figure.py ...\n"
            "python -X utf8 paper/build_internal_rehearsal.py ...\n"
            "pdfinfo paper/CUMCM2026_synthetic_rehearsal.pdf\n"
            "pdftoppm -png paper/CUMCM2026_synthetic_rehearsal.pdf qa/page",
            code,
        ),
        paragraph("附录 B 核心求解代码节选", subheading),
        XPreformatted("\n".join(solve_path.read_text(encoding="utf-8").splitlines()[15:31]), code),
        paragraph(
            "本附录只用于说明源数据—结果—图—论文的追溯关系。完整命令、冻结SHA与"
            "Reviewer结论位于同一scratch；未提供的正式赛题和官方格式保持UNVERIFIED。",
            small,
        ),
    ]
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    return {
        "pdf": str(output),
        "font_path": font_path,
        "source_root": str(source_root),
        "synthetic": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = build(Path(args.source_root), Path(args.out).resolve())
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
