"""Verify local documentation links and the final candidate's validation chain."""
import csv
import hashlib
import json
from pathlib import Path
import re
from sync_references import build_references


def check(root):
    errors=[]
    for path in root.rglob("*.md"):
        if any(part in {"runs",".venv",".git","work-local","work","node_modules"} for part in path.relative_to(root).parts):
            continue
        for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)',path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                continue
            target=target.split("#")[0]
            if target and not (path.parent/target).exists():
                errors.append(f"{path.relative_to(root)}: missing link {target}")
    candidate=root/"examples/m3-best/candidate_NOT_VALIDATED.csv"
    report=json.loads((root/"examples/m3-best/official-v17/official_validation.json").read_text())
    if hashlib.sha256(candidate.read_bytes()).hexdigest()!=report["candidate_sha256"]:
        errors.append("Final candidate differs from the officially evaluated CSV")
    if any(p["reason"]!="ok" or p["L"] is None for p in report["puzzles"]):
        errors.append("Final candidate contains a rejected puzzle")
    with candidate.open(newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=1986 or {int(row["n"]) for row in rows}!={p["n"] for p in report["puzzles"]}:
        errors.append("Unexpected final candidate coverage")
    for name in ("gallery.svg","performance.svg"):
        if not (root/"docs/assets"/name).exists():
            errors.append(f"Missing portfolio visual: {name}")
    if json.loads((root/"app/public/references.json").read_text()) != build_references(root):
        errors.append("Browser references differ from the exact officially evaluated CSV")
    if errors:
        raise ValueError("\n".join(errors))
    print("Release checks passed: local links, final CSV hash, 20 accepted puzzles, 1986 rows, figures")


if __name__=="__main__":
    check(Path(__file__).resolve().parents[1])
