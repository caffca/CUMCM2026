#!/usr/bin/env python3
"""Targeted structural check for the current multi-page rehearsal PDF."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

from pypdf import PdfReader


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    pdf = Path(args.pdf).resolve()
    render_dir = Path(args.render_dir).resolve()
    report = Path(args.out).resolve()
    if not pdf.is_file():
        raise SystemExit(f"missing PDF: {pdf}")
    reader = PdfReader(str(pdf))
    pages = len(reader.pages)
    if pages < 3 or pages > 5:
        raise SystemExit(f"expected 3-5 pages, got {pages}")
    text_result = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    extracted = text_result.stdout
    required = [
        "SYNTHETIC TEST", "摘要", "式(1)", "表1", "图1", "第二问",
        "测试参考项", "附录 A", "56", "60",
    ]
    normalized = re.sub(r"\s+", "", extracted)
    missing = [item for item in required if re.sub(r"\s+", "", item) not in normalized]
    if missing:
        raise SystemExit(f"required extracted text missing: {missing}")
    extracted_pages = extracted.split("\f")[:pages]
    if len(extracted_pages) != pages or any(len(page.strip()) < 80 for page in extracted_pages):
        raise SystemExit("one or more pages have too little extractable text")
    widths = []
    for page in reader.pages:
        width_mm = float(page.mediabox.width) * 25.4 / 72
        height_mm = float(page.mediabox.height) * 25.4 / 72
        widths.append([round(width_mm, 2), round(height_mm, 2)])
        if not (209 <= width_mm <= 211 and 296 <= height_mm <= 298):
            raise SystemExit(f"non-A4 media box: {width_mm} x {height_mm}")
    render_dir.mkdir(parents=True, exist_ok=False)
    prefix = render_dir / "page"
    subprocess.run(["pdftoppm", "-r", "150", "-png", str(pdf), str(prefix)],
                   check=True, capture_output=True)
    pngs = sorted(render_dir.glob("page-*.png"))
    if len(pngs) != pages or any(path.stat().st_size < 10_000 for path in pngs):
        raise SystemExit("rendered page count/size check failed")
    payload = {
        "status": "STRUCTURE_AND_RENDER_PASS_PIXEL_REVIEW_PENDING",
        "pdf": str(pdf),
        "pages": pages,
        "a4_mm": widths,
        "required_text": required,
        "rendered_pages": [str(path) for path in pngs],
        "synthetic": True,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
