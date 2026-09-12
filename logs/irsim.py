# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\6verity\scripts")
import gate_common as gc

vp = json.load(io.open("reports/VALIDATION_PLAN.json", encoding="utf-8"))
print("rev", vp["plan_revision"])

def load(p):
    d = json.load(io.open(p, encoding="utf-8"))
    return d.get("result", d)

for pr in vp["evidence_contract"]["independent_reproduction"]["pairs"]:
    pd = load(pr["primary_file"]); rd = load(pr["reproduction_file"])
    for path in pr["compare_paths"]:
        a = gc.dot_get(pd, path); b = gc.dot_get(rd, path)
        ok = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
        if ok(a) and ok(b) and a == b:
            tag = "OK"
        elif a is None or b is None:
            tag = "MIRROR-PENDING-H"
        else:
            tag = "BAD"
        print("  {} {}: {} ({!r} vs {!r})".format(pr["pair_id"], path, tag, a, b))
