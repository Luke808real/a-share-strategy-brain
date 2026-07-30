from __future__ import annotations

from datetime import date
from pathlib import Path
import shutil

import pytest

from tools.build_context_delta import (
    build_context_delta_text,
    write_context_delta,
)
from tools.chatlib import validate_conversation_frontmatter, with_content_hash
from tools.context_sync import empty_sync_manifest
from tools.ingest_chat_inbox import ingest_inbox, plan_ingest
from tools.promote_digest_to_case import promote_digest_to_case
from tools.review_chat_digest import review_digest


def copied_vault(source: Path, destination: Path) -> Path:
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
    )
    return destination


def chat_session_text(
    session_id: str,
    *,
    topic: str = "中文策略讨论",
    facts: str = "002606的人工观察；尚未验证。",
) -> str:
    return with_content_hash(
        f"""---
type: chat_session
session_id: {session_id}
date: 2026-07-31
topic: {topic}
strategy_version: phase-2b2
status: captured
source: manual_chatgpt_copy
contains_cases: true
contains_proposals: false
contains_decisions: false
content_hash: ""
---

# {topic}

## 用户目标

验证本地归档。

## 原始事实与数据

{facts}

## 涉及案例

002606。

## 新候选规则

TODO

## 本轮已接受结论

无。

## 本轮未接受或有争议观点

单个案例不能冻结规则。

## 对冻结策略的影响

无。

## Codex待办

TODO

## 待补充数据

TODO

## 下一次继续讨论的起点

复核事实。
"""
    )


def write_inbox(root: Path, session_id: str, **kwargs: str) -> Path:
    path = root / "07_Inbox" / "ChatGPT" / f"{session_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(chat_session_text(session_id, **kwargs), encoding="utf-8")
    return path


def test_chat_session_frontmatter_is_valid(tmp_path):
    path = tmp_path / "中文会话.md"
    path.write_text(chat_session_text("chat-2026-07-31-001"), encoding="utf-8")

    assert validate_conversation_frontmatter(path) == []


def test_duplicate_session_id_and_hash_are_rejected(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    first = write_inbox(root, "chat-2026-07-31-001")
    second = root / "07_Inbox" / "ChatGPT" / "duplicate-copy.md"
    second.write_text(first.read_text(encoding="utf-8"), encoding="utf-8")

    _, errors = plan_ingest(root)

    assert any("duplicate session_id" in error for error in errors)
    assert any("duplicate content_hash" in error for error in errors)


def test_dry_run_has_no_side_effects(vault_root_path, tmp_path):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    write_inbox(root, "chat-2026-07-31-002")
    manifest = root / "06_Conversations" / "IMPORT_MANIFEST.yaml"
    before = manifest.read_bytes()

    planned = ingest_inbox(root, dry_run=True)

    assert len(planned) == 1
    assert manifest.read_bytes() == before
    assert not (
        root / "06_Conversations" / "Raw" / "chat-2026-07-31-002.md"
    ).exists()
    assert not (
        root / "06_Conversations" / "Digests" / "chat-2026-07-31-002.md"
    ).exists()


def test_ingest_creates_raw_digest_and_chinese_content(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    source = write_inbox(root, "chat-2026-07-31-003", topic="涨停回调复核")

    ingested = ingest_inbox(root)

    raw = root / "06_Conversations" / "Raw" / "chat-2026-07-31-003.md"
    digest = (
        root / "06_Conversations" / "Digests" / "chat-2026-07-31-003.md"
    )
    assert len(ingested) == 1
    assert source.exists()
    assert raw.exists() and digest.exists()
    assert "涨停回调复核" in digest.read_text(encoding="utf-8")
    assert validate_conversation_frontmatter(raw) == []
    assert validate_conversation_frontmatter(digest) == []


def test_unreviewed_digest_is_excluded_and_accepted_enters_delta(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    session_id = "chat-2026-07-31-004"
    write_inbox(root, session_id)
    ingest_inbox(root)

    draft_delta = build_context_delta_text(root, empty_sync_manifest())
    review_digest(root, session_id, "accepted")
    accepted_delta = build_context_delta_text(root, empty_sync_manifest())

    assert session_id not in draft_delta
    assert session_id in accepted_delta


def test_same_session_does_not_repeat_in_delta(vault_root_path, tmp_path):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    session_id = "chat-2026-07-31-005"
    write_inbox(root, session_id)
    ingest_inbox(root)
    review_digest(root, session_id, "accepted")

    write_context_delta(root, rebuild_full=True)
    first = (root / "exports" / "LLM_CONTEXT_DELTA.md").read_text(
        encoding="utf-8"
    )
    write_context_delta(root)
    second = (root / "exports" / "LLM_CONTEXT_DELTA.md").read_text(
        encoding="utf-8"
    )

    assert session_id in first
    assert session_id not in second
    assert "无增量" in second


def test_promote_case_is_observed_and_never_overwrites(
    vault_root_path,
    tmp_path,
):
    root = copied_vault(vault_root_path, tmp_path / "vault")
    session_id = "chat-2026-07-31-006"
    write_inbox(root, session_id)
    ingest_inbox(root)
    review_digest(root, session_id, "accepted")
    kwargs = dict(
        root=root,
        session_id=session_id,
        code="002606",
        name="大连电瓷",
        observation_date=date(2026, 7, 29),
        outcome="watching",
    )

    case_path = promote_digest_to_case(**kwargs)

    assert "case_status: observed" in case_path.read_text(encoding="utf-8")
    assert "source_session_id" in case_path.read_text(encoding="utf-8")
    with pytest.raises(FileExistsError, match="case already exists"):
        promote_digest_to_case(**kwargs)
