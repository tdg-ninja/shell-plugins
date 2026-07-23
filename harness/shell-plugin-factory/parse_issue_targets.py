#!/usr/bin/env python3
"""Parse shell-plugin factory target names from workflow input or issue-form body."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import List

TARGET_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$|^[a-z0-9]$")


def split_targets(raw: str) -> List[str]:
    targets: List[str] = []
    for part in re.split(r"[,\n]", raw):
        target = part.strip().lower()
        if not target or target.startswith("-") and "[" in target:
            continue
        target = target.removeprefix("plugins/").strip("/ ")
        if target and target not in targets:
            targets.append(target)
    return targets


def issue_form_field(body: str, heading: str) -> str:
    marker = f"### {heading}"
    start = body.find(marker)
    if start == -1:
        return ""
    rest = body[start + len(marker) :]
    next_heading = rest.find("\n### ")
    if next_heading != -1:
        rest = rest[:next_heading]
    return rest.strip()


def main() -> int:
    raw = os.environ.get("TARGETS", "").strip()
    if not raw:
        raw = issue_form_field(os.environ.get("ISSUE_BODY", ""), "Target CLI integrations")

    targets = split_targets(raw)
    invalid = [target for target in targets if not TARGET_RE.match(target)]
    if invalid:
        print(f"Invalid target name(s): {', '.join(invalid)}", file=sys.stderr)
        return 2
    if not targets:
        print("No target CLI integrations found.", file=sys.stderr)
        return 2

    print(json.dumps(targets))

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"targets={json.dumps(targets)}\n")
            fh.write(f"target_list={', '.join(targets)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
