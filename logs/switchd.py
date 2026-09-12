# -*- coding: utf-8 -*-
"""切到 run-D（rev4 计划绑定）+ 决策日志登记。"""
import io, json, datetime, py_compile

def sub(path, pairs):
    s = io.open(path, encoding="utf-8").read()
    for a, b in pairs:
        assert a in s, (path, a[:50])
        s = s.replace(a, b)
    io.open(path, "w", encoding="utf-8").write(s)
    py_compile.compile(path, doraise=True)
    print("patched", path)

sub("code/prod/run_prod.py", [('RUN = os.environ.get("DSH_RUN", "FULL-D2026-PROD-C")',
                               'RUN = os.environ.get("DSH_RUN", "FULL-D2026-PROD-D")')])
sub("code/prod/pipeline.py", [('"--run-id", "FULL-D2026-PROD-C"', '"--run-id", "FULL-D2026-PROD-D"')])
sub("code/prod/make_report.py", [("python code/prod/write_results.py --run-id FULL-D2026-PROD-B",
                                  "python code/prod/write_results.py --run-id FULL-D2026-PROD-D")])

d = json.load(io.open("state/decision_log.json", encoding="utf-8"))
d["decisions"].append({
    "id": "D-REV4-RERUN", "stage": "coding_visual",
    "decision": ("判据 revision 4（EV-CRIT-001 criterion_invalid：worker 交叉一致→解级第二实现重算一致；权威解=verified_best）"
                 "使 VALIDATION_PLAN sha 变化 → sharded_run 的 source plan 绑定失配 → 按规则以新 run-id FULL-D2026-PROD-D "
                 "全链重跑 19 任务（FMS/IDEA sha 不变；hint 生效+Q2 权威 rev 预期 6；Q3/Q4 基座随之增强）。"
                 "run-C 的 18 个 attempt 保留在盘上作为修订前证据（不进权威链）。"),
    "reason": "revision 纪律：计划绑定 hash 变化即重跑，禁止新旧混用；同时质量收益大",
    "recorded_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
json.dump(d, io.open("state/decision_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("decision logged")
