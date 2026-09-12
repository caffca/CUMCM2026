# -*- coding: utf-8 -*-
"""P2-5 静态审计：code/prod/*.py 中 (a) 硬编码结果数字（非注释语境）(b) 未固定 seed 的随机路径。"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

PROD = os.path.join(P.ROOT, "code", "prod")

# 只可能来自计算的结果性数字（写死即嫌疑）；题面常量 643/100/10/5/8/12/3/150 等不列
RESULT_NUMS = {"297", "1693", "2117", "4582", "6013", "369", "2270", "1996", "1894", "661", "148",
               "11175", "6012119960661", "6011818940661", "14698", "15600", "48700", "676", "335",
               "2301", "2176", "1907", "1894", "129", "118", "121", "140", "144", "663", "739", "751",
               "607", "660", "661", "657", "103", "99"}
NUM = re.compile(r"(?<![\w.\-])\d+(?![\w.])")
STR = re.compile(r"\"[^\"]*\"|'[^']*'")
RAND = re.compile(r"\b(random|randint|randrange|choice|choices|shuffle|sample|permutation|default_rng|uniform|betavariate)\b")


def code_only(line):
    body = line.split("#", 1)[0]
    return body


def main():
    hits, rand_hits = [], []
    for fn in sorted(os.listdir(PROD)):
        if not fn.endswith(".py"):
            continue
        path = os.path.join(PROD, fn)
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        doc = False
        for i, raw in enumerate(lines, 1):
            st = raw.strip()
            if st.startswith('"""') or st.endswith('"""'):
                if st.count('"""') == 1:
                    doc = not doc
                if doc or st.startswith('"""'):
                    continue
            if st.startswith("#"):
                continue
            body = code_only(raw)
            stripped = STR.sub("", body)          # 去掉字符串字面量，避免图例/标题文本误报
            nums = set(NUM.findall(stripped))
            bad = sorted(n for n in nums if n in RESULT_NUMS)
            if bad:
                hits.append({"file": fn, "line": i, "numbers": bad, "code": raw.strip()[:170]})
            if RAND.search(stripped):
                rand_hits.append({"file": fn, "line": i, "code": raw.strip()[:170]})

    # 随机路径逐文件溯源：是否所有 Random/np.random 实例都带确定种子
    files_random = sorted({r["file"] for r in rand_hits})
    gov = {}
    for fn in files_random:
        txt = open(os.path.join(PROD, fn), encoding="utf-8").read()
        ctors = re.findall(r"random\.Random\(\s*([^)]{0,60})\)", txt) + re.findall(r"Random\(\s*([^)]{0,60})\)", txt)
        seeds = re.findall(r"(grasp_seed|a\.seed|--seed|seed\s*=)", txt)
        gov[fn] = {"constructors": sorted(set(c.strip() for c in ctors)),
                   "seed_tokens": sorted(set(seeds)),
                   "module_level_random_calls": bool(re.search(r"(?<!\.)\brandom\.(random|choice|shuffle|randint|randrange)\(", txt)),
                   "np_random": bool(re.search(r"np\.random|numpy\.random", txt))}
    unseeded = [f for f, g in gov.items() if g["module_level_random_calls"] or g["np_random"]]
    res = {"check": "code/prod 静态审计",
           "hardcoded_result_number_hits": hits, "n_hits": len(hits),
           "random_usage_hits": rand_hits, "random_governance": gov, "unseeded_random_files": unseeded,
           "RESULT_NUMS_watchlist": sorted(RESULT_NUMS, key=lambda x: (-len(x), x))[:40]}
    res["verdict_hardcode"] = "PASS" if not hits else "FLAG"
    res["verdict_random"] = "PASS" if not unseeded else "FLAG"
    P.wr("p2_static_audit.json", res)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
