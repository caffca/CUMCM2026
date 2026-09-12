# -*- coding: utf-8 -*-
"""P2-7：溯源与冗余动作检查。
(a) 是否调整了本来不冲突的计划（无谓调整，违反 lex 第 2 级最小化的合理性）；
(b) results/*.json 的 _meta 输入指纹与 data/canonical_plans.csv、code/prod 实现文件 sha 是否对得上。
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    plans = P.load_plans()
    pmap = {p["id"]: p for p in plans}
    q1 = P.rj(os.path.join("results", "Q1_detect.json"))
    in_conflict = {x for e in q1["edges"] for x in e}
    isolated = set(pmap) - in_conflict

    out = {"check": "溯源 + 冗余动作", "isolated_by_auth_q1": sorted(isolated)}
    for tag in ("Q2", "Q4"):
        acts = P.rj(os.path.join("results", f"{tag}_solution.json"))["actions"]
        wasteful = {}
        for pid, o in acts.items():
            if pid in isolated and not o.get("revoke"):
                wasteful[pid] = o
        out[f"{tag}_adjusted_isolated_plans"] = wasteful
        out[f"{tag}_revoked_isolated_plans"] = sorted(pid for pid, o in acts.items() if pid in isolated and o.get("revoke"))
        # 撤销计划原本参与多少条冲突边
        deg = {}
        for pid in [k for k, v in acts.items() if v.get("revoke")]:
            deg[pid] = sum(1 for e in q1["edges"] if pid in e)
        out[f"{tag}_revoked_conflict_degree"] = deg

    # ---- _meta 指纹核对 ----
    csv_sha = sha(os.path.join(P.ROOT, "data", "canonical_plans.csv"))
    meta = {}
    for fn in sorted(os.listdir(os.path.join(P.ROOT, "results"))):
        if not fn.endswith(".json"):
            continue
        d = json.load(open(os.path.join(P.ROOT, "results", fn), encoding="utf-8"))
        m = d.get("_meta") or {}
        ins = m.get("inputs") or m.get("input_files") or []
        ih = m.get("input_hashes") or {}
        rec = {"meta_keys": sorted(m)[:14], "role": m.get("role"), "n_inputs": len(ins) if isinstance(ins, list) else None,
               "seed_policy": m.get("seed_policy"), "seeds": m.get("seeds"),
               "solver_family": m.get("solver_family"), "n_input_hashes": len(ih)}
        if isinstance(ih, dict):
            for pth, sh in ih.items():
                ap = os.path.join(P.ROOT, str(pth))
                if os.path.exists(ap):
                    actual = sha(ap)
                    ok = (sh == actual)
                    rec["n_hash_ok"] = rec.get("n_hash_ok", 0) + (1 if ok else 0)
                    if not ok:
                        rec.setdefault("input_hash_mismatch", []).append({"path": pth, "recorded": str(sh)[:16], "actual": actual[:16]})
                else:
                    rec.setdefault("input_missing", []).append(pth)
        meta[fn] = rec
    out["data_csv_sha256_actual"] = csv_sha
    out["results_meta"] = meta
    # FMS computation_contract 的实现文件 sha 对账
    fms = P.rj(os.path.join("reports", "FINAL_MODEL_SPEC.json"))
    contract_check = []
    for prob in fms["problems"]:
        cc = prob.get("computation_contract") or {}
        impl = cc.get("implementation")
        if impl and os.path.exists(os.path.join(P.ROOT, impl)):
            actual = sha(os.path.join(P.ROOT, impl))
            contract_check.append({"problem": prob["problem_id"], "impl": impl,
                                   "recorded": (cc.get("implementation_sha256") or "")[:16],
                                   "actual": actual[:16],
                                   "match": actual == cc.get("implementation_sha256")})
        elif impl:
            contract_check.append({"problem": prob["problem_id"], "impl": impl, "match": "FILE_MISSING"})
    out["fms_contract_impl_sha"] = contract_check
    out["all_impl_sha_ok"] = all(c.get("match") is True for c in contract_check) if contract_check else None

    # Q1 edges 指纹自洽（字段 sha 是否等于字段 edges 列表自身的 sha）
    auth = q1["edges_sha256"]
    out["q1_sha_of_stored_edges_list"] = P.sha_of_edges([list(e) for e in q1["edges"]])
    out["q1_sha_selfconsistent"] = out["q1_sha_of_stored_edges_list"] == auth
    out["verdict"] = P.verdict(out["q1_sha_selfconsistent"] and out["all_impl_sha_ok"] is not False
                               and not any(rec.get("input_hash_mismatch") for rec in meta.values())
                               and not any(rec.get("input_missing") for rec in meta.values()))
    P.wr("p2_provenance.json", out)
    slim = {k: v for k, v in out.items() if k != "results_meta"}
    print(json.dumps(slim, ensure_ascii=False, indent=1)[:4000])
    print("--- results_meta 摘要（输入指纹核对）---")
    for fn, rec in meta.items():
        print(fn, "role=", rec.get("role"), "n_in=", rec.get("n_input_hashes"),
              "ok=", rec.get("n_hash_ok", 0),
              "MISMATCH=", json.dumps(rec.get("input_hash_mismatch", []), ensure_ascii=False)[:300],
              "MISSING=", rec.get("input_missing", []))


if __name__ == "__main__":
    main()
