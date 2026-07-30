#!/usr/bin/env bash
set -euo pipefail

bridge_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$bridge_root"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "pull stopped: working tree is dirty; commit or discard changes explicitly first" >&2
  exit 2
fi

git pull --ff-only
