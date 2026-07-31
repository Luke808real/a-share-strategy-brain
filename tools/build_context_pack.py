"""Build a deterministic, bounded Markdown context pack for LLM projects."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Sequence

try:
    from .agentlib import (
        agent_case_paths,
        change_request_paths,
        reasoning_digest_paths,
    )
    from .chatlib import reviewed_digests
    from .context_sync import (
        artifact_state,
        code_baseline_state,
        load_sync_manifest,
        manifest_from_state,
        write_sync_manifest,
    )
    from .vaultlib import (
        case_paths,
        content_sha256,
        parse_rule_catalog,
        read_frontmatter,
        read_text,
        vault_root,
    )
except ImportError:
    from agentlib import (
        agent_case_paths,
        change_request_paths,
        reasoning_digest_paths,
    )
    from chatlib import reviewed_digests
    from context_sync import (
        artifact_state,
        code_baseline_state,
        load_sync_manifest,
        manifest_from_state,
        write_sync_manifest,
    )
    from vaultlib import (
        case_paths,
        content_sha256,
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


def _reviewed_digest_summaries(root: Path) -> str:
    blocks: list[str] = []
    for path in reviewed_digests(root):
        data = read_frontmatter(path)
        relative = path.relative_to(root).with_suffix("").as_posix()
        body = _without_first_heading(
            re.sub(
                r"\A---\r?\n.*?\r?\n---\r?\n",
                "",
                read_text(path),
                count=1,
                flags=re.DOTALL,
            )
        )
        blocks.append(
            f"### {data['session_id']}\n\n"
            f"> Source: [[{relative}]]；review_status={data['review_status']}\n\n"
            f"{_bounded(body, 5_000)}"
        )
    return "\n\n".join(blocks) if blocks else "暂无已人工审核会话。"


def _recent_reviewed_cases(root: Path) -> str:
    paths = sorted(
        case_paths(root),
        key=lambda path: (
            str(read_frontmatter(path)["observation_date"]),
            path.name,
        ),
    )[-5:]
    if not paths:
        return "暂无已审核案例。"
    return "\n".join(
        f"- [[{path.relative_to(root).with_suffix('').as_posix()}]]："
        f"{read_frontmatter(path)['code']} {read_frontmatter(path)['name']}，"
        f"case_status={read_frontmatter(path)['case_status']}，"
        f"outcome={read_frontmatter(path)['outcome']}"
        for path in paths
    )


def _reviewed_reasoning(root: Path) -> str:
    blocks: list[str] = []
    for path in reasoning_digest_paths(root):
        data = read_frontmatter(path)
        if data["review_status"] not in {"human_reviewed", "accepted"}:
            continue
        body = re.sub(
            r"\A---\r?\n.*?\r?\n---\r?\n",
            "",
            read_text(path),
            count=1,
            flags=re.DOTALL,
        ).strip()
        link = path.relative_to(root).with_suffix("").as_posix()
        blocks.append(
            f"### {data['digest_id']}\n\n"
            f"> Source: [[{link}]]；review_status={data['review_status']}\n\n"
            f"{_bounded(body, 4_000)}"
        )
    return "\n\n".join(blocks) if blocks else "暂无已审核推理摘要。"


def _pending_agent_intakes(root: Path) -> str:
    blocks: list[str] = []
    for path in agent_case_paths(root):
        if path.parent.name != "Incoming":
            continue
        data = read_frontmatter(path)
        text = read_text(path)
        link = path.relative_to(root).with_suffix("").as_posix()
        limitations = _extract_section(text, "数据限制")
        conclusion = _extract_section(text, "当前结论")
        blocks.append(
            f"- [[{link}|{data['case_id']}]]：{data['stock_code']} "
            f"{data['stock_name']}，status={data['case_status']}；"
            f"数据限制={_bounded(limitations, 500)}；"
            f"当前结论={_bounded(conclusion, 500)}"
        )
    return "\n".join(blocks) if blocks else "暂无待审核Agent Intake。"


def _approved_change_requests(root: Path) -> str:
    blocks: list[str] = []
    for path in change_request_paths(root):
        data = read_frontmatter(path)
        if data["status"] != "approved_for_implementation":
            continue
        link = path.relative_to(root).with_suffix("").as_posix()
        blocks.append(
            f"- [[{link}|{data['change_request_id']}]]："
            f"{data['proposed_scope']}；rules="
            f"{', '.join(data['source_rule_ids'])}；"
            f"history_impact={data['expected_history_impact']}"
        )
    return "\n".join(blocks) if blocks else "暂无获批代码变更请求。"


def _code_baseline(root: Path) -> str:
    state = code_baseline_state(root)
    return "\n".join(
        (
            f"- 代码仓库：`{state['code_repository']}`",
            f"- 冻结策略版本：`{state['strategy_version']}`",
            f"- 冻结tag：`{state['strategy_repo_tag']}`",
            f"- 策略内容commit：`{state['strategy_content_commit']}`",
            f"- main集成commit：`{state['strategy_main_integration_commit']}`",
            f"- 策略tree：`{state['strategy_tree_sha']}`",
            f"- 基线关系：`{state['baseline_relation']}`",
            f"- 当前分支：`{state['observed_branch']}`",
            f"- 当前commit：`{state['observed_commit']}`",
            f"- 观测main：`{state['observed_main_commit']}`",
            f"- 观测tag：`{state['observed_tag_commit']}`",
            f"- drift状态：`{state['drift_status']}`",
        )
    )


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
            f"## {section_number + 6}. 已人工审核会话",
            "",
            "> Source: [[06_Conversations/CONVERSATION_INDEX]]及"
            "human_reviewed/accepted Digests；不读取Raw。",
            "",
            _bounded(_reviewed_digest_summaries(root), 12_000),
            "",
            f"## {section_number + 7}. 最近已审核案例",
            "",
            "> Source: [[02_Cases/CASE_INDEX]]。",
            "",
            _recent_reviewed_cases(root),
            "",
            f"## {section_number + 8}. 最近可审计推理摘要",
            "",
            "> Source: [[06_Conversations/REASONING_INDEX]]；仅包含"
            "human_reviewed/accepted。",
            "",
            _bounded(_reviewed_reasoning(root), 10_000),
            "",
            f"## {section_number + 9}. 待审核Agent Intake",
            "",
            "> 下列内容尚未进入正式策略摘要，仅供人工审核。",
            "",
            _bounded(_pending_agent_intakes(root), 7_000),
            "",
            f"## {section_number + 10}. 获批代码变更请求",
            "",
            "> Source: [[05_Codex/IMPLEMENTATION_QUEUE]]；仅包含"
            "approved_for_implementation。",
            "",
            _approved_change_requests(root),
            "",
            f"## {section_number + 11}. 代码仓库基线与drift",
            "",
            "> Source: `01_Strategy/BASELINE_MANIFEST.yaml`及本地Git只读状态。",
            "",
            _code_baseline(root),
            "",
        ]
    )
    return "\n".join(parts)


def build_case_context_pack_text(root: Path) -> str:
    return "\n".join(
        (
            "# Case Context Pack",
            "",
            "> 只包含结构化案例摘要，不包含聊天Raw或截图二进制。",
            "",
            "## 成功案例",
            "",
            _case_summaries(root, "success"),
            "",
            "## 失败案例",
            "",
            _case_summaries(root, "failure"),
            "",
            "## 观察案例",
            "",
            _case_summaries(root, "watching"),
            "",
        )
    )


def write_context_pack(root: Path, output: Path | None = None) -> Path:
    destination = output or root / "exports" / "LLM_CONTEXT_PACK.md"
    if not destination.is_absolute():
        destination = root / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_context_pack_text(root), encoding="utf-8")
    return destination


def rebuild_full_context(root: Path, output: Path | None = None) -> tuple[Path, Path]:
    full_path = write_context_pack(root, output)
    case_path = root / "exports" / "CASE_CONTEXT_PACK.md"
    case_path.write_text(build_case_context_pack_text(root), encoding="utf-8")
    sync_path = root / "exports" / "CHAT_SYNC_MANIFEST.yaml"
    previous = load_sync_manifest(sync_path)
    state = artifact_state(root)
    manifest = manifest_from_state(
        root,
        state,
        last_full_pack_hash=content_sha256(read_text(full_path)),
        last_delta_pack_hash=str(previous.get("last_delta_pack_hash", "")),
    )
    write_sync_manifest(root, manifest)
    return full_path, case_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build LLM_CONTEXT_PACK.md")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("exports/LLM_CONTEXT_PACK.md"),
    )
    parser.add_argument(
        "--rebuild-full",
        action="store_true",
        help="also rebuild case pack and advance the sync manifest",
    )
    args = parser.parse_args(argv)
    root = vault_root()
    if args.rebuild_full:
        for path in rebuild_full_context(root, args.output):
            print(path)
    else:
        print(write_context_pack(root, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
