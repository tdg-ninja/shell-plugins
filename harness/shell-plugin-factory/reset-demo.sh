#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

usage() {
  cat <<'USAGE'
Reset demo-generated working-tree artifacts.

Default dry-run:
  bash harness/shell-plugin-factory/reset-demo.sh

Actually remove generated plugin dirs and harness run reports:
  bash harness/shell-plugin-factory/reset-demo.sh --apply

Keeps the harness scripts/README/skill. Removes only:
  plugins/supabase/
  plugins/planetscale/
  plugins/render/
  harness/shell-plugin-factory/runs/
  harness/shell-plugin-factory/latest-report.md
USAGE
}

APPLY=0
case "${1:-}" in
  --apply) APPLY=1 ;;
  -h|--help) usage; exit 0 ;;
  "") ;;
  *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
esac

paths=(
  "plugins/supabase"
  "plugins/planetscale"
  "plugins/render"
  "harness/shell-plugin-factory/runs"
  "harness/shell-plugin-factory/latest-report.md"
)

echo "# Demo reset"
echo "Scope: fork checkout only ($(git config --get remote.origin.url || true))"
echo

for path in "${paths[@]}"; do
  if [[ -e "$path" ]]; then
    if [[ "$APPLY" -eq 1 ]]; then
      rm -rf "$path"
      echo "removed $path"
    else
      echo "would remove $path"
    fi
  else
    echo "absent $path"
  fi
done

if [[ "$APPLY" -eq 0 ]]; then
  echo
  echo "Dry-run only. Re-run with --apply to remove these artifacts."
fi
