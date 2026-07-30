"""Preview and selectively import a local official ChatGPT data export."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Sequence
import zipfile

try:
    from .build_chat_digest import write_digest
    from .chatlib import (
        SESSION_ID_PATTERN,
        load_import_manifest,
        with_content_hash,
        write_import_manifest,
    )
    from .conversation_views import write_conversation_views
    from .vaultlib import content_sha256, vault_root
except ImportError:
    from build_chat_digest import write_digest
    from chatlib import (
        SESSION_ID_PATTERN,
        load_import_manifest,
        with_content_hash,
        write_import_manifest,
    )
    from conversation_views import write_conversation_views
    from vaultlib import content_sha256, vault_root


class UnsupportedExportSchema(ValueError):
    """Raised before writes when an export shape is not explicitly supported."""


@dataclass(frozen=True)
class ExportMessage:
    role: str
    timestamp: str
    text: str
    attachment_metadata: tuple[str, ...]


@dataclass(frozen=True)
class ExportConversation:
    conversation_id: str
    title: str
    created_at: str
    updated_at: str
    messages: tuple[ExportMessage, ...]

    @property
    def searchable_text(self) -> str:
        return "\n".join(
            (self.title, *(message.text for message in self.messages))
        )


def _iso_timestamp(value: Any, field: str) -> str:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise UnsupportedExportSchema(
                f"{field} is not a supported timestamp"
            ) from exc
        if parsed.tzinfo is None:
            raise UnsupportedExportSchema(f"{field} has no timezone")
        return parsed.isoformat()
    raise UnsupportedExportSchema(f"{field} is missing or unsupported")


def _json_attachment(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _linear_nodes(conversation: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = conversation.get("mapping")
    if not isinstance(mapping, dict) or not mapping:
        raise UnsupportedExportSchema("conversation.mapping must be a non-empty object")
    current = conversation.get("current_node")
    if current is not None:
        chain: list[dict[str, Any]] = []
        seen: set[str] = set()
        node_id: Any = current
        while node_id is not None:
            if not isinstance(node_id, str) or node_id in seen:
                raise UnsupportedExportSchema("invalid or cyclic current_node chain")
            node = mapping.get(node_id)
            if not isinstance(node, dict):
                raise UnsupportedExportSchema("current_node references a missing node")
            seen.add(node_id)
            chain.append(node)
            node_id = node.get("parent")
        return list(reversed(chain))

    roots = [
        (node_id, node)
        for node_id, node in mapping.items()
        if isinstance(node, dict) and node.get("parent") is None
    ]
    if len(roots) != 1:
        raise UnsupportedExportSchema(
            "export lacks current_node and does not contain one linear root"
        )
    ordered: list[dict[str, Any]] = []
    node_id, node = roots[0]
    seen: set[str] = set()
    while True:
        if node_id in seen:
            raise UnsupportedExportSchema("cyclic conversation mapping")
        seen.add(node_id)
        ordered.append(node)
        children = node.get("children", [])
        if not isinstance(children, list):
            raise UnsupportedExportSchema("node.children must be a list")
        if not children:
            break
        if len(children) != 1 or not isinstance(children[0], str):
            raise UnsupportedExportSchema(
                "branching export requires a valid current_node"
            )
        node_id = children[0]
        child = mapping.get(node_id)
        if not isinstance(child, dict):
            raise UnsupportedExportSchema("node references a missing child")
        node = child
    return ordered


def _message_from_node(node: dict[str, Any]) -> ExportMessage | None:
    message = node.get("message")
    if message is None:
        return None
    if not isinstance(message, dict):
        raise UnsupportedExportSchema("node.message must be an object or null")
    author = message.get("author")
    content = message.get("content")
    if not isinstance(author, dict) or not isinstance(author.get("role"), str):
        raise UnsupportedExportSchema("message.author.role is missing")
    if not isinstance(content, dict) or not isinstance(content.get("parts"), list):
        raise UnsupportedExportSchema("message.content.parts is missing")
    text_parts: list[str] = []
    attachments: list[str] = []
    for part in content["parts"]:
        if isinstance(part, str):
            text_parts.append(part)
        elif isinstance(part, dict):
            attachments.append(_json_attachment(part))
        elif part is not None:
            raise UnsupportedExportSchema("unsupported message content part")
    metadata = message.get("metadata", {})
    if not isinstance(metadata, dict):
        raise UnsupportedExportSchema("message.metadata must be an object")
    for key in ("attachments", "files"):
        if key in metadata:
            value = metadata[key]
            if not isinstance(value, list):
                raise UnsupportedExportSchema(f"message.metadata.{key} must be a list")
            attachments.extend(_json_attachment(item) for item in value)
    timestamp_value = message.get("create_time")
    timestamp = (
        _iso_timestamp(timestamp_value, "message.create_time")
        if timestamp_value is not None
        else "unknown"
    )
    return ExportMessage(
        role=author["role"],
        timestamp=timestamp,
        text="\n".join(text_parts).strip() or "[无文字内容]",
        attachment_metadata=tuple(attachments),
    )


def parse_conversation(value: Any) -> ExportConversation:
    if not isinstance(value, dict):
        raise UnsupportedExportSchema("each conversation must be an object")
    conversation_id = value.get("id", value.get("conversation_id"))
    title = value.get("title")
    if not isinstance(conversation_id, str) or not conversation_id:
        raise UnsupportedExportSchema("conversation id is missing")
    if SESSION_ID_PATTERN.fullmatch(conversation_id) is None:
        raise UnsupportedExportSchema(
            "conversation id contains unsafe filename characters"
        )
    if not isinstance(title, str):
        raise UnsupportedExportSchema("conversation title is missing")
    messages = tuple(
        message
        for node in _linear_nodes(value)
        if (message := _message_from_node(node)) is not None
    )
    return ExportConversation(
        conversation_id=conversation_id,
        title=title or "无标题会话",
        created_at=_iso_timestamp(value.get("create_time"), "create_time"),
        updated_at=_iso_timestamp(value.get("update_time"), "update_time"),
        messages=messages,
    )


def _conversations_from_json(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        if not all(isinstance(item, dict) for item in value):
            raise UnsupportedExportSchema("conversation JSON list contains non-objects")
        return value
    if isinstance(value, dict) and (
        "mapping" in value or "current_node" in value
    ):
        return [value]
    raise UnsupportedExportSchema(
        "unsupported ChatGPT export JSON; expected conversations list or one "
        "conversation object"
    )


def _numbered_conversation_json(path: Path) -> bool:
    return bool(
        re.fullmatch(r"conversations?(?:-\d+)?\.json", path.name, re.IGNORECASE)
    )


def _parse_json_bytes(raw_bytes: bytes, label: str) -> list[dict[str, Any]]:
    try:
        value = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UnsupportedExportSchema(f"{label}: invalid UTF-8 JSON") from exc
    return _conversations_from_json(value)


def load_export(path: Path) -> tuple[tuple[ExportConversation, ...], str]:
    path = path.expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    objects: list[dict[str, Any]] = []
    if path.is_dir():
        files = sorted(
            item for item in path.iterdir()
            if item.is_file() and _numbered_conversation_json(item)
        )
        if not files:
            raise UnsupportedExportSchema(
                "directory contains no conversations.json or numbered "
                "conversation JSON files"
            )
        digest_input = b"".join(
            item.name.encode("utf-8") + b"\0" + item.read_bytes() + b"\0"
            for item in files
        )
        batch_id = (
            f"chatgpt-export-{sha256(digest_input).hexdigest()[:16]}"
        )
        for item in files:
            objects.extend(_parse_json_bytes(item.read_bytes(), item.name))
    else:
        raw_bytes = path.read_bytes()
        batch_id = f"chatgpt-export-{sha256(raw_bytes).hexdigest()[:16]}"
    if path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            names = sorted(
                name
                for name in archive.namelist()
                if Path(name).name == "conversations.json"
            )
            if not names:
                names = sorted(
                    name
                    for name in archive.namelist()
                    if name.lower().endswith(".json")
                    and Path(name).name.lower() != "user.json"
                )
            if not names:
                raise UnsupportedExportSchema(
                    "ZIP contains no supported conversation JSON"
                )
            for name in names:
                objects.extend(_parse_json_bytes(archive.read(name), name))
    elif path.is_file():
        objects.extend(_parse_json_bytes(raw_bytes, path.name))
    parsed = tuple(parse_conversation(item) for item in objects)
    ids = [item.conversation_id for item in parsed]
    if len(set(ids)) != len(ids):
        raise UnsupportedExportSchema("export contains duplicate conversation ids")
    return tuple(sorted(parsed, key=lambda item: item.conversation_id)), batch_id


def load_exports(
    paths: Sequence[Path],
) -> tuple[tuple[ExportConversation, ...], str]:
    loaded = [load_export(path) for path in paths]
    conversations = tuple(
        item for items, _ in loaded for item in items
    )
    ids = [item.conversation_id for item in conversations]
    if len(set(ids)) != len(ids):
        raise UnsupportedExportSchema(
            "selected export inputs contain duplicate conversation ids"
        )
    batch_material = "\n".join(batch for _, batch in loaded).encode("utf-8")
    batch_id = f"chatgpt-export-{sha256(batch_material).hexdigest()[:16]}"
    return (
        tuple(sorted(conversations, key=lambda item: item.conversation_id)),
        batch_id,
    )


def select_conversations(
    conversations: Sequence[ExportConversation],
    *,
    title_contains: str | None = None,
    content_contains: str | None = None,
    conversation_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[ExportConversation, ...]:
    selected: list[ExportConversation] = []
    for item in conversations:
        created = datetime.fromisoformat(item.created_at).date()
        if conversation_id is not None and item.conversation_id != conversation_id:
            continue
        if title_contains is not None and title_contains not in item.title:
            continue
        if content_contains is not None and content_contains not in item.searchable_text:
            continue
        if date_from is not None and created < date_from:
            continue
        if date_to is not None and created > date_to:
            continue
        selected.append(item)
    return tuple(selected)


def render_raw_export(item: ExportConversation, batch_id: str) -> str:
    lines = [
        "---",
        "type: chat_raw_export",
        f"conversation_id: {json.dumps(item.conversation_id, ensure_ascii=False)}",
        f"title: {json.dumps(item.title, ensure_ascii=False)}",
        f"created_at: {json.dumps(item.created_at)}",
        f"updated_at: {json.dumps(item.updated_at)}",
        "source: chatgpt_data_export",
        'content_hash: ""',
        f"import_batch_id: {batch_id}",
        "---",
        "",
        f"# {item.title}",
        "",
        "> 来自本地ChatGPT官方数据导出；附件只保留元数据引用。",
        "",
        "## 消息",
    ]
    for index, message in enumerate(item.messages, start=1):
        lines.extend(
            [
                "",
                f"### {index}. {message.role}",
                "",
                f"- 时间：`{message.timestamp}`",
                "",
                message.text,
            ]
        )
        if message.attachment_metadata:
            lines.extend(["", "- 附件元数据："])
            lines.extend(
                f"  - `{metadata}`" for metadata in message.attachment_metadata
            )
    lines.append("")
    return with_content_hash("\n".join(lines))


def import_selected(
    root: Path,
    selected: Sequence[ExportConversation],
    batch_id: str,
) -> tuple[Path, ...]:
    if not selected:
        raise ValueError("selection matched no conversations")
    manifest = load_import_manifest(root)
    known_ids = {str(item["session_id"]) for item in manifest["sessions"]}
    duplicates = sorted(
        item.conversation_id for item in selected if item.conversation_id in known_ids
    )
    if duplicates:
        raise ValueError(
            "conversation_id already imported: " + ", ".join(duplicates)
        )
    rendered = {
        item.conversation_id: render_raw_export(item, batch_id)
        for item in selected
    }
    destinations = {
        session_id: root / "06_Conversations" / "Raw" / f"{session_id}.md"
        for session_id in rendered
    }
    conflicts = [str(path) for path in destinations.values() if path.exists()]
    if conflicts:
        raise FileExistsError("Raw files already exist: " + ", ".join(conflicts))

    written: list[Path] = []
    for item in sorted(selected, key=lambda value: value.conversation_id):
        path = destinations[item.conversation_id]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered[item.conversation_id], encoding="utf-8")
        digest_path = write_digest(root, path)
        manifest["sessions"].append(
            {
                "session_id": item.conversation_id,
                "content_hash": content_sha256(rendered[item.conversation_id]),
                "raw_file": path.relative_to(root).as_posix(),
                "digest_file": digest_path.relative_to(root).as_posix(),
                "source_type": "chat_raw_export",
                "review_status": "draft",
                "import_batch_id": batch_id,
            }
        )
        written.append(path)
    if batch_id not in {
        str(item.get("import_batch_id")) for item in manifest["import_batches"]
    }:
        manifest["import_batches"].append(
            {
                "import_batch_id": batch_id,
                "conversation_ids": sorted(
                    item.conversation_id for item in selected
                ),
            }
        )
    write_import_manifest(root, manifest)
    write_conversation_views(root)
    return tuple(written)


def _print_preview(items: Sequence[ExportConversation]) -> None:
    print(f"matched {len(items)} conversation(s)")
    for item in items:
        print(
            f"- {item.conversation_id} | {item.created_at[:10]} | "
            f"{item.title} | {len(item.messages)} message(s)"
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Preview or selectively import a local ChatGPT export"
    )
    parser.add_argument(
        "export_path",
        type=Path,
        nargs="+",
        help="one ZIP/JSON, a directory, or multiple numbered JSON files",
    )
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--title-contains")
    parser.add_argument("--content-contains")
    parser.add_argument("--conversation-id")
    parser.add_argument("--date-from", type=date.fromisoformat)
    parser.add_argument("--date-to", type=date.fromisoformat)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--dry-run", action="store_true")
    action.add_argument("--import", dest="do_import", action="store_true")
    args = parser.parse_args(argv)
    try:
        conversations, batch_id = load_exports(args.export_path)
        has_selector = any(
            (
                args.title_contains,
                args.content_contains,
                args.conversation_id,
                args.date_from,
                args.date_to,
            )
        )
        if args.list or not has_selector:
            _print_preview(conversations)
            if args.do_import and not has_selector:
                print("refusing to import all account history without a selector")
                return 1
            return 0
        selected = select_conversations(
            conversations,
            title_contains=args.title_contains,
            content_contains=args.content_contains,
            conversation_id=args.conversation_id,
            date_from=args.date_from,
            date_to=args.date_to,
        )
        _print_preview(selected)
        if args.do_import:
            written = import_selected(vault_root(), selected, batch_id)
            for path in written:
                print(path)
    except (
        FileExistsError,
        FileNotFoundError,
        UnsupportedExportSchema,
        ValueError,
    ) as exc:
        print(f"import failed safely: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
