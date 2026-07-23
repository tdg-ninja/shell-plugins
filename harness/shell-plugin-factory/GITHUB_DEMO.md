# GitHub Demo: Shell Plugin Factory

## What this demo proves

This is a **development-process demo** in the `tdg-ninja/shell-plugins` fork.

It shows a fork-scoped S4-style factory loop:

```text
GitHub issue / target list
  → Tessl cloud sandbox
  → tessl agent with author-shell-plugin
  → generated plugin working tree
  → make <plugin>/validate + make test
  → bounded retry or escalation
  → GitHub Actions summary / issue or PR comment / artifacts
```

It does **not** show direct upstream `1Password/shell-plugins` automation, auto-merge, or a Tessl-vs-non-Tessl benchmark.

## Before / after

- **Before:** one-off manual agent prompting, manual make-gate runs, manual retry decisions, terminal-only evidence.
- **After:** GitHub-triggered Tessl cloud sandbox, explicit skill loading, repo gates, bounded retry/escalation, and GitHub-visible evidence.

## Visual surface

Use GitHub, not the terminal:

1. **Issue template** — request/track a target batch:
   - `.github/ISSUE_TEMPLATE/5-shell-plugin-factory-demo.yml`
2. **Cloud workflow** — `Shell Plugin Factory Cloud Run`:
   - parses issue targets
   - launches `tessl launch skill --cloud`
   - comments back with the Tessl cloud run status and raw launch output
3. **Pull request or branch** — shows generated plugin dirs and harness files for human review.
4. **Receipt workflow** — `Shell Plugin Factory Demo`:
   - fork-scope check
   - factory result summary
   - live `make <plugin>/validate` evidence
   - uploaded logs/report artifacts
5. **PR comment** — sticky summary comment when the receipt workflow runs on a pull request.

## Talk track

1. "This is scoped to our fork, `tdg-ninja/shell-plugins`, not upstream."
2. "The request starts as a GitHub issue: here are the missing CLI targets."
3. "The GitHub issue launches a Tessl cloud sandbox, so the requester does not need local agent CLIs, Go tooling, or repo dependencies."
4. "The cloud agent composes the installed `author-shell-plugin` skill through `tessl agent`."
5. "The harness does not call anything done until the repo gates pass."
6. "The result is visible where developers already work: issue comment, PR check, job summary, sticky comment, and artifacts."
7. "The human still reviews the working tree; the harness does not push, merge, or open upstream PRs."

## Commands for setup / rerun

Manual cloud run after pushing the branch. Requires `TESSL_TOKEN` set in GitHub Actions secrets for a `tessl-gtm` API key with `publisher` role or higher:

```bash
gh workflow run shell-plugin-factory-cloud.yml --ref <branch> -f targets="supabase, planetscale, render" -f agent="tessl-agent" -f workspace="tessl-gtm"
```

Manual receipt run after pushing the branch:

```bash
gh workflow run shell-plugin-factory-demo.yml --ref <branch>
```

Local fallback if GitHub is unavailable:

```bash
bash harness/shell-plugin-factory/demo.sh
```

Full local factory run, only if runtime variability is acceptable:

```bash
python3 harness/shell-plugin-factory/factory.py supabase planetscale render
```
