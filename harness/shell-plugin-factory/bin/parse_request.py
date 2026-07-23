#!/usr/bin/env python3
"""Create a normalized shell-plugin factory request JSON from GitHub inputs."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

TARGET_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$|^[a-z0-9]$")


def issue_field(body: str, heading: str) -> str:
    marker = f"### {heading}"
    start = body.find(marker)
    if start == -1:
        return ""
    rest = body[start + len(marker):]
    nxt = rest.find("\n### ")
    if nxt != -1:
        rest = rest[:nxt]
    return rest.strip()


def split_targets(raw: str) -> List[str]:
    out: List[str] = []
    for part in re.split(r"[,\n]", raw):
        target = part.strip().lower().removeprefix("plugins/").strip("/ ")
        if not target:
            continue
        if not TARGET_RE.match(target):
            raise SystemExit(f"invalid target name: {target}")
        if target not in out:
            out.append(target)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--targets", default=os.environ.get("TARGETS", ""))
    p.add_argument("--mode", default=os.environ.get("MODE", ""))
    p.add_argument("--issue-number", default=os.environ.get("ISSUE_NUMBER", ""))
    p.add_argument("--issue-title", default=os.environ.get("ISSUE_TITLE", ""))
    p.add_argument("--issue-body", default=os.environ.get("ISSUE_BODY", ""))
    p.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    p.add_argument("--base-branch", default=os.environ.get("BASE_BRANCH", "main"))
    p.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", "local"))
    args = p.parse_args()

    raw_targets = args.targets or issue_field(args.issue_body, "Target CLI integrations")
    targets = split_targets(raw_targets)
    if not targets:
        raise SystemExit("no target CLI integrations found")

    requested_mode = (args.mode or issue_field(args.issue_body, "Requested mode")).lower()
    mode = "pr" if "pr" in requested_mode or "pull" in requested_mode else "report"

    request: Dict[str, Any] = {
        "run_id": args.run_id,
        "repo": args.repo,
        "fork_scope": "tdg-ninja/shell-plugins",
        "base_branch": args.base_branch,
        "mode": mode,
        "targets": targets,
        "issue": {
            "number": args.issue_number,
            "title": args.issue_title,
        },
        "acceptance_gates": ["make <target>/validate", "make test"],
        "guardrails": [
            "fork-only",
            "no upstream PR",
            "no auto-merge",
            "only edit plugins/<target>/ for target work",
            "do not hand-edit generated registry files",
        ],
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(request, indent=2) + "\n")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"targets={json.dumps(targets)}\n")
            fh.write(f"target_list={', '.join(targets)}\n")
            fh.write(f"mode={mode}\n")
            fh.write(f"request_file={out}\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
