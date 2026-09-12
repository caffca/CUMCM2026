# -*- coding: utf-8 -*-
import json, io, hashlib, os
R = r"F:\2026 数模\D题重跑\D题\runs\competitive\CS-20260911T071520-D2026"

def routes(f, want):
    d = json.loads(io.open(os.path.join(R, "routes", f), encoding="utf-8").read())
    for r_ in d["routes"]:
        if r_.get("idea_id_suggested") == want:
            print("====", f, want, "tier=", r_.get("tier"), "family=", r_.get("method_family"))
            for k in ("problem_reformulation", "solver", "bound_plan", "scout_plan",
                      "failure_conditions", "evidence_against_minimal"):
                if k in r_:
                    print("--", k, ":", json.dumps(r_[k], ensure_ascii=False)[:1600])

routes("CH-01.route.json", "Q3-R11")
routes("CH-02.route.json", "Q3-R23")
routes("CH-05.route.json", "Q3-R51")
d1 = json.loads(io.open(os.path.join(R, "routes", "CH-01.route.json"), encoding="utf-8").read())
print("\nCH-01 role:", d1["role"], "ideas:", [r_.get("idea_id_suggested") for r_ in d1["routes"]])
for idea in ("Q3-R11", "Q3-R23", "Q3-R51"):
    p = os.path.join(R, "scouts", idea, "eval_q3.json")
    ev = io.open(p, encoding="utf-8").read()
    sol = json.loads(io.open(os.path.join(R, "scouts", idea, "solution_newc.json"), encoding="utf-8").read())
    sha = hashlib.sha256(io.open(os.path.join(R, "scouts", idea, "solution_newc.json"), "rb").read()).hexdigest()
    print(idea, "| eval:", ev.replace("\n", "").replace(" ", "")[:180])
    print("   n_placements=", len(sol), "unique=", len({tuple(x) for x in sol}),
          "sha=", sha[:20], "ranges_ok=", all(0 <= a <= 97 and 0 <= b <= 531 for a, b in sol))
