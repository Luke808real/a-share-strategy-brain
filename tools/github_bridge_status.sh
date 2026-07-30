#!/usr/bin/env bash
set -euo pipefail

bridge_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$bridge_root"

echo "vault_root=$bridge_root"
echo "branch=$(git branch --show-current)"
echo "head=$(git rev-parse HEAD)"
git remote -v
git status --short --branch

upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
if [[ -n "$upstream" ]]; then
  counts="$(git rev-list --left-right --count "$upstream...HEAD")"
  echo "upstream=$upstream"
  echo "behind_ahead=$counts"
else
  echo "upstream=none"
fi
