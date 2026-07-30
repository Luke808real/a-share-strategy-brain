"""Build a code-repository Issue draft from one approved Change Request."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Sequence

try:
    from .agentlib import (
        change_request_paths,
        extract_section,
        validate_agent_note,
    )
    from .build_reasoning_index import write_reasoning_indexes
    from .vaultlib import read_frontmatter, read_text, vault_root
except ImportError:
    from agentlib import (
        change_request_paths,
        extract_section,
        validate_agent_note,
    )
    from build_reasoning_index import write_reasoning_indexes
    from vaultlib import read_frontmatter, read_text, vault_root


def locate_change_request(root: Path, change_request_id: str) -> Path:
    matches = [
        path
        for path in change_request_paths(root)
        if str(read_frontmatter(path).get("change_request_id"))
        == change_request_id
    ]
    if len(matches) != 1:
        raise FileNotFoundError(
            f"expected one Change Request {change_request_id!r}, "
            f"found {len(matches)}"
        )
    return matches[0]


def build_issue_draft_text(root: Path, request_path: Path) -> str:
    errors = validate_agent_note(root, request_path)
    if errors:
        raise ValueError("\n".join(errors))
    data = read_frontmatter(request_path)
    if data["status"] != "approved_for_implementation":
        raise ValueError(
            "Change Request is not approved_for_implementation"
        )
    text = read_text(request_path)
    adr_links = sorted(
        set(
            re.findall(
                r"\[\[(03_Decisions/ADR-[^|\]#]+)",
                text,
            )
        )
    )
    request_link = request_path.relative_to(root).with_suffix("").as_posix()
    cases = "\n".join(f"- `{value}`" for value in data["source_cases"])
    rules = "\n".join(f"- `{value}`" for value in data["source_rule_ids"])
    adrs = (
        "\n".join(f"- `a-share-strategy-brain/{value}.md`" for value in adr_links)
        if adr_links
        else "- TODO：关联ADR尚未填写"
    )
    return "\n".join(
        (
            f"# [{data['change_request_id']}] {data['proposed_scope']}",
            "",
            "## 知识库来源",
            "",
            f"- Change Request: `a-share-strategy-brain/{request_link}.md`",
            "",
            "### Source cases",
            "",
            cases,
            "",
            "### Rule IDs",
            "",
            rules,
            "",
            "### ADR",
            "",
            adrs,
            "",
            "## 当前规则",
            "",
            extract_section(text, "当前规则") or "TODO",
            "",
            "## 预期历史信号影响",
            "",
            str(data["expected_history_impact"]),
            "",
            "## 必需Golden Regression",
            "",
            "\n".join(
                f"- {value}" for value in data["required_regression_cases"]
            ),
            "",
            "## 实现PR必须报告",
            "",
            "- 修改文件；",
            "- 配置变化；",
            "- Golden Regression；",
            "- 默认离线测试；",
            "- integration测试；",
            "- 历史信号变化说明；",
            "- 回滚方法。",
            "",
            "> 本文件只是Issue草稿，不自动创建Issue、修改代码或合并PR。",
            "",
        )
    )


def write_issue_draft(root: Path, change_request_id: str) -> Path:
    request_path = locate_change_request(root, change_request_id)
    destination = (
        root
        / "05_Codex"
        / "ChangeRequests"
        / "IssueDrafts"
        / f"{change_request_id}.md"
    )
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        build_issue_draft_text(root, request_path),
        encoding="utf-8",
    )
    write_reasoning_indexes(root)
    return destination


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a code Issue draft from an approved Change Request"
    )
    parser.add_argument("--change-request-id", required=True)
    args = parser.parse_args(argv)
    try:
        print(write_issue_draft(vault_root(), args.change_request_id))
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
