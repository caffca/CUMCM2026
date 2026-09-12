# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")
c = io.open(r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts\sharded_run.py", encoding="utf-8").read()
for m in re.finditer(r"execution_policy[^\n]*", c):
    i = m.start()
    seg = c[max(0, i - 250):i + 400]
    if "deadline" in seg:
        print(seg)
        print("========")
        break
# where is 1800 set?
for m in re.finditer(r"1800|deadline", c):
    i = m.start()
    line = c[i - 80:i + 120].replace("\n", " ")
    print("...", line[:190])
