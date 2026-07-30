from __future__ import annotations

import json

import pytest

from tools.import_chatgpt_export import (
    UnsupportedExportSchema,
    load_export,
    render_raw_export,
)


def export_conversation() -> dict:
    return {
        "id": "conv-2026-07-31-001",
        "title": "涨停回调讨论",
        "create_time": 1785427200,
        "update_time": 1785427260,
        "current_node": "assistant",
        "mapping": {
            "root": {
                "parent": None,
                "children": ["user"],
                "message": None,
            },
            "user": {
                "parent": "root",
                "children": ["assistant"],
                "message": {
                    "author": {"role": "user"},
                    "create_time": 1785427201,
                    "content": {"parts": ["先看事实。"]},
                    "metadata": {},
                },
            },
            "assistant": {
                "parent": "user",
                "children": [],
                "message": {
                    "author": {"role": "assistant"},
                    "create_time": 1785427202,
                    "content": {"parts": ["再写推论。"]},
                    "metadata": {"attachments": [{"name": "chart.png"}]},
                },
            },
        },
    }


def test_chatgpt_json_import_preserves_message_order_and_metadata(tmp_path):
    source = tmp_path / "selected-conversation.json"
    source.write_text(
        json.dumps(export_conversation(), ensure_ascii=False),
        encoding="utf-8",
    )

    conversations, batch_id = load_export(source)
    rendered = render_raw_export(conversations[0], batch_id)

    assert [message.role for message in conversations[0].messages] == [
        "user",
        "assistant",
    ]
    assert rendered.index("先看事实") < rendered.index("再写推论")
    assert "chart.png" in rendered
    assert "conv-2026-07-31-001" in rendered


def test_unknown_export_schema_fails_without_writes(tmp_path):
    source = tmp_path / "unknown.json"
    source.write_text('{"unexpected": true}', encoding="utf-8")
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    with pytest.raises(UnsupportedExportSchema, match="unsupported"):
        load_export(source)

    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    assert after == before


def test_numbered_conversation_json_directory_is_supported(tmp_path):
    first = export_conversation()
    second = export_conversation()
    second["id"] = "conv-2026-07-31-002"
    second["title"] = "第二段导出"
    (tmp_path / "conversations-000.json").write_text(
        json.dumps([first], ensure_ascii=False),
        encoding="utf-8",
    )
    (tmp_path / "conversations-001.json").write_text(
        json.dumps([second], ensure_ascii=False),
        encoding="utf-8",
    )

    conversations, _ = load_export(tmp_path)

    assert [item.conversation_id for item in conversations] == [
        "conv-2026-07-31-001",
        "conv-2026-07-31-002",
    ]
