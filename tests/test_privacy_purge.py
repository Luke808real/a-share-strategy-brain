from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest

from tools.build_context_delta import build_context_delta_text
from tools.chatlib import with_content_hash
from tools.context_sync import empty_sync_manifest
from tools.ingest_chat_inbox import ingest_inbox
from tools.purge_session import SessionDependencyError, purge_session


def copied_vault(source: Path, destination: Path) -> Path:
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
    )
    return destination


def minimal_session(session_id: str) -> str:
    return with_content_hash(
        f"""---
type: chat_session
session_id: {session_id}
date: 2026-07-31
topic: 清理测试
strategy_version: phase-2b2
status: captured
source: manual_chatgpt_copy
contains_cases: false
contains_proposals: false
contains_decisions: false
content_hash: ""
---

# 清理测试

## 用户目标

测试依赖保护。
"""
    )


def test_private_raw_exports_and_zip_are_git_ignored(vault_root_path):
    values = (
        "06_Conversations/Raw/private.md",
        "07_Inbox/ChatGPT/private.md",
        "conversations.json",
        "private-export.zip",
        "attachments/screenshots/private.png",
    )
    completed = subprocess.run(
        ("git", "check-ignore", *values),
        cwd=vault_root_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert set(completed.stdout.splitlines()) == set(values)


def test_purge_stops_when_accepted_adr_depends_on_session(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    session_id = "chat-2026-07-31-099"
    inbox = root / "07_Inbox" / "ChatGPT" / f"{session_id}.md"
    inbox.write_text(minimal_session(session_id), encoding="utf-8")
    ingest_inbox(root)
    raw = root / "06_Conversations" / "Raw" / f"{session_id}.md"
    adr = root / "03_Decisions" / "ADR-999-purge-dependency.md"
    adr.write_text(
        f"""---
type: strategy_decision
adr_id: ADR-999
title: 清理依赖测试
status: ACCEPTED
decision_date: 2026-07-31
strategy_version: phase-2b2
---

# 清理依赖

来源会话：{session_id}
""",
        encoding="utf-8",
    )

    with pytest.raises(SessionDependencyError, match="protected dependencies"):
        purge_session(root, session_id, session_id)

    assert raw.exists()


def test_context_delta_is_deterministic_for_identical_inputs(
    vault_root_path,
):
    first = build_context_delta_text(vault_root_path, empty_sync_manifest())
    second = build_context_delta_text(vault_root_path, empty_sync_manifest())

    assert first == second
