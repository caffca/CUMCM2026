# -*- coding: utf-8 -*-
"""Canonical Evaluator（Competitive Search 冻结件，Manager 产物）
对 Q1-Q4 的任意候选方案做统一、确定性、可复核的评估。
口径裁定见同目录 ADJUDICATION.json（决策 D-HORIZON-001 / D-Q3-001）。

用法：
  python canonical_evaluator.py --question Q1 --solution pairs.json
      pairs.json: [[id1,id2],...] 冲突对列表
  python canonical_evaluator.py --question Q2 --solution actions.json
      actions.json: {"C004":{"df":-3}, "C010":{"dt":2}, "C013":{"revoke":true}}
      df/dt 为平移量（整数），revoke 表示撤销；每条目至多一个键
  python canonical_evaluator.py --question Q3 --solution newc.json
      newc.json: [[f_lo,t_first_lo],...] 新增C计划起点（宽3/时长2/间隔8/次数12）
  python canonical_evaluator.py --question Q4 --solution actions4.json
      同 Q2 格式，C 条目允许 {"dg":x}（|x|<=10, g'>=1）
输出 JSON：feasible/violations/objective(元组)/direction；退出码 0=评估完成。
"""
import argparse, io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
T_MAX = 643          # 时间视界（既有计划最晚结束，C083: 531+11*10+2）
B_MAX = 100          # 频段数
HERE = os.path.dirname(os.path.abspath(__file__))

def load_plans():
    plans = {}
    path = os.path.join(HERE, "..", "..", "..", "data", "canonical_plans.csv")
    if not os.path.isfile(path):
        path = "data/canonical_plans.csv"
    rd = io.open(path, encoding="utf-8").read().splitlines()
    for line in rd[1:]:
        a = line.split(",")
        plans[a[0]] = dict(id=a[0], cls=a[0][0], f0=int(a[2]), f1=int(a[3]),
                           t0=int(a[4]), t1=int(a[5]), g=int(a[6]), n=int(a[7]),
                           d=int(a[5]) - int(a[4]))
    assert len(plans) == 150
    return plans

def slots_of(p, dt=0, dg=0):
    """全部占用时段；dt 首次时间平移；dg 间隔调整（仅 Q4/C 允许）。"""
    g = p["g"] + dg
    assert g >= 1
    return [(p["t0"] + dt + k * (g + p["d"]), p["t0"] + dt + k * (g + p["d"]) + p["d"])
            for k in range(p["n"])]

def mask_of(p, df=0, dt=0, dg=0):
    m = set()
    f0, f1 = p["f0"] + df, p["f1"] + df
    if f0 < 0 or f1 > B_MAX:
        return None
    for (s, e) in slots_of(p, dt, dg):
        if s < 0 or e > T_MAX:
            return None
        for t in range(s, e):
            for f in range(f0, f1):
                m.add(t * 100 + f)
    return m

def overlap(a, b):
    return max(0, min(a["f1"], b["f1"]) - max(a["f0"], b["f0"])) > 0

def truth_conflicts(plans):
    """基准冲突集（原始计划，无任何调整）。"""
    ids = sorted(plans)
    out = []
    masks = {}
    for i in ids:
        p = plans[i]
        m = set()
        for (s, e) in slots_of(p):
            for t in range(s, e):
                for f in range(p["f0"], p["f1"]):
                    m.add(t * 100 + f)
        masks[i] = m
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            a, b = plans[ids[x]], plans[ids[y]]
            if overlap(a, b) and not masks[ids[x]].isdisjoint(masks[ids[y]]):
                out.append([ids[x], ids[y]])
    return out

def norm_pair(l):
    return tuple(sorted(l))

def eval_q1(plans, sol):
    truth = set(map(tuple, map(sorted, truth_conflicts(plans))))
    got = set(norm_pair(x) for x in sol)
    missing = sorted(truth - got)
    spurious = sorted(got - truth)
    return {"question": "Q1", "feasible": True,
            "objective": [len(missing) + len(spurious)], "direction": "minimize",
            "unit": "symmetric_difference_pairs",
            "counts": {"truth": len(truth), "submitted": len(got),
                       "missing": len(missing), "spurious": len(spurious)},
            "violations": [[f"missing:{a},{b}"] for a, b in missing[:20]] +
                          [[f"spurious:{a},{b}"] for a, b in spurious[:20]]}

def apply_actions(plans, actions, allow_gap=False):
    """返回 (new_plans_mask, kept_stats, violations)。"""
    viol = []
    eff = {}
    for pid, act in actions.items():
        if pid not in plans:
            viol.append(f"unknown_plan:{pid}")
            continue
        keys = [k for k in act if act.get(k) not in (None, False)] if isinstance(act, dict) else []
        if len(keys) == 0:
            viol.append(f"empty_action:{pid}")
            continue
        if len(keys) > 1:
            viol.append(f"multi_param:{pid}:{keys}")
            continue
        k = keys[0]
        if k == "revoke":
            eff[pid] = {"revoke": True}
        elif k in ("df", "dt"):
            if k == "dt" and not allow_gap:
                pass
            if k == "dg" and not allow_gap:
                viol.append(f"gap_not_allowed:{pid}")
                continue
            v = int(act[k])
            lim = {"df": 10, "dt": 5, "dg": 10}[k]
            if abs(v) > lim:
                viol.append(f"magnitude_exceeded:{pid}:{k}:{v}")
            eff[pid] = {k: v}
        elif k == "dg":
            if not allow_gap:
                viol.append(f"gap_not_allowed:{pid}")
                continue
            if plans[pid]["cls"] != "C":
                viol.append(f"gap_only_C:{pid}")
                continue
            v = int(act[k])
            if abs(v) > 10 or plans[pid]["g"] + v < 1:
                viol.append(f"gap_range:{pid}:{v}")
            eff[pid] = {"dg": v}
        else:
            viol.append(f"bad_action_key:{pid}:{k}")
    kept = {pid: p for pid, p in plans.items() if not eff.get(pid, {}).get("revoke")}
    masks = {}
    for pid, p in kept.items():
        a = eff.get(pid, {})
        m = mask_of(p, df=a.get("df", 0), dt=a.get("dt", 0), dg=a.get("dg", 0))
        if m is None:
            viol.append(f"out_of_resource:{pid}")
            continue
        masks[pid] = m
    for ids in [sorted(kept)]:
        for x in range(len(ids)):
            for y in range(x + 1, len(ids)):
                if not masks.get(ids[x], set()).isdisjoint(masks.get(ids[y], set())):
                    viol.append(f"residual_conflict:{ids[x]}:{ids[y]}")
    stats = {"kept": 0, "adjusted": 0, "revoked": len([e for e in eff.values() if e.get("revoke")]),
             "by_class": {}}
    for pid, p in plans.items():
        c = p["cls"]
        st = stats["by_class"].setdefault(c, {"kept": 0, "adjusted": 0, "revoked": 0})
        e = eff.get(pid, {})
        if e.get("revoke"):
            st["revoked"] += 1
        elif e:
            st["adjusted"] += 1
            stats["adjusted"] += 1
        else:
            st["kept"] += 1
            stats["kept"] += 1
    return stats, viol

def objective_tuple(plans, actions, allow_gap=False):
    """题面词典序四级（ADJUDICATION §4）：
    [撤销数, 调整数, 优先级损失(=A类被改数*100+B类被改数*10+C类被改数), 幅度总和]"""
    prio = {"A": 100, "B": 10, "C": 1}
    rev = adj = 0
    ploss = mag = 0
    for pid, act in actions.items():
        if not isinstance(act, dict):
            continue
        c = plans[pid]["cls"]
        if act.get("revoke"):
            rev += 1
            ploss += prio[c] * 2  # 撤销的优先级损失按调整两倍记（同层级内保序）
        else:
            ks = [k for k in ("df", "dt", "dg") if act.get(k)]
            if ks:
                adj += 1
                ploss += prio[c]
                mag += sum(abs(int(act[k])) for k in ks)
    return [rev, adj, ploss, mag]

def eval_q2q4(plans, sol, allow_gap):
    stats, viol = apply_actions(plans, sol, allow_gap=allow_gap)
    feasible = not any(v.startswith("residual_conflict") or v.startswith("out_of_resource")
                       or v.startswith("multi_param") or v.startswith("magnitude_exceeded")
                       or v.startswith("bad_action_key") or v.startswith("unknown_plan")
                       or v.startswith("empty_action")
                       for v in viol)
    if allow_gap:
        for v in viol:
            if v.startswith("gap_not_allowed") or v.startswith("gap_only_C") or v.startswith("gap_range"):
                feasible = False
    obj = objective_tuple(plans, sol, allow_gap)
    return {"question": "Q4" if allow_gap else "Q2", "feasible": feasible,
            "objective": obj, "direction": "lexicographic_minimize",
            "unit": "revoked,adjusted,priority_loss,magnitude_sum",
            "stats": stats, "violations": viol[:200], "n_violations": len(viol)}

def eval_q3(plans, sol, base_actions=None):
    """Q3：基线=Q2 冻结方案（base_actions 提供时应用之），新增C=[f0,t0]列表。
    新增C参数模板：宽3/时长2/间隔8/次数12；全部落 [0,643)×[0,100)。"""
    viol = []
    base = {pid: dict(p) for pid, p in plans.items()}
    for pid, act in (base_actions or {}).items():
        if act.get("revoke"):
            base.pop(pid, None)
    existing = {}
    for pid, p in base.items():
        a = (base_actions or {}).get(pid, {})
        m = mask_of(p, df=int(a.get("df", 0)), dt=int(a.get("dt", 0)))
        if m is None:
            viol.append(f"base_invalid:{pid}")
            continue
        existing[pid] = m
    newm = []
    for idx, item in enumerate(sol):
        f0, t0 = int(item[0]), int(item[1])
        w, d, g, n = 3, 2, 8, 12
        if f0 < 0 or f0 + w > B_MAX or t0 < 0:
            viol.append(f"newc_out_of_bounds:{idx}")
            continue
        m = set()
        ok = True
        for k in range(n):
            s = t0 + k * (g + d)
            if s + d > T_MAX:
                ok = False
                break
            for t in range(s, s + d):
                for f in range(f0, f0 + w):
                    m.add(t * 100 + f)
        if not ok:
            viol.append(f"newc_beyond_horizon:{idx}")
            continue
        for pid, em in existing.items():
            if not m.isdisjoint(em):
                viol.append(f"newc_conflict:{idx}:{pid}")
                break
        for j, (m2, _) in enumerate(newm):
            if not m.isdisjoint(m2):
                viol.append(f"newc_internal:{idx}:{j}")
                break
        newm.append((m, idx))
    feasible = not viol
    return {"question": "Q3", "feasible": feasible,
            "objective": [len(sol)], "direction": "maximize", "unit": "new_C_plans",
            "counts": {"submitted": len(sol), "non_conflicting": len(newm) if feasible else -1},
            "violations": viol[:200], "n_violations": len(viol)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True, choices=["Q1", "Q2", "Q3", "Q4"])
    ap.add_argument("--solution", required=True)
    ap.add_argument("--base-actions", default=None, help="Q3 用：Q2 冻结方案 JSON")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    plans = load_plans()
    sol = json.load(io.open(a.solution, encoding="utf-8"))
    if a.question == "Q1":
        r = eval_q1(plans, sol)
    elif a.question in ("Q2", "Q4"):
        r = eval_q2q4(plans, sol, allow_gap=(a.question == "Q4"))
    else:
        base = json.load(io.open(a.base_actions, encoding="utf-8")) if a.base_actions else {}
        r = eval_q3(plans, sol, base)
    txt = json.dumps(r, ensure_ascii=False, indent=1)
    if a.out:
        io.open(a.out, "w", encoding="utf-8").write(txt)
    print(txt[:2000])

if __name__ == "__main__":
    main()
