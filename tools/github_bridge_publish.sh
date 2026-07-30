#!/usr/bin/env bash
set -euo pipefail

bridge_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$bridge_root"

confirmed=false
message="Knowledge bridge update"
if [[ "${1:-}" == "--confirm" ]]; then
  confirmed=true
  if [[ -n "${2:-}" ]]; then
    message="$2"
  fi
elif [[ $# -gt 0 ]]; then
  echo "usage: tools/github_bridge_publish.sh [--confirm [commit-message]]" >&2
  exit 2
fi

python tools/validate_agent_exchange.py
python tools/validate_vault.py
python tools/scan_sensitive_content.py
pytest -q
git diff --check

branch="$(git branch --show-current)"
if [[ "$branch" == chatgpt/* ]]; then
  protected="$(git status --porcelain -- \
    01_Strategy/STRATEGY_MASTER.md \
    01_Strategy/BASELINE_MANIFEST.yaml)"
  if [[ -n "$protected" ]]; then
    echo "publish stopped: chatgpt branches cannot modify protected strategy truth" >&2
    exit 3
  fi
fi

git diff --stat
git status --short

if [[ "$confirmed" != true ]]; then
  echo "preview only: pass --confirm to stage, commit and push"
  exit 0
fi

git add -- \
  .github \
  .gitignore \
  00_INDEX.md \
  01_Strategy \
  02_Cases \
  03_Decisions \
  04_Research \
  05_Codex \
  06_Conversations \
  07_Inbox \
  08_AgentExchange \
  attachments/README.md \
  attachments/screenshots/.gitkeep \
  CHATGPT_PROJECT_INSTRUCTIONS.md \
  PRIVACY.md \
  README.md \
  docs \
  exports \
  pyproject.toml \
  tests \
  tools

forbidden="$(git diff --cached --name-only | grep -E \
  '(^|/)(Raw|Screenshots|screenshots)/|conversations\.json$|\.zip$|(^|/)\.env($|\.)' \
  | grep -vE '/\.gitkeep$' \
  || true)"
if [[ -n "$forbidden" ]]; then
  echo "publish stopped: forbidden private files were staged" >&2
  echo "$forbidden" >&2
  exit 4
fi

if git diff --cached --quiet; then
  echo "nothing to commit"
  exit 0
fi

git diff --cached --stat
git commit -m "$message"
git push -u origin "$branch"
