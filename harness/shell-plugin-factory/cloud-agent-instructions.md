# Shell Plugin Factory Cloud Run Instructions

You are running inside a Tessl cloud sandbox for the `tdg-ninja/shell-plugins` fork.

## Objective

For each requested target CLI integration, use the installed `author-shell-plugin` skill to add exactly one shell plugin under `plugins/<target>/`, then run the repository gates and report the outcome.

## Inputs

- Target list: provided by the GitHub issue or manual workflow dispatch.
- Skill recipe: `tessl-gtm/1password-shell-plugin-codex#author-shell-plugin`.
- Scope: fork only. Do not open or target upstream `1Password/shell-plugins`.

## Rules

- Only create or edit files under each target's own `plugins/<target>/` directory.
- Do not hand-edit `plugins/plugins.go` or `plugins/registry.json`.
- Do not commit, push, merge, or open upstream PRs unless the workflow explicitly asks for a fork PR.
- Do not call a target built unless both gates pass:
  - `make <target>/validate`
  - `make test`
- Retry failed targets with gate output as feedback, bounded at 3 iterations.
- If a target is unsuitable or still failing after 3 iterations, mark it escalated and explain why.
- Use fake fixture values that cannot be mistaken for real provider tokens by GitHub secret scanning.

## Report

Write a concise final report with:

- target
- outcome: built or escalated
- iterations used
- wall-clock time if available
- final validate output summary
- final test output summary
- files changed
- ambiguity, substitutions, or escalation reasons
