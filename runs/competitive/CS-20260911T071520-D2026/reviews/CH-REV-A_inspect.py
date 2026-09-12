# Read-only inspection helper for independent Route Reviewer CH-REV-A.
# Prints JSON structure; never writes anything.
import json, sys, hashlib
from pathlib import Path

ROOT = Path(r"F:\2026 数模\D题重跑\D题\runs\competitive\CS-20260911T071520-D2026")

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def brief(obj, depth=0, max_depth=2):
    pad = "  " * depth
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and depth < max_depth:
                print(f"{pad}{k}: ({type(v).__name__}, len={len(v)})")
                brief(v, depth + 1, max_depth)
            else:
                s = json.dumps(v, ensure_ascii=False)
                if len(s) > 300: s = s[:300] + f"...<+{len(s)-300} chars>"
                print(f"{pad}{k}: {s}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:5]):
            if isinstance(v, (dict, list)) and depth < max_depth:
                print(f"{pad}[{i}] ({type(v).__name__}, len={len(v)})")
                brief(v, depth + 1, max_depth)
            else:
                s = json.dumps(v, ensure_ascii=False)
                if len(s) > 300: s = s[:300] + f"...<+{len(s)-300} chars>"
                print(f"{pad}[{i}]: {s}")
        if len(obj) > 5:
            print(f"{pad}... ({len(obj)-5} more items)")

cmd = sys.argv[1]
if cmd == "keys":
    p = ROOT / sys.argv[2]
    obj = load(p)
    brief(obj, max_depth=int(sys.argv[3]) if len(sys.argv) > 3 else 2)
elif cmd == "get":
    p = ROOT / sys.argv[2]
    obj = load(p)
    for part in sys.argv[3].split("."):
        if isinstance(obj, list):
            obj = obj[int(part)]
        else:
            obj = obj.get(part) if part in obj else (obj[part] if False else None)
            if obj is None:
                print("MISSING KEY:", part); sys.exit(1)
    s = json.dumps(obj, ensure_ascii=False, indent=2)
    lim = int(sys.argv[4]) if len(sys.argv) > 4 else 6000
    print(s[:lim])
    if len(s) > lim: print(f"...<truncated {len(s)-lim} chars>")
elif cmd == "sha":
    for rel in sys.argv[2:]:
        p = ROOT / rel
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        print(f"{h}  {rel}")
elif cmd == "shaabs":
    for rel in sys.argv[2:]:
        p = Path(rel)
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        print(f"{h}  {rel}")
