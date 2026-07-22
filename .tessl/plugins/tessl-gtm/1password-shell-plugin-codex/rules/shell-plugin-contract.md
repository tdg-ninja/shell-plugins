# Shell Plugin Contract

Governs any change under `plugins/<name>/` in `1Password/shell-plugins`. Sourced from the maintainers' own `CONTRIBUTING.md` and the structure of accepted plugins (`vercel`, `ngrok`, `fastly`).

## Scope
- In scope: CLIs that authenticate to **one** platform's backend (SaaS, cloud vendor, database).
- Out of scope: unofficial/community CLIs, and CLIs that authenticate to *different* backends depending on the project (`terraform`, `ansible`, framework CLIs like `flask run`). Do not start a plugin for these.

## Required file shape (one package per plugin, `plugins/<name>/`)
- `plugin.go` — `func New() schema.Plugin` registering `Name`, `Platform` (`Name`, `Homepage`), `Credentials`, `Executables`.
- `<name>.go` — `func <Name>CLI() schema.Executable` with `Runs`, `DocsURL`, a `NeedsAuth` predicate (always exclude help/version/no-args/login via `needsauth.NotForHelpOrVersion()`, `NotWithoutArgs()`, `NotWhenContainsArgs("login")` etc.), and `Uses` naming the credential.
- `<credential>.go` — `func <Name>() schema.CredentialType` with `Fields` (mark secrets `Secret: true`), a `DefaultProvisioner` (implements `Provision`/`Deprovision`/`Description`), and an `Importer` reading the CLI's real on-disk config or supporting env-var provisioning where the CLI documents one.
- `<credential>_test.go` — provisioner + importer tests using the SDK's `plugintest` package (`plugintest.TestProvisioner`, `plugintest.TestImporter`, `plugintest.LoadFixture`). Fixtures live in `test-fixtures/`.

## Hard rules
- **No new third-party dependencies** without strong justification — reviews slow down and are more likely rejected. Reading a file on disk should use the SDK's existing `importer` helpers, not a new library.
- **Commits must be signed** — unsigned commits cannot merge.
- **Every provisioner and importer needs a test** via `plugintest`, not ad hoc assertions.
- **Don't touch other plugins' files.** A new plugin is a new, isolated directory — it must not require edits to existing plugin packages.
- `plugins/plugins.go` and `plugins/registry.json` are generated (`make registry`) — never hand-edit them.

## Release gate (this is the maintainers' actual bar, not Tessl's)
A plugin is only real once both of these are clean:
```
make <plugin>/validate   # regenerates the registry, then validates schema + wiring
make test                 # go test ./... — runs every plugin's plugintest suite
```
Nothing "graduates" — i.e. nothing should be presented as done — until both commands exit 0.
