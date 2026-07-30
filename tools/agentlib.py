"""Schema and Markdown helpers for the auditable Agent Exchange."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime
import json
from pathlib import Path
import re
from typing import Any, Iterable

try:
    from .vaultlib import (
        content_sha256,
        read_frontmatter,
        read_text,
        split_frontmatter_text,
    )
except ImportError:
    from vaultlib import (
        content_sha256,
        read_frontmatter,
        read_text,
        split_frontmatter_text,
    )


CASE_SECTIONS = (
    "图片可确认事实",
    "用户提供的背景",
    "数据限制",
    "当前setup状态",
    "支撑与压力",
    "B1/B2判断",
    "风险事件",
    "候选特征",
    "反对证据",
    "当前结论",
    "置信度",
    "次日验证条件",
    "对冻结策略的影响",
    "建议动作",
)
REASONING_SECTIONS = (
    "已知事实",
    "数据限制",
    "使用的冻结规则ID",
    "使用的候选规则ID",
    "推断过程摘要",
    "备选解释",
    "反对证据",
    "最终结论",
    "置信度",
    "不确定性",
    "结论失效条件",
    "对策略和代码的影响",
    "后续验证计划",
)
CHANGE_REQUEST_SECTIONS = (
    "当前规则",
    "新观察",
    "成功样本",
    "失败对照",
    "候选规则",
    "历史B1/B2日期影响",
    "INVALID影响",
    "新阈值需求",
    "必需测试",
    "回滚方案",
    "人工审批",
)
SCHEMA_BY_TYPE = {
    "case_intake": "case_intake.schema.json",
    "reasoning_digest": "reasoning_digest.schema.json",
    "strategy_change_request": "strategy_change_request.schema.json",
}
SECTIONS_BY_TYPE = {
    "case_intake": CASE_SECTIONS,
    "reasoning_digest": REASONING_SECTIONS,
    "strategy_change_request": CHANGE_REQUEST_SECTIONS,
}


def _json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    return value


def load_schema(root: Path, note_type: str) -> dict[str, Any]:
    name = SCHEMA_BY_TYPE.get(note_type)
    if name is None:
        raise ValueError(f"unsupported Agent Exchange type: {note_type!r}")
    path = root / "08_AgentExchange" / "Schemas" / name
    parsed = json.loads(read_text(path))
    if not isinstance(parsed, dict):
        raise ValueError(f"{path}: schema must be a JSON object")
    return parsed


def _matches_type(value: Any, expected: str) -> bool:
    return {
        "string": isinstance(value, str),
        "array": isinstance(value, list),
        "object": isinstance(value, dict),
        "boolean": isinstance(value, bool),
        "null": value is None,
        "integer": isinstance(value, int) and not isinstance(value, bool),
    }.get(expected, True)


def validate_schema_data(
    data: dict[str, Any],
    schema: dict[str, Any],
    *,
    label: str,
) -> list[str]:
    normalized = _json_value(data)
    errors: list[str] = []
    required = schema.get("required", [])
    for field in required:
        if field not in normalized:
            errors.append(f"{label}: missing required field {field}")
    properties = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        extras = sorted(set(normalized) - set(properties))
        if extras:
            errors.append(
                f"{label}: unexpected fields {', '.join(extras)}"
            )
    for field, rules in properties.items():
        if field not in normalized:
            continue
        value = normalized[field]
        expected = rules.get("type")
        expected_types = (
            expected if isinstance(expected, list) else [expected]
        )
        if expected is not None and not any(
            _matches_type(value, item) for item in expected_types
        ):
            errors.append(f"{label}: {field} has invalid type")
            continue
        if "const" in rules and value != rules["const"]:
            errors.append(f"{label}: {field} must equal {rules['const']!r}")
        if "enum" in rules and value not in rules["enum"]:
            errors.append(f"{label}: {field} has unsupported value {value!r}")
        if isinstance(value, str):
            if len(value) < rules.get("minLength", 0):
                errors.append(f"{label}: {field} is too short")
            pattern = rules.get("pattern")
            if pattern and re.fullmatch(pattern, value) is None:
                errors.append(f"{label}: {field} does not match schema pattern")
            if rules.get("format") == "date":
                try:
                    date.fromisoformat(value)
                except ValueError:
                    errors.append(f"{label}: {field} must be YYYY-MM-DD")
        if isinstance(value, list):
            if len(value) < rules.get("minItems", 0):
                errors.append(f"{label}: {field} has too few items")
            if rules.get("uniqueItems") and len(
                {json.dumps(item, sort_keys=True) for item in value}
            ) != len(value):
                errors.append(f"{label}: {field} must contain unique items")
            item_rules = rules.get("items", {})
            for index, item in enumerate(value):
                item_type = item_rules.get("type")
                if item_type and not _matches_type(item, item_type):
                    errors.append(
                        f"{label}: {field}[{index}] has invalid type"
                    )
                    continue
                pattern = item_rules.get("pattern")
                if pattern and (
                    not isinstance(item, str)
                    or re.fullmatch(pattern, item) is None
                ):
                    errors.append(
                        f"{label}: {field}[{index}] does not match pattern"
                    )
    return errors


def missing_sections(text: str, headings: Iterable[str]) -> tuple[str, ...]:
    lines = {line.strip() for line in text.splitlines()}
    return tuple(
        heading for heading in headings if f"## {heading}" not in lines
    )


def validate_agent_note(
    root: Path,
    path: Path,
    *,
    verify_hash: bool = True,
) -> list[str]:
    try:
        text = read_text(path)
        data, _ = split_frontmatter_text(text)
    except (OSError, ValueError) as exc:
        return [f"{path}: {exc}"]
    note_type = str(data.get("type", ""))
    try:
        schema = load_schema(root, note_type)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"{path}: {exc}"]
    errors = validate_schema_data(data, schema, label=str(path))
    missing = missing_sections(text, SECTIONS_BY_TYPE[note_type])
    if missing:
        errors.append(f"{path}: missing sections {', '.join(missing)}")
    if verify_hash and data.get("content_hash") != content_sha256(text):
        errors.append(f"{path}: content_hash does not match normalized content")
    if note_type == "reasoning_digest":
        for heading in ("反对证据", "不确定性"):
            body = extract_section(text, heading)
            if not body or body == "TODO":
                errors.append(f"{path}: {heading} must be explicitly recorded")
    if note_type == "strategy_change_request" and data.get("status") in {
        "draft",
        "proposed",
    }:
        if "approved_for_implementation" in str(
            data.get("status")
        ) and data.get("status") != "approved_for_implementation":
            errors.append(f"{path}: invalid implementation approval")
    return errors


def extract_section(text: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$\n(?P<body>.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if match is None:
        return None
    value = match.group("body").strip()
    return value or None


def agent_case_paths(root: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    for directory in ("Incoming", "Processed", "Rejected"):
        paths.extend(
            (root / "08_AgentExchange" / directory).glob("*.md")
        )
    return tuple(sorted(paths, key=lambda path: path.as_posix()))


def reasoning_digest_paths(root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            (root / "06_Conversations" / "ReasoningDigests").glob("*.md"),
            key=lambda path: path.as_posix(),
        )
    )


def change_request_paths(root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            (root / "05_Codex" / "ChangeRequests").glob("*.md"),
            key=lambda path: path.as_posix(),
        )
    )


def duplicate_values(values: Iterable[str]) -> tuple[str, ...]:
    counts = Counter(values)
    return tuple(sorted(value for value, count in counts.items() if count > 1))


def note_identity(data: dict[str, Any]) -> str:
    for field in ("case_id", "digest_id", "change_request_id"):
        if field in data:
            return str(data[field])
    raise ValueError("Agent note has no stable identity")
