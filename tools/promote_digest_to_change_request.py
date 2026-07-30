"""Explicitly create a PROPOSED change request from a reviewed Digest."""

from __future__ import annotations

import argparse
from datetime import date, datetime
from typing import Sequence

try:
    from .chatlib import (
        REVIEWED_DIGEST_STATUSES,
        locate_digest,
        locate_raw,
    )
    from .new_change_request import create_change_request
    from .vaultlib import read_frontmatter, vault_root
except ImportError:
    from chatlib import REVIEWED_DIGEST_STATUSES, locate_digest, locate_raw
    from new_change_request import create_change_request
    from vaultlib import read_frontmatter, vault_root


def _source_date(root, session_id: str) -> date:
    raw = read_frontmatter(locate_raw(root, session_id))
    value = raw.get("date", raw.get("created_at"))
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError as exc:
            raise ValueError("source conversation has no usable date") from exc
    raise ValueError("source conversation has no usable date")


def promote_digest_to_change_request(
    *,
    root,
    session_id: str,
    title: str,
    created_date: date | None = None,
):
    digest_path = locate_digest(root, session_id)
    digest = read_frontmatter(digest_path)
    if digest["review_status"] not in REVIEWED_DIGEST_STATUSES:
        raise ValueError("Digest must be human_reviewed or accepted before promotion")
    return create_change_request(
        root=root,
        title=title,
        status="proposed",
        created_date=created_date or _source_date(root, session_id),
        source_session_id=session_id,
        source_digest=digest_path.relative_to(root).as_posix(),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Promote a reviewed Digest to a PROPOSED change request"
    )
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--date", type=date.fromisoformat)
    args = parser.parse_args(argv)
    try:
        print(
            promote_digest_to_change_request(
                root=vault_root(),
                session_id=args.session_id,
                title=args.title,
                created_date=args.date,
            )
        )
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
