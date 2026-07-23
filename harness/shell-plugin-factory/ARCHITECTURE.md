# Architecture

## Goal

Provide the shell-plugin version of 1Password's S4 harness: orchestrate the full suite for a requested integration, iterate on failures, and complete or escalate to the engineer.

## Surfaces

- **GitHub Issues:** request target CLI integrations.
- **GitHub Actions:** launch Tessl cloud, publish summary, upload artifacts.
- **Tessl plugin:** `harness/shell-plugin-factory/plugin` contains the factory skills.
- **Repo gates:** `make <target>/validate` and `make test` are the release bar.

## Control plane

The workflow creates a `request.json` with:

- repo and fork scope
- issue metadata
- targets
- mode: `report` or `pr`
- acceptance gates
- guardrails

The cloud skill reads that file and owns the loop.

## Data plane

Each target follows:

```text
attempt started
  → author-shell-plugin implementation
  → scope check
  → make <target>/validate
  → make test
  → pass, retry, or escalate
```

## Instrumentation contract

Each run should produce:

- `request.json` — normalized input.
- `launch.json` — Tessl cloud launch result.
- `summary.md` — human-readable result.
- `run.json` — structured target outcomes.
- `events.jsonl` — attempt/gate/retry/escalation events.
- per-target logs — agent, validate, and test output.

## Human gate

The harness may open a PR in the fork when mode is `pr`, but it never merges and never opens upstream PRs.
