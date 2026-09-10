# Workspace Setup

## Current source of truth

All current work is performed in:

```text
C:\Users\ysw\Desktop\CUMCM2026
```

The repository is currently on `main`, with no configured GitHub remote. The
official problem and attachments have not yet been copied into the repository.

## Data placement

When D题 is brought into the workspace, keep an unchanged copy under:

```text
data/raw/D题/
├─ D题.pdf
└─ 附件/
   ├─ 附件1.xlsx
   └─ 附件2/
      ├─ result1.xlsx
      ├─ result2.xlsx
      ├─ result3.xlsx
      └─ result4.xlsx
```

`data/raw/` is read-only input. Cleaning, unit conversion and derived data go
to `data/processed/` through scripts. Do not overwrite the original files.

## Git boundary

Track source, tests, configuration, concise decisions, question summaries and
formal plot/table sources. Keep `.venv/`, `tmp/`, `data/raw/`,
`data/processed/`, `references/papers/`, caches and generated run outputs out
of normal Git history. Formal question results belong under `outputs/qX/`.

Use semantic local commits on `main` or a short-lived `codex/*` branch. Do not
use `git reset --hard`, `git clean -fd`, force push, rebase or automatic merge.

## GitHub connection

The remote cannot be configured until the exact GitHub repository URL is known.
After the URL is confirmed, add it explicitly and verify before pushing:

```powershell
git remote add origin https://github.com/<owner>/<repository>.git
git remote -v
git push -u origin main
```

The push is an external mutation and should be performed only after confirming
the repository owner/name and visibility. GitHub CLI is not currently installed;
HTTPS plus Git Credential Manager is the simplest expected path on this machine.
