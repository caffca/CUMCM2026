# -*- coding: utf-8 -*-
"""P2-5b：系统性"结果数字泄漏进代码"检测。

做法：把 results/*.json 里出现的全部 >=3 位数值收集为"结果值集合"，
再扫描 code/prod/*.py 的非注释、非字符串字面量位置上的整数常量，
报告任何"恰好等于某个结果值、且不属于题面/模型合法常量"的硬编码。
"""
import json
import os
import re
import sys
import tokenize
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

PROD = os.path.join(P.ROOT, "code", "prod")
RESULTS = os.path.join(P.ROOT, "results")

# 题面/裁定/模型内置常量（允许出现），以及纯技术性数字
LEGAL = {643, 100, 10, 5, 8, 12, 3, 2, 150, 40, 20, 90, 60, 1, 0, 7, 4, 9, 11, 6, 97, 531, 72,
         1000, 10000, 100000, 1000000, 9999, 200, 250, 300, 500, 600, 800, 900, 1200, 1700, 3600,
         10, 5, 15, 25, 30, 45, 55, 65, 75, 85, 95, 24, 48, 96, 144, 288, 512, 1024, 4096}


def result_values():
    vals = set()

    def walk(o):
        if isinstance(o, bool):
            return
        if isinstance(o, int):
            if abs(o) >= 100:
                vals.add(abs(o))
        elif isinstance(o, float):
            if abs(o) >= 100 and float(o).is_integer():
                vals.add(int(abs(o)))
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for fn in sorted(os.listdir(RESULTS)):
        if fn.endswith(".json"):
            try:
                walk(json.load(open(os.path.join(RESULTS, fn), encoding="utf-8")))
            except Exception:
                pass
    return vals


def ints_in_code(path):
    """用 tokenize 取 NUMBER 常量（自动排除字符串/注释）。"""
    out = []
    with open(path, "rb") as fh:
        for tok in tokenize.tokenize(fh.readline):
            if tok.type == tokenize.NUMBER:
                try:
                    v = int(tok.string)
                except ValueError:
                    continue
                out.append((tok.start[0], v))
    return out


def main():
    vals = result_values()
    hits = []
    for fn in sorted(os.listdir(PROD)):
        if not fn.endswith(".py"):
            continue
        path = os.path.join(PROD, fn)
        lines = open(path, encoding="utf-8").read().splitlines()
        for ln, v in ints_in_code(path):
            if v in vals and v not in LEGAL:
                hits.append({"file": fn, "line": ln, "value": v, "code": lines[ln - 1].strip()[:170]})
    # 按文件汇总
    per_file = {}
    for h in hits:
        per_file.setdefault(h["file"], []).append(h["value"])
    res = {"check": "结果数字泄漏检测（tokenize 级）",
           "n_distinct_result_values": len(vals),
           "n_hits": len(hits), "hits": hits, "per_file_summary": {k: sorted(set(v)) for k, v in per_file.items()}}
    res["verdict"] = "PASS" if not hits else "FLAG"
    P.wr("p2_leak_scan.json", res)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
