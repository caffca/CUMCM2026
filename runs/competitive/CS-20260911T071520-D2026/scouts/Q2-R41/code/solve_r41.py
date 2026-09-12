# -*- coding: utf-8 -*-
"""Q2-R41 baseline 路线（Prototype Engineer 侦察实现：冲突图 GRASP + 局部搜索/ILS）

口径：ADJUDICATION.json（T_MAX=643、半开区间、词典序四级、单参数/撤销语义）。
结构事实（code/q2_common.py 复算，掩码语义与 canonical_evaluator 一致；权威值仍以 evaluator 为准）：
  原冲突边 297；全势冲突边 G* = 1693（动作邻域内仍可能同格共占的计划对）。
  可行性判据在 G* 上维护：非 G* 的任何计划对在任意合法动作下都不可能共占
  ⇒ "G* 残留边 = 0" ⇔ evaluator 的 residual_conflict 为空；输出前再做掩码全量复核。

算法（随机路线，冻结 seeds=[11,29,47]，每重复独立墙钟预算，协议取中位数）：
  构造（冲突导向修复贪心）：每步从残留冲突边采样 4 条，枚举其端点全部可行动作（含撤销），
    只保留"严格减少残留边数"的动作，打分 = Δ残留×W_RES + Δ词典序代价标量
    （W_RES=1e6 ≪ 撤销权重 1e12 ⇒ 只要调整能减冲突就绝不先撤销；CH-04 route 的
    "贪心易过早撤销"教训被显式写进打分函数），取 RCL(top α) 随机执行；
    连续 20 步无单边改进 ⇒ 撤销该边类别优先级较低的一端（保证终止）。
  LS1 去撤销：被撤销计划按代价升序试前 10 个动作 + 有界修复，元组严格变好才接受（层1 主导）；
  LS2 缩幅/去调整：被调整计划换更便宜动作，要求不增加残留边；
  LS3 负担转移：A/B 类被调计划换恒等，冲突由低优先级邻居吸收（protect 自身）；
  ILS：局部最优后随机扰动 2-6 个计划 → 再消解 → 再 LS；全程保留最优元组。
参数（α、采样数、W_RES、修复步数、扰动规模）在跑实验前冻结，随 record 落盘；不看结果调参。
"""
import argparse
import io
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import q2_common as Q  # noqa: E402

W_RES, W_REV, W_ADJ, W_PRI = 1e6, 1e12, 1e8, 1e4
PARAMS = {"alpha_construct": 0.35, "alpha_ils": 0.5, "edge_sample": 4,
          "topk_per_endpoint": 8, "repair_max_moves": 8, "ls1_topact": 12,
          "stall_limit": 20, "ils_perturb": [2, 3, 4, 6], "W_RES": W_RES,
          "lns_rounds_per_start": 6, "lns_unrevoke_prob": 0.75, "lns_unrevoke_max": 6,
          "max_construct_iters": 8000}


# ------------------------------------------------------------------ 实例
def load_instance(edge_cache=None):
    plans = Q.load_plans()
    ids, acts, masks = Q.build_action_tables(plans)
    if edge_cache and os.path.isfile(edge_cache):
        raw = json.load(io.open(edge_cache, encoding="utf-8"))
        edges = {tuple(k.split("|")): [tuple(v) for v in vv] for k, vv in raw["edges"].items()}
        stats = raw["stats"]
    else:
        edges, stats = Q.build_star_edges(plans, acts, masks, verify=False)
    E = {k: set(ai * 64 + aj for (ai, aj) in v) for k, v in edges.items()}
    adj = {i: [] for i in ids}
    for (i, j) in E:
        adj[i].append(j)
        adj[j].append(i)
    cost = {i: [Q.act_cost(plans[i]["cls"], a) for a in acts[i]] for i in ids}
    kind = {i: [a[0] for a in acts[i]] for i in ids}
    nact = {i: len(acts[i]) for i in ids}
    order = {i: sorted(range(nact[i]), key=lambda a: (cost[i][a][1], cost[i][a][2], cost[i][a][3]))
             for i in ids}
    return dict(plans=plans, ids=ids, acts=acts, masks=masks, E=E, adj=adj, cost=cost,
                kind=kind, nact=nact, order=order, stats=stats,
                rev={i: nact[i] - 1 for i in ids}, cls={i: plans[i]["cls"] for i in ids})


# ------------------------------------------------------------------ 状态
class Sol(object):
    __slots__ = ("ins", "choice", "bad", "tup")

    def __init__(self, ins, choice=None):
        self.ins = ins
        ch = self.choice = dict(choice) if choice is not None else {i: 0 for i in ins["ids"]}
        E = ins["E"]
        self.bad = set(k for k in E if (ch[k[0]] * 64 + ch[k[1]]) in E[k])
        c = ins["cost"]
        self.tup = [sum(c[i][ch[i]][x] for i in ins["ids"]) for x in range(4)]

    def copy(self):
        s = Sol.__new__(Sol)
        s.ins = self.ins
        s.choice = dict(self.choice)
        s.bad = set(self.bad)
        s.tup = list(self.tup)
        return s

    def absorb(self, other):
        self.choice = dict(other.choice)
        self.bad = set(other.bad)
        self.tup = list(other.tup)

    def d_res(self, i, a):
        """计划 i 改用动作 a 后，G* 残留边数的变化（只扫 i 的邻居 ⇒ O(deg)）。"""
        if self.ins["kind"][i][a] == "revoke":
            return -sum(1 for j in self.ins["adj"][i] if self._key(i, j) in self.bad)
        ins, ch, E = self.ins, self.choice, self.ins["E"]
        d = 0
        for j in ins["adj"][i]:
            key = (i, j) if i < j else (j, i)
            ci = a if key[0] == i else ch[key[0]]
            cj = a if key[1] == i else ch[key[1]]
            now = (ci * 64 + cj) in E[key]
            was = key in self.bad
            if was and not now:
                d -= 1
            elif now and not was:
                d += 1
        return d

    @staticmethod
    def _key(i, j):
        return (i, j) if i < j else (j, i)

    def score_move(self, i, a):
        ins, ch = self.ins, self.choice
        d = self.d_res(i, a)
        c = ins["cost"][i]
        dc = tuple(c[a][x] - c[ch[i]][x] for x in range(4))
        return d, dc, d * W_RES + dc[0] * W_REV + dc[1] * W_ADJ + dc[2] * W_PRI + dc[3]

    def apply(self, i, a):
        ins, ch, E = self.ins, self.choice, self.ins["E"]
        old = ch[i]
        if old == a:
            return
        for j in ins["adj"][i]:
            key = (i, j) if i < j else (j, i)
            p, q = key
            ci = a if p == i else ch[p]
            cj = a if q == i else ch[q]
            if (ci * 64 + cj) in E[key]:
                self.bad.add(key)
            else:
                self.bad.discard(key)
        ch[i] = a
        c = ins["cost"][i]
        for x in range(4):
            self.tup[x] += c[a][x] - c[old][x]


# ------------------------------------------------------------------ 贪心构造 / 修复
def edge_candidates(st, key, topk=None):
    """一条残留边的修复候选：两端各取"与该边对端当前动作相容、按动作代价升序的前 topk 个"。
    相容 ⇒ 本边必被修好；撤销恒相容且代价最贵 ⇒ 只有调整都不可行时才轮到它（防过早撤销）。
    这是对"枚举端点全部动作"的等价加速：被跳过的只是更贵且同样能修好本边的动作。"""
    topk = topk or PARAMS["topk_per_endpoint"]
    ins, ch, E = st.ins, st.choice, st.ins["E"]
    i, j = key
    s_ij = E[key]
    out = []
    for v, w in ((i, j), (j, i)):
        cw = ch[w]
        got = 0
        for a in ins["order"][v]:
            if a == ch[v]:
                continue
            ci = a if key[0] == v else ch[key[0]]
            cj = a if key[1] == v else ch[key[1]]
            if (ci * 64 + cj) in s_ij:
                continue
            d, dc, sc = st.score_move(v, a)
            if d < 0:
                out.append((sc, dc[0], dc[1], dc[2], dc[3], v, a))
                got += 1
                if got >= topk:
                    break
    out.sort()
    return out


def edge_joint(st, key, topk=3):
    """双边逃生口：两端同时换动作（单边无严格改进动作时用）。"""
    ins, ch, E = st.ins, st.choice, st.ins["E"]
    i, j = key
    s_ij = E[key]
    out = []
    for a in ins["order"][i][:topk]:
        for b in ins["order"][j][:topk]:
            if a == ch[i] and b == ch[j]:
                continue
            if (a * 64 + b) in s_ij:
                continue
            d = st.d_res_pair(i, a, j, b)
            if d >= 0:
                continue
            c = ins["cost"]
            dc = tuple(c[i][a][x] + c[j][b][x] - c[i][ch[i]][x] - c[j][ch[j]][x]
                       for x in range(4))
            sc = d * W_RES + dc[0] * W_REV + dc[1] * W_ADJ + dc[2] * W_PRI + dc[3]
            out.append((sc, dc[0], dc[1], dc[2], dc[3], i, a, j, b))
    out.sort()
    return out


def _rcl(rng, cands, alpha):
    n = max(1, int(round(alpha * len(cands))))
    return rng.choice(cands[:n]) if len(cands) > 1 and rng.random() < 0.4 else cands[0]


def _do(st, mv):
    st.apply(mv[5], mv[6])
    if len(mv) > 7:
        st.apply(mv[7], mv[8])


def descend(st, rng, deadline, alpha):
    """冲突导向下降：每步执行一个"严格减残留"动作；停滞则撤销类别优先级较低的一端兜底。"""
    ins = st.ins
    stall, it = 0, 0
    while st.bad:
        it += 1
        if it > PARAMS["max_construct_iters"]:
            return False
        if time.time() > deadline:
            return False
        keys = rng.sample(list(st.bad), min(PARAMS["edge_sample"], len(st.bad)))
        cands = []
        for key in keys:
            cands.extend(edge_candidates(st, key))
        if cands:
            cands.sort()
            _do(st, _rcl(rng, cands, alpha))
            stall = 0
            continue
        cands = []
        for key in keys:
            cands.extend(edge_joint(st, key))
        if cands:
            cands.sort()
            _do(st, cands[0])
            stall = 0
            continue
        stall += 1
        if stall >= PARAMS["stall_limit"]:
            (i, j) = rng.choice(list(st.bad))
            v = i if Q.PRIO[ins["cls"][i]] <= Q.PRIO[ins["cls"][j]] else j
            st.apply(v, ins["rev"][v])
            stall = 0
    return True


def repair(st, rng, deadline, max_moves=None, protect=frozenset()):
    max_moves = max_moves or PARAMS["repair_max_moves"]
    for _ in range(max_moves):
        if not st.bad:
            return True
        if time.time() > deadline:
            return False
        keys = rng.sample(list(st.bad), min(4, len(st.bad)))
        cands = [c for c in sum((edge_candidates(st, k) for k in keys), [])
                 if c[5] not in protect]
        if not cands:
            cands = [c for c in sum((edge_joint(st, k) for k in keys), [])
                     if c[5] not in protect and c[7] not in protect]
        if not cands:
            return False
        cands.sort()
        _do(st, cands[0])
    return not st.bad


# ------------------------------------------------------------------ 局部搜索
def local_search(st, rng, deadline):
    ins = st.ins
    improved = True
    while improved:
        if time.time() > deadline:
            break
        improved = False
        # LS1 去撤销
        revs = [i for i in ins["ids"] if ins["kind"][i][st.choice[i]] == "revoke"]
        revs.sort(key=lambda i: -sum(1 for j in ins["adj"][i] if Sol._key(i, j) in st.bad))
        for i in revs:
            if time.time() > deadline:
                break
            base = st.copy()
            best_alt, best_tup = None, None
            for a in ins["order"][i][:PARAMS["ls1_topact"]]:
                # order 按 (调整,优先级,幅度) 升序：前若干已覆盖"最可能改善元组"的动作
                trial = st.copy()
                trial.apply(i, a)
                if trial.bad and not repair(trial, rng, deadline, max_moves=4):
                    continue
                if trial.bad:
                    continue
                if best_tup is None or trial.tup < best_tup:
                    best_alt, best_tup = trial, list(trial.tup)
            if best_alt is not None and best_tup < base.tup:
                st.absorb(best_alt)
                improved = True
        # LS2 缩幅 / 去调整（不增加残留边）
        for i in ins["ids"]:
            if time.time() > deadline:
                break
            cur = st.choice[i]
            if ins["kind"][i][cur] in ("keep", "revoke"):
                continue
            cc = ins["cost"][i][cur]
            best = None
            for a in ins["order"][i]:
                ca = ins["cost"][i][a]
                if (ca[1], ca[2], ca[3]) >= (cc[1], cc[2], cc[3]):
                    break
                if a == cur or ins["kind"][i][a] == "revoke":
                    continue
                if st.d_res(i, a) <= 0 and (best is None or (ca[1], ca[2], ca[3]) < best[0]):
                    best = ((ca[1], ca[2], ca[3]), a)
            if best:
                st.apply(i, best[1])
                improved = True
        # LS3 负担转移：A/B 被调 → 恒等，由邻居吸收
        hi = [i for i in ins["ids"] if Q.PRIO[ins["cls"][i]] >= 10
              and ins["kind"][i][st.choice[i]] != "keep"]
        hi.sort(key=lambda x: -Q.PRIO[ins["cls"][x]])
        for i in hi:
            if time.time() > deadline:
                break
            base = st.copy()
            trial = st.copy()
            trial.apply(i, 0)
            if not trial.bad:
                if trial.tup < base.tup:
                    st.absorb(trial)
                    improved = True
                continue
            if repair(trial, rng, deadline, max_moves=3, protect={i}) and trial.tup < base.tup:
                st.absorb(trial)
                improved = True
    return st


def perturb(st, rng, k):
    ins = st.ins
    for _ in range(k):
        v = rng.choice(ins["ids"])
        st.apply(v, rng.randrange(ins["nact"][v]))


# ------------------------------------------------------------------ LNS / 单种子
def lnns_round(st, rng, deadline, best):
    """Large-neighborhood：成批"去撤销"（层1 主导）或随机破坏，再重新消解 + LS。"""
    ins = st.ins
    revs = [i for i in ins["ids"] if ins["kind"][i][st.choice[i]] == "revoke"]
    trial = st.copy()
    if revs and rng.random() < PARAMS["lns_unrevoke_prob"]:
        k = rng.randint(1, min(len(revs), PARAMS["lns_unrevoke_max"]))
        # 优先释放"撤销代价最高"（A/B 类）的计划：层3 与层1 同向改善
        revs.sort(key=lambda i: (-Q.PRIO[ins["cls"][i]], i))
        pool = revs[:max(k, int(0.6 * len(revs)))]
        for i in rng.sample(pool, min(k, len(pool))):
            trial.apply(i, 0)
    else:
        perturb(trial, rng, rng.choice(PARAMS["ils_perturb"]))
    if not descend(trial, rng, deadline, PARAMS["alpha_ils"]):
        return None
    local_search(trial, rng, deadline)
    if trial.bad:
        return None
    return trial


def solve_seed(seed, budget, ins, log):
    rng = random.Random(seed)
    t0 = time.time()
    deadline = t0 + budget
    best, starts, fails, hist = None, 0, 0, []
    while time.time() < deadline:
        starts += 1
        st = Sol(ins)
        if not descend(st, rng, deadline - 2, PARAMS["alpha_construct"]):
            fails += 1
            continue
        local_search(st, rng, deadline)
        if st.bad:
            fails += 1
            continue
        if best is None or st.tup < best[0]:
            best = (list(st.tup), dict(st.choice))
            hist.append({"t": round(time.time() - t0, 1), "start": starts, "tuple": list(st.tup)})
            log("seed=%s start=%d tuple=%s" % (seed, starts, st.tup))
        # 从当前最优出发做若干 LNS 轮（层1 主攻方向）
        cur = Sol(ins, best[1])
        for _lns in range(PARAMS["lns_rounds_per_start"]):
            if time.time() > deadline:
                break
            trial = lnns_round(cur, rng, deadline, best)
            if trial is None:
                continue
            if trial.tup < best[0]:
                best = (list(trial.tup), dict(trial.choice))
                cur = Sol(ins, best[1])
                hist.append({"t": round(time.time() - t0, 1), "start": starts,
                             "tuple": list(trial.tup), "lns": True})
                log("seed=%s LNS tuple=%s" % (seed, trial.tup))
            elif trial.tup == cur.tup:
                cur = trial
    rec = {"seed": seed, "budget_s": budget, "wall_s": round(time.time() - t0, 2),
           "starts": starts, "failed_descents": fails, "history": hist[-40:], "params": PARAMS}
    if best is None:
        rec["failure"] = "no_feasible_within_budget"
        return None, rec
    rec["tuple"] = best[0]
    return best, rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=190.0, help="每重复墙钟秒（协议 ≤600）")
    ap.add_argument("--seeds", default="11,29,47")
    ap.add_argument("--out-dir", default=os.path.abspath(os.path.join(HERE, "..")))
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    logf = io.open(os.path.join(a.out_dir, "grasp_log.txt"), "w", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        logf.write(msg + "\n")
        logf.flush()

    ins = load_instance(os.path.join(HERE, "star_edges.json"))
    log("instance: star_edges=%d combos=%d" % (ins["stats"]["star_edges"],
                                               ins["stats"]["infeasible_combos"]))
    summary = {}
    for s in [int(x) for x in a.seeds.split(",")]:
        best, rec = solve_seed(s, a.budget, ins, log)
        if best:
            sol = Q.solution_from_choice(ins["plans"], ins["acts"], best[1])
            resid = Q.residual_pairs(ins["plans"], ins["acts"], ins["masks"], best[1])
            json.dump(sol, io.open(os.path.join(a.out_dir, "solution_actions_seed%d.json" % s),
                                   "w", encoding="utf-8"), ensure_ascii=False, indent=1,
                      sort_keys=True)
            rec.update(internal_residual_full_mask=len(resid),
                       internal_objective_tuple=list(best[0]), n_listed=len(sol),
                       objective_scalar_internal=Q.scalarize(best[0]))
        json.dump(rec, io.open(os.path.join(a.out_dir, "grasp_record_seed%d.json" % s), "w",
                               encoding="utf-8"), ensure_ascii=False, indent=1)
        summary[str(s)] = {"tuple": rec.get("tuple"), "wall_s": rec["wall_s"],
                           "starts": rec["starts"], "residual": rec.get("internal_residual_full_mask"),
                           "failure": rec.get("failure")}
        log("seed %s -> tuple=%s wall=%ss starts=%s residual=%s"
            % (s, rec.get("tuple"), rec["wall_s"], rec["starts"],
               rec.get("internal_residual_full_mask")))
    json.dump(summary, io.open(os.path.join(a.out_dir, "grasp_seeds_summary.json"), "w",
                               encoding="utf-8"), ensure_ascii=False, indent=1)
    logf.close()
    return 0 if any(v["tuple"] for v in summary.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
