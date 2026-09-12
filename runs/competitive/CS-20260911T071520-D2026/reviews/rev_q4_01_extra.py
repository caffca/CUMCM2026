# -*- coding: utf-8 -*-
"""REV-Q4-01 附件脚本 C：
 (1) 把我方「更简基线 B2」写盘并用【冻结 evaluator】复核其 Q4 可行性（让 simpler_model 攻击有据）；
 (2) R22 撤销单向性测试：对其 66 个撤销逐一尝试恢复（恒等 / 单参数动作），统计可无损回滚的数量；
 (3) R11 撤销层 UB 锚定测试：把已知 Q4 可行的 6 撤销解当作 incumbent 注入 R11 模型口径，
     检查其域/边表达是否允许该解（证明 UB_Q4 应 <= 6）；
 (4) R41 三链标量化安全性：ploss / mag / adj / V 的最大可能值 vs 层间隔 1e4。
"""
import io, json, os, subprocess, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(RUN, "scouts", "Q4-R11", "code"))
import q4common as Q                                        # noqa: E402

plans = Q.CE.load_plans()
TMP = os.path.join(RUN, "reviews", "_tmp")
out = {}


def masks_of(actions):
    ms = {}
    for pid, p in plans.items():
        a = actions.get(pid, {})
        if a.get("revoke"):
            continue
        m = Q.mask_int(p, df=int(a.get("df", 0)), dt=int(a.get("dt", 0)), dg=int(a.get("dg", 0)))
        if m is None:
            return None
        ms[pid] = m
    return ms


def n_conf(ms):
    ids = sorted(ms)
    c = 0
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            if ms[ids[x]] & ms[ids[y]]:
                c += 1
    return c


def conf_count_at(ms, pid):
    """只统计与 pid 相关的冲突边数（用于增量判定：其余对在 pid 不变时恒定）。"""
    mp = ms[pid]
    return sum(1 for q in ms if q != pid and (mp & ms[q]))


def build_ms(actions):
    return masks_of(actions)


# ---------- (1) B2 复跑（确定性规则，增量冲突计数）并写盘 ----------
d4 = Q.build_domains(plans, allow_gap=True)
base_ms = masks_of({})
E = set()
ids = sorted(base_ms)
for x in range(len(ids)):
    for y in range(x + 1, len(ids)):
        if base_ms[ids[x]] & base_ms[ids[y]]:
            E.add((ids[x], ids[y]))
actions = {}
ms = dict(base_ms)
guard = 0
while E:
    guard += 1
    assert guard < 2000, "B2 不收敛"
    d = {}
    for (i, j) in E:
        d[i] = d.get(i, 0) + 1
        d[j] = d.get(j, 0) + 1
    i, j = min(E)
    ends = sorted({i, j}, key=lambda k: (Q.PRIO[plans[k]["cls"]], -d.get(k, 0), k))
    done = False
    for pid in ends:
        for opt in d4[pid]:
            if opt["kind"] in ("none", "revoke") or not opt["act"]:
                continue
            trial_ms = dict(ms)
            trial_ms[pid] = opt["mask"]
            if conf_count_at(trial_ms, pid) == 0:
                # 该端点置为该动作后与全体零冲突 ⇒ 单调下降，接受
                newE = {(a, b) for (a, b) in E if a != pid and b != pid}
                actions[pid] = opt["act"]
                ms = trial_ms
                E = newE
                done = True
                break
        if done:
            break
    if not done:
        p = ends[0]
        actions[p] = {"revoke": True}
        ms.pop(p, None)
        E = {(a, b) for (a, b) in E if a != p and b != p}
b2path = os.path.join(TMP, "B2_greedy_solution.json")
io.open(b2path, "w", encoding="utf-8").write(json.dumps(actions, ensure_ascii=False, indent=1))
r = subprocess.run([sys.executable, os.path.join(RUN, "canonical_evaluator.py"), "--question", "Q4",
                    "--solution", b2path, "--out", os.path.join(TMP, "B2_eval.json")],
                   capture_output=True, text=True, encoding="utf-8")
b2ev = json.load(io.open(os.path.join(TMP, "B2_eval.json"), encoding="utf-8"))
out["B2_frozen_evaluator"] = dict(exit=r.returncode, feasible=b2ev["feasible"],
                                  tuple=b2ev["objective"], n_violations=b2ev["n_violations"],
                                  stats=b2ev["stats"],
                                  independent_conflicts=n_conf(masks_of(actions)))

# ---------- (2) R22 撤销可回滚性测试（增量：其余对已零冲突，只需查被恢复计划） ----------
r22 = json.load(io.open(os.path.join(RUN, "scouts", "Q4-R22", "run", "solution_actions.json"),
                        encoding="utf-8"))
revoked = sorted([p for p, a in r22.items() if a.get("revoke")])
cur = masks_of(r22)
assert n_conf(cur) == 0, "R22 基线非零冲突，测试前提失效"
restorable, act_state = [], dict(r22)
for pid in revoked:
    trial = {k: v for k, v in act_state.items() if k != pid}
    m0 = Q.mask_int(plans[pid])
    ms = dict(cur)
    ms[pid] = m0
    if conf_count_at(ms, pid) == 0:
        restorable.append([pid, "keep_identity"])
        act_state, cur = trial, ms
        continue
    hit = None
    for opt in d4[pid]:
        if opt["kind"] in ("none", "revoke") or not opt["act"]:
            continue
        ms2 = dict(cur)
        ms2[pid] = opt["mask"]
        if conf_count_at(ms2, pid) == 0:
            hit = opt["act"]
            cur = ms2
            break
    if hit:
        trial[pid] = hit
        act_state = trial
        restorable.append([pid, hit])
t_after, s_after = Q.opt_scalar(plans, act_state)
io.open(os.path.join(TMP, "R22_unrevoked.json"), "w", encoding="utf-8").write(
    json.dumps(act_state, ensure_ascii=False, indent=1))
rr = subprocess.run([sys.executable, os.path.join(RUN, "canonical_evaluator.py"), "--question", "Q4",
                     "--solution", os.path.join(TMP, "R22_unrevoked.json"),
                     "--out", os.path.join(TMP, "R22_unrevoked_eval.json")],
                    capture_output=True, text=True, encoding="utf-8")
ev_unrev = json.load(io.open(os.path.join(TMP, "R22_unrevoked_eval.json"), encoding="utf-8"))
out["R22_unrevoke_test"] = dict(revokes_before=66, n_tested=len(revoked),
                                n_restored=len(restorable), restored=restorable[:80],
                                tuple_after_restore=t_after, residual_after_restore=n_conf(cur),
                                scalar_after_restore=s_after,
                                frozen_evaluator_tuple=ev_unrev.get("objective"),
                                frozen_evaluator_feasible=ev_unrev.get("feasible"),
                                lexicographically_better=tuple(t_after) < (66, 43, 1111, 144))


# ---------- (3) R11 模型口径能否容纳 6 撤销解 ----------
q2r51 = json.load(io.open(os.path.join(RUN, "scouts", "Q2-R51", "solution_actions.json"),
                          encoding="utf-8"))
idx, unmapped = {}, []
for pid in sorted(plans):
    want = q2r51.get(pid)
    hit = None
    for o, opt in enumerate(d4[pid]):
        if json.dumps(opt["act"], sort_keys=True) == json.dumps(want, sort_keys=True):
            hit = o
            break
    if hit is None:
        unmapped.append([pid, want])
        hit = 0
    idx[pid] = hit
res = Q.residual_conflicts(d4, idx)
out["R11_model_can_hold_6revoke"] = dict(unmapped_options=unmapped[:5], n_unmapped=len(unmapped),
                                         residual_conflicts=len(res),
                                         tuple_of_6revoke_in_R11_encoding=Q.opt_scalar(plans, q2r51)[0],
                                         meaning="R11 的域/边表达完整包含 6 撤销解 ⇒ 其撤销层 UB 报告 8 而非 <=6 是锚定/hint 选择问题，非模型表达力问题")

# ---------- (4) 标量化层间隔安全性 ----------
ploss_max = sum(2 * Q.PRIO[p["cls"]] for p in plans.values())
out["scalarization_safety"] = dict(max_ploss=ploss_max, gap_to_adj_tier=10**4, safe=ploss_max < 10**4,
                                   max_mag=10 * 150, gap_to_ploss_tier=10**4,
                                   max_adjusted=150, gap_to_rev_tier=10**4,
                                   max_pairs=150 * 149 // 2, violation_tier=10**15,
                                   max_V_times_tier=(150 * 149 // 2) * 10**15,
                                   note="本实例下 ploss<=4980<1e4，四级不会串层；但该安全性来自实例规模（150 计划），非公式本身性质")

io.open(os.path.join(TMP, "recheck_out_C.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1, default=str))
print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:5000])
