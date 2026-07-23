---
name: author-shell-plugin
description: Use when adding a new shell plugin or integration to 1Password/shell-plugins, or when asked to create/scaffold a new plugin — scaffolds a compliant plugin.go / <name>.go / credential file / test, following the SDK's schema (the plugin's structure), provisioner (how a credential gets passed to the CLI), importer (how an existing local login gets picked up), and plugintest (the SDK's test helpers) conventions, then validates the result against the maintainers' own make <plugin>/validate and make test gates.
---

Follow the [shell-plugin-contract](../../rules/shell-plugin-contract.md) rule for the file shape and hard rules. This skill is the step-by-step execution of that contract for one new plugin.

## Steps

1. **Confirm scope.** The target CLI must authenticate to exactly one backend. If it doesn't, stop and say so instead of building it.
2. **Find the closest existing plugin to model.** Read 1–2 existing plugins under `plugins/` that use the same auth shape as your target:
   - Single static API token passed as a CLI flag → model on `plugins/vercel/`.
   - Single static API token via an environment variable the CLI documents → model on `plugins/ngrok/`'s `AddEnvVar` pattern.
   - Reuse `credname.APIToken` and `fieldname.Token` from `sdk/schema/credname` / `sdk/schema/fieldname` unless the CLI's own docs use different terminology.
3. **Write the four files** (`plugin.go`, `<name>.go`, the credential file, the test file) matching the shape in the contract rule. Use the CLI's real, documented auth mechanism — don't invent one.
4. **Add an importer** that reads the CLI's actual existing config file/location if it has one, so a user's existing login is picked up automatically. Use `importer.TryFile` / `importer.MacOnly` / `importer.LinuxOnly` as needed, matching how `vercel`'s importer is structured.
5. **Write the test fixture(s)** under `test-fixtures/` with a realistic (but fake) token value, then write `plugintest.TestProvisioner` and `plugintest.TestImporter` cases covering it.
6. **Validate against the maintainers' own gate, not just your own read of the code:**
   ```
   make <plugin>/validate
   make test
   ```
   Fix and re-run until both are clean. Do not report success before both exit 0 — paste the actual output.
7. **Do not touch any file outside `plugins/<name>/` and its own `test-fixtures/`.** If validation seems to require editing something else, that's a signal the plugin is scoped wrong — stop and reconsider scope rather than widening the change.
