"""Apply an explicit human review decision to one chat Digest."""

from __future__ import annotations

import argparse
from typing import Sequence

try:
    from .chatlib import (
        load_import_manifest,
        locate_digest,
        with_content_hash,
        write_import_manifest,
    )
    from .conversation_views import write_conversation_views
    from .vaultlib import (
        read_frontmatter,
        read_text,
        render_frontmatter,
        split_frontmatter_text,
        vault_root,
    )
except ImportError:
    from chatlib import (
        load_import_manifest,
        locate_digest,
        with_content_hash,
        write_import_manifest,
    )
    from conversation_views import write_conversation_views
    from vaultlib import (
        read_frontmatter,
        read_text,
        render_frontmatter,
        split_frontmatter_text,
        vault_root,
    )


def review_digest(root, session_id: str, status: str):
    if status not in {"accepted", "rejected"}:
        raise ValueError("review status must be accepted or rejected")
    path = locate_digest(root, session_id)
    data = read_frontmatter(path)
    if data["review_status"] == status:
        return path
    if data["review_status"] not in {"draft", "human_reviewed"}:
        raise ValueError(
            f"cannot change review_status from {data['review_status']!r}"
        )
    manifest = load_import_manifest(root)
    items = [
        item
        for item in manifest["sessions"]
        if str(item["session_id"]) == session_id
    ]
    if len(items) != 1:
        raise ValueError(
            f"IMPORT_MANIFEST must contain exactly one {session_id!r} record"
        )
    _, body = split_frontmatter_text(read_text(path))
    data["review_status"] = status
    data["content_hash"] = ""
    path.write_text(
        with_content_hash(render_frontmatter(data, body)),
        encoding="utf-8",
    )
    items[0]["review_status"] = status
    write_import_manifest(root, manifest)
    write_conversation_views(root)
    return path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review one chat Digest")
    parser.add_argument("--session-id", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--accept", action="store_true")
    group.add_argument("--reject", action="store_true")
    args = parser.parse_args(argv)
    try:
        path = review_digest(
            vault_root(),
            args.session_id,
            "accepted" if args.accept else "rejected",
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
