---
name: run-shell-plugin-factory
description: "Build requested 1Password shell plugins in a fork-scoped factory run: use author-shell-plugin for each target, run make gates, retry up to 3 times, and either open a fork PR or report escalation."
---

1. Confirm the repo is `tdg-ninja/shell-plugins` or another explicit fork, never upstream `1Password/shell-plugins`.
2. Read the request file named in the instructions; extract targets, mode (`report` or `pr`), issue number, and base branch.
3. For each target, use `tessl-gtm/1password-shell-plugin-codex#author-shell-plugin` as the implementation recipe.
4. For each target, allow edits only under `plugins/<target>/`; do not hand-edit `plugins/plugins.go` or `plugins/registry.json`.
5. Run `make <target>/validate` and `make test`; retry failures with gate output as feedback, bounded at 3 attempts.
6. If a target is unsuitable or still failing after 3 attempts, mark it escalated with the reason and evidence.
7. Write `harness/shell-plugin-factory/reports/<run-id>/run.json`, `events.jsonl`, `summary.md`, and per-target logs.
8. If mode is `pr` and at least one target is built, push a branch in the fork and open a PR against the fork base branch only.
9. Comment on the source issue with the summary, PR URL if any, escalations, and links to run evidence.
10. Do not merge, open upstream PRs, or weaken gates to make a run pass.
