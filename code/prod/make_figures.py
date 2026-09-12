# -*- coding: utf-8 -*-
"""D 题数据草图生成（FigureBuilder → figures/drafts/ + draft_figure_manifest.json）。
正式图由 figure_editorial 依 FigureSpec 重制；本阶段只产证据草图。"""
import json, os, sys, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\mathmodel-figure-templates\scripts")
sys.path.insert(0, "code/prod")
from figure_builder import FigureBuilder, despine  # noqa
import mpl_paper_style as _mps
palette = _mps.palette()

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False
T_MAX, B_MAX = 643, 100
CLS = {"A": 0, "B": 1, "C": 2}
CCLR = ["#2b6cb0", "#dd6b20", "#38a169"]
GEN = "code/prod/make_figures.py"


def R(p):
    d = json.load(open(p, encoding="utf-8"))
    return d.get("result", d)


def plans():
    import io
    out = []
    for ln in io.open("data/canonical_plans.csv", encoding="utf-8").read().splitlines()[1:]:
        c = ln.split(",")
        out.append(dict(id=c[0], cls=c[0][0], f0=int(c[2]), f1=int(c[3]), t0=int(c[4]),
                        t1=int(c[5]), g=int(c[6]), n=int(c[7]), d=int(c[5]) - int(c[4])))
    return out


def grid_from_actions(acts):
    g = np.zeros((B_MAX, T_MAX))
    for p in plans():
        o = (acts or {}).get(p["id"], {})
        if o.get("revoke"):
            continue
        df, dt = int(o.get("df", 0)), int(o.get("dt", 0))
        gg = p["g"] + int(o.get("dg", 0))
        for k in range(p["n"]):
            s = p["t0"] + dt + k * (gg + p["d"])
            for t in range(s, s + p["d"]):
                if 0 <= t < T_MAX:
                    for f in range(p["f0"] + df, p["f1"] + df):
                        if 0 <= f < B_MAX:
                            g[f, t] = CLS[p["cls"]] + 1
    return g


def manifest(fid, srcs):
    mp = "figures/figure_manifest.json"
    m = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else []
    item = next((x for x in m if x["id"] == fid), {"id": fid, "story": {"main_message": ""}})
    item = dict(item)
    item["source_results"] = srcs
    return item


def main():
    os.makedirs("figures/drafts", exist_ok=True)
    q1 = R("results/Q1_detect.json")
    q2 = R("results/Q2_solution.json")
    q3 = R("results/Q3_solution.json")
    q4 = R("results/Q4_solution.json")
    q2t = R("results/Q2_table1.json")
    q4t = R("results/Q4_table1.json")
    cats = ["A", "B", "C"]
    from matplotlib.patches import Patch

    def finish(fb, fig, specs, caption):
        fb.save(fig, specs, out_dir="figures/drafts", caption=caption, generator=GEN)
        plt.close(fig)

    # 1 grid conflict
    g = grid_from_actions({})
    occ = {}
    for p in plans():
        cs = []
        for k in range(p["n"]):
            s = p["t0"] + k * (p["g"] + p["d"])
            for t in range(s, s + p["d"]):
                for f in range(p["f0"], p["f1"]):
                    cs.append((f, t))
        occ[p["id"]] = set(cs)
    conflict = np.zeros_like(g)
    for a, b in q1["edges"]:
        for (f, t) in (occ[a] & occ[b]):
            conflict[f, t] = 1
    fb = FigureBuilder("fig-q1-grid-conflict", manifest("fig-q1-grid-conflict",
        [{"file": "Q1_detect.json", "keys": ["counts.edges", "edges_sha256"]}]), ".")
    fig, ax = plt.subplots(figsize=(8.6, 3.4))
    ax.imshow(g, aspect="auto", origin="lower", cmap=matplotlib.colors.ListedColormap(
        ["#f5f5f5"] + CCLR), vmin=0, vmax=3, extent=[0, T_MAX, 0, B_MAX])
    ys, xs = np.nonzero(conflict)
    ax.scatter(xs, ys, s=2, c="#d5303f", marker="s", linewidths=0)
    ax.set_xlabel("时间（Δt 格）"); ax.set_ylabel("频段（Δf 格）")
    ax.legend(handles=[Patch(color=CCLR[i], label=l) for i, l in enumerate("ABC")] +
                    [Patch(color="#d5303f", label="冲突单元")], loc="upper right", fontsize=7)
    despine(ax)
    fb.annotate_value(ax, "冲突对", "counts.edges", fmt="{:d}", xy=(0.985, 0.04))
    finish(fb, fig, [{"ax": ax, "panel_id": "A"}], "时频占用栅格与冲突单元")

    # 2 degree dist
    deg = collections.Counter()
    for a, b in q1["edges"]:
        deg[a] += 1; deg[b] += 1
    byc = {"A": [], "B": [], "C": []}
    for p in plans():
        byc[p["cls"]].append(deg.get(p["id"], 0))
    fb = FigureBuilder("fig-q1-degree-dist", manifest("fig-q1-degree-dist",
        [{"file": "Q1_detect.json", "keys": ["involved_plans"]}]), ".")
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.hist([byc["A"], byc["B"], byc["C"]], bins=np.arange(0, 10.5), stacked=True, color=CCLR, label=list("ABC"))
    ax.set_xlabel("计划冲突度"); ax.set_ylabel("计划数"); ax.legend(fontsize=8); despine(ax)
    fb.annotate_value(ax, "涉及计划", "involved_plans", fmt="{:d}/150", xy=(0.98, 0.95))
    finish(fb, fig, [{"ax": ax, "panel_id": "A"}], "冲突度分布")

    # 3 classpairs
    fb = FigureBuilder("fig-q1-classpairs", manifest("fig-q1-classpairs",
        [{"file": "Q1_detect.json", "keys": ["counts.AB", "counts.AC", "counts.BC", "counts.BB", "counts.CC"]}]), ".")
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    ks = ["AB", "AC", "BB", "BC", "CC"]
    vals = [q1["counts"][k] for k in ks]
    ax.bar(ks, vals, color=["#718096", "#718096", "#718096", palette["primary"], "#718096"])
    for i, v in enumerate(vals):
        ax.text(i, v + 3, str(v), ha="center", fontsize=8)
    ax.set_ylabel("冲突对数"); ax.set_xlabel("类别组合"); despine(ax)
    finish(fb, fig, [{"ax": ax, "panel_id": "A"}], "冲突对类别构成")

    # 4 hero lex
    t = q2["objective_tuple"]
    lay = {l["layer"]: l for l in q2.get("layers", [])}
    lb1 = q2["ladder_proven_revoke_lb"]
    fb = FigureBuilder("fig-q2-hero-lex", manifest("fig-q2-hero-lex",
        [{"file": "Q2_solution.json", "keys": ["revoke", "ladder_proven_revoke_lb", "gap_revoke"]}]), ".")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.8, 3.4), gridspec_kw={"width_ratios": [1.5, 1]})
    rows = [("撤销数", lb1, t[0]), ("调整数", lay.get("L2_minA", {}).get("best_bound", t[1]), t[1]),
            ("优先级损失", lay.get("L3_minPL", {}).get("best_bound", t[2]), t[2]),
            ("幅度合计", lay.get("L4_minMG", {}).get("best_bound", t[3]), t[3])]
    for i, (nm, lo, hi) in enumerate(rows):
        lo = min(lo, hi)
        ax1.plot([lo, hi], [i, i], lw=6, color=palette["primary"] if lo < hi else "#38a169", solid_capstyle="butt")
        ax1.text(hi, i + 0.28, f"{hi:g}", fontsize=8, ha="center")
        ax1.text(lo, i + 0.28, f"LB {lo:g}" if lo < hi else "闭合", fontsize=7, ha="center",
                 color="#718096" if lo < hi else "#38a169")
    ax1.set_yticks(range(4), [r[0] for r in rows])
    ax1.set_yscale("symlog"); ax1.set_ylim(-0.6, 3.6)
    ax1.set_xlabel("证书下界 → 达成上界"); despine(ax1)
    pre = q1["counts"]["edges"]
    post = q2["residual_pairs_second_impl"]
    ax2.bar(["消解前", "消解后"], [pre, post], color=["#e53e3e", "#38a169"], width=.55)
    ax2.text(0, pre + 5, str(pre), ha="center", fontsize=9); ax2.text(1, post + 5, str(post), ha="center", fontsize=9)
    ax2.set_ylabel("残留冲突对"); despine(ax2)
    finish(fb, fig, [{"ax": ax1, "panel_id": "A"}, {"ax": ax2, "panel_id": "B"}], "四级目标证书与消解效果")

    # 5 table1
    fb = FigureBuilder("fig-q2-table1", manifest("fig-q2-table1",
        [{"file": "Q2_table1.json", "keys": ["by_class", "table_closure_diff"]}]), ".")
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    w = 0.26
    for i, (k, c) in enumerate((("kept", "#38a169"), ("adjusted", palette["primary"]), ("revoked", "#e53e3e"))):
        vs = [q2t["by_class"][c2][k] for c2 in cats]
        ax.bar(np.arange(3) + (i - 1) * w, vs, w, color=c,
               label={"kept": "保留", "adjusted": "调整", "revoked": "撤销"}[k])
        for x, v in zip(np.arange(3) + (i - 1) * w, vs):
            ax.text(x, v + 0.7, str(v), ha="center", fontsize=8)
    ax.set_xticks(range(3), cats); ax.set_ylabel("计划数"); ax.legend(fontsize=8); despine(ax)
    finish(fb, fig, [{"ax": ax, "panel_id": "A"}], "问题二按类统计（表1）")

    # 6 ladder
    fb = FigureBuilder("fig-q2-ladder", manifest("fig-q2-ladder",
        [{"file": "Q2_solution.json", "keys": ["ladder_proven_revoke_lb", "revoke"]}]), ".")
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    layers = q2.get("layers", [])
    stat = {"OPTIMAL": 2, "FEASIBLE": 1, "INFEASIBLE": 0, "UNKNOWN": -1}
    yy = [stat.get(l["status"], -1) for l in layers]
    cols = ["#e53e3e" if v == 0 else "#38a169" if v == 1 else palette["primary"] if v == 2 else "#a0aec0" for v in yy]
    ax.bar(range(len(layers)), [max(v, 0) + 0.15 for v in yy], color=cols)
    ax.set_xticks(range(len(layers)), [l["layer"] for l in layers], rotation=30, fontsize=7)
    ax.set_yticks([0, 1, 2], ["INFEASIBLE", "FEASIBLE", "OPTIMAL"], fontsize=7)
    ax.set_ylabel("求解状态"); despine(ax)
    finish(fb, fig, [{"ax": ax, "panel_id": "A"}], "撤销阶梯证书序列")

    # 7 q3 utilization
    fb = FigureBuilder("fig-q3-utilization", manifest("fig-q3-utilization",
        [{"file": "Q3_solution.json", "keys": ["phi", "ub_min"]}]), ".")
    fig, ax = plt.subplots(figsize=(8.6, 3.4))
    g3 = grid_from_actions(q2["actions"])
    ax.imshow(g3, aspect="auto", origin="lower", cmap=matplotlib.colors.ListedColormap(
        ["#ffffff"] + CCLR), vmin=0, vmax=3, extent=[0, T_MAX, 0, B_MAX])
    ys, xs = [], []
    for f0, t0 in q3["selected"]:
        for k in range(12):
            s = t0 + k * 10
            xs += [s, s + 1] * 3
            ys += list(range(f0, f0 + 3)) * 2
    ax.scatter(xs, ys, s=2, c="#805ad5", marker="s", linewidths=0)
    ax.set_xlabel("时间（Δt 格）"); ax.set_ylabel("频段（Δf 格）")
    ax.legend(handles=[Patch(color=CCLR[i], label=l + "类(既有)") for i, l in enumerate("ABC")] +
                    [Patch(color="#805ad5", label="新增C类")], loc="upper right", fontsize=7)
    despine(ax)
    fb.annotate_value(ax, "新增", "phi", fmt="{:d} 台", xy=(0.985, 0.04), fontsize=9)
    finish(fb, fig, [{"ax": ax, "panel_id": "A"}], "问题三加装后的资源利用")

    # 8 bounds meet
    fb = FigureBuilder("fig-q3-bound-meet", manifest("fig-q3-bound-meet",
        [{"file": "Q3_solution.json", "keys": ["phi", "ub_cp", "ub_lp", "ub_phase"]}]), ".")
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    items = [("构造/认证值 φ", q3["phi"], "#38a169"),
             ("CP-SAT 整数上界", q3.get("ub_cp"), palette["primary"]),
             ("LP 上界(HiGHS)", int(q3["ub_lp"]) if q3.get("ub_lp") else None, "#dd6b20"),
             ("相位×块初等界", q3.get("ub_phase"), "#a0aec0")]
    used = [(nm, v, c) for nm, v, c in items if v is not None]
    ax.barh(range(len(used)), [v for _, v, _ in used], color=[c for _, _, c in used], height=.55)
    for i, (nm, v, c) in enumerate(used):
        ax.text(v + 2, i, str(v), va="center", fontsize=8)
    ax.set_yticks(range(len(used)), [nm for nm, _, _ in used], fontsize=8)
    ax.invert_yaxis(); ax.set_xlabel("新增 C 计划数"); despine(ax)
    finish(fb, fig, [{"ax": ax, "panel_id": "A"}], "加装数量上下界会合")

    # 9 q4 vs q2
    fb = FigureBuilder("fig-q4-vs-q2", manifest("fig-q4-vs-q2",
        [{"file": "Q4_table1.json", "keys": ["by_class", "objective_tuple"]},
         {"file": "Q4_solution.json", "keys": ["revoke_gain_vs_q2"]}]), ".")
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(8.6, 3.2), gridspec_kw={"width_ratios": [1.4, 1]})
    for i, (k, c, lab) in enumerate((("kept", "#38a169", "保留"), ("adjusted", palette["primary"], "调整"),
                                       ("revoked", "#e53e3e", "撤销"))):
        v2 = [q2t["by_class"][c2][k] for c2 in cats]
        v4 = [q4t["by_class"][c2][k] for c2 in cats]
        axa.bar(np.arange(3) + (i - 1) * .38 - .19, v2, .19, color=c, alpha=.45, hatch="//", label=f"Q2 {lab}")
        axa.bar(np.arange(3) + (i - 1) * .38 + .19, v4, .19, color=c, label=f"Q4 {lab}")
    axa.set_xticks(range(3), cats); axa.set_ylabel("计划数"); axa.legend(fontsize=6.5, ncol=2); despine(axa)
    t2, t4 = q2["objective_tuple"], q4["objective_tuple"]
    xx = np.arange(4)
    axb.bar(xx - .19, t2, .38, color="#718096", label="Q2")
    axb.bar(xx + .19, t4, .38, color=palette["primary"], label="Q4")
    axb.set_yscale("symlog"); axb.set_xticks(xx, ["撤销", "调整", "优先级", "幅度"], fontsize=8)
    axb.legend(fontsize=8); despine(axb)
    finish(fb, fig, [{"ax": axa, "panel_id": "A"}, {"ax": axb, "panel_id": "B"}], "问题四与问题二对比")

    # 10 dg dist
    fb = FigureBuilder("fig-q4-dg-dist", manifest("fig-q4-dg-dist",
        [{"file": "Q4_solution.json", "keys": ["dg_options_dropped_by_horizon",
                                                     "dg_dropped_infeasible_gap", "dg_dropped_horizon",
                                                     "objective_tuple"]}]), ".")
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    dgs = [int(o["dg"]) for o in q4["actions"].values() if "dg" in o]
    if dgs:
        ax.hist(dgs, bins=np.arange(-10.5, 11.5), color=palette["primary"])
    ax.set_xlabel("间隔调整量 dg（Δt）"); ax.set_ylabel("计划数"); despine(ax)
    fb.annotate_value(ax, "被禁 dg 选项", "dg_options_dropped_by_horizon", fmt="{:d} 项",
                      xy=(0.98, 0.92), fontsize=8)
    fb.annotate_value(ax, "其中时域越界", "dg_dropped_horizon", fmt="{:d} 项",
                      xy=(0.98, 0.84), fontsize=8)
    finish(fb, fig, [{"ax": ax, "panel_id": "A"}], "间隔重定时调整分布")

    # draft manifest
    reqs = {x["id"]: x for x in json.load(open("reports/FIGURE_REQUIREMENTS.json", encoding="utf-8"))["figures"]}
    dm = []
    for f in sorted(os.listdir("figures/drafts")):
        if f.endswith(".pdf"):
            fid = f[:-4]
            meta = json.load(open(f"figures/drafts/{fid}.meta.json", encoding="utf-8"))
            rq = reqs.get(fid, {})
            dm.append({"id": fid, "question_id": rq.get("question_id"), "status": "drafted",
                       "files": [f"figures/drafts/{fid}.pdf"], "meta": f"figures/drafts/{fid}.meta.json",
                       "story": {"main_message": rq.get("main_message", ""), "claim_bind": rq.get("claim_bind", [])},
                       "panels": rq.get("panels", []), "data_source": rq.get("data_source", ""),
                       "source": {"generator": GEN}, "source_hash": meta.get("source_hash"),
                       "caption": meta.get("caption", "")})
    json.dump(dm, open("figures/draft_figure_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("draft figures written:", len(dm))


if __name__ == "__main__":
    main()
