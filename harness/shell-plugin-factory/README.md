# Tessl Shell Plugin Factory

Fork-scoped S4-style harness for `tdg-ninja/shell-plugins`. It turns a GitHub issue into a Tessl cloud factory run that builds requested shell-plugin integrations, validates them with this repo's gates, and reports or opens a fork PR for human review.

## What this is

- **Request surface:** GitHub issue template `.github/ISSUE_TEMPLATE/5-shell-plugin-factory.yml`.
- **Automation surface:** GitHub workflow `.github/workflows/tessl-shell-plugin-factory.yml`.
- **Agent skill:** local Tessl plugin `harness/shell-plugin-factory/plugin#run-shell-plugin-factory`.
- **Implementation recipe:** installed `tessl-gtm/1password-shell-plugin-codex#author-shell-plugin`.
- **Evidence:** per-run files under `harness/shell-plugin-factory/reports/<github-run-id>/`, uploaded as Actions artifacts.

## Flow

```text
GitHub issue or workflow_dispatch
  → normalized request.json
  → tessl launch skill file:harness/shell-plugin-factory/plugin#run-shell-plugin-factory --cloud
  → one target plugin per requested CLI
  → make <target>/validate + make test
  → retry up to 3 attempts or escalate
  → summary.md + run.json/events/logs
  → issue comment and optional fork PR
```

## Modes

- **report:** run the factory and comment back with outcomes/evidence.
- **pr:** run the factory, push a branch in `tdg-ninja/shell-plugins`, and open a PR against fork `main` if at least one target is built.

Neither mode merges code or opens upstream `1Password/shell-plugins` PRs.

## GitHub setup

Required labels:

- `tessl:shell-plugin-factory` — triggers the unified factory workflow from issues.

Required secret:

- `TESSL_TOKEN` — Tessl API key for workspace `tessl-gtm` with `publisher` role or higher, because Tessl cloud launches require publisher permission.

Workflow display name:

- `tessl - Shell Plugin Factory`

## Run manually

```bash
gh workflow run tessl-shell-plugin-factory.yml \
  --repo tdg-ninja/shell-plugins \
  --ref main \
  -f targets="railway" \
  -f mode="pr" \
  -f agent="claude-code" \
  -f workspace="tessl-gtm"
```

## Guardrails

- Fork-only: target `tdg-ninja/shell-plugins`, not upstream.
- Target edits only: `plugins/<target>/` for each requested target.
- Never hand-edit generated registry files.
- Never call a target built unless `make <target>/validate` and `make test` pass.
- Retry failures up to 3 attempts, then escalate with evidence.
- Human gate remains final: no auto-merge.

## Files

- `plugin/skills/run-shell-plugin-factory/SKILL.md` — cloud agent factory instructions.
- `plugin/skills/triage-shell-plugin-request/SKILL.md` — request triage instructions.
- `bin/parse_request.py` — normalizes GitHub issue/manual inputs into `request.json`.
- `bin/render_summary.py` — renders the Actions summary and issue comment body.
- `reports/` — runtime output location; generated reports are uploaded by Actions.
