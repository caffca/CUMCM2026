"""SYNTHETIC TEST: local Windows ReportLab + Poppler publication fallback.

Run with bundled Python (reportlab/pypdf), after smoke.py with the project Python.
"""
import argparse
import json
from pathlib import Path
import subprocess
from io import BytesIO

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter, Transformation


def build(work):
    work = Path(work).resolve()
    reports = json.loads((work / "smoke-evidence.json").read_text(encoding="utf-8"))
    font = reports["comparison"]["font_path"]
    # ReportLab cannot embed OpenType CFF; use installed TrueType SimHei if needed.
    candidates = [font, "C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/msyh.ttc"]
    for path in candidates:
        try:
            pdfmetrics.registerFont(TTFont("Chinese", path))
            font = path
            break
        except Exception:
            continue
    else:
        raise RuntimeError("BLOCKED: no locally usable Chinese TrueType font")
    pdfmetrics.registerFont(TTFont("Symbols", "C:/Windows/Fonts/segoeui.ttf"))
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    def draw_text(x, y, text, size=9):
        # ReportLab does not provide Matplotlib's glyph fallback. Resolve each
        # character explicitly, including U+2212, and fail before silent tofu.
        cursor = x
        for char in text:
            chosen = next((f for f in ("Chinese", "Symbols")
                           if ord(char) in pdfmetrics.getFont(f).face.charToGlyph), None)
            if chosen is None:
                raise ValueError(f"BLOCKED: publication font missing U+{ord(char):04X}")
            c.setFont(chosen, size)
            c.drawString(cursor, y, char)
            cursor += pdfmetrics.stringWidth(char, chosen, size)
    c.setTitle("SYNTHETIC TEST - Chinese figure page")
    draw_text(27*mm, 272*mm, "中文绘图与页面验收", 15)
    draw_text(27*mm, 260*mm, "SYNTHETIC TEST · 本页仅验证出版链路，不代表竞赛结果。", 10)
    draw_text(27*mm, 247*mm, "公式：残差 r = 预测值 − 观测值；均值 μ 与误差 ± ε。", 10)
    draw_text(27*mm, 233*mm, "图 1  给定场景下的成本比较（实际宽度 155 mm）", 10)
    for y, line in ((130,"点为给定情景代表成本，线段为给定情景范围，非置信区间。"),
                    (123,"主方案代表成本低于基线，但范围重叠；不据此推断统计显著性。"),
                    (111,"表 1  合成输入核对（单位：元；未作重新聚合）")):
        draw_text(27*mm, y*mm, line)
    c.line(27*mm, 106*mm, 182*mm, 106*mm)
    rows = [("方案", "代表值", "下界", "上界")]
    fixture = json.loads((work / "inputs/fixture.json").read_text(encoding="utf-8"))
    rows += [(v["label"], str(v["value"]), str(v["lower"]), str(v["upper"])) for v in fixture["comparison"]["values"]]
    for i, row in enumerate(rows):
        for x, text in zip((30,85,120,153), row):
            draw_text(x*mm, (100-i*9)*mm, text)
    c.line(27*mm, 94*mm, 182*mm, 94*mm)
    c.line(27*mm, 67*mm, 182*mm, 67*mm)
    draw_text(27*mm, 51*mm, "检查：中文、English、−2、数学符号、矢量图及表格在同一页面。")
    draw_text(27*mm, 18*mm, "SYNTHETIC TEST | 1")
    c.save()
    page = PdfReader(buffer).pages[0]
    figure = PdfReader(work / "figures/comparison.pdf").pages[0]
    assert abs(float(figure.mediabox.width)*25.4/72-155) < .01
    page.merge_transformed_page(figure, Transformation().translate(27*mm, 137*mm))
    writer = PdfWriter()
    writer.add_page(page)
    output = work / "chinese-page.pdf"
    writer.write(output)
    extracted = "".join(PdfReader(output).pages[0].extract_text().split())
    assert "中文绘图" in extracted and "残差" in extracted and "基线" in extracted
    subprocess.run(["pdftoppm", "-scale-to", "1600", "-png", "-singlefile", str(output), str(work / "chinese-page")], check=True, capture_output=True)
    print(json.dumps({"pdf":str(output),"font":font,"width_mm":155,"text_check":"PASS","pixel_review":"PENDING"}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", required=True)
    build(parser.parse_args().work)
