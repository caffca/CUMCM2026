# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"runs/fresh/FULL-D2026-PROD-C/tasks/Q2-Q2-R51-main-N-A-p0/attempts"
import os, glob
d = glob.glob(os.path.join(p, "*", "payload.json"))
if not d:
    print("no payload yet")
else:
    x = json.load(io.open(d[0], encoding="utf-8"))
    print("tuple", x["objective_tuple"], "| hint", x.get("hint_source"), "| lb", x["revocation"]["proven_lb"],
          "| closed", x["revocation"]["lb_closed"])
    for l in x["layers"]:
        print("  ", l["layer"], l["status"], l.get("objective"), l.get("best_bound"))
