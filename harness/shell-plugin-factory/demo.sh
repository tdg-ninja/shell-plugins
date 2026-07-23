#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

REPORT="harness/shell-plugin-factory/latest-report.md"
RENDER_VALIDATE_LOG="harness/shell-plugin-factory/runs/20260722-215003/render-iteration-1-validate.log"

echo "# Shell Plugin Factory Demo"
echo
echo "## 1. Fork scope"
git remote -v | sed -n '1,4p'
echo
echo "This demo is scoped to origin=tdg-ninja/shell-plugins, not direct upstream changes."
echo
echo "## 2. Local Tessl skill being composed"
echo ".tessl/plugins/tessl-gtm/1password-shell-plugin-codex/skills/author-shell-plugin/SKILL.md"
sed -n '1,80p' .tessl/plugins/tessl-gtm/1password-shell-plugin-codex/skills/author-shell-plugin/SKILL.md
echo
echo "## 3. Factory harness"
sed -n '1,120p' harness/shell-plugin-factory/README.md
echo
echo "## 4. Latest report summary"
if [[ -f "$REPORT" ]]; then
  sed -n '1,80p' "$REPORT"
else
  echo "No latest report found. Run: python3 harness/shell-plugin-factory/factory.py supabase planetscale render"
fi
echo
echo "## 5. Observable run artifacts"
if [[ -d harness/shell-plugin-factory/runs ]]; then
  find harness/shell-plugin-factory/runs -maxdepth 2 -type f | sort | sed -n '1,80p'
else
  echo "No runs directory found."
fi
echo
echo "## 6. Generated Render plugin file shape"
if [[ -d plugins/render ]]; then
  find plugins/render -maxdepth 2 -type f | sort
else
  echo "plugins/render is not present."
fi
echo
echo "## 7. Live deterministic gate"
if [[ -d plugins/render ]]; then
  make render/validate
else
  echo "Skipping make render/validate because plugins/render is not present."
fi
