# Shell Plugin Factory Cloud PR Instructions

You are running inside a Tessl cloud sandbox for the `tdg-ninja/shell-plugins` fork.

## Objective

For each requested target CLI integration, use the installed `author-shell-plugin` skill to add exactly one shell plugin, validate it with the repository gates, then open a pull request against the fork only.

## Inputs

- Target list: provided by the GitHub issue or manual workflow dispatch.
- Skill recipe: `tessl-gtm/1password-shell-plugin-codex#author-shell-plugin`.
- Scope: fork only. Do not open or target upstream `1Password/shell-plugins`.

## Rules

- Create a branch in `tdg-ninja/shell-plugins` named `factory/shell-plugin-<issue-or-run-id>`.
- Only create or edit files under each target's own `plugins/<target>/` directory.
- Do not hand-edit `plugins/plugins.go` or `plugins/registry.json`.
- Do not merge the PR.
- Do not open an upstream PR.
- Do not call a target built unless both gates pass:
  - `make <target>/validate`
  - `make test`
- Retry failed targets with gate output as feedback, bounded at 3 iterations.
- If a target is unsuitable or still failing after 3 iterations, mark it escalated and explain why in the PR or issue comment.
- Use fake fixture values that cannot be mistaken for real provider tokens by GitHub secret scanning.

## PR requirements

Open one PR against `tdg-ninja/shell-plugins:main` with:

- Title: `Add shell plugins: <target list>`
- Body including:
  - source GitHub issue, if provided
  - per-target outcome
  - iterations used
  - final `make <target>/validate` result
  - final `make test` result
  - files changed
  - substitutions, ambiguity, or escalation reasons
  - confirmation that no upstream PR was opened

## Report back

Comment on the source issue, if provided, with:

- PR URL, if opened
- any escalated targets
- gate summary
- link to the Tessl/GitHub Actions run if available
