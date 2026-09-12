# -*- coding: utf-8 -*-
"""intake 资产登记构建器：扫描工作区官方资产，计算真实 SHA256，产出 ASSET_REGISTRY v3。
运行：python code/intake_build_registry.py  （工作目录=项目根）
"""
import hashlib, json, os, sys, io

sys.stdout.reconfigure(encoding="utf-8")
WS = os.getcwd()

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def rel(p):
    return os.path.relpath(p, WS).replace("\\", "/")

ASSETS = []

def add(path, typ, source, authority, basis, **kw):
    full = os.path.join(WS, path.replace("/", os.sep))
    st = os.stat(full)
    e = {
        "asset_id": "A-" + rel(path).replace("/", "_").replace(" ", ""),
        "path": rel(path), "type": typ, "sha256": sha(full),
        "size": st.st_size, "mtime_ns": st.st_mtime_ns,
        "source": source, "authority": authority, "basis": basis,
    }
    e.update(kw)
    ASSETS.append(e)

OFFICIAL_BASIS = "官方赛题材料（组委会随题发布），用户原样提供，内容未改动；哈希为登记时点真实 SHA256"

add("D题.pdf", "problem", "official", "primary_official", OFFICIAL_BASIS,
    notes="2026 高教社杯 D 题《时频冲突检测与消解》题面（含附件说明）")
add("附件/附件1.xlsx", "data", "official", "primary_official", OFFICIAL_BASIS,
    notes="150 个用频计划：A001-A020 / B001-B040 / C001-C090，列=编号,频段区间,时间区间,间隔时长,使用次数")
for n in ("result1", "result2", "result3", "result4"):
    add(f"附件/附件2/{n}.xlsx", "template", "official", "primary_official",
        OFFICIAL_BASIS, notes=f"{n}.xlsx 官方结果模板（问题{n[-1]}提交表结构）")
add("cQMeL0YY905244c8bd4b9af832f1699446d8385e.pdf", "format_spec", "official", "primary_official",
    OFFICIAL_BASIS, notes="全国大学生数学建模竞赛论文格式规范（2026 年修订稿）")
add("FlQt6kJV6f5d5b4603e06c3c60acf89b72d7f298.pdf", "rules", "official", "primary_official",
    OFFICIAL_BASIS, notes="参赛规则（2026 年修订稿）")
add("Glps6mBh6563c55c45300fede72ddbf6eb33d3a8.pdf", "rules", "official", "primary_official",
    OFFICIAL_BASIS, notes="人工智能工具使用规定（2026 年试行）")
add("format2026.doc", "format_spec", "official", "primary_official",
    OFFICIAL_BASIS, notes="官方 Word 格式模板（本项目按 manifest engine=latex 采用 cumcm-latex 模板，此件仅作格式口径核对，不作编译输入）")

# intake 派生计算输入（无损规范化）：verified_legacy + frozen，可被后续 canonical evaluator 复核失效
_clean = "data/canonical_plans.csv"
if os.path.exists(_clean):
    add(_clean, "data", "generated", "verified_legacy",
        "intake 由附件1.xlsx（primary_official）无损规范化派生：区间字符串->整数列，未删改任何记录；"
        "frozen=登记时点冻结，若与后续 canonical 校验冲突按 V7-P0-06 降级 conflicting",
        frozen=True,
        notes="canonical_plans.csv：150 行清洗后计划表，全下游唯一机读口径")

registry = {
    "schema_version": 3,
    "generated_at": "intake",
    "assets": ASSETS,
    "missing_assets": [
        "submission/result1.xlsx（问题1输出，待 coding_visual 产出后登记）",
        "submission/result2.xlsx（问题2输出）",
        "submission/result3.xlsx（问题3输出）",
        "submission/result4.xlsx（问题4输出）",
        "results/*.json（各问计算结果权威）",
        "figures/*.pdf + *.meta.json（数据图/概念图）",
        "paper/main.tex + main.pdf（LaTeX 论文）",
        "AI工具使用详情.pdf（支撑材料，AI 规定第4条）",
    ],
    "high_severity_count": 0,
}
os.makedirs("reports/intake", exist_ok=True)
io.open("reports/intake/ASSET_REGISTRY.json", "w", encoding="utf-8").write(
    json.dumps(registry, ensure_ascii=False, indent=2))
print("assets:", len(ASSETS), "-> reports/intake/ASSET_REGISTRY.json")
