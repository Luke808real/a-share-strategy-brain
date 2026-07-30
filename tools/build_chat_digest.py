"""Create one deterministic review draft from a local Raw conversation."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

try:
    from .chatlib import (
        FIXED_SESSION_SECTIONS,
        conversation_id,
        extract_section,
        locate_raw,
        source_relative,
        with_content_hash,
    )
    from .vaultlib import read_frontmatter, read_text, vault_root
except ImportError:
    from chatlib import (
        FIXED_SESSION_SECTIONS,
        conversation_id,
        extract_section,
        locate_raw,
        source_relative,
        with_content_hash,
    )
    from vaultlib import read_frontmatter, read_text, vault_root


def build_digest_text(root: Path, raw_path: Path) -> str:
    raw_text = read_text(raw_path)
    raw = read_frontmatter(raw_path)
    session_id = conversation_id(raw)
    strategy_version = str(raw.get("strategy_version", "phase-2b2"))
    booleans = {
        key: bool(raw.get(key, False))
        for key in (
            "contains_cases",
            "contains_proposals",
            "contains_decisions",
        )
    }
    title = str(raw.get("topic") or raw.get("title") or session_id)
    lines = [
        "---",
        "type: chat_digest",
        f"session_id: {session_id}",
        f"source_file: {source_relative(root, raw_path)}",
        "review_status: draft",
        f"strategy_version: {strategy_version}",
        f"contains_cases: {str(booleans['contains_cases']).lower()}",
        f"contains_proposals: {str(booleans['contains_proposals']).lower()}",
        f"contains_decisions: {str(booleans['contains_decisions']).lower()}",
        'content_hash: ""',
        "---",
        "",
        f"# {title} — 会话Digest",
        "",
        "> 本草稿由确定性本地工具生成，只复制明确章节；TODO表示原文没有对应"
        "结构。它不推断交易规则，也不修改冻结策略。",
    ]
    if raw.get("type") == "chat_raw_export":
        lines.extend(
            [
                "",
                "## 导出会话原文",
                "",
                "TODO：官方导出没有固定策略章节。请人工阅读Raw后，把事实与推论"
                "分别填写到下列章节。",
            ]
        )
    for section in FIXED_SESSION_SECTIONS:
        value = extract_section(raw_text, section)
        lines.extend(["", f"## {section}", "", value or "TODO"])
    lines.extend(
        [
            "",
            "## 建议派生项",
            "",
            "- OBSERVED案例：TODO（必须使用显式提升命令）",
            "- Candidate Rule：TODO（只能OBSERVED或PROPOSED）",
            "- ADR草稿：TODO（不得自动采纳）",
            "",
        ]
    )
    return with_content_hash("\n".join(lines))


def write_digest(
    root: Path,
    raw_path: Path,
    *,
    overwrite_draft: bool = False,
) -> Path:
    raw = read_frontmatter(raw_path)
    session_id = conversation_id(raw)
    destination = root / "06_Conversations" / "Digests" / f"{session_id}.md"
    if destination.exists():
        existing = read_frontmatter(destination)
        if not overwrite_draft or existing.get("review_status") != "draft":
            raise FileExistsError(f"digest already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_digest_text(root, raw_path), encoding="utf-8")
    return destination


def resolve_raw_input(root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_file():
        return candidate.resolve()
    rooted = root / candidate
    if rooted.is_file():
        return rooted.resolve()
    return locate_raw(root, value)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a deterministic chat Digest draft"
    )
    parser.add_argument("raw_or_session_id")
    parser.add_argument(
        "--overwrite-draft",
        action="store_true",
        help="replace an existing draft only; reviewed Digests remain protected",
    )
    args = parser.parse_args(argv)
    root = vault_root()
    try:
        raw_path = resolve_raw_input(root, args.raw_or_session_id)
        print(
            write_digest(
                root,
                raw_path,
                overwrite_draft=args.overwrite_draft,
            )
        )
    except (FileNotFoundError, FileExistsError, ValueError) as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
