# -*- coding: utf-8 -*-
"""REV-Q4-01 附件脚本 G：两项归因测试
 G1. R22 空条带边 C033|C043：『R3 视界截断所致』这一因果归因是否成立
     —— 放开 643 视界（只看 g'>=1 与 |dg|<=10）重算可分离性。
 G2. R22 阶段 II 收缩规则里 (kind_rank, mag) 的偏序把 df/dt 排在 dg 之前：
     对最终解里每个被调整的计划，检验是否存在「更大幅度的任意合法动作」能保持零冲突
     ⇒ 若存在，则交付解的第四级（Σ|δ|）被非规范偏序抬高，属实现自伤而非题面极限。
"""
import io, json, os, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(RUN, "scouts", "Q4-R11", "code"))
import q4common as Q                                        # noqa: E402
sys.stdout.reconfigure(encoding="utf-8")
T_MAX_H, B_MAX = 643, 100
plans = Q.CE.load_plans()
out = {}


def mask_unbounded(p, df=0, dt=0, dg=0):
    """只保留 |df|<=10/|dt|<=5/|dg|<=10、g'>=1、频段界内；时间视界放开到 +inf。"""
    gp = p["g"] + dg
    if gp < 1 or abs(df) > 10 or abs(dt) > 5 or abs(dg) > 10:
        return None
    f0, f1 = p["f0"] + df, p["f1"] + df
    if f0 < 0 or f1 > B_MAX:
        return None
    m = 0
    for k in range(p["n"]):
        s = p["t0"] + dt + k * (gp + p["d"])
        for t in range(s, s + p["d"]):
            for f in range(f0, f1):
                m |= 1 << (t * B_MAX + f)
    return m


# ---------------- G1 ----------------
# 注意：合法 dg 域本身要求 g'=g+dg>=1（evaluator slots_of 对 g'<=0 直接 assert 崩溃，
#       这是冻结件对『负例』的唯一反应方式，见 neg_gap_nonpositive 测试）。
i, j = "C033", "C043"
feas_trunc, feas_open = [], []
for di in range(-10, 11):
    if plans[i]["g"] + di < 1:
        continue
    for dj in range(-10, 11):
        if plans[j]["g"] + dj < 1:
            continue
        mi_t = Q.mask_int(plans[i], dg=di)
        mj_t = Q.mask_int(plans[j], dg=dj)
        if mi_t is not None and mj_t is not None and not (mi_t & mj_t):
            feas_trunc.append((di, dj))
        mi_o = mask_unbounded(plans[i], dg=di)
        mj_o = mask_unbounded(plans[j], dg=dj)
        if mi_o is not None and mj_o is not None and not (mi_o & mj_o):
            feas_open.append((di, dj))
band = min(plans[i]["f1"], plans[j]["f1"]) - max(plans[i]["f0"], plans[j]["f0"])
out["G1_empty_strip_attribution"] = dict(
    edge=[i, j], band_overlap=band, t0=(plans[i]["t0"], plans[j]["t0"]),
    delta_t1=plans[i]["t0"] - plans[j]["t0"],
    feasible_dg_pairs_with_643=feas_trunc,
    feasible_dg_pairs_without_horizon=feas_open,
    claim="无任何 (g'_i,g'_j) 组合可消解（R3 视界截断所致）",
    empty_under_643=len(feas_trunc) == 0,
    empty_without_horizon=len(feas_open) == 0,
    verdict=("归因错误" if len(feas_trunc) == 0 and len(feas_open) > 0 else
             "归因成立（与视界无关，是同余/带宽结构本身）"))
# 若放开视界后仍空，再检验：允许 df/dt（题面在 Q4 也允许）能否分离该边
feas_shift = []
for di in range(-10, 11):
    for key, lim in (("df", 10), ("dt", 5)):
        for v in range(-lim, lim + 1):
            if v == 0:
                continue
            a = {key: v}
            mi = Q.mask_int(plans[i], **a)
            if mi is None:
                continue
            for dj in range(-10, 11):
                for key2, lim2 in (("df", 10), ("dt", 5)):
                    for v2 in range(-lim2, lim2 + 1):
                        if v2 == 0:
                            continue
                        mj = Q.mask_int(plans[j], **{key2: v2})
                        if mj is not None and not (mi & mj):
                            feas_shift.append((f"{key}:{v}", f"{key2}:{v2}"))
        if feas_shift:
            break
    if feas_shift:
        break
out["G1_empty_strip_attribution"]["separable_by_df_dt_sample"] = feas_shift[:4]

# ---------------- G2 ----------------
d4 = Q.build_domains(plans, allow_gap=True)
sol = json.load(io.open(os.path.join(RUN, "scouts", "Q4-R22", "run", "solution_actions.json"),
                        encoding="utf-8"))


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


ms = masks_of(sol)
assert ms and n_conf(ms) == 0
found = []
for pid, a in sorted(sol.items()):
    if a.get("revoke"):
        continue
    cur_mag = sum(abs(int(v)) for k, v in a.items())
    for opt in d4[pid]:
        if opt["kind"] in ("none", "revoke") or not opt["act"]:
            continue
        if opt["mag"] >= cur_mag:
            continue
        trial = dict(sol)
        trial[pid] = opt["act"]
        m2 = masks_of(trial)
        if m2 is not None and n_conf(m2) == 0:
            found.append(dict(plan=pid, current=a, better=opt["act"], cur_mag=cur_mag,
                              new_mag=opt["mag"], kind=opt["kind"], cls=plans[pid]["cls"]))
            break
t_before, s_before = Q.opt_scalar(plans, sol)
cur = dict(sol)
for f in found:
    cur[f["plan"]] = f["better"]
t_after, s_after = Q.opt_scalar(plans, cur)
out["G2_shrink_kind_preference"] = dict(
    n_adjusted_plans=sum(1 for a in sol.values() if not a.get("revoke")),
    n_improvable_same_pass=len(found), first_examples=found[:8],
    tuple_before=t_before, tuple_after=t_after,
    mag_reduction=t_before[3] - t_after[3],
    lexicographically_better=tuple(t_after) < tuple(t_before),
    note=("R22 收缩偏序 (df<dt<dg, |v|) 不是题面第四级（Σ|δ| 与动作类型无关）；"
          "上表证明存在保持零冲突的更小幅度动作 ⇒ 交付解的幅度层被实现规则抬高。"))

io.open(os.path.join(RUN, "reviews", "_tmp", "recheck_out_G.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1, default=str))
print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:5000])
