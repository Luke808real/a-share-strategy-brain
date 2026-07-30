"""Rebuild deterministic conversation index and human review queue."""

from __future__ import annotations

from pathlib import Path
import re

try:
    from .chatlib import digest_paths
    from .vaultlib import read_frontmatter, read_text
except ImportError:
    from chatlib import digest_paths
    from vaultlib import read_frontmatter, read_text


def _cell(value: str) -> str:
    return value.replace("|", r"\|").replace("\n", " ").strip() or "—"


def _stock_codes(text: str) -> str:
    return ", ".join(sorted(set(re.findall(r"(?<!\d)\d{6}(?!\d)", text)))) or "—"


def _candidate_ids(text: str) -> str:
    values = set(re.findall(r"`([A-Z][A-Z0-9_]+)`", text))
    return ", ".join(sorted(values)) or "—"


def build_conversation_index_text(root: Path) -> str:
    lines = [
        "# 对话索引",
        "",
        "> Raw原文仅保留本地且被Git忽略；本索引只记录可审计元数据。",
        "",
        "| session_id | 主题 | review_status | Raw | Digest |",
        "|---|---|---|---|---|",
        "| legacy-2026-07-30 | 策略迭代与第二大脑初始化 | legacy | "
        "[[06_Conversations/2026-07-30-strategy-iteration-summary]] | — |",
    ]
    for path in digest_paths(root):
        data = read_frontmatter(path)
        session_id = str(data["session_id"])
        source = Path(str(data["source_file"])).with_suffix("").as_posix()
        digest = path.relative_to(root).with_suffix("").as_posix()
        heading = next(
            (
                line.removeprefix("# ").removesuffix(" — 会话Digest")
                for line in read_text(path).splitlines()
                if line.startswith("# ")
            ),
            session_id,
        )
        lines.append(
            f"| {_cell(session_id)} | {_cell(heading)} | "
            f"{_cell(str(data['review_status']))} | [[{source}]] | "
            f"[[{digest}]] |"
        )
    return "\n".join(lines) + "\n"


def build_review_queue_text(root: Path) -> str:
    lines = [
        "# ChatGPT会话人工审核队列",
        "",
        "> `accepted`只表示Digest已人工确认并可进入Context Pack，不代表任何"
        "规则已被ACCEPTED或FROZEN。",
        "",
        "| session_id | Raw | Digest | 涉及股票 | Candidate Rules | "
        "建议案例 | 建议ADR | review_status |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for path in digest_paths(root):
        data = read_frontmatter(path)
        if data["review_status"] == "rejected":
            continue
        text = read_text(path)
        raw_link = Path(str(data["source_file"])).with_suffix("").as_posix()
        digest_link = path.relative_to(root).with_suffix("").as_posix()
        has_cases = "待人工判断" if data["contains_cases"] else "—"
        has_adr = "待人工判断" if data["contains_decisions"] else "—"
        lines.append(
            f"| {_cell(str(data['session_id']))} | [[{raw_link}]] | "
            f"[[{digest_link}]] | {_cell(_stock_codes(text))} | "
            f"{_cell(_candidate_ids(text))} | {has_cases} | {has_adr} | "
            f"{_cell(str(data['review_status']))} |"
        )
    return "\n".join(lines) + "\n"


def write_conversation_views(root: Path) -> tuple[Path, Path]:
    index = root / "06_Conversations" / "CONVERSATION_INDEX.md"
    queue = root / "05_Codex" / "REVIEW_QUEUE.md"
    index.write_text(build_conversation_index_text(root), encoding="utf-8")
    queue.write_text(build_review_queue_text(root), encoding="utf-8")
    return index, queue
