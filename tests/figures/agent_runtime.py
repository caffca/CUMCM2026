"""One bounded real custom-agent discovery test in an isolated synthetic repository."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


def snapshot(work):
    return {str(p.relative_to(work)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in work.rglob("*") if p.is_file() and ".git" not in p.parts}


def run(work):
    work = Path(work).resolve()
    root = Path(__file__).resolve().parents[2]
    if work.exists():
        raise ValueError("Use fresh scratch path")
    (work / ".codex/agents").mkdir(parents=True)
    shutil.copy2(root / ".codex/config.toml", work / ".codex/config.toml")
    for name in ("figure-designer.toml", "visual-critic.toml"):
        shutil.copy2(root / ".codex/agents" / name, work / ".codex/agents" / name)
    (work / "ignored-input.json").write_text('{"synthetic":true,"protected_value":42}', encoding="utf-8")
    (work / ".gitignore").write_text("ignored-input.json\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main", str(work)], check=True, capture_output=True)
    before = snapshot(work)
    prompt = """SYNTHETIC TEST ONLY. No writes, no network, no training, no installs, no Git changes.
Using project custom-agent discovery, call exactly figure_designer once, then visual_critic once
sequentially, not a generic substituted agent. Do not override their configured model/effort/sandbox.
For figure_designer give only this intentionally incomplete brief: figure_id=synthetic_missing,
purpose=check missing frozen input. It should return BLOCKED without writing. For visual_critic
give no image and request honest NOT_VISUALLY_VERIFIED, no fabricated inspection.
Wait for each response. Report whether the custom role was actually available, actual model,
effort, sandbox if runtime exposes them, and both returned statuses. Do not infer runtime model
from its own text. If role selection is unavailable say CONFIGURED_NOT_RUNTIME_VERIFIED and stop.
Do not spawn other roles or read anything outside this scratch repo."""
    command = [shutil.which("codex"), "--strict-config", "-C", str(work), "--ask-for-approval", "never",
               "exec", "--model", "gpt-5.6-sol", "-c", 'model_reasoning_effort="xhigh"',
               "--sandbox", "read-only", "--ephemeral", "--json", prompt]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    status = "FINISHED"
    try:
        stdout, stderr = process.communicate(timeout=150)
    except subprocess.TimeoutExpired:
        # Terminate only this explicitly launched CLI process and its descendants.
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
        stdout, stderr = process.communicate(timeout=15)
        status = "TIMEOUT"
    after = snapshot(work)
    evidence = work.parent / (work.name + "-evidence.json")
    evidence.write_text(json.dumps({"status":status,"exit_code":process.returncode,"cwd":str(work),
                        "requested_root_model":"gpt-5.6-sol","requested_root_effort":"xhigh",
                        "command":command[:-1],"stdout":stdout,"stderr":stderr,
                        "files_unchanged":before == after,"changed_paths":sorted(k for k in before.keys()|after.keys() if before.get(k)!=after.get(k))}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(evidence)
    print(status, "files_unchanged=", before == after)
    print(stdout[-16000:])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--work", required=True)
    run(p.parse_args().work)
