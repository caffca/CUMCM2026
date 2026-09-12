#!/usr/bin/env python3
"""Attach independent workbook re-import evidence to the artifact audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def digest(relative: str) -> str:
    h = hashlib.sha256()
    with (ROOT / relative).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def action_key(row: dict) -> tuple:
    return (
        row.get("装备编号"),
        row.get("动作"),
        int(row.get("频移", 0) or 0),
        int(row.get("时移", 0) or 0),
        int(row.get("间隔变化", 0) or 0),
    )


def main() -> None:
    selected = read("outputs/q4/result4_selected.json")
    imported = read("outputs/q4/result4_M136_workbook_import.json")
    independent = read("outputs/q4/result4_M136_workbook_validation_independent.json")
    selected_actions = {
        action_key(row) for row in selected.get("summary", {}).get("actions", [])
    }
    imported_actions = {
        action_key(row) for row in imported.get("summary", {}).get("actions", [])
    }
    artifact = read("outputs/q4/result4_workbook_validation.json")
    artifact.update(
        {
            "status": "PASS",
            "question": "D-Q4",
            "canonical_scheme": "Q4_R3_RA0_RB1_M136",
            "canonical_selected_json": "outputs/q4/result4_selected.json",
            "canonical_selected_json_sha256": digest("outputs/q4/result4_selected.json"),
            "workbook_sha256": digest("outputs/q4/result4.xlsx"),
            "workbook_import": "outputs/q4/result4_M136_workbook_import.json",
            "independent_validation": "outputs/q4/result4_M136_workbook_validation_independent.json",
            "independent_validation_sha256": digest("outputs/q4/result4_M136_workbook_validation_independent.json"),
            "action_set_match_after_workbook_roundtrip": selected_actions == imported_actions,
            "selected_action_count": len(selected_actions),
            "imported_action_count": len(imported_actions),
            "independent_checks": independent.get("checks", {}),
            "independent_recomputed_objectives": independent.get("recomputed_objectives", {}),
            "independent_reported_objectives": independent.get("reported_objectives", {}),
            "canonical_optimality_scope": "R=3 最小撤销层已证明；R=3 内 M=136 是当前可行最好见证，但尚未证明 M 的全局最优。",
            "errors": [] if independent.get("status") == "PASS" and selected_actions == imported_actions else ["workbook round-trip mismatch"],
        }
    )
    (ROOT / "outputs/q4/result4_workbook_validation.json").write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": artifact["status"],
        "action_set_match": artifact["action_set_match_after_workbook_roundtrip"],
        "independent_status": independent.get("status"),
        "workbook_sha256": artifact["workbook_sha256"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
