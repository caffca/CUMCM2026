#!/usr/bin/env python3
"""Lightweight repository governance checker.

Hard errors are safe, objective violations. Warnings flag likely documentation
or publication-maintenance omissions that still require human/agent judgment.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT_REQUIRED = [
    "AGENTS.md",
    "REPOSITORY_OPERATING_GUIDE.md",
    "README_START_HERE.md",
    "PROJECT_BOOTSTRAP_CHECKLIST.md",
    ".gitignore",
    "docs/CURRENT_PROGRESS.md",
    "docs/CODEX_EXECUTION_JOURNAL.md",
    "docs/REPOSITORY_MAP.md",
    "docs/ENVIRONMENT.md",
    "docs/MODELING_PROTOCOL.md",
    "docs/DATA_PROTOCOL.md",
    "docs/DECISIONS.md",
    "docs/RESULTS_EVIDENCE_MATRIX.md",
    "docs/FIGURE_STYLE_GUIDE.md",
    "docs/FIGURE_TABLE_INDEX.md",
    "docs/PAPER_WRITING_GUIDE.md",
    "docs/SUBMISSION_SPEC.md",
    "docs/AI_USAGE_LOG.md",
]

FORBIDDEN_ROOT_SUFFIXES = {".log", ".zip", ".pth", ".pt", ".ckpt", ".npy", ".npz"}
SECRET_NAME_PATTERNS = [re.compile(r"(^|/)(\.env|.*\.pem|.*\.key)$", re.I)]
MAX_TRACKED_BYTES = 20 * 1024 * 1024


def git(root: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=False
    )
    return proc.returncode, proc.stdout.strip()


def changed_files(root: Path) -> set[str]:
    code, out = git(root, "status", "--porcelain")
    if code != 0:
        return set()
    changed = set()
    for line in out.splitlines():
        if len(line) >= 4:
            path = line[3:]
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            changed.add(path.replace("\\", "/"))
    return changed


def tracked_files(root: Path) -> list[str]:
    code, out = git(root, "ls-files")
    return out.splitlines() if code == 0 and out else []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    warnings: list[str] = []

    for rel in ROOT_REQUIRED:
        if not (root / rel).exists():
            errors.append(f"missing required governance file: {rel}")

    for child in root.iterdir():
        if child.is_file() and child.suffix.lower() in FORBIDDEN_ROOT_SUFFIXES:
            errors.append(f"forbidden artifact in repository root: {child.name}")

    tracked = tracked_files(root)
    for rel in tracked:
        norm = rel.replace("\\", "/")
        for pat in SECRET_NAME_PATTERNS:
            if pat.search(norm):
                errors.append(f"possible secret tracked by git: {norm}")
        p = root / rel
        if p.exists() and p.is_file() and p.stat().st_size > MAX_TRACKED_BYTES:
            warnings.append(f"large tracked file >20 MiB: {norm}")

    changed = changed_files(root)
    if changed:
        if any(p.startswith(("outputs/figures/", "outputs/tables/", "paper/figures/")) for p in changed):
            if "docs/FIGURE_TABLE_INDEX.md" not in changed:
                warnings.append("figure/table artifacts changed but FIGURE_TABLE_INDEX.md was not touched")

        env_markers = ("requirements", "pyproject.toml", "environment.yml", "environment.yaml", "Pipfile")
        if any(any(m in p for m in env_markers) for p in changed):
            if "docs/ENVIRONMENT.md" not in changed:
                warnings.append("environment/dependency files changed but ENVIRONMENT.md was not touched")

        if any(p.startswith("paper/") and p not in {"paper/", "paper/README.md"} for p in changed):
            if "docs/SUBMISSION_SPEC.md" not in changed:
                warnings.append(
                    "paper changed: re-check SUBMISSION_SPEC; it need not be edited unless official facts changed"
                )

    code, out = git(root, "diff", "--check")
    if code != 0:
        errors.append("git diff --check failed")
        if out:
            errors.append(out)

    print("Governance check")
    print(f"root: {root}")
    if errors:
        print("\nERRORS")
        for e in errors:
            print(f"- {e}")
    if warnings:
        print("\nWARNINGS")
        for w in warnings:
            print(f"- {w}")
    if not errors and not warnings:
        print("- no issues found")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
