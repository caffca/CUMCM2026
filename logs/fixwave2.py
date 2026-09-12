# -*- coding: utf-8 -*-
import io, json, py_compile, re

# 1) run_prod: 去掉全局 failed 判定，改为逐任务判定（含 failed 显示）
p = "code/prod/run_prod.py"
s = io.open(p, encoding="utf-8").read()
a = """        import re as _re
        m = _re.search(r'"failed": (\\d+)', st)
        failed = int(m.group(1)) if m else 99
        m2 = _re.search(r'"complete": (\\d+)', st)
        comp = int(m2.group(1)) if m2 else 0
        print(f"=== WAVE {w} launch_rc={rc} complete={comp} failed={failed}", flush=True)
        if failed > 0:
            sys.exit(2)
        if comp < 19:
            # 核对 wave 任务确已全部 complete
            for t in tl:
                ln = next((l for l in st.splitlines() if l.startswith('| ' + t + ' ')), '')
                if 'complete' not in ln:
                    print("WAVE-INCOMPLETE", t, ln[:80], flush=True)
                    sys.exit(3)"""
b = """        print(f"=== WAVE {w} launch_rc={rc}", flush=True)
        for t in tl:
            ln = next((l for l in st.splitlines() if l.startswith('| ' + t + ' ')), '')
            if "complete" not in ln:
                print("WAVE-INCOMPLETE", t, ln[:100], flush=True)
                sys.exit(3)"""
assert a in s
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("run_prod per-task judgement ok")
