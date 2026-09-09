"""Check an explicit delivery allowlist; never zip the repository or certify eligibility."""
import argparse
import json
from pathlib import Path
import re

DENIED = {".git", ".venv", "venv", "__pycache__", ".cache", "tmp", "references", ".codex", ".agents"}
SECRET = re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:sk-|ghp_)[A-Za-z0-9_-]{20,}|(?:password|api_key|access_token)\s*[:=]\s*['\"][^'\"]{8,}", re.I)
PERSONAL = re.compile(rb"(?<!\d)(?:1[3-9]\d{9}|\d{17}[\dXx])(?!\d)")


def check(root, entries):
    root = Path(root).resolve()
    paths = []
    for entry in entries:
        relative = Path(entry["path"])
        if not entry.get("reuse_allowed") or not entry.get("purpose"):
            raise ValueError("BLOCKED: every included file needs purpose and reuse_allowed")
        target = (root / relative).resolve()
        if relative.is_absolute() or ".." in relative.parts or not target.is_relative_to(root) or any(p.lower() in DENIED for p in relative.parts):
            raise ValueError(f"BLOCKED: excluded path {relative}")
        original = root / relative
        components = [original, *[p for p in original.parents if p != root and p.is_relative_to(root)]]
        if any(p.is_symlink() or getattr(p, "is_junction", lambda: False)() for p in components):
            raise ValueError(f"BLOCKED: linked path {relative}")
        if not target.is_file() or target.suffix.lower() in {".key", ".pem", ".pkl", ".pyc"} or target.name.startswith(".env"):
            raise ValueError(f"BLOCKED: non-deliverable file {relative}")
        if target.stat().st_size > 20*1024*1024:
            raise ValueError(f"BLOCKED: large file requires explicit packaging decision: {relative}")
        payload = target.read_bytes()
        if SECRET.search(payload) or PERSONAL.search(payload):
            raise ValueError(f"BLOCKED: credential/personal-data candidate in {relative}; inspect locally")
        paths.append(str(relative))
    return {"status":"ALLOWLIST_CHECK_PASS", "files":paths, "archive_created":False,
            "format_pages_size_anonymity":"TBD - user template not supplied",
            "limitation":"Binary metadata and private information require actual content review; this is not submission approval."}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True)
    p.add_argument("--allowlist", required=True)
    args = p.parse_args()
    try:
        print(json.dumps(check(args.root, json.loads(Path(args.allowlist).read_text(encoding="utf-8"))), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        p.exit(2, str(exc)+"\n")
