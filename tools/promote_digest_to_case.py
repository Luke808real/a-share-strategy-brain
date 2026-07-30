"""Explicitly create one OBSERVED case from a human-reviewed Digest."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
from typing import Sequence

try:
    from .build_case_index import write_case_index
    from .chatlib import REVIEWED_DIGEST_STATUSES, extract_section, locate_digest
    from .new_case import create_case
    from .vaultlib import (
        read_frontmatter,
        read_text,
        render_frontmatter,
        split_frontmatter_text,
        vault_root,
    )
except ImportError:
    from build_case_index import write_case_index
    from chatlib import REVIEWED_DIGEST_STATUSES, extract_section, locate_digest
    from new_case import create_case
    from vaultlib import (
        read_frontmatter,
        read_text,
        render_frontmatter,
        split_frontmatter_text,
        vault_root,
    )


def _replace_section(text: str, heading: str, body: str) -> str:
    pattern = re.compile(
        rf"(^## {re.escape(heading)}\s*$\n)(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    return pattern.sub(rf"\1\n{body.strip()}\n\n", text, count=1)


def promote_digest_to_case(
    *,
    root: Path,
    session_id: str,
    code: str,
    name: str,
    observation_date: date,
    outcome: str,
) -> Path:
    digest_path = locate_digest(root, session_id)
    digest = read_frontmatter(digest_path)
    if digest["review_status"] not in REVIEWED_DIGEST_STATUSES:
        raise ValueError("Digest must be human_reviewed or accepted before promotion")
    relative_digest = digest_path.relative_to(root).as_posix()
    destination = create_case(
        root=root,
        code=code,
        name=name,
        observation_date=observation_date,
        outcome=outcome,
        strategy_version=str(digest["strategy_version"]),
        confidence="low",
        data_source="chat_digest",
        source_session_id=session_id,
        source_digest=relative_digest,
    )
    text = read_text(destination)
    facts = extract_section(read_text(digest_path), "原始事实与数据")
    facts_text = facts if facts and facts != "TODO" else (
        "TODO：Digest中的原始事实不足。不得猜测价格、日期、成交量或指标。"
    )
    text = _replace_section(
        text,
        "原始数据",
        f"{facts_text}\n\n来源：[[{digest_path.relative_to(root).with_suffix('').as_posix()}]]",
    )
    data, body = split_frontmatter_text(text)
    data["case_status"] = "observed"
    destination.write_text(render_frontmatter(data, body), encoding="utf-8")
    write_case_index(root)
    return destination


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Promote one reviewed Digest to an OBSERVED case"
    )
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--code", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--date", required=True, type=date.fromisoformat)
    parser.add_argument(
        "--outcome",
        required=True,
        choices=("success", "failure", "watching"),
    )
    args = parser.parse_args(argv)
    try:
        print(
            promote_digest_to_case(
                root=vault_root(),
                session_id=args.session_id,
                code=args.code,
                name=args.name,
                observation_date=args.date,
                outcome=args.outcome,
            )
        )
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
