---
name: triage-shell-plugin-request
description: "Triage a GitHub issue requesting shell-plugin integrations: verify scope, normalize target names, choose report or PR mode, and prepare the request file for run-shell-plugin-factory."
---

1. Read the GitHub issue body or workflow inputs named in the instructions.
2. Extract target CLI names and normalize them to lowercase plugin directory names.
3. Confirm each target appears to authenticate to one platform backend; flag ambiguous targets for escalation.
4. Choose mode: `pr` only when the request explicitly asks for a fork PR; otherwise `report`.
5. Write a request JSON file with targets, mode, issue number, base branch, fork repo, and acceptance criteria.
6. Do not build plugins; hand off to `run-shell-plugin-factory`.
