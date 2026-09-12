# -*- coding: utf-8 -*-
"""REV-Q4-01 附件脚本 D：口径与工件同一性（全部只读；输出写到 reviews/_tmp/）
 - 冻结 evaluator 的 SHA256 是否 == TOURNAMENT_PROTOCOL / ADJUDICATION 绑定值
 - 三候选 code/q4common.py 是否逐字同源（口径共享的直接证据）
 - 候选内 evaluator 绑定字符串与协议 SHA 一致
 - T_MAX=643 数据事实复算（基实例最晚占用结束点）；C083 例算核对
 - 词典序标量 1e12/1e8/1e4 在三候选代码中的实际写法（grep 结果）
 - 全部被审工件 SHA256（供 input_artifact_sha256s 磁盘重算）
"""
import hashlib, io, json, os, re, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS = os.path.abspath(os.path.join(RUN, "..", "..", ".."))     # workspace root
sys.stdout.reconfigure(encoding="utf-8")
out = {}


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


# --- SHA 绑定 ---
ev_sha = sha(os.path.join(RUN, "canonical_evaluator.py"))
proto = json.load(io.open(os.path.join(RUN, "TOURNAMENT_PROTOCOL.json"), encoding="utf-8"))
adj = json.load(io.open(os.path.join(RUN, "ADJUDICATION.json"), encoding="utf-8"))
out["evaluator_sha"] = dict(on_disk=ev_sha, protocol_bound=proto["canonical_evaluator_sha256"],
                            adjudication_bound=adj["evaluator"]["sha256"],
                            matches_all=(ev_sha == proto["canonical_evaluator_sha256"] ==
                                         adj["evaluator"]["sha256"]))
shas = {}
for rel in ["common_input.json", "TOURNAMENT_PROTOCOL.json", "ADJUDICATION.json",
            "canonical_evaluator.py",
            "routes/CH-01.route.json", "routes/CH-02.route.json", "routes/CH-04.route.json",
            "routes/CH-05.route.json",
            "scouts/Q4-R11/result.json", "scouts/Q4-R11/scout.json",
            "scouts/Q4-R11/run/q2_inclusion_check.json", "scouts/Q4-R11/run/r11_layers.json",
            "scouts/Q4-R11/run/solution_actions.json", "scouts/Q4-R11/run/eval_q4.json",
            "scouts/Q4-R11/run_q2reduction/solution_q2reduction.json",
            "scouts/Q4-R11/code/q4common.py", "scouts/Q4-R11/code/solve_r11.py",
            "scouts/Q4-R41/result.json", "scouts/Q4-R41/scout.json",
            "scouts/Q4-R41/run/solution_seed11.json", "scouts/Q4-R41/run/solution_seed29.json",
            "scouts/Q4-R41/run/solution_seed47.json",
            "scouts/Q4-R41/run/eval_seed11.json", "scouts/Q4-R41/run/eval_seed29.json",
            "scouts/Q4-R41/run/eval_seed47.json",
            "scouts/Q4-R41/run/sa_record_seed11.json", "scouts/Q4-R41/run/sa_record_seed29.json",
            "scouts/Q4-R41/run/sa_record_seed47.json",
            "scouts/Q4-R41/code/solve_sa.py", "scouts/Q4-R41/code/q4common.py",
            "scouts/Q4-R22/result.json", "scouts/Q4-R22/scout.json",
            "scouts/Q4-R22/run/solution_actions.json", "scouts/Q4-R22/run/eval_q4.json",
            "scouts/Q4-R22/run/r22_log.json",
            "scouts/Q4-R22/code/solve_r22.py", "scouts/Q4-R22/code/q4common.py",
            "scouts/Q2-R51/solution_actions.json", "scouts/Q2-R51/eval.json",
            "data/canonical_plans.csv"]:
    p = os.path.join(RUN, rel.replace("/", os.sep))
    if not os.path.isfile(p):
        p = os.path.join(os.path.dirname(RUN), "..", rel.replace("/", os.sep))
        p = os.path.abspath(p)
    shas[rel] = sha(p) if os.path.isfile(p) else "MISSING"
out["input_artifact_sha256s"] = shas
out["q4common_identical_across_scouts"] = (
    shas["scouts/Q4-R11/code/q4common.py"] == shas["scouts/Q4-R41/code/q4common.py"] ==
    shas["scouts/Q4-R22/code/q4common.py"])

# --- scout.json 里绑定的 evaluator sha ---
b = {}
for cid in ("Q4-R11", "Q4-R41", "Q4-R22"):
    s = json.load(io.open(os.path.join(RUN, "scouts", cid, "scout.json"), encoding="utf-8"))
    b[cid] = dict(bound=s.get("evaluator_sha256_bound"), matches=(s.get("evaluator_sha256_bound") == ev_sha))
out["scout_evaluator_binding"] = b

# --- 标量公式在各候选代码中的写法 ---
pat = re.compile(r"10\s*\*\*\s*15|10\*\*12|10\s*\*\*\s*12|10\*\*8|1e12|1e8|1e4|10\*\*4")
sc = {}
for rel in ["scouts/Q4-R11/code/q4common.py", "scouts/Q4-R11/code/solve_r11.py",
            "scouts/Q4-R41/code/solve_sa.py", "scouts/Q4-R22/code/solve_r22.py"]:
    txt = io.open(os.path.join(RUN, rel.replace("/", os.sep)), encoding="utf-8").read()
    sc[rel] = sorted({m.group(0) for m in pat.finditer(txt)})
out["scalar_literals_in_code"] = sc

# --- 643 数据事实 ---
lines = io.open(os.path.join(WS, "data", "canonical_plans.csv"),
                encoding="utf-8").read().splitlines()
mx, mx_id, c083 = -1, None, None
for line in lines[1:]:
    a = line.split(",")
    f0, f1, t0, t1, g, n = int(a[2]), int(a[3]), int(a[4]), int(a[5]), int(a[6]), int(a[7])
    d = t1 - t0
    last = t0 + (n - 1) * (g + d) + d
    if last > mx:
        mx, mx_id = last, a[0]
    if a[0] == "C083":
        c083 = dict(t0=t0, t1=t1, g=g, n=n, d=d, last_end=last)
out["horizon_fact"] = dict(max_base_last_end=mx, argmax=mx_id, evaluator_T_MAX=643,
                           c083=c083, adjudication_R1_consistent=(mx == 643))
# 基实例是否有任何计划原始占用越 643
over = []
for line in lines[1:]:
    a = line.split(",")
    t0, t1, g, n = int(a[4]), int(a[5]), int(a[6]), int(a[7])
    d = t1 - t0
    if t0 + (n - 1) * (g + d) + d > 643:
        over.append(a[0])
out["horizon_fact"]["base_plans_beyond_643"] = over

io.open(os.path.join(RUN, "reviews", "_tmp", "recheck_out_D.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "input_artifact_sha256s"},
                 ensure_ascii=False, indent=1))

