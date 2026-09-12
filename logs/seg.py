# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding="utf-8")
c = io.open(r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts\sharded_run.py", encoding="utf-8").read()
i = c.find("differs from recomputed")
print(c[max(0, i - 1500):i + 60])
