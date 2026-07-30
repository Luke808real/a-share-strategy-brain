"""Deterministic helpers for local ChatGPT conversation archives."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from pathlib import Path
import re
from typing import Any, Iterable

try:
    from .vaultlib import (
        content_sha256,
        read_frontmatter,
        read_text,
        read_yaml,
        render_frontmatter,
        split_frontmatter_text,
        write_yaml,
    )
except ImportError:
    from vaultlib import (
        content_sha256,
        read_frontmatter,
        read_text,
        read_yaml,
        render_frontmatter,
        split_frontmatter_text,
        write_yaml,
    )


CHAT_SESSION_STATUSES = frozenset(
    {"captured", "reviewed", "processed", "rejected"}
)
DIGEST_REVIEW_STATUSES = frozenset(
    {"draft", "human_reviewed", "accepted", "rejected"}
)
REVIEWED_DIGEST_STATUSES = frozenset({"human_reviewed", "accepted"})
SESSION_REQUIRED_FIELDS = (
    "type",
    "session_id",
    "date",
    "topic",
    "strategy_version",
    "status",
    "source",
    "contains_cases",
    "contains_proposals",
    "contains_decisions",
    "content_hash",
)
RAW_EXPORT_REQUIRED_FIELDS = (
    "type",
    "conversation_id",
    "title",
    "created_at",
    "updated_at",
    "source",
    "content_hash",
    "import_batch_id",
)
DIGEST_REQUIRED_FIELDS = (
    "type",
    "session_id",
    "source_file",
    "review_status",
    "strategy_version",
    "contains_cases",
    "contains_proposals",
    "contains_decisions",
    "content_hash",
)
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
FIXED_SESSION_SECTIONS = (
    "用户目标",
    "原始事实与数据",
    "涉及案例",
    "新候选规则",
    "本轮已接受结论",
    "本轮未接受或有争议观点",
    "对冻结策略的影响",
    "Codex待办",
    "待补充数据",
    "下一次继续讨论的起点",
)


def _iso_date(value: Any) -> bool:
    if isinstance(value, date) and not isinstance(value, datetime):
        return True
    if isinstance(value, str):
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
        return True
    return False


def _iso_datetime(value: Any) -> bool:
    if isinstance(value, datetime):
        return value.tzinfo is not None
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _boolean_fields(data: dict[str, Any]) -> list[str]:
    return [
        field
        for field in (
            "contains_cases",
            "contains_proposals",
            "contains_decisions",
        )
        if not isinstance(data.get(field), bool)
    ]


def validate_conversation_frontmatter(
    path: Path,
    *,
    verify_hash: bool = True,
) -> list[str]:
    try:
        text = read_text(path)
        data, _ = split_frontmatter_text(text)
    except (OSError, ValueError) as exc:
        return [f"{path}: {exc}"]
    note_type = data.get("type")
    if note_type == "chat_session":
        required = SESSION_REQUIRED_FIELDS
    elif note_type == "chat_raw_export":
        required = RAW_EXPORT_REQUIRED_FIELDS
    elif note_type == "chat_digest":
        required = DIGEST_REQUIRED_FIELDS
    else:
        return [f"{path}: unsupported conversation type {note_type!r}"]
    errors: list[str] = []
    missing = [field for field in required if field not in data]
    if missing:
        return [f"{path}: missing conversation fields {', '.join(missing)}"]

    if note_type == "chat_session":
        session_id = str(data["session_id"])
        if SESSION_ID_PATTERN.fullmatch(session_id) is None:
            errors.append(f"{path}: invalid session_id {session_id!r}")
        if not _iso_date(data["date"]):
            errors.append(f"{path}: date must be YYYY-MM-DD")
        if data["status"] not in CHAT_SESSION_STATUSES:
            errors.append(f"{path}: invalid chat session status")
        invalid_bools = _boolean_fields(data)
        if invalid_bools:
            errors.append(
                f"{path}: fields must be boolean: {', '.join(invalid_bools)}"
            )
    elif note_type == "chat_raw_export":
        conversation_id = str(data["conversation_id"])
        if SESSION_ID_PATTERN.fullmatch(conversation_id) is None:
            errors.append(f"{path}: invalid conversation_id {conversation_id!r}")
        if data["source"] != "chatgpt_data_export":
            errors.append(f"{path}: raw export source must be chatgpt_data_export")
        for field in ("created_at", "updated_at"):
            if not _iso_datetime(data[field]):
                errors.append(f"{path}: {field} must include a timezone")
    else:
        session_id = str(data["session_id"])
        if SESSION_ID_PATTERN.fullmatch(session_id) is None:
            errors.append(f"{path}: invalid digest session_id {session_id!r}")
        if data["review_status"] not in DIGEST_REVIEW_STATUSES:
            errors.append(f"{path}: invalid digest review_status")
        invalid_bools = _boolean_fields(data)
        if invalid_bools:
            errors.append(
                f"{path}: fields must be boolean: {', '.join(invalid_bools)}"
            )

    hash_value = str(data.get("content_hash", ""))
    if verify_hash and hash_value != content_sha256(text):
        errors.append(f"{path}: content_hash does not match normalized content")
    elif hash_value and re.fullmatch(r"[0-9a-f]{64}", hash_value) is None:
        errors.append(f"{path}: content_hash must be lowercase SHA-256")
    return errors


def with_content_hash(text: str) -> str:
    data, body = split_frontmatter_text(text)
    data["content_hash"] = ""
    unhashed = render_frontmatter(data, body)
    data["content_hash"] = content_sha256(unhashed)
    return render_frontmatter(data, body)


def extract_section(text: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$\n(?P<body>.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if match is None:
        return None
    body = match.group("body").strip()
    return body or None


def conversation_id(data: dict[str, Any]) -> str:
    if data.get("type") == "chat_raw_export":
        return str(data["conversation_id"])
    return str(data["session_id"])


def raw_paths(root: Path) -> tuple[Path, ...]:
    raw = root / "06_Conversations" / "Raw"
    return tuple(sorted(raw.glob("*.md"), key=lambda path: path.name))


def digest_paths(root: Path) -> tuple[Path, ...]:
    digests = root / "06_Conversations" / "Digests"
    return tuple(sorted(digests.glob("*.md"), key=lambda path: path.name))


def locate_raw(root: Path, session_id: str) -> Path:
    matches = [
        path
        for path in raw_paths(root)
        if conversation_id(read_frontmatter(path)) == session_id
    ]
    if len(matches) != 1:
        raise FileNotFoundError(
            f"expected one Raw note for {session_id!r}, found {len(matches)}"
        )
    return matches[0]


def locate_digest(root: Path, session_id: str) -> Path:
    matches = [
        path
        for path in digest_paths(root)
        if str(read_frontmatter(path).get("session_id")) == session_id
    ]
    if len(matches) != 1:
        raise FileNotFoundError(
            f"expected one Digest for {session_id!r}, found {len(matches)}"
        )
    return matches[0]


def load_import_manifest(root: Path) -> dict[str, Any]:
    path = root / "06_Conversations" / "IMPORT_MANIFEST.yaml"
    data = read_yaml(path)
    data.setdefault("schema_version", "1.0")
    data.setdefault("sessions", [])
    data.setdefault("import_batches", [])
    return data


def write_import_manifest(root: Path, data: dict[str, Any]) -> None:
    sessions = sorted(
        data.get("sessions", []),
        key=lambda item: (str(item["session_id"]), str(item["content_hash"])),
    )
    batches = sorted(
        data.get("import_batches", []),
        key=lambda item: str(item.get("import_batch_id", "")),
    )
    write_yaml(
        root / "06_Conversations" / "IMPORT_MANIFEST.yaml",
        {
            "schema_version": str(data.get("schema_version", "1.0")),
            "sessions": sessions,
            "import_batches": batches,
        },
    )


def manifest_session_ids(root: Path) -> tuple[str, ...]:
    return tuple(
        str(item["session_id"])
        for item in load_import_manifest(root).get("sessions", [])
    )


def manifest_hashes(root: Path) -> tuple[str, ...]:
    return tuple(
        str(item["content_hash"])
        for item in load_import_manifest(root).get("sessions", [])
    )


def reviewed_digests(root: Path) -> tuple[Path, ...]:
    return tuple(
        path
        for path in digest_paths(root)
        if read_frontmatter(path).get("review_status")
        in REVIEWED_DIGEST_STATUSES
    )


def duplicate_values(values: Iterable[str]) -> tuple[str, ...]:
    counts = Counter(values)
    return tuple(sorted(value for value, count in counts.items() if count > 1))


def source_relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()
