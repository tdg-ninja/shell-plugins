# Shell Plugin Factory Harness

Local S4-shaped factory loop for the fork checkout at `tdg-ninja/shell-plugins` (`origin`), not for direct changes to upstream `1Password/shell-plugins`.

It composes the installed `author-shell-plugin` skill through `tessl agent`, then runs the repository gates:

- `make <plugin>/validate`
- `make test`

If either gate fails, it feeds the captured failure back to `tessl agent` and retries, bounded by `--max-iterations` (default: 3). It records outcome, iterations, wall-clock time, agent logs, and final gate output in a standalone report.

## GitHub demo

Use GitHub as the primary visual surface: Issue template, Tessl cloud run, PR/check run, Actions summary, sticky PR comment, and uploaded artifacts. See `harness/shell-plugin-factory/GITHUB_DEMO.md`.

After pushing the branch to the fork, launch the cloud factory run:

```bash
gh workflow run shell-plugin-factory-cloud.yml --ref <branch> -f targets="supabase, planetscale, render" -f agent="tessl-agent" -f workspace="tessl-gtm"
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
