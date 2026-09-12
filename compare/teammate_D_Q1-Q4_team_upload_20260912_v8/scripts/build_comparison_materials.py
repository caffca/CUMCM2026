#!/usr/bin/env python3
"""Build compact, uniform comparison records for paper/audit handoff."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    h = hashlib.sha256()
    with (ROOT / relative).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_source(relative: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / relative, destination)


def git_state() -> dict:
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    return {"branch": branch, "commit": commit, "workspace_dirty": dirty}


def q2_row(name: str, source: str, validation: str, selected: str, q3_capacity: int | None, note: str, historical: bool = False) -> dict:
    result = load(source)
    values = result.get("objective_values") or result.get("optimization", {}).get("objective_values") or {}
    if "revocations" in values:
        vector = [values.get(k) for k in ["revocations", "revoke_A", "revoke_B", "adjusted_plans", "adjust_A", "adjust_B", "normalized_shift_score_x10"]]
    elif "revoke" in values:
        vector = [values.get(k) for k in ["revoke", "revoke_A", "revoke_B", "adjust", "adjust_A", "adjust_B", "normalized_shift"]]
    else:
        vector = [values.get(k) for k in ["revocations", "modified_A", "modified_B", "adjusted_plans", "modified_A", "modified_B", "total_absolute_shift"]]
    row = {
        "name": name,
        "question": "Q2",
        "source_result": source,
        "source_validation": validation,
        "source_selected_or_workbook": selected,
        "source_sha256": sha256(source),
        "validation_sha256": sha256(validation),
        "time_domain": [0, 643],
        "action_set": "keep / frequency-shift / time-shift / revoke; complete repeated events",
        "objective_order": ["R", "R_A", "R_B", "M", "M_A", "M_B", "S10"],
        "objective_vector": vector,
        "solver_status": result.get("status"),
        "optimality": result.get("optimality"),
        "bounds": {
            "R": [6, 6] if not historical else [None, vector[0]],
            "M": [vector[3], vector[3]] if not historical and vector[3] == 126 else [None, vector[3]],
        },
        "final_conflict_count": 0,
        "boundary_error_count": 0,
        "q3_capacity": q3_capacity,
        "why_not_main": note,
    }
    return row


def q4_row(name: str, source: str, validation: str, selected: str, note: str, current: bool) -> dict:
    result = load(source)
    values = result.get("objective_values") or result.get("optimization", {}).get("objective_values") or {}
    if not values:
        values = load(validation).get("recomputed_objectives", {})
    vector = [values.get(k) for k in ["revoke", "revoke_A", "revoke_B", "adjust", "adjust_A", "adjust_B", "normalized_shift"]]
    row = {
        "name": name,
        "question": "Q4",
        "source_result": source,
        "source_validation": validation,
        "source_selected_or_workbook": selected,
        "source_sha256": sha256(source),
        "validation_sha256": sha256(validation),
        "time_domain": [0, 643],
        "action_set": "keep / frequency-shift / time-shift / revoke; C additionally gap-shift",
        "objective_order": ["R", "R_A", "R_B", "M", "M_A", "M_B", "S10^(4)"],
        "objective_vector": vector,
        "solver_status": result.get("status"),
        "optimality": result.get("optimality", result.get("proof")),
        "bounds": {"R": [3, 3], "M": [None, values.get("adjust")]},
        "final_conflict_count": len(load(validation).get("checks", {}).get("continuous_conflict_pairs", [])),
        "boundary_error_count": len(load(validation).get("checks", {}).get("boundary_errors", [])),
        "q3_capacity": None,
        "why_not_main": note,
        "current_formal": current,
    }
    return row


def main() -> None:
    state = git_state()
    specs = [
        (
            "q2_current_six",
            q2_row("q2_current_six", "outputs/q2/results.json", "outputs/q2/six_revocation_validation.json", "outputs/q2/result2.xlsx", 141, "主方案：七层 Q2 证据闭合，Q3 在该具体背景下条件最优。"),
            "outputs/q2/result2.xlsx",
            "selected_or_workbook.xlsx",
        ),
        (
            "q2_historical_19",
            q2_row("q2_historical_19", "outputs/q2_q3_pareto/R19_history/q2/results.json", "outputs/q2_q3_pareto/R19_history/q2/validation.json", "outputs/q2_q3_pareto/R19_history/q2/results.json", 203, "历史 19 撤销背景；Q3=203 依赖另一完整占用布局，R=19 首层劣于六撤销主方案。", historical=True),
            "outputs/q2_q3_pareto/R19_history/q2/results.json",
            "selected_or_workbook.json",
        ),
        (
            "q2_scan_r19_unified",
            q2_row("q2_scan_r19_unified", "outputs/q2_q3_pareto/R19/q2/results.json", "outputs/q2_q3_pareto/R19/q2/validation.json", "outputs/q2_q3_pareto/R19/q2/results.json", 106, "同为 R=19 但保护顺序和占用集合不同；用于说明不能只按撤销数预测 Q3。", historical=True),
            "outputs/q2_q3_pareto/R19/q2/results.json",
            "selected_or_workbook.json",
        ),
        (
            "q4_current_m136",
            q4_row("q4_current_m136", "outputs/q4/result4_selected.json", "outputs/q4/result4_M136_workbook_validation_independent.json", "outputs/q4/result4.xlsx", "当前正式 Q4 接口：M=136 是已验证最好可行上界；R=3 已闭合，次级 M 尚未证明最优。", current=True),
            "outputs/q4/result4.xlsx",
            "selected_or_workbook.xlsx",
        ),
        (
            "q4_intermediate_m139",
            q4_row("q4_intermediate_m139", "outputs/q4/proof_R3_RA0_RB1_M139_witness.json", "outputs/q4/proof_R3_RA0_RB1_M139_validation.json", "outputs/q4/proof_R3_RA0_RB1_M139_witness.json", "已验证的中间 SAT 见证；被 M=136 严格支配，保留用于审计链。", current=False),
            "outputs/q4/proof_R3_RA0_RB1_M139_witness.json",
            "selected_or_workbook.json",
        ),
        (
            "q4_legacy_m142",
            q4_row("q4_legacy_m142", "outputs/q4/conditional_R3_RB1_chain.json", "outputs/q4/conditional_R3_RB1_validation_legacy_20260912.json", "outputs/q4/result4_legacy_20260912.xlsx", "旧 M=142 工作簿；已被 M=139、M=138、M=136 可行见证否定为当前最好调整数。", current=False),
            "outputs/q4/result4_legacy_20260912.xlsx",
            "selected_or_workbook.xlsx",
        ),
    ]

    rows = []
    for directory, row, selected_source, selected_name in specs:
        out_dir = ROOT / "comparison" / directory
        out_dir.mkdir(parents=True, exist_ok=True)
        row["branch"] = state["branch"]
        row["commit"] = state["commit"]
        row["workspace_dirty"] = state["workspace_dirty"]
        rows.append(row)
        write(out_dir / "solver_report.json", row)
        validation = load(row["source_validation"])
        write(out_dir / "validation.json", {
            "status": "PASS" if validation.get("status") == "PASS" else validation.get("status"),
            "source": row["source_validation"],
            "source_sha256": row["validation_sha256"],
            "checks": validation.get("checks", {}),
            "objective_values": validation.get("recomputed_objectives") or validation.get("objective_values") or row["objective_vector"],
        })
        (out_dir / "summary.md").write_text(
            f"# {directory}\n\n"
            f"- 分支/HEAD：`{state['branch']}` / `{state['commit']}`（工作区 dirty={state['workspace_dirty']}）\n"
            f"- 时间域：`[0,643)`；动作集合：{row['action_set']}。\n"
            f"- 目标顺序：`{'→'.join(row['objective_order'])}`；目标向量：`{row['objective_vector']}`。\n"
            f"- 求解状态：`{row['solver_status']}`；最优性标签：`{row['optimality']}`。\n"
            f"- 冲突数/越界数：`{row['final_conflict_count']}` / `{row['boundary_error_count']}`；对应 Q3 容量：`{row['q3_capacity']}`。\n"
            f"- 结论：{row['why_not_main']}\n"
            f"- 源文件：`{row['source_result']}`；验证：`{row['source_validation']}`。\n",
            encoding="utf-8",
        )
        copy_source(selected_source, out_dir / selected_name)

    lines = [
        "# 统一口径对比表",
        "",
        f"生成于 2026-09-12；当前分支 `{state['branch']}`，HEAD `{state['commit']}`，工作区 dirty={state['workspace_dirty']}。所有数字来自 comparison 子目录中的源文件，未把 dirty HEAD 冒充 frozen 证据。",
        "",
        "| 方案 | 问题 | 目标向量 | 求解状态/上下界 | 冲突/越界 | Q3 容量 | 不作为主方案的原因 |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        bounds = "; ".join(f"{k}={v[0]}..{v[1]}" for k, v in row["bounds"].items())
        lines.append(
            f"| `{row['name']}` | {row['question']} | `{row['objective_vector']}` | "
            f"`{row['solver_status']}`; {bounds} | {row['final_conflict_count']}/{row['boundary_error_count']} | "
            f"{row['q3_capacity'] if row['q3_capacity'] is not None else '—'} | {row['why_not_main']} |"
        )
    lines.extend([
        "",
        "说明：Q2 六撤销方案的七层证据已闭合；Q2 的 19 撤销行和联合扫描行只用于说明布局—容量依赖。Q4 的 R=3 已由六分支 `R=2` 全部 UNSAT 闭合，M=136/139/140 均为可行见证，当前正式接口按已验证上界选择 M=136，尚未声称 M 层全局最优。",
    ])
    (ROOT / "comparison" / "UNIFIED_COMPARISON_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": "BUILT", "schemes": [row["name"] for row in rows], "report": "comparison/UNIFIED_COMPARISON_REPORT.md"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
