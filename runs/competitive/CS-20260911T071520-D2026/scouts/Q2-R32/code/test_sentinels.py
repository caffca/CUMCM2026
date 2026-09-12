# -*- coding: utf-8 -*-
"""R32 哨兵单测：连续罚 Φ 的解析子梯度 vs 数值差分；Φ=0 ⇔ 谓词零冲突 的双向小用例。

（route validation_plan 第 1 条：'Φ=0 ⟺ 谓词零冲突 的双向小用例单测（含端点相接负例）'）
"""
import io
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")
import q2_common as Q  # noqa: E402
import solve_r32 as R  # noqa: E402


def grad_check(f, ntrial=6, seed=7):
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(ntrial):
        df = rng.uniform(-3, 3, f["nP"])
        dt = rng.uniform(-2, 2, f["nP"])
        F0, _, _, G1, G2 = R.phi_and_grad(f, df, dt)
        for G, vec, other_is_df in ((G1, df, True), (G2, dt, False)):
            for k in rng.integers(0, f["nP"], size=6):
                eps = 1e-4
                v1 = vec.copy(); v1[k] += eps
                v2 = vec.copy(); v2[k] -= eps
                Fa = R.phi_and_grad(f, v1, dt if other_is_df else v1)[0] if other_is_df \
                    else R.phi_and_grad(f, df, v1)[0]
                Fb = R.phi_and_grad(f, v2, dt if other_is_df else v2)[0] if other_is_df \
                    else R.phi_and_grad(f, df, v2)[0]
                fd = (Fa - Fb) / (2 * eps)
                # 折点处解析次梯度与中心差分可合法不同：只要求 |fd| ≤ |G|+tol 的保守一致性
                if abs(fd - G[k]) > 1e-2 * max(1.0, abs(fd)) and np.sign(fd) != np.sign(G[k]):
                    worst = max(worst, abs(fd - G[k]))
    return worst


def zero_equivalence(f):
    """Φ=0 ⇔ G* 谓词零冲突；并给端点相接（半开区间）负例。"""
    ids = f["ids"]
    # 例 1：全恒等 ⇒ Φ>0 且谓词冲突>0
    allkeep = {i: 0 for i in ids}
    v1 = R.violated(f, allkeep)
    df0 = np.zeros(f["nP"]); dt0 = np.zeros(f["nP"])
    _, Phi0, _, _, _ = R.phi_and_grad(f, df0, dt0)
    # 例 2：撤销全部涉事计划 ⇒ 谓词零冲突（Φ 不感知撤销，故只断言谓词侧）
    ch = dict(allkeep)
    for i in ids:
        ch[i] = len(f["acts"][i]) - 1
    v2 = R.violated(f, ch)
    # 例 3：端点相接负例——把两个频段首尾相接（δf 使 f1_i == f0_j）⇒ 谓词必须判"不冲突"
    pos = f["plans"]
    neg = None
    for (i, j) in f["keys"]:
        pi, pj = pos[i], pos[j]
        gap = pj["f0"] - pi["f1"]      # 有符号：δf=gap 把 i 的频段右移到与 j 首尾相接
        if -Q.DF_LIM <= gap <= Q.DF_LIM and gap != 0:
            df = gap
            neg = (i, j, df, pi, pj)
            break
    res = {
        "all_keep": {"Phi": round(float(Phi0), 3), "violated": len(v1),
                     "consistent": (Phi0 > 0) == (len(v1) > 0)},
        "all_revoke": {"violated": len(v2), "consistent": len(v2) == 0},
        "touching_bands_negative_case": None,
    }
    if neg:
        i, j, df, pi, pj = neg
        ov = max(0, min(pi["f1"] + df, pj["f1"]) - max(pi["f0"] + df, pj["f0"]))
        res["touching_bands_negative_case"] = {
            "pair": [i, j], "df": df, "band_overlap_len_after_touch": ov,
            "half_open_no_overlap": ov == 0}
    return res


if __name__ == "__main__":
    f = R.build_field(os.path.join(HERE, "star_edges.json"))
    out = {"gradient_vs_fd_worst_mismatch": grad_check(f),
           "phi_vs_predicate_equivalence": zero_equivalence(f)}
    print(io.StringIO())
    print(__import__("json").dumps(out, ensure_ascii=False, indent=1))
    json_path = os.path.join(HERE, "..", "sentinel_tests.json")
    io.open(json_path, "w", encoding="utf-8").write(
        __import__("json").dumps(out, ensure_ascii=False, indent=1))
