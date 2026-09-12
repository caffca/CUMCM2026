# -*- coding: utf-8 -*-
"""②b 判据描述同步（v() 第二参数文本与 rev 标记）。"""
import io, py_compile
p = "code/vp_build.py"
s = io.open(p, encoding="utf-8").read()
subs = [
    ('"workers=1 与 workers=8 的 incumbent 第一级（撤销数）一致（完整四级差登记为诊断；多最优下四级全等过苛）"',
     '"权威解四级元组经独立 checker 第二实现全量重算逐位一致（解级复现，rev4/EV-CRIT-001）；w1/w8 交叉差异为诊断字段"'),
    ('"workers=1 与 workers=8 incumbent 第一级一致", "不一致 ⇒ BLOCK"',
     '"Q4 权威解元组经第二实现重算一致（解级复现，rev4/EV-CRIT-001）", "不一致 ⇒ BLOCK"'),
    ('"workers=1 与 workers=8 的 incumbent 四级元组逐位一致"',
     '"权威解四级元组经独立 checker 第二实现全量重算逐位一致（rev4/EV-CRIT-001）"'),
]
n = 0
for a, b in subs:
    if a in s:
        s = s.replace(a, b); n += 1
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("desc synced:", n)
