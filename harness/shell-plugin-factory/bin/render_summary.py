#!/usr/bin/env python3
"""Render a GitHub summary from a factory request and optional cloud launch JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def load_json(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--launch", default="")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    request = load_json(args.request)
    launch = load_json(args.launch) if args.launch else {}
    targets = ", ".join(request.get("targets", []))
    mode = request.get("mode", "unknown")
    status = launch.get("status", "not-started")
    result = launch.get("result", {})
    failure = launch.get("failureReason", {})

    lines = [
        "# tessl - Shell Plugin Factory",
        "",
        f"- **Repository:** `{request.get('repo', '')}`",
        f"- **Fork scope:** `{request.get('fork_scope', 'tdg-ninja/shell-plugins')}`",
        f"- **Mode:** `{mode}`",
        f"- **Targets:** {targets}",
        f"- **Cloud launch status:** `{status}`",
        "",
        "## Contract",
        "",
        "- Uses `tessl-gtm/shell-plugin-factory#run-shell-plugin-factory` for orchestration.",
        "- Uses `tessl-gtm/1password-shell-plugin-codex#author-shell-plugin` for implementation.",
        "- Built targets must pass `make <target>/validate` and `make test`.",
        "- Fork-only: no upstream PR, no auto-merge.",
        "",
    ]
    if result:
        lines += ["## Result", "", result.get("summary", json.dumps(result, indent=2)), ""]
    if failure:
        lines += ["## Failure", "", "```json", json.dumps(failure, indent=2), "```", ""]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
