#!/usr/bin/env python3
"""Create a bounded, self-contained teammate evidence package.

The package is explicit rather than a whole-repository copy.  It contains the
statement, raw attachment/templates needed for a rerun, requested outputs,
scripts, handoff notes, and comparison records.  Existing package targets are
never overwritten.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[1]
# Keep earlier packages immutable; this v8 package incorporates the final
# SAT/CP-SAT evidence-index note.
PACKAGE_DIR = ROOT / "docs/team_upload_20260912_v8"
ZIP_PATH = ROOT / "docs/team_upload_20260912_v8.zip"


BASE_FILES = [
    "README_REPRO.md",
    "requirements-cumcm.txt",
    "docs/TEAM_EVIDENCE_HANDOFF_20260912.md",
    "docs/WINDOW_HANDOFF_GUIDE.md",
    "data/raw/D题/D题.pdf",
    "data/raw/D题/附件/附件1.xlsx",
    "data/raw/D题/附件/附件2/result1.xlsx",
    "data/raw/D题/附件/附件2/result2.xlsx",
    "data/raw/D题/附件/附件2/result3.xlsx",
    "data/raw/D题/附件/附件2/result4.xlsx",
    "outputs/q1/result1.xlsx",
    "outputs/q1/conflict_pairs.csv",
    "outputs/q1/summary.md",
    "outputs/q1/results.json",
    "outputs/q1/validation.json",
    "outputs/q2/summary.md",
    "outputs/q2/result2.xlsx",
    "outputs/q2/results.json",
    "outputs/q2/validation.json",
    "outputs/q2/six_revocation_candidate.json",
    "outputs/q2/six_revocation_validation.json",
    "outputs/q2/workbook_validation.json",
    "outputs/q2/revocation_bound.json",
    "outputs/q2/priority_prefix_run.json",
    "outputs/q2/q2_optimization_audit.md",
    "outputs/q2/q2_proof_matrix.csv",
    "outputs/q2/proof/sat_b_le_3.json",
    "outputs/q2/proof/sat_adjust_le_125.json",
    "outputs/q2/proof/sat_adjust_a_le_15.json",
    "outputs/q2/proof/sat_adjust_b_le_33.json",
    "outputs/q2/proof/sat_shift_le_774_full.json",
    "outputs/q2/proof/SAT_EVIDENCE_INDEX.md",
    "outputs/q2/proof/sat_evidence_validation.json",
    "outputs/q3/q2_input_from_result2.json",
    "outputs/q3/result3.xlsx",
    "outputs/q3/results.json",
    "outputs/q3/validation.json",
    "outputs/q3/q3_optimality_audit.json",
    "outputs/q3/q3_optimization_audit.md",
    "outputs/q3/summary.md",
    "outputs/q4/proof_R_le_3.json",
    "outputs/q4/proof_R_le_3_validation_final.json",
    "outputs/q4/proof_R_le_2_active_sat_r2_A0B0C2_pruned120.json",
    "outputs/q4/proof_R_le_2_active_sat_r2_A0B1C1_compact600.json",
    "outputs/q4/proof_R_le_2_active_sat_r2_A0B2C0_pruned300.json",
    "outputs/q4/proof_R_le_2_active_sat_r2_A1B0C1_pruned300.json",
    "outputs/q4/proof_R_le_2_active_sat_r2_A1B1C0_pruned300.json",
    "outputs/q4/proof_R_le_2_active_sat_r2_A2B0C0_pruned300.json",
    "outputs/q4/proof_R_le_2_dominance_validation.json",
    "outputs/q4/proof_R_le_2_global_coverage_validation.json",
    "outputs/q4/r2_global_proof_status.md",
    "outputs/q4/proof_R3_RA0_RB1_M140_witness.json",
    "outputs/q4/proof_R3_RA0_RB1_M140_validation.json",
    "outputs/q4/proof_R3_RA0_RB1_M139_witness.json",
    "outputs/q4/proof_R3_RA0_RB1_M139_validation.json",
    "outputs/q4/proof_R3_RA0_RB1_M136_witness.json",
    "outputs/q4/proof_R3_RA0_RB1_M136_validation.json",
    "outputs/q4/result4.xlsx",
    "outputs/q4/result4_selected.json",
    "outputs/q4/result4_workbook_validation.json",
    "outputs/q4/result4_M136_workbook_import.json",
    "outputs/q4/result4_M136_workbook_validation_independent.json",
    "outputs/q4/q4_secondary_proof_matrix.md",
    "outputs/q4/q4_optimization_audit.md",
    "outputs/q4/summary.md",
    "outputs/q2_q3_pareto/global_joint_pareto_proof.md",
    "outputs/q2_q3_pareto/pareto_results_with_history.csv",
    "outputs/q2_q3_global_frontier/global_frontier_closure_status_20260912.md",
    "outputs/q2_q3_global_frontier/global_frontier_lower_bound_table.csv",
    "outputs/q2_q3_global_frontier/global_frontier_lower_bound_table.json",
    "scripts/solve_q1.py",
    "scripts/solve_q2_cp_sat.py",
    "scripts/prove_q2_sat.py",
    "scripts/prove_q2_shift_sat.py",
    "scripts/validate_q2.py",
    "scripts/validate_result2_workbook.py",
    "scripts/solve_q3.py",
    "scripts/validate_q3.py",
    "scripts/solve_q4_cp_sat.py",
    "scripts/prove_q4_active_sat.py",
    "scripts/validate_q4.py",
    "scripts/import_q4_workbook.py",
    "scripts/build_result4.mjs",
    "scripts/prepare_team_evidence.py",
    "scripts/finalize_q4_workbook_validation.py",
    "scripts/build_comparison_materials.py",
    "scripts/build_team_upload_package.py",
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_state() -> dict:
    return {
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "workspace_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
    }


def main() -> None:
    if PACKAGE_DIR.exists() or ZIP_PATH.exists():
        raise SystemExit(f"Refusing to overwrite existing package target: {PACKAGE_DIR} or {ZIP_PATH}")
    comparison_files = [
        p.relative_to(ROOT).as_posix()
        for p in sorted((ROOT / "comparison").rglob("*"))
        if p.is_file()
    ]
    files = list(dict.fromkeys(BASE_FILES + comparison_files))
    missing = [relative for relative in files if not (ROOT / relative).is_file()]
    if missing:
        raise SystemExit("Missing required package files:\n" + "\n".join(missing))

    PACKAGE_DIR.mkdir(parents=True)
    entries = []
    for relative in files:
        source = ROOT / relative
        target = PACKAGE_DIR / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        entries.append({"path": relative, "size": source.stat().st_size, "sha256": digest(source)})

    state = git_state()
    manifest = {
        "package": "D题_Q1-Q4_team_evidence_20260912",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": str(ROOT),
        "git": state,
        "raw_attachment_sha256": digest(ROOT / "data/raw/D题/附件/附件1.xlsx"),
        "raw_data_modified_in_this_package": False,
        "canonical_claims": {
            "q2_objective_vector": [6, 0, 4, 126, 16, 34, 775],
            "q2_status": "FULL_LEXICOGRAPHIC_PROVED",
            "q3_capacity_under_bound_q2": 141,
            "q4_min_revocations": 3,
            "q4_current_formal_objective_vector": [3, 0, 1, 136, 19, 36, 924],
            "q4_current_formal_scope": "M=136 is the best validated feasible upper bound under R=3,R_A=0,R_B=1; M optimality is not closed.",
        },
        "manifest_self_hash_excluded": True,
        "files": entries,
        "missing_files": [],
    }
    (ROOT / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PACKAGE_DIR / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PACKAGE_DIR.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(PACKAGE_DIR).as_posix())
    print(json.dumps({
        "status": "BUILT",
        "package_dir": str(PACKAGE_DIR),
        "zip": str(ZIP_PATH),
        "file_count": len(entries),
        "zip_size": ZIP_PATH.stat().st_size,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
