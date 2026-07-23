#!/usr/bin/env python3
"""Render the shell-plugin factory result as GitHub Actions summary markdown."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = ROOT / "harness" / "shell-plugin-factory" / "runs" / "20260722-215003" / "results.json"
LATEST_REPORT = ROOT / "harness" / "shell-plugin-factory" / "latest-report.md"
COMMENT_MARKER = "<!-- shell-plugin-factory-demo-summary -->"


def load_results(path: Path) -> List[Dict[str, Any]]:
    if path.exists():
        return json.loads(path.read_text())
    return []


def status_icon(result: Dict[str, Any]) -> str:
    return "✅" if result.get("outcome") == "built" else "⚠️"


def render(results: List[Dict[str, Any]], validate_summary: str = "") -> str:
    lines: List[str] = [
        COMMENT_MARKER,
        "# Shell Plugin Factory Demo",
        "",
        "This is a GitHub-visible receipt for a fork-scoped factory run in `tdg-ninja/shell-plugins`.",
        "It does **not** automate direct changes to upstream `1Password/shell-plugins`.",
        "",
        "## Demo objective",
        "",
        "Show the development process moving from a one-off agent run to a governed factory loop:",
        "",
        "```text",
        "GitHub issue / target list",
        "  → Tessl cloud sandbox",
        "  → tessl agent + author-shell-plugin",
        "  → generated plugin working tree",
        "  → make gates",
        "  → bounded retry or escalation",
        "  → PR check, summary, comment, artifacts",
        "```",
        "",
        "## At a glance",
        "",
        "- **Before:** manual prompt, manual validation, terminal-only evidence.",
        "- **After:** GitHub-triggered Tessl cloud sandbox, explicit skill loading, repo gates, retry budget, audit report.",
        "- **Human gate:** the harness does not commit, push, merge, or open upstream PRs.",
        "",
        "## Factory result",
        "",
    ]

    if not results:
        lines.extend([
            "No `results.json` was found. Run the local factory first:",
            "",
            "```bash",
            "python3 harness/shell-plugin-factory/factory.py supabase planetscale render",
            "```",
            "",
        ])
    else:
        for result in results:
            target = result.get("target", "unknown")
            outcome = result.get("outcome", "unknown")
            iterations = result.get("iterations_used", "?")
            seconds = result.get("wall_clock_seconds", "?")
            lines.extend([
                f"- {status_icon(result)} **{target}**",
                f"  - Outcome: `{outcome}`",
                f"  - Iterations: `{iterations}/3`",
                f"  - Wall-clock: `{seconds}s`",
                f"  - Validate log: `{result.get('validate_log')}`",
                f"  - Test log: `{result.get('test_log')}`",
            ])
            if result.get("escalation_reason"):
                lines.append(f"  - Escalation: {result['escalation_reason']}")
        lines.append("")

    lines.extend([
        "## GitHub evidence",
        "",
        "- **PR check:** this workflow is visible in the normal review flow.",
        "- **Job summary:** the Actions summary is the screenshot-friendly view.",
        "- **Sticky comment:** pull requests get this same summary as a comment.",
        "- **Artifacts:** the full report and per-target logs are uploaded for inspection.",
        "- **Cloud run:** issue-driven target batches can launch `tessl launch skill --cloud`, so requesters do not need local agent CLIs, Go tooling, or repo dependencies.",
        "- **Live gate:** the receipt job re-runs deterministic `make <plugin>/validate` checks when generated plugin directories are present.",
        "",
    ])

    if validate_summary:
        lines.extend(["## Live validation in this Actions run", "", validate_summary.strip(), ""])

    lines.extend([
        "## Re-run locally",
        "",
        "```bash",
        "bash harness/shell-plugin-factory/demo.sh",
        "```",
        "",
        "Full factory run, if runtime variability is acceptable:",
        "",
        "```bash",
        "python3 harness/shell-plugin-factory/factory.py supabase planetscale render",
        "```",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    results_path = Path(os.environ.get("FACTORY_RESULTS", str(DEFAULT_RESULTS)))
    output_path = Path(os.environ.get("FACTORY_SUMMARY_OUT", "harness/shell-plugin-factory/github-summary.md"))
    validate_summary = os.environ.get("VALIDATE_SUMMARY", "")

    results = load_results(results_path)
    summary = render(results, validate_summary)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary + "\n")

    github_step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_step_summary:
        with open(github_step_summary, "a", encoding="utf-8") as fh:
            fh.write(summary + "\n")

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
