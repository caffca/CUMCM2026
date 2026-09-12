# -*- coding: utf-8 -*-
"""REV-Q4-01（CH-REV-B）：输入工件 + 评审证据附件 SHA256 磁盘重算。
输出 reviews/_tmp/rev_q4_01_input_shas.json（供 REV-Q4-CH-R3.json 逐字引用）。
"""
import hashlib, io, json, os, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # tournament dir
WS = os.path.abspath(os.path.join(RUN, "..", "..", ".."))             # workspace root
sys.stdout.reconfigure(encoding="utf-8")
P = "runs/competitive/CS-20260911T071520-D2026/"


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


INPUTS = [
    P + "common_input.json", P + "TOURNAMENT_PROTOCOL.json", P + "ADJUDICATION.json",
    P + "canonical_evaluator.py",
    P + "routes/CH-01.route.json", P + "routes/CH-02.route.json",
    P + "routes/CH-04.route.json", P + "routes/CH-05.route.json",
    "data/canonical_plans.csv",
    P + "scouts/Q4-R11/result.json", P + "scouts/Q4-R11/scout.json",
    P + "scouts/Q4-R11/run/solution_actions.json", P + "scouts/Q4-R11/run/eval_q4.json",
    P + "scouts/Q4-R11/run/r11_layers.json", P + "scouts/Q4-R11/run/q2_inclusion_check.json",
    P + "scouts/Q4-R11/run_q2reduction/solution_q2reduction.json",
    P + "scouts/Q4-R11/run_q2reduction/r11_layers.json",
    P + "scouts/Q4-R11/code/q4common.py", P + "scouts/Q4-R11/code/solve_r11.py",
    P + "scouts/Q4-R41/result.json", P + "scouts/Q4-R41/scout.json",
    P + "scouts/Q4-R41/run/solution_seed11.json", P + "scouts/Q4-R41/run/solution_seed29.json",
    P + "scouts/Q4-R41/run/solution_seed47.json",
    P + "scouts/Q4-R41/run/eval_seed11.json", P + "scouts/Q4-R41/run/eval_seed29.json",
    P + "scouts/Q4-R41/run/eval_seed47.json",
    P + "scouts/Q4-R41/run/sa_record_seed11.json", P + "scouts/Q4-R41/run/sa_record_seed29.json",
    P + "scouts/Q4-R41/run/sa_record_seed47.json",
    P + "scouts/Q4-R41/code/solve_sa.py", P + "scouts/Q4-R41/code/finalize_q4.py",
    P + "scouts/Q4-R22/result.json", P + "scouts/Q4-R22/scout.json",
    P + "scouts/Q4-R22/run/solution_actions.json", P + "scouts/Q4-R22/run/eval_q4.json",
    P + "scouts/Q4-R22/run/r22_log.json", P + "scouts/Q4-R22/code/solve_r22.py",
    P + "scouts/Q2-R51/result.json", P + "scouts/Q2-R51/eval.json",
    P + "scouts/Q2-R51/solution_actions.json",
]
EVID = [
    P + "reviews/rev_q4_01_recheck.py", P + "reviews/rev_q4_01_inclusion.py",
    P + "reviews/rev_q4_01_extra.py", P + "reviews/rev_q4_01_caliber.py",
    P + "reviews/rev_q4_01_edgeaudit.py", P + "reviews/rev_q4_01_detail.py",
    P + "reviews/rev_q4_01_attribution.py", P + "reviews/rev_q4_01_polish.py",
    P + "reviews/rev_q4_01_sentinels.py", P + "reviews/rev_q4_01_shas.py",
    P + "reviews/_tmp/recheck_out.json", P + "reviews/_tmp/recheck_out_B.json",
    P + "reviews/_tmp/recheck_out_C.json", P + "reviews/_tmp/recheck_out_D.json",
    P + "reviews/_tmp/recheck_out_E.json", P + "reviews/_tmp/recheck_out_F.json",
    P + "reviews/_tmp/recheck_out_G.json", P + "reviews/_tmp/recheck_out_H.json",
    P + "reviews/_tmp/recheck_out_I.json",
    P + "reviews/_tmp/B2_greedy_solution.json", P + "reviews/_tmp/B2_eval.json",
    P + "reviews/_tmp/R22_unrevoked.json", P + "reviews/_tmp/R22_unrevoked_eval.json",
    P + "reviews/_tmp/polished_R11.json", P + "reviews/_tmp/polished_R11.json.eval.json",
    P + "reviews/_tmp/sentinel_q4_dg_nonpositive_gap.json",
    P + "reviews/_tmp/sentinel_q4_unknown_plan.json",
    P + "reviews/_tmp/neg_gap_nonpositive.json.out",
    P + "reviews/_tmp/neg_gap_over10.json.out",
    P + "reviews/_tmp/neg_dg_under_q2.out",
]

o = {"inputs": [], "evidence": [], "missing": []}
for rel in INPUTS:
    p = os.path.join(WS, rel.replace("/", os.sep))
    if os.path.isfile(p):
        o["inputs"].append({"path": rel, "sha256": sha(p)})
    else:
        o["missing"].append({"path": rel, "note": "input not found on disk"})
for rel in EVID:
    p = os.path.join(WS, rel.replace("/", os.sep))
    if os.path.isfile(p):
        o["evidence"].append({"path": rel, "sha256": sha(p)})
    else:
        o["missing"].append({"path": rel, "note": "evidence not found on disk"})

io.open(os.path.join(RUN, "reviews", "_tmp", "rev_q4_01_input_shas.json"), "w",
        encoding="utf-8").write(json.dumps(o, ensure_ascii=False, indent=1))
print("inputs:", len(o["inputs"]), " evidence:", len(o["evidence"]),
      " missing:", json.dumps(o["missing"], ensure_ascii=False))
for x in o["inputs"]:
    print(x["sha256"][:16], x["path"].replace(P, ""))
