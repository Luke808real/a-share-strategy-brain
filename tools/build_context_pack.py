"""Build a deterministic, bounded Markdown context pack for LLM projects."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Sequence

try:
    from .vaultlib import (
        case_paths,
        parse_rule_catalog,
        read_frontmatter,
        read_text,
        vault_root,
    )
except ImportError:
    from vaultlib import (
        case_paths,
        parse_rule_catalog,
        read_frontmatter,
        read_text,
        vault_root,
    )


SECTION_SOURCES = (
    ("当前阶段", "05_Codex/CURRENT_PHASE.md", 5_000),
    ("当前冻结策略摘要", "01_Strategy/STRATEGY_MASTER.md", 14_000),
    ("状态机", "01_Strategy/STATE_MACHINE.md", 7_000),
)


def _bounded(text: str, limit: int) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[:limit].rstrip() + "\n\n> 内容已按确定性长度上限截断。"


def _without_first_heading(text: str) -> str:
    return re.sub(r"\A# [^\n]+\n+", "", text.strip(), count=1)


def _extract_section(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$\n(?P<body>.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group("body").strip() if match else "未记录。"


def _accepted_decisions(root: Path) -> str:
    blocks: list[str] = []
    paths = sorted((root / "03_Decisions").glob("ADR-[0-9][0-9][0-9]-*.md"))
    for path in paths[-3:]:
        data = read_frontmatter(path)
        if data.get("status") != "ACCEPTED":
            continue
        decision = _extract_section(read_text(path), "决策")
        relative = path.relative_to(root).with_suffix("").as_posix()
        blocks.append(
            f"### {data['adr_id']} {data['title']}\n\n"
            f"> Source: [[{relative}]]\n\n{_bounded(decision, 2_500)}"
        )
    return "\n\n".join(blocks) if blocks else "暂无已采纳决策。"


def _proposed_rules(root: Path) -> str:
    path = root / "01_Strategy" / "RULE_CATALOG.md"
    rows, errors = parse_rule_catalog(path)
    if errors:
        raise ValueError("; ".join(errors))
    proposed = sorted(
        (row for row in rows if row["状态"] == "PROPOSED"),
        key=lambda row: row["rule_id"],
    )
    if not proposed:
        return "暂无PROPOSED规则。"
    return "\n".join(
        f"- `{row['rule_id']}`（{row['适用层级']}）：{row['判断语义']}；"
        f"代码实现={row['代码实现']}；来源={row['来源决策']}"
        for row in proposed
    )


def _case_summaries(root: Path, outcome: str) -> str:
    blocks: list[str] = []
    for path in case_paths(root):
        data = read_frontmatter(path)
        if data.get("outcome") != outcome:
            continue
        text = read_text(path)
        features = _extract_section(text, "可提炼特征")
        limits = _extract_section(text, "不能得出的结论")
        relation = _extract_section(text, "与当前策略的关系")
        relative = path.relative_to(root).with_suffix("").as_posix()
        tags = ", ".join(str(tag) for tag in data.get("tags", []))
        blocks.append(
            f"### {data['code']} {data['name']} "
            f"({data['observation_date']})\n\n"
            f"> Source: [[{relative}]]\n\n"
            f"- 状态：{data['case_status']}；置信度：{data['confidence']}\n"
            f"- 标签：{tags or '无'}\n"
            f"- 可提炼特征：{features}\n"
            f"- 不能得出的结论：{limits}\n"
            f"- 与当前策略关系：{relation}"
        )
    return "\n\n".join(blocks) if blocks else "暂无案例。"


def build_context_pack_text(root: Path) -> str:
    parts = [
        "# LLM Context Pack",
        "",
        "> 用途：ChatGPT Project/Codex上下文。由本地确定性工具生成；"
        "不包含图片二进制或完整历史聊天原文。",
    ]
    section_number = 1
    for title, relative, limit in SECTION_SOURCES:
        source = root / relative
        parts.extend(
            [
                "",
                f"## {section_number}. {title}",
                "",
                f"> Source: [[{Path(relative).with_suffix('').as_posix()}]]",
                "",
                _bounded(_without_first_heading(read_text(source)), limit),
            ]
        )
        section_number += 1

    parts.extend(
        [
            "",
            f"## {section_number}. 最近已采纳决策",
            "",
            "> Sources: [[03_Decisions/DECISION_INDEX]]及最近三份ACCEPTED ADR",
            "",
            _accepted_decisions(root),
            "",
            f"## {section_number + 1}. 当前PROPOSED规则",
            "",
            "> Sources: [[01_Strategy/RULE_CATALOG]]、"
            "[[04_Research/Candidate-Rules]]",
            "",
            _bounded(_proposed_rules(root), 9_000),
            "",
            f"## {section_number + 2}. 成功案例摘要",
            "",
            "> Source: [[02_Cases/CASE_INDEX]]及Success案例",
            "",
            _bounded(_case_summaries(root, "success"), 9_000),
            "",
            f"## {section_number + 3}. 失败案例摘要",
            "",
            "> Source: [[02_Cases/CASE_INDEX]]及Failure案例",
            "",
            _bounded(_case_summaries(root, "failure"), 5_000),
            "",
            f"## {section_number + 4}. 当前待办",
            "",
            "> Source: [[04_Research/Research-Backlog]]",
            "",
            _bounded(
                _without_first_heading(
                    read_text(root / "04_Research" / "Research-Backlog.md")
                ),
                6_000,
            ),
            "",
            f"## {section_number + 5}. 最新Codex提示",
            "",
            "> Source: [[05_Codex/NEXT_PROMPT]]",
            "",
            _bounded(
                _without_first_heading(
                    read_text(root / "05_Codex" / "NEXT_PROMPT.md")
                ),
                6_000,
            ),
            "",
        ]
    )
    return "\n".join(parts)


def write_context_pack(root: Path, output: Path | None = None) -> Path:
    destination = output or root / "exports" / "LLM_CONTEXT_PACK.md"
    if not destination.is_absolute():
        destination = root / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_context_pack_text(root), encoding="utf-8")
    return destination


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build LLM_CONTEXT_PACK.md")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("exports/LLM_CONTEXT_PACK.md"),
    )
    args = parser.parse_args(argv)
    print(write_context_pack(vault_root(), args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
