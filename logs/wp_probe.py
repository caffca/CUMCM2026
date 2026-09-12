# -*- coding: utf-8 -*-
import importlib.util, io, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
SPEC = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\brainstorm-mathmodel\scripts\whole_problem_route_bundle.py"
spec = importlib.util.spec_from_file_location("wpb", SPEC)
wpb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wpb)
ws = Path(".").resolve()
req = json.load(io.open("logs/wp_req.json", encoding="utf-8"))
req.setdefault("shared_states", [])
req.setdefault("consistency_constraints", [])
qids, contexts, docs = wpb._question_contexts(ws, req)
for q in qids:
    c = contexts[q]
    print(q, "candidate_ids:", c.get("candidate_ids"))
    tr = c.get("tournament")
    if isinstance(tr, dict):
        print("   tournament keys:", list(tr)[:14])
    else:
        print("   tournament:", type(tr).__name__, (list(tr[0])[:8] if isinstance(tr, list) and tr else ""))
