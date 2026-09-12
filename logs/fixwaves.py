# -*- coding: utf-8 -*-
"""run_prod v3：波次 rc 不作数（runner 总做全量 aggregate → 部分完成必 rc=1）；
以 RUN_STATE counts.failed 与最终聚合判定。"""
import io, py_compile
p = "code/prod/run_prod.py"
s = io.open(p, encoding="utf-8").read()

a = """        print(f"=== WAVE {w}: {tl}", flush=True)
        rc = launch(tl)
        print(f"=== WAVE {w} rc={rc}", flush=True)
        if rc != 0:
            sys.exit(rc)"""
b = """        print(f"=== WAVE {w}: {tl}", flush=True)
        rc = launch(tl)
        import time as _t
        _t.sleep(2)
        st = open(os.path.join("runs", "fresh", RUN, "RUN_STATE.md"), encoding="utf-8").read()
        import re as _re
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
assert a in s
s = s.replace(a, b)
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("run_prod v3 ok")
