"""Human-gated review and promotion of one Agent case intake."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import shutil
from typing import Sequence

try:
    from .agentlib import (
        extract_section,
        reasoning_digest_paths,
        validate_agent_note,
    )
    from .build_case_index import write_case_index
    from .chatlib import with_content_hash
    from .new_case import create_case
    from .vaultlib import (
        read_frontmatter,
        read_text,
        render_frontmatter,
        split_frontmatter_text,
        vault_root,
    )
except ImportError:
    from agentlib import (
        extract_section,
        reasoning_digest_paths,
        validate_agent_note,
    )
    from build_case_index import write_case_index
    from chatlib import with_content_hash
    from new_case import create_case
    from vaultlib import (
        read_frontmatter,
        read_text,
        render_frontmatter,
        split_frontmatter_text,
        vault_root,
    )


def _incoming_path(root: Path, case_id: str) -> Path:
    path = root / "08_AgentExchange" / "Incoming" / f"{case_id}.md"
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def _set_case_status(path: Path, status: str) -> None:
    data, body = split_frontmatter_text(read_text(path))
    data["case_status"] = status
    data["content_hash"] = ""
    path.write_text(
        with_content_hash(render_frontmatter(data, body)),
        encoding="utf-8",
    )


def review_agent_case(root: Path, case_id: str) -> Path:
    path = _incoming_path(root, case_id)
    data = read_frontmatter(path)
    if data["case_status"] == "captured":
        _set_case_status(path, "reviewed")
    elif data["case_status"] not in {"reviewed", "validated"}:
        raise ValueError(
            f"cannot review case from status {data['case_status']!r}"
        )
    return path


def _reviewed_digest_for_case(root: Path, case_id: str) -> str | None:
    matches: list[Path] = []
    for path in reasoning_digest_paths(root):
        data = read_frontmatter(path)
        if (
            case_id in data.get("source_case_ids", [])
            and data.get("review_status") in {"human_reviewed", "accepted"}
        ):
            matches.append(path)
    if not matches:
        return None
    return matches[0].relative_to(root).as_posix()


def _replace_section(text: str, heading: str, body: str) -> str:
    pattern = re.compile(
        rf"(^## {re.escape(heading)}\s*$\n)(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    return pattern.sub(rf"\1\n{body.strip()}\n\n", text, count=1)


def promote_agent_case(
    *,
    root: Path,
    case_id: str,
    outcome: str,
) -> Path:
    source = _incoming_path(root, case_id)
    errors = validate_agent_note(root, source)
    if errors:
        raise ValueError("\n".join(errors))
    intake = read_frontmatter(source)
    if intake["case_status"] not in {"reviewed", "validated"}:
        raise ValueError(
            "CAPTURED case cannot be promoted; run explicit review first"
        )
    processed = (
        root / "08_AgentExchange" / "Processed" / f"{case_id}.md"
    )
    if processed.exists():
        raise FileExistsError(processed)
    source_digest = intake.get("source_digest") or _reviewed_digest_for_case(
        root, case_id
    )
    observation = intake["observation_date"]
    if isinstance(observation, str):
        observation = date.fromisoformat(observation)
    destination = create_case(
        root=root,
        code=str(intake["stock_code"]),
        name=str(intake["stock_name"]),
        observation_date=observation,
        outcome=outcome,
        strategy_version=str(intake["strategy_version"]),
        confidence=(
            (extract_section(read_text(source), "置信度") or "low")
            .splitlines()[0]
            .strip()
            .lower()
        ),
        data_source="agent_exchange",
        source_case_id=case_id,
        source_session_id=str(intake["source_session_id"]),
        source_digest=str(source_digest) if source_digest else None,
    )
    text = read_text(source)
    formal = read_text(destination)
    raw_facts = "\n\n".join(
        (
            "### 图片可确认事实\n\n"
            + (extract_section(text, "图片可确认事实") or "TODO"),
            "### 用户提供的背景\n\n"
            + (extract_section(text, "用户提供的背景") or "TODO"),
            "### 数据限制\n\n"
            + (extract_section(text, "数据限制") or "TODO"),
        )
    )
    replacements = {
        "原始数据": raw_facts,
        "支撑与压力": extract_section(text, "支撑与压力") or "TODO",
        "setup时间线": (
            "当前setup状态：\n\n"
            + (extract_section(text, "当前setup状态") or "TODO")
            + "\n\nB1/B2判断：\n\n"
            + (extract_section(text, "B1/B2判断") or "TODO")
        ),
        "成功或失败原因": (
            "风险事件：\n\n"
            + (extract_section(text, "风险事件") or "TODO")
            + "\n\n反对证据：\n\n"
            + (extract_section(text, "反对证据") or "TODO")
        ),
        "可提炼特征": extract_section(text, "候选特征") or "TODO",
        "不能得出的结论": (
            extract_section(text, "数据限制")
            or "TODO：不得由单一案例修改冻结策略。"
        ),
        "与当前策略的关系": (
            extract_section(text, "对冻结策略的影响")
            or "无自动影响。"
        ),
        "后续需要验证的问题": (
            extract_section(text, "次日验证条件") or "TODO"
        ),
    }
    for heading, body in replacements.items():
        formal = _replace_section(formal, heading, body)
    destination.write_text(formal, encoding="utf-8")

    _set_case_status(source, "observed")
    processed.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(processed))
    write_case_index(root)
    return destination


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Review or promote one Agent case with human approval"
    )
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--approve", action="store_true", required=True)
    parser.add_argument(
        "--outcome",
        choices=("watching", "success", "failure"),
        help="omit on first call to move CAPTURED to REVIEWED",
    )
    args = parser.parse_args(argv)
    try:
        if args.outcome is None:
            path = review_agent_case(vault_root(), args.case_id)
            print(f"reviewed: {path}")
        else:
            path = promote_agent_case(
                root=vault_root(),
                case_id=args.case_id,
                outcome=args.outcome,
            )
            print(f"promoted: {path}")
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
