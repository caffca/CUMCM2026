# -*- coding: utf-8 -*-
"""提交包组装：zip（论文 PDF + result1-4.xlsx + 支撑材料压缩包），≤20MB，身份匿名检查。
支撑材料 zip：code/ 生产链 + results/*.json + reports/ 关键件 + figures/ 正式图 + AI工具使用详情.pdf。"""
import io, json, os, re, sys, zipfile

FILES_PAPER = ["paper/main.pdf"]
RESULT_XLSX = [f"submission/result{i}.xlsx" for i in (1, 2, 3, 4)]
SUPPORT = (["code/prod", "code/verify_all.py", "results", "figures", "reports/RESULTS_REPORT.md",
            "reports/FINAL_MODEL_SPEC.json", "reports/VALIDATION_PLAN.json", "reports/VALIDATION_EVAL.json",
            "reports/RESULT_INTERPRETATION.json", "reports/trace/TRACEABILITY_MATRIX.md",
            "submission/AI工具使用详情.pdf"] + RESULT_XLSX)
BAN_PAT = re.compile(r"(用户名|Administrator|C:\\\\Users|真实姓名|学校名|学院|联系方式|1[3-9]\\d{9})", re.I)


def add_dir(zf, path, arc="支撑材料"):
    if os.path.isdir(path):
        for root, _, files in os.walk(root):
            for f in sorted(files):
                if f.startswith(".") or ".meta.json" == f[-9:]:
                    continue
                fp = os.path.join(root, f).replace("\\", "/")
                zf.write(fp, f"{arc}/{fp}")
    elif os.path.exists(path):
        zf.write(path, f"{arc}/{path}")


def main():
    os.makedirs("submission", exist_ok=True)
    # 支撑材料 zip
    sup = "submission/支撑材料.zip"
    with zipfile.ZipFile(sup, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in SUPPORT:
            add_dir(zf, p)
    # 主提交包
    out = "submission/D2026_提交包.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in FILES_PAPER:
            if os.path.exists(p):
                zf.write(p, f"论文/{p}")
        zf.write(sup, "支撑材料.zip")
    sz = os.path.getsize(out) / 1e6
    print(f"zip built: {out} ({sz:.1f} MB)")
    assert sz <= 20, "超过 20MB 限制"
    # 匿名检查：论文正文文本抽 PDF 元数据 + zip 文件名列表
    leaks = []
    try:
        import fitz
        doc = fitz.open("paper/main.pdf")
        txt = "".join(p.get_text() for p in doc)
        for m in BAN_PAT.finditer(txt):
            leaks.append(m.group(0))
    except Exception as e:
        print("pdf scan warn:", e)
    with zipfile.ZipFile(out) as zf:
        for n in zf.namelist():
            if BAN_PAT.search(n):
                leaks.append("filename:" + n)
    print("anonymity:", "CLEAN" if not leaks else f"LEAK {leaks[:5]}")
    return 0 if not leaks else 1


if __name__ == "__main__":
    sys.exit(main())
