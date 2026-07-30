"""Build deterministic indexes for reasoning digests and implementation queue."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

try:
    from .agentlib import change_request_paths, reasoning_digest_paths
    from .vaultlib import read_frontmatter, vault_root
except ImportError:
    from agentlib import change_request_paths, reasoning_digest_paths
    from vaultlib import read_frontmatter, vault_root


def build_reasoning_index_text(root: Path) -> str:
    lines = [
        "# 可审计推理摘要索引",
        "",
        "> 由 `python tools/build_reasoning_index.py` 确定性生成。",
        "",
        "| digest_id | source_session_id | review_status | confidence | 文件 |",
        "|---|---|---|---|---|",
    ]
    for path in reasoning_digest_paths(root):
        data = read_frontmatter(path)
        link = path.relative_to(root).with_suffix("").as_posix()
        lines.append(
            f"| {data['digest_id']} | {data['source_session_id']} | "
            f"{data['review_status']} | {data['confidence']} | [[{link}]] |"
        )
    return "\n".join(lines) + "\n"


def build_implementation_queue_text(root: Path) -> str:
    lines = [
        "# 策略代码实现队列",
        "",
        "> 只列出状态为`approved_for_implementation`的Change Request。",
        "",
        "| change_request_id | source cases | rule IDs | Issue草稿 |",
        "|---|---|---|---|",
    ]
    for path in change_request_paths(root):
        data = read_frontmatter(path)
        if data["status"] != "approved_for_implementation":
            continue
        cases = ", ".join(str(value) for value in data["source_cases"])
        rules = ", ".join(str(value) for value in data["source_rule_ids"])
        issue = (
            root
            / "05_Codex"
            / "ChangeRequests"
            / "IssueDrafts"
            / f"{data['change_request_id']}.md"
        )
        issue_cell = (
            f"[[{issue.relative_to(root).with_suffix('').as_posix()}]]"
            if issue.is_file()
            else "待生成"
        )
        link = path.relative_to(root).with_suffix("").as_posix()
        lines.append(
            f"| [[{link}|{data['change_request_id']}]] | {cases} | "
            f"{rules} | {issue_cell} |"
        )
    return "\n".join(lines) + "\n"


def write_reasoning_indexes(root: Path) -> tuple[Path, Path]:
    reasoning = root / "06_Conversations" / "REASONING_INDEX.md"
    queue = root / "05_Codex" / "IMPLEMENTATION_QUEUE.md"
    reasoning.write_text(build_reasoning_index_text(root), encoding="utf-8")
    queue.write_text(build_implementation_queue_text(root), encoding="utf-8")
    return reasoning, queue


def main(argv: Sequence[str] | None = None) -> int:
    argparse.ArgumentParser(
        description="Build reasoning and approved implementation indexes"
    ).parse_args(argv)
    for path in write_reasoning_indexes(vault_root()):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
