<!-- shell-plugin-factory-demo-summary -->
# Shell Plugin Factory Demo

This is a GitHub-visible receipt for a fork-scoped factory run in `tdg-ninja/shell-plugins`.
It does **not** automate direct changes to upstream `1Password/shell-plugins`.

## Demo objective

Show the development process moving from a one-off agent run to a governed factory loop:

```text
GitHub issue / target list
  → Tessl cloud sandbox
  → tessl agent + author-shell-plugin
  → generated plugin working tree
  → make gates
  → bounded retry or escalation
  → PR check, summary, comment, artifacts
```

## At a glance

- **Before:** manual prompt, manual validation, terminal-only evidence.
- **After:** GitHub-triggered Tessl cloud sandbox, explicit skill loading, repo gates, retry budget, audit report.
- **Human gate:** the harness does not commit, push, merge, or open upstream PRs.

## Factory result

- ✅ **supabase**
  - Outcome: `built`
  - Iterations: `1/3`
  - Wall-clock: `142.0s`
  - Validate log: `harness/shell-plugin-factory/runs/20260722-215003/supabase-iteration-1-validate.log`
  - Test log: `harness/shell-plugin-factory/runs/20260722-215003/supabase-iteration-1-test.log`
- ✅ **planetscale**
  - Outcome: `built`
  - Iterations: `1/3`
  - Wall-clock: `185.5s`
  - Validate log: `harness/shell-plugin-factory/runs/20260722-215003/planetscale-iteration-1-validate.log`
  - Test log: `harness/shell-plugin-factory/runs/20260722-215003/planetscale-iteration-1-test.log`
- ✅ **render**
  - Outcome: `built`
  - Iterations: `1/3`
  - Wall-clock: `140.5s`
  - Validate log: `harness/shell-plugin-factory/runs/20260722-215003/render-iteration-1-validate.log`
  - Test log: `harness/shell-plugin-factory/runs/20260722-215003/render-iteration-1-test.log`

## GitHub evidence

- **PR check:** this workflow is visible in the normal review flow.
- **Job summary:** the Actions summary is the screenshot-friendly view.
- **Sticky comment:** pull requests get this same summary as a comment.
- **Artifacts:** the full report and per-target logs are uploaded for inspection.
- **Cloud run:** issue-driven target batches can launch `tessl launch skill --cloud`, so requesters do not need local agent CLIs, Go tooling, or repo dependencies.
- **Live gate:** the receipt job re-runs deterministic `make <plugin>/validate` checks when generated plugin directories are present.

## Re-run locally

```bash
bash harness/shell-plugin-factory/demo.sh
```

Full factory run, if runtime variability is acceptable:

```bash
python3 harness/shell-plugin-factory/factory.py supabase planetscale render
```

