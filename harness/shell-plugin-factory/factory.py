#!/usr/bin/env python3
"""Run a bounded Tessl-agent shell-plugin factory loop.

The harness composes the installed author-shell-plugin skill for one target at a
term, validates with the repository make gates, and retries failures up to a
bounded iteration count. It leaves plugin directories as an inspectable working
tree and writes a standalone report under this harness directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
HARNESS_DIR = ROOT / "harness" / "shell-plugin-factory"
RUNS_DIR = HARNESS_DIR / "runs"
DEFAULT_SKILL = ROOT / ".tessl" / "plugins" / "tessl-gtm" / "1password-shell-plugin-codex" / "skills" / "author-shell-plugin" / "SKILL.md"
DEFAULT_TARGETS = ["supabase", "planetscale", "render"]
MAX_LOG_CHARS_FOR_PROMPT = 12000


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def slug_ts() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def run_cmd(cmd: List[str], *, timeout: int | None = None, input_text: str | None = None) -> Tuple[int, str]:
    started = now_iso()
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        output = proc.stdout
        code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode(errors="replace")
        output = partial + f"\n[TIMEOUT after {timeout}s]\n"
        code = 124
    rendered = f"$ {shlex.join(cmd)}\n# started: {started}\n# exit: {code}\n\n{output}"
    return code, rendered


def git_status_map() -> Dict[str, str]:
    code, out = run_cmd(["git", "status", "--porcelain=v1", "-z"], timeout=30)
    if code != 0:
        raise RuntimeError(out)
    raw = out.split("\n\n", 1)[-1]
    entries = raw.split("\0")
    status: Dict[str, str] = {}
    i = 0
    while i < len(entries):
        entry = entries[i]
        if not entry:
            i += 1
            continue
        code_part = entry[:2]
        path = entry[3:]
        if code_part.startswith("R") or code_part.startswith("C"):
            # Porcelain -z emits the destination followed by the source.
            status[path] = code_part
            i += 2
            continue
        status[path] = code_part
        i += 1
    return status


def path_allowed_for_agent(path: str, target: str) -> bool:
    return path == f"plugins/{target}" or path.startswith(f"plugins/{target}/")


def status_delta(before: Dict[str, str], after: Dict[str, str]) -> Dict[str, Tuple[str | None, str | None]]:
    keys = set(before) | set(after)
    return {k: (before.get(k), after.get(k)) for k in sorted(keys) if before.get(k) != after.get(k)}


def restore_generated_and_other_gate_drift(target: str, baseline: Dict[str, str], log_path: Path) -> None:
    """Undo tracked/untracked changes outside plugin target caused by make gates.

    This keeps the final tree human-reviewable while still capturing the gate
    output that observed generated registry behavior.
    """
    current = git_status_map()
    delta = status_delta(baseline, current)
    outside = [p for p in delta if not path_allowed_for_agent(p, target) and not p.startswith("harness/shell-plugin-factory/")]
    if not outside:
        return

    lines = ["# Restoring outside-target gate drift", ""]
    for p in outside:
        before, after = delta[p]
        lines.append(f"- {p}: {before!r} -> {after!r}")
        abs_path = ROOT / p
        if after == "??":
            # Only remove untracked paths created during this target, never pre-existing untracked files.
            if before is None and abs_path.exists():
                if abs_path.is_dir():
                    subprocess.run(["rm", "-rf", str(abs_path)], cwd=ROOT)
                else:
                    abs_path.unlink()
        else:
            subprocess.run(["git", "restore", "--", p], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log_path.write_text("\n".join(lines) + "\n")


def write_prompt(target: str, iteration: int, run_dir: Path, previous_failure_path: Path | None) -> Path:
    plugin_dir = f"plugins/{target}/"
    lines = [
        f"Build the {target} shell plugin in this repository.",
        "Use only the loaded author-shell-plugin skill as the shell-plugin recipe.",
        f"Only create or edit files under {plugin_dir}.",
        "Do not commit, push, open a PR, or edit generated registry files by hand.",
        "If the CLI is out of scope for the skill, write a short explanation in the final response and do not create a plugin.",
    ]
    if previous_failure_path is not None:
        rel = previous_failure_path.relative_to(ROOT)
        lines.extend([
            "",
            f"This is retry iteration {iteration}. Read {rel} first, fix only the reported issues, and keep all edits inside {plugin_dir}.",
        ])
    lines.append("")
    lines.append("End with a concise summary of what you changed and any ambiguity or escalation reason.")
    prompt_path = run_dir / f"{target}-iteration-{iteration}-prompt.md"
    prompt_path.write_text("\n".join(lines) + "\n")
    return prompt_path


def call_tessl_agent(target: str, iteration: int, run_dir: Path, skill_path: Path, previous_failure_path: Path | None) -> Tuple[int, Path, str]:
    prompt_path = write_prompt(target, iteration, run_dir, previous_failure_path)
    rel_prompt = prompt_path.relative_to(ROOT)
    cmd = [
        "tessl", "agent", "--print", "--output", "text", "--no-session", "--permission-mode", "yolo",
        "--no-skills", "--skill", str(skill_path),
        f"Read {rel_prompt} and complete the requested bounded shell-plugin task.",
    ]
    code, out = run_cmd(cmd, timeout=3600, input_text="")
    out_path = run_dir / f"{target}-iteration-{iteration}-agent.log"
    out_path.write_text(out)
    return code, out_path, out


def run_gates(target: str, iteration: int, run_dir: Path) -> Tuple[bool, Path, str, str]:
    validate_code, validate_out = run_cmd(["make", f"{target}/validate"], timeout=900)
    validate_path = run_dir / f"{target}-iteration-{iteration}-validate.log"
    validate_path.write_text(validate_out)

    test_code, test_out = run_cmd(["make", "test"], timeout=1800)
    test_path = run_dir / f"{target}-iteration-{iteration}-test.log"
    test_path.write_text(test_out)

    combined = (
        f"# Gate result for {target}, iteration {iteration}\n\n"
        f"- validate exit: {validate_code}\n"
        f"- test exit: {test_code}\n"
        f"- validate log: {validate_path.relative_to(ROOT)}\n"
        f"- test log: {test_path.relative_to(ROOT)}\n\n"
        "## validate output\n\n```text\n" + validate_out[-MAX_LOG_CHARS_FOR_PROMPT:] + "\n```\n\n"
        "## test output\n\n```text\n" + test_out[-MAX_LOG_CHARS_FOR_PROMPT:] + "\n```\n"
    )
    failure_path = run_dir / f"{target}-iteration-{iteration}-failure.md"
    if validate_code != 0 or test_code != 0:
        failure_path.write_text(combined)
    return validate_code == 0 and test_code == 0, failure_path, validate_out, test_out


def final_outputs_for_target(target: str, iteration: int, run_dir: Path) -> Tuple[str, str]:
    validate_path = run_dir / f"{target}-iteration-{iteration}-validate.log"
    test_path = run_dir / f"{target}-iteration-{iteration}-test.log"
    return validate_path.read_text() if validate_path.exists() else "", test_path.read_text() if test_path.exists() else ""


def run_target(target: str, run_dir: Path, skill_path: Path, max_iterations: int) -> Dict[str, object]:
    target_start = time.monotonic()
    result: Dict[str, object] = {
        "target": target,
        "started_at": now_iso(),
        "outcome": "escalated",
        "iterations_used": 0,
        "wall_clock_seconds": None,
        "agent_logs": [],
        "validate_log": None,
        "test_log": None,
        "scope_violations": [],
        "escalation_reason": None,
    }
    previous_failure: Path | None = None

    for iteration in range(1, max_iterations + 1):
        result["iterations_used"] = iteration
        baseline = git_status_map()
        agent_code, agent_log_path, _ = call_tessl_agent(target, iteration, run_dir, skill_path, previous_failure)
        result["agent_logs"].append(str(agent_log_path.relative_to(ROOT)))

        after_agent = git_status_map()
        delta = status_delta(baseline, after_agent)
        violations = [p for p in delta if not path_allowed_for_agent(p, target) and not p.startswith("harness/shell-plugin-factory/")]
        if violations:
            result["scope_violations"].extend(violations)
            violation_path = run_dir / f"{target}-iteration-{iteration}-scope-violation.md"
            violation_path.write_text("\n".join(["# Scope violation", "", *[f"- {p}: {delta[p][0]!r} -> {delta[p][1]!r}" for p in violations]]) + "\n")
            previous_failure = violation_path
            if iteration == max_iterations:
                result["escalation_reason"] = "Agent touched files outside the target plugin directory."
            continue

        if agent_code != 0:
            failure_path = run_dir / f"{target}-iteration-{iteration}-agent-failure.md"
            failure_path.write_text(f"# Agent command failed\n\nSee {agent_log_path.relative_to(ROOT)}.\n")
            previous_failure = failure_path
            if iteration == max_iterations:
                result["escalation_reason"] = "tessl agent command returned a non-zero exit code."
            continue

        gate_baseline = git_status_map()
        gates_ok, failure_path, validate_out, test_out = run_gates(target, iteration, run_dir)
        restore_log = run_dir / f"{target}-iteration-{iteration}-restore.log"
        restore_generated_and_other_gate_drift(target, gate_baseline, restore_log)

        result["validate_log"] = str((run_dir / f"{target}-iteration-{iteration}-validate.log").relative_to(ROOT))
        result["test_log"] = str((run_dir / f"{target}-iteration-{iteration}-test.log").relative_to(ROOT))

        if gates_ok:
            result["outcome"] = "built"
            result["escalation_reason"] = None
            break

        previous_failure = failure_path
        if iteration == max_iterations:
            result["escalation_reason"] = "Repo make gate still failed after the bounded retry budget."

    result["finished_at"] = now_iso()
    result["wall_clock_seconds"] = round(time.monotonic() - target_start, 1)
    return result


def make_report(run_dir: Path, results: List[Dict[str, object]], max_iterations: int) -> Path:
    report_path = run_dir / "final-report.md"
    lines: List[str] = [
        "# Shell Plugin Factory Harness Report",
        "",
        f"- **Run directory:** `{run_dir.relative_to(ROOT)}`",
        "- **Repository scope:** fork checkout `tdg-ninja/shell-plugins` (`origin`), not direct changes to upstream `1Password/shell-plugins`.",
        f"- **Started targets:** {', '.join(str(r['target']) for r in results)}",
        f"- **Retry budget:** {max_iterations} iterations per target",
        f"- **Skill:** `{DEFAULT_SKILL.relative_to(ROOT)}`",
        f"- **Generated at:** {now_iso()}",
        "",
        "## Summary",
        "",
    ]
    for r in results:
        lines.append(f"- **{r['target']}**: {r['outcome']} in {r['iterations_used']} iteration(s), {r['wall_clock_seconds']}s")
        if r.get("escalation_reason"):
            lines.append(f"  - Escalation reason: {r['escalation_reason']}")
        if r.get("scope_violations"):
            lines.append(f"  - Scope violations: {', '.join(r['scope_violations'])}")
    lines.extend([
        "",
        "## Per-target details",
        "",
    ])
    for r in results:
        target = str(r["target"])
        lines.extend([
            f"### {target}",
            "",
            f"- **Outcome:** {r['outcome']}",
            f"- **Iterations used:** {r['iterations_used']}",
            f"- **Wall-clock time:** {r['wall_clock_seconds']} seconds",
            f"- **Agent logs:** {', '.join('`' + p + '`' for p in r['agent_logs'])}",
            f"- **Validate log:** `{r.get('validate_log')}`",
            f"- **Test log:** `{r.get('test_log')}`",
        ])
        if r.get("escalation_reason"):
            lines.append(f"- **Escalation reason:** {r['escalation_reason']}")
        if r.get("scope_violations"):
            lines.append(f"- **Scope violations:** {', '.join(r['scope_violations'])}")
        lines.extend(["", "#### Final validate output", ""])
        validate_text = ""
        if r.get("validate_log") and (ROOT / str(r["validate_log"])).exists():
            validate_text = (ROOT / str(r["validate_log"])).read_text()
        lines.extend(["```text", validate_text[-20000:] if validate_text else "(no validate run captured)", "```", ""])
        lines.extend(["#### Final test output", ""])
        test_text = ""
        if r.get("test_log") and (ROOT / str(r["test_log"])).exists():
            test_text = (ROOT / str(r["test_log"])).read_text()
        lines.extend(["```text", test_text[-20000:] if test_text else "(no test run captured)", "```", ""])
    lines.extend([
        "## Deviations and observations",
        "",
        "- This harness is a local script rather than a packaged Tessl plugin because the proof only needs one repository-specific loop tonight.",
        "- `make <plugin>/validate` regenerates registry files as part of the repo's own gate; the harness captures that output and restores outside-target generated drift afterward so the final working tree stays human-gated and target-scoped.",
        "- Tessl-agent behavior notes should be added by the operator after reviewing the agent logs for this run.",
        "",
    ])
    report_path.write_text("\n".join(lines))
    json_path = run_dir / "results.json"
    json_path.write_text(json.dumps(results, indent=2) + "\n")
    latest_path = HARNESS_DIR / "latest-report.md"
    latest_path.write_text(report_path.read_text())
    return report_path


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the shell-plugin factory harness.")
    parser.add_argument("targets", nargs="*", default=DEFAULT_TARGETS, help="Plugin target names, e.g. supabase planetscale render")
    parser.add_argument("--max-iterations", type=int, default=3, help="Retry budget per target")
    parser.add_argument("--skill", type=Path, default=DEFAULT_SKILL, help="author-shell-plugin SKILL.md path")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)
    if not args.skill.exists():
        print(f"Skill not found: {args.skill}", file=sys.stderr)
        return 2
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_dir = RUNS_DIR / slug_ts()
    run_dir.mkdir(parents=True)

    results: List[Dict[str, object]] = []
    for target in args.targets:
        results.append(run_target(target.lower(), run_dir, args.skill.resolve(), args.max_iterations))
        report_path = make_report(run_dir, results, args.max_iterations)
        print(f"Updated report: {report_path.relative_to(ROOT)}")

    print(f"Final report: {report_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
