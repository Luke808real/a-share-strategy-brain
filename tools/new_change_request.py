"""Create a deterministic strategy change-request draft."""

from __future__ import annotations

import argparse
from datetime import date
from hashlib import sha256
from pathlib import Path
from typing import Sequence

try:
    from .vaultlib import vault_root
except ImportError:
    from vaultlib import vault_root


CHANGE_STATUSES = ("observed", "proposed", "accepted", "rejected")


def create_change_request(
    *,
    root: Path,
    title: str,
    status: str,
    created_date: date,
    source_session_id: str | None = None,
    source_digest: str | None = None,
) -> Path:
    if not title.strip():
        raise ValueError("title cannot be empty")
    if status not in CHANGE_STATUSES:
        raise ValueError(f"unsupported status: {status}")
    template = (
        root / "05_Codex" / "CHANGE_REQUEST_TEMPLATE.md"
    ).read_text(encoding="utf-8")
    content = (
        template.replace("{{title}}", title.strip())
        .replace("{{status}}", status)
        .replace("{{created_date}}", created_date.isoformat())
        .replace(
            "{{source_session_id}}",
            f'"{source_session_id}"' if source_session_id else "null",
        )
        .replace(
            "{{source_digest}}",
            f'"{source_digest}"' if source_digest else "null",
        )
    )
    digest = sha256(title.strip().encode("utf-8")).hexdigest()[:10]
    destination = (
        root
        / "03_Decisions"
        / "Requests"
        / f"{created_date.isoformat()}-change-{digest}.md"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"change request already exists: {destination}")
    destination.write_text(content, encoding="utf-8")
    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create one strategy change-request draft"
    )
    parser.add_argument("--title", required=True)
    parser.add_argument("--status", choices=CHANGE_STATUSES, required=True)
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = create_change_request(
            root=vault_root(),
            title=args.title,
            status=args.status,
            created_date=args.date,
        )
    except (ValueError, FileExistsError) as exc:
        print(str(exc))
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
