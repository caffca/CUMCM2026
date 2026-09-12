# -*- coding: utf-8 -*-
"""Q4 共享构件（Prototype Engineer Q4 组，三候选同源复用）。
与冻结件 canonical_evaluator.py 逐字对齐：
  - 计划数据直接复用 evaluator.load_plans（data/canonical_plans.csv）
  - 掩码合法性判据复用 evaluator.mask_of 的边界规则（频段 [0,100]、时间 [0,643]）
  - 目标口径 = evaluator.objective_tuple（ADJUDICATION R4/R6）：
      [撤销数, 调整数, 优先级损失(撤销×2), 幅度Σ|δ|]
  - 词典序标量 = TOURNAMENT_PROTOCOL.objective_scalar
      1e12*rev + 1e8*adj + 1e4*ploss + mag
选项域（协议/任务冻结）：{恒等} ∪ {df:0<|df|<=10} ∪ {dt:0<|dt|<=5}
  ∪（仅 C，allow_gap）{dg:0<|dg|<=10, g+dg>=1} ∪ {撤销}；
  任何使 slot 越出 [0,643) 或频段越出 [0,100) 的选项为无效动作（R3 约束），直接剔除。
"""
import io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOURN_DIR = os.path.abspath(os.path.join(HERE, "..", "..", ".."))  # scouts/<id>/code -> 上3级 = tournament 目录
if TOURN_DIR not in sys.path:
    sys.path.insert(0, TOURN_DIR)
LIB_DIR = r"F:\dsh_envlibs\mathmodel"
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

import canonical_evaluator as CE  # 冻结件，只读 import

T_MAX, B_MAX = CE.T_MAX, CE.B_MAX
PRIO = {"A": 100, "B": 10, "C": 1}


def mask_int(p, df=0, dt=0, dg=0):
    """占用格集 int 位图（t*100+f 位）。越界 → None（与 CE.mask_of 同判据）。"""
    s = CE.mask_of(p, df=df, dt=dt, dg=dg)
    if s is None:
        return None
    m = 0
    for cell in s:
        m |= 1 << cell
    return m


def build_domains(plans, allow_gap=True):
    """返回 domains: pid -> list of option dicts。
    option: {"kind": one of none/df/dt/dg/revoke, "v": int, "mask": int|None(撤销为 None=空占用),
             "rev":0/1, "adj":0/1, "ploss":int, "mag":int, "act": json动作(dict或None)}
    顺序确定性：none, df(±1..±10 按 |v|升, 负先), dt(±1..±5 同), dg(±1..±10 同, 仅C), revoke 末位。
    """
    doms = {}
    for pid, p in sorted(plans.items()):
        opts = []
        m0 = mask_int(p)
        assert m0 is not None, f"基础计划越界？{pid}"
        opts.append(dict(kind="none", v=0, mask=m0, rev=0, adj=0, ploss=0, mag=0, act=None))
        for key, lim in (("df", 10), ("dt", 5)):
            for a in range(1, lim + 1):
                for v in (-a, a):
                    kw = {key: v}
                    m = mask_int(p, **kw)
                    if m is not None:
                        opts.append(dict(kind=key, v=v, mask=m, rev=0, adj=1,
                                         ploss=PRIO[p["cls"]], mag=abs(v), act={key: v}))
        if allow_gap and p["cls"] == "C":
            for a in range(1, 11):
                for v in (-a, a):
                    if p["g"] + v < 1:
                        continue
                    m = mask_int(p, dg=v)
                    if m is not None:
                        opts.append(dict(kind="dg", v=v, mask=m, rev=0, adj=1,
                                         ploss=PRIO[p["cls"]], mag=abs(v), act={"dg": v}))
        opts.append(dict(kind="revoke", v=0, mask=0, rev=1, adj=0,
                         ploss=2 * PRIO[p["cls"]], mag=0, act={"revoke": True}))
        doms[pid] = opts
    return doms


def bbox(mask):
    """位图的时间/频段包络 (fmin,fmax,tmin,tmax)（mask=0 → None）。"""
    if not mask:
        return None
    lo = (mask & -mask).bit_length() - 1
    hi = mask.bit_length() - 1
    return (lo % B_MAX, hi % B_MAX, lo // B_MAX, hi // B_MAX)


def build_edges(plans, doms):
    """势冲突边：存在一对非撤销选项掩码相交的计划对。
    返回 edges: [(i,j)], forb[(i,j)] = dict o1 -> frozenset(o2)（互斥选项对，两侧对称）。
    """
    ids = sorted(plans)
    n = len(ids)
    # 每选项包络（撤销选项 mask=0 -> bbox None 不参与）
    ob = {pid: [bbox(o["mask"]) if o["mask"] else None for o in doms[pid]] for pid in ids}
    # 计划级包络过滤（频段+时间粗筛）
    def plan_box(pid):
        bs = [b for b in ob[pid] if b is not None]
        return (min(b[0] for b in bs), max(b[1] for b in bs),
                min(b[2] for b in bs), max(b[3] for b in bs))
    pb = {pid: plan_box(pid) for pid in ids}
    edges, forb = [], {}
    msk = {pid: [o["mask"] for o in doms[pid]] for pid in ids}
    for x in range(n):
        i = ids[x]
        fi0, fi1, ti0, ti1 = pb[i]
        for y in range(x + 1, n):
            j = ids[y]
            fj0, fj1, tj0, tj1 = pb[j]
            if fi0 > fj1 or fj0 > fi1 or ti0 > tj1 or tj0 > ti1:
                continue
            # 选项对精判（先选项级包络）
            fi = {}
            any_pair = False
            for o1, b1 in enumerate(ob[i]):
                if b1 is None:
                    continue
                for o2, b2 in enumerate(ob[j]):
                    if b2 is None:
                        continue
                    if b1[0] > b2[1] or b2[0] > b1[1] or b1[2] > b2[3] or b2[2] > b1[3]:
                        continue
                    if msk[i][o1] & msk[j][o2]:
                        fi.setdefault(o1, []).append(o2)
                        any_pair = True
            if any_pair:
                edges.append((i, j))
                f = {o1: frozenset(o2s) for o1, o2s in fi.items()}
                g = {}
                for o1, o2s in f.items():
                    for o2 in o2s:
                        g.setdefault(o2, []).append(o1)
                forb[(i, j)] = (f, {o2: frozenset(v) for o2, v in g.items()})
    return edges, forb


def base_conflict_set(plans):
    """原始冲突集（evaluator truth_conflicts，int 位图重算一致后返回 sorted list）。"""
    truth = set(tuple(sorted(l)) for l in CE.truth_conflicts(plans))
    ids = sorted(plans)
    m0 = {pid: mask_int(plans[pid]) for pid in ids}
    mine = set()
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            if m0[ids[x]] & m0[ids[y]]:
                mine.add((ids[x], ids[y]))
    assert mine == truth, "位图重算与 evaluator truth 不一致"
    return sorted(mine)


def state_masks(doms, opt_idx):
    return {pid: doms[pid][opt_idx[pid]]["mask"] for pid in doms}


def residual_conflicts(doms, opt_idx):
    ms = state_masks(doms, opt_idx)
    ids = sorted(doms)
    out = []
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            if ms[ids[x]] and ms[ids[y]] and (ms[ids[x]] & ms[ids[y]]):
                out.append((ids[x], ids[y]))
    return out


def actions_from_state(doms, opt_idx):
    sol = {}
    for pid in sorted(doms):
        a = doms[pid][opt_idx[pid]]["act"]
        if a:
            sol[pid] = a
    return sol


def opt_scalar(plans, actions):
    obj = CE.objective_tuple(plans, actions, allow_gap=True)
    return obj, obj[0] * 10**12 + obj[1] * 10**8 + obj[2] * 10**4 + obj[3]


def load_all(allow_gap=True):
    plans = CE.load_plans()
    doms = build_domains(plans, allow_gap=allow_gap)
    edges, forb = build_edges(plans, doms)
    return plans, doms, edges, forb
