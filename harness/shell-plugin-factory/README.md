# Shell Plugin Factory Harness

Local S4-shaped factory loop for the fork checkout at `tdg-ninja/shell-plugins` (`origin`), not for direct changes to upstream `1Password/shell-plugins`.

It composes the installed `author-shell-plugin` skill through Tessl cloud/local agent execution, then runs the repository gates:

- `make <plugin>/validate`
- `make test`

If either gate fails, the factory contract is to feed the captured failure back to the agent and retry, bounded by 3 iterations. It records outcome, iterations, wall-clock time, agent logs, and final gate output in a standalone report.

## What was built

This demo has three GitHub-facing paths plus a local fallback:

- **Issue request surface:** `.github/ISSUE_TEMPLATE/5-shell-plugin-factory-demo.yml`
  - Lets a developer request target CLI integrations from GitHub.
  - `shell-plugin-factory` label triggers a cloud run/report.
  - `shell-plugin-factory-pr` label triggers a cloud run that attempts to open a fork PR.
- **Cloud report workflow:** `.github/workflows/shell-plugin-factory-cloud.yml`
  - Parses issue/manual targets.
  - Runs `tessl launch skill ... --cloud` in workspace `tessl-gtm`.
  - Comments cloud run status back on the issue.
- **Cloud PR workflow:** `.github/workflows/shell-plugin-factory-cloud-pr.yml`
  - Runs `tessl launch skill ... --cloud`.
  - Instructs the cloud agent to build plugins, validate gates, push a branch, and open a PR in `tdg-ninja/shell-plugins` only.
- **Receipt workflow:** `.github/workflows/shell-plugin-factory-demo.yml`
  - Creates the screenshot-friendly Actions summary / PR comment.
  - Re-runs deterministic `make <plugin>/validate` checks for generated plugin dirs.
  - Uploads report/log artifacts.
- **Harness scripts and docs:** `harness/shell-plugin-factory/`
  - `factory.py` — local bounded retry harness.
  - `cloud-agent-instructions.md` — cloud report-run instructions.
  - `cloud-pr-instructions.md` — cloud PR-run instructions.
  - `parse_issue_targets.py` — parses target lists from issue forms or workflow inputs.
  - `github-summary.py` — renders the Actions/PR summary markdown.
  - `GITHUB_DEMO.md` — walkthrough and talk track.
- **Generated demo plugin outputs:** `plugins/supabase/`, `plugins/planetscale/`, `plugins/render/`.
- **Captured local run evidence:** `harness/shell-plugin-factory/runs/20260722-215003/` and `harness/shell-plugin-factory/latest-report.md`.

## Working GitHub examples

- **Cloud report issue:** https://github.com/tdg-ninja/shell-plugins/issues/2
- **Successful cloud report run:** https://github.com/tdg-ninja/shell-plugins/actions/runs/30010433505
- **Cloud PR issue:** https://github.com/tdg-ninja/shell-plugins/issues/3
- **Successful cloud PR run:** https://github.com/tdg-ninja/shell-plugins/actions/runs/30011066728
- **Fork PR from cloud-generated branch:** https://github.com/tdg-ninja/shell-plugins/pull/4

## GitHub demo

Use GitHub as the primary visual surface: Issue template, Tessl cloud run, PR/check run, Actions summary, sticky PR comment, and uploaded artifacts. See `harness/shell-plugin-factory/GITHUB_DEMO.md`.

Required GitHub secret: `TESSL_TOKEN` for a `tessl-gtm` API key with `publisher` role or higher, because Tessl cloud launches require publisher permission.

After pushing the branch to the fork, launch the cloud factory run:

```bash
gh workflow run shell-plugin-factory-cloud.yml --ref <branch> -f targets="supabase, planetscale, render" -f agent="claude-code" -f workspace="tessl-gtm"
```

Run the receipt workflow:

```bash
gh workflow run shell-plugin-factory-demo.yml --ref <branch>
```

## Local fallback demo

```bash
bash harness/shell-plugin-factory/demo.sh
```

This shows fork scope, the composed skill, the latest report, run artifacts, generated plugin file shape, and a live `make render/validate` gate.

## Reset demo artifacts

Dry-run first:

```bash
bash harness/shell-plugin-factory/reset-demo.sh
```

Apply after confirmation:

```bash
bash harness/shell-plugin-factory/reset-demo.sh --apply
```

This removes generated plugin directories and run reports, but keeps the harness scripts, README, and demo skill.

## Run the full factory

```bash
python3 harness/shell-plugin-factory/factory.py supabase planetscale render
```

Optional:

```bash
python3 harness/shell-plugin-factory/factory.py --max-iterations 3 supabase
```

Reports are written to `harness/shell-plugin-factory/runs/<timestamp>/final-report.md`, with a copy at `harness/shell-plugin-factory/latest-report.md`.

## Guardrails

- The agent prompt only authorizes edits under `plugins/<target>/`.
- The harness detects agent edits outside that target directory and treats them as retry/escalation evidence.
- The harness does not commit, push, open PRs, or mark a plugin built unless both make gates exit 0.
- `make <plugin>/validate` regenerates registry files; the harness captures gate output and restores outside-target generated drift afterward so the final working tree remains target-scoped for human review.
