#!/usr/bin/env python3
"""Export a bounded, self-contained window handoff snapshot.

This reads repository state only. It never checks out, stages, commits, or treats a
source SHA as scientific validation.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

TEXT_LIMIT = 200_000
ATTACHMENT_LIMIT = 2 * 1024 * 1024
TOTAL_ATTACHMENT_LIMIT = 5 * 1024 * 1024
ALLOWED_SUFFIXES = {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".py", ".png", ".pdf", ".svg"}
DENIED_PARTS = {".git", ".venv", "venv", ".env", "secrets", "credentials", "__pycache__"}
DENIED_NAMES = {"id_rsa", "id_ed25519", "credentials.json", "token.json", "auth.json"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".pfx", ".p12"}
BT = chr(96)


def run_git(repo: Path, *args: str, binary: bool = False, check: bool = True):
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=not binary,
        encoding=None if binary else "utf-8",
        errors=None if binary else "replace",
    )
    if check and result.returncode:
        detail = result.stderr.decode("utf-8", "replace") if binary else result.stderr
        raise ValueError(f"git {' '.join(args)} failed: {detail.strip()}")
    return result


def canonical_repo(value: str) -> Path:
    requested = Path(value).resolve()
    if not requested.is_dir():
        raise ValueError(f"repository directory missing: {requested}")
    root = Path(run_git(requested, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    if root != requested:
        raise ValueError(f"--repo must be the repository root: {root}")
    return root


def safe_relative(value: str) -> str:
    normalized = value.replace("\\", "/")
    candidate = PurePosixPath(normalized)
    if not normalized or candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"attachment path must stay repository-relative: {value}")
    lowered = [part.lower() for part in candidate.parts]
    name = lowered[-1]
    if any(part in DENIED_PARTS or part.startswith(".env") for part in lowered):
        raise ValueError(f"credential/environment path is not exportable: {value}")
    if name in DENIED_NAMES or Path(name).suffix.lower() in SENSITIVE_SUFFIXES:
        raise ValueError(f"credential-like file is not exportable: {value}")
    if Path(name).suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError(f"attachment type is not allowlisted: {value}")
    return candidate.as_posix()


def safe_worktree_bytes(repo: Path, relative: str) -> bytes:
    relative = safe_relative(relative)
    path = repo.joinpath(*PurePosixPath(relative).parts)
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"working-copy attachment is missing or a symlink: {relative}")
    resolved = path.resolve()
    try:
        resolved.relative_to(repo)
    except ValueError as exc:
        raise ValueError(f"attachment resolves outside repository: {relative}") from exc
    payload = path.read_bytes()
    if len(payload) > ATTACHMENT_LIMIT:
        raise ValueError(f"attachment exceeds {ATTACHMENT_LIMIT} bytes: {relative}")
    return payload


def frozen_bytes(repo: Path, sha: str, relative: str) -> bytes:
    relative = safe_relative(relative)
    tree = run_git(repo, "ls-tree", sha, "--", relative).stdout.strip()
    if not tree:
        raise ValueError(f"attachment is not tracked at {sha[:12]}: {relative}")
    mode, object_type, _, listed = re.split(r"\s+", tree, maxsplit=3)
    listed = listed.split("\t")[-1]
    if mode == "120000" or object_type != "blob" or listed.replace("\\", "/") != relative:
        raise ValueError(f"attachment is not a regular tracked file: {relative}")
    payload = run_git(repo, "show", f"{sha}:{relative}", binary=True).stdout
    if len(payload) > ATTACHMENT_LIMIT:
        raise ValueError(f"attachment exceeds {ATTACHMENT_LIMIT} bytes: {relative}")
    return payload


def text_or_marker(payload: bytes, relative: str) -> str:
    if Path(relative).suffix.lower() not in {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".py"}:
        return f"[binary attachment: {relative}]"
    if len(payload) > TEXT_LIMIT:
        return f"[text omitted: {relative} exceeds {TEXT_LIMIT} bytes]"
    try:
        return payload.decode("utf-8-sig")
    except UnicodeDecodeError:
        return f"[text omitted: {relative} is not UTF-8]"


def write_attachments(out: Path, records: list[tuple[str, bytes, str]]) -> list[dict[str, str | int]]:
    total = sum(len(payload) for _, payload, _ in records)
    if total > TOTAL_ATTACHMENT_LIMIT:
        raise ValueError(f"attachments exceed total limit {TOTAL_ATTACHMENT_LIMIT} bytes")
    if not records:
        return []
    target_root = out.with_name(out.stem + "_attachments")
    if target_root.exists():
        raise ValueError(f"attachment output already exists: {target_root}")
    written = []
    for relative, payload, provenance in records:
        target = target_root.joinpath(*PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        written.append({
            "path": target.relative_to(out.parent).as_posix(),
            "source": relative,
            "provenance": provenance,
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        })
    return written


def quote(value: str) -> str:
    return BT + value + BT


def md_code(value: str, language: str = "text") -> str:
    safe = value.replace(BT * 3, BT * 2 + " ")
    fence = BT * 3
    return f"\n\n{fence}{language}\n{safe.rstrip()}\n{fence}\n"


def status_packet(repo: Path, out: Path, working_attachments: list[str]) -> str:
    head = run_git(repo, "rev-parse", "HEAD").stdout.strip()
    branch = run_git(repo, "branch", "--show-current").stdout.strip() or "DETACHED"
    dirty = run_git(repo, "status", "--short").stdout.rstrip()
    worktrees = run_git(repo, "worktree", "list", "--porcelain").stdout.rstrip()
    progress_path = "docs/CURRENT_PROGRESS.md"
    decisions_path = "docs/DECISIONS.md"
    index_path = "references/design_priors/INDEX.md"
    guide_path = "docs/WINDOW_HANDOFF_GUIDE.md"
    progress = text_or_marker(safe_worktree_bytes(repo, progress_path), progress_path)
    decisions = text_or_marker(safe_worktree_bytes(repo, decisions_path), decisions_path)
    index = text_or_marker(safe_worktree_bytes(repo, index_path), index_path)
    guide = safe_worktree_bytes(repo, guide_path).decode("utf-8-sig")
    core = guide.split("## 2.", 1)[0][:6000].rstrip()
    question_summaries: list[tuple[str, str]] = []
    for summary_path in sorted(repo.glob("outputs/q*/summary.md")):
        relative = summary_path.relative_to(repo).as_posix()
        question_summaries.append(
            (relative, text_or_marker(safe_worktree_bytes(repo, relative), relative))
        )
    attachment_records = [
        (safe_relative(item), safe_worktree_bytes(repo, item), "WORKING_COPY_NOT_FROZEN")
        for item in working_attachments
    ]
    attachments = write_attachments(out, attachment_records)
    lines = [
        "# WINDOW_PACKET - working status",
        "",
        f"- 生成时间：{datetime.now().astimezone().isoformat(timespec='seconds')}",
        "- 受众：网页分析 / 本机Builder接续",
        f"- 仓库：{quote(str(repo))}",
        f"- 分支 / HEAD：{quote(branch)} / {quote(head)}",
        f"- dirty：{'yes' if dirty else 'no'}",
        "- 包类型：WORKING_STATUS（不是冻结证据）",
        "- base_sha：not_applicable",
        "- 当前赛题：未提供；不得从历史论文构造Q1",
        "- 访问边界：接收者若无本机权限，只能使用本包正文和随包附件。",
        "",
        "## Git时间点证据",
        md_code(dirty or "(clean)"),
        "### Worktrees",
        md_code(worktrees or "(none)"),
        "## 当前进度原文",
        f"来源：{quote(progress_path)}（dirty工作区时间点快照）",
        md_code(progress, "markdown"),
        "## 已有决定原文",
        f"来源：{quote(decisions_path)}（dirty工作区时间点快照）",
        md_code(decisions, "markdown"),
        "## 先验库存与边界原文",
        f"来源：{quote(index_path)}（dirty工作区时间点快照）",
        md_code(index, "markdown"),
        "## 稳定手册短核心",
        f"来源：{quote(guide_path)}；完整手册应与本包一起交接。",
        md_code(core, "markdown"),
        "## 各问摘要",
    ]
    if question_summaries:
        for relative, content in question_summaries:
            lines.extend([f"### {quote(relative)}", md_code(content, "markdown")])
    else:
        lines.append("- none（当前尚无正式赛题问题摘要）")
    lines.extend([
        "## 恢复结论",
        "- 当前任务是赛前收尾，没有正式题面、Q1数据或比赛结果。",
        "- 不重跑已完成6篇pilot、用户种子核验和无关旧测试。",
        "- 若开始比赛，先补选定题面与全部附件，再进入三scout和Q1。",
        "- dirty快照只用于恢复讨论，不能声称其内容来自某个冻结commit。",
        "",
        "## 附件",
    ])
    if attachments:
        lines.extend(
            f"- {quote(str(a['path']))} <- {quote(str(a['source']))}; {a['provenance']}; "
            f"{a['bytes']} bytes; SHA256 {quote(str(a['sha256']))}"
            for a in attachments
        )
    else:
        lines.append("- none")
    return "\n".join(lines).replace("\n\n\n", "\n\n") + "\n"


def frozen_packet(
    repo: Path,
    out: Path,
    sha_input: str,
    question: str,
    tracked_attachments: list[str],
    external_attachments: list[str],
) -> str:
    resolved = run_git(repo, "rev-parse", "--verify", f"{sha_input}^{{commit}}").stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", resolved):
        raise ValueError("base_sha did not resolve to a full commit")
    if not re.fullmatch(r"q[1-9][0-9]*", question):
        raise ValueError("--question must look like q1")
    prefix = f"outputs/{question}"
    default_text = ["docs/CURRENT_PROGRESS.md", "docs/DECISIONS.md",
                    f"{prefix}/summary.md", f"{prefix}/results.json",
                    f"{prefix}/results.csv", f"{prefix}/figure_briefs.md"]
    embedded: list[tuple[str, str]] = []
    missing: list[str] = []
    for relative in default_text:
        try:
            payload = frozen_bytes(repo, resolved, relative)
        except ValueError:
            missing.append(relative)
            continue
        embedded.append((relative, text_or_marker(payload, relative)))
    records: list[tuple[str, bytes, str]] = []
    for item in tracked_attachments:
        relative = safe_relative(item)
        records.append((relative, frozen_bytes(repo, resolved, relative), f"GIT:{resolved}"))
    for item in external_attachments:
        relative = safe_relative(item)
        records.append((relative, safe_worktree_bytes(repo, relative), "EXTERNAL_WORKING_COPY_NOT_IN_BASE_SHA"))
    attachments = write_attachments(out, records)
    tree = run_git(repo, "ls-tree", "-r", "--name-only", resolved, "--", prefix).stdout.rstrip()
    has_question_summary = any(relative == f"{prefix}/summary.md" for relative, _ in embedded)
    packet_status = "COMPLETE_FOR_DECLARED_SCOPE" if has_question_summary else "PARTIAL_MISSING_QUESTION_SUMMARY"
    lines = [
        f"# WINDOW_PACKET - frozen {question}",
        "",
        f"- 生成时间：{datetime.now().astimezone().isoformat(timespec='seconds')}",
        "- 受众：冻结Reviewer / 网页复核",
        f"- 源仓库：{quote(str(repo))}",
        f"- base_sha：{quote(resolved)}",
        f"- 当前问：{quote(question)}（SYNTHETIC与否以正文标记为准）",
        "- 包类型：FROZEN_EVIDENCE",
        f"- 包状态：{packet_status}",
        "- dirty工作区：未作为tracked证据读取；外置附件若有会单独标识。",
        "- 重要边界：来自该SHA只证明版本身份，不证明科学结论正确。",
        "",
        "## 该SHA中的问题文件",
        md_code(tree or "(none)"),
    ]
    for relative, content in embedded:
        lines.extend([f"## 内嵌：{quote(relative)}", md_code(content, "markdown")])
    lines.append("## 缺失的默认材料")
    lines.extend([f"- {quote(item)}" for item in missing] or ["- none"])
    lines.extend(["", "## 随包附件"])
    if attachments:
        lines.extend(
            f"- {quote(str(a['path']))} <- {quote(str(a['source']))}; {a['provenance']}; "
            f"{a['bytes']} bytes; SHA256 {quote(str(a['sha256']))}"
            for a in attachments
        )
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## 接收者最短检查",
        "1. 先确认任务、base_sha与SYNTHETIC/真实比赛身份。",
        "2. 用内嵌results/summary回答数值来源；不要改读Builder实时同名文件。",
        "3. 检查图只支持brief中的命题，不把文本批准当科学证明。",
        "4. 缺题面、原始数据或权限时只列最小缺失，不猜测。",
        "5. 不重跑已声明无需重跑的历史任务，不自动回流或合并。",
    ])
    return "\n".join(lines).replace("\n\n\n", "\n\n") + "\n"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--mode", choices=("status", "frozen"), required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--base-sha")
    parser.add_argument("--question")
    parser.add_argument("--attach", action="append", default=[],
                        help="status: explicit working-copy file; frozen: tracked file from base_sha")
    parser.add_argument("--external-attach", action="append", default=[],
                        help="repo-relative working-copy file, explicitly marked outside base_sha")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        repo = canonical_repo(args.repo)
        out = Path(args.out).resolve()
        if out.exists():
            raise ValueError(f"output already exists: {out}")
        if args.mode == "status":
            if args.base_sha or args.question or args.external_attach:
                raise ValueError("status mode does not use base_sha/question/external-attach")
            content = status_packet(repo, out, args.attach)
        else:
            if not args.base_sha or not args.question:
                raise ValueError("frozen mode requires --base-sha and --question")
            content = frozen_packet(
                repo, out, args.base_sha, args.question, args.attach, args.external_attach
            )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        print(out)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
