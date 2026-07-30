"""Validate and ingest structured ChatGPT notes from the local-only Inbox."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Sequence

try:
    from .build_chat_digest import write_digest
    from .chatlib import (
        conversation_id,
        load_import_manifest,
        validate_conversation_frontmatter,
        with_content_hash,
        write_import_manifest,
    )
    from .conversation_views import write_conversation_views
    from .vaultlib import content_sha256, read_frontmatter, read_text, vault_root
except ImportError:
    from build_chat_digest import write_digest
    from chatlib import (
        conversation_id,
        load_import_manifest,
        validate_conversation_frontmatter,
        with_content_hash,
        write_import_manifest,
    )
    from conversation_views import write_conversation_views
    from vaultlib import content_sha256, read_frontmatter, read_text, vault_root


@dataclass(frozen=True)
class PreparedInboxNote:
    source: Path
    session_id: str
    content_hash: str
    raw_text: str
    raw_destination: Path
    archive_destination: Path
    note_type: str


def plan_ingest(root: Path) -> tuple[list[PreparedInboxNote], list[str]]:
    inbox = root / "07_Inbox" / "ChatGPT"
    manifest = load_import_manifest(root)
    known_ids = {str(item["session_id"]) for item in manifest["sessions"]}
    known_hashes = {str(item["content_hash"]) for item in manifest["sessions"]}
    planned_ids: set[str] = set()
    planned_hashes: set[str] = set()
    prepared: list[PreparedInboxNote] = []
    errors: list[str] = []
    for path in sorted(inbox.glob("*.md"), key=lambda item: item.name):
        note_errors = validate_conversation_frontmatter(path, verify_hash=False)
        if note_errors:
            errors.extend(note_errors)
            continue
        data = read_frontmatter(path)
        session_id = conversation_id(data)
        normalized = with_content_hash(read_text(path))
        digest = content_sha256(normalized)
        if session_id in known_ids or session_id in planned_ids:
            errors.append(f"{path}: duplicate session_id {session_id}")
        if digest in known_hashes or digest in planned_hashes:
            errors.append(f"{path}: duplicate content_hash {digest}")
        raw_destination = (
            root / "06_Conversations" / "Raw" / f"{session_id}.md"
        )
        archive_destination = (
            root / "06_Conversations" / "Processed" / f"{session_id}.md"
        )
        if raw_destination.exists():
            errors.append(f"{path}: Raw destination already exists")
        planned_ids.add(session_id)
        planned_hashes.add(digest)
        prepared.append(
            PreparedInboxNote(
                source=path,
                session_id=session_id,
                content_hash=digest,
                raw_text=normalized,
                raw_destination=raw_destination,
                archive_destination=archive_destination,
                note_type=str(data["type"]),
            )
        )
    return prepared, errors


def ingest_inbox(
    root: Path,
    *,
    dry_run: bool = False,
    archive: bool = False,
) -> list[PreparedInboxNote]:
    prepared, errors = plan_ingest(root)
    if errors:
        raise ValueError("\n".join(errors))
    if dry_run:
        return prepared
    if archive:
        conflicts = [
            item.archive_destination
            for item in prepared
            if item.archive_destination.exists()
        ]
        if conflicts:
            raise FileExistsError(
                "archive destinations already exist: "
                + ", ".join(str(path) for path in conflicts)
            )

    manifest = load_import_manifest(root)
    for item in prepared:
        item.raw_destination.parent.mkdir(parents=True, exist_ok=True)
        item.raw_destination.write_text(item.raw_text, encoding="utf-8")
        write_digest(root, item.raw_destination)
        manifest["sessions"].append(
            {
                "session_id": item.session_id,
                "content_hash": item.content_hash,
                "raw_file": item.raw_destination.relative_to(root).as_posix(),
                "digest_file": (
                    f"06_Conversations/Digests/{item.session_id}.md"
                ),
                "source_type": item.note_type,
                "review_status": "draft",
            }
        )
    write_import_manifest(root, manifest)
    write_conversation_views(root)
    if archive:
        for item in prepared:
            item.archive_destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item.source), str(item.archive_destination))
    return prepared


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest ChatGPT Inbox notes")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument(
        "--archive",
        action="store_true",
        help="move successfully ingested Inbox sources to Processed",
    )
    args = parser.parse_args(argv)
    try:
        prepared = ingest_inbox(
            vault_root(),
            dry_run=args.dry_run,
            archive=args.archive,
        )
    except (FileExistsError, ValueError) as exc:
        print(str(exc))
        return 1
    action = "would ingest" if args.dry_run else "ingested"
    if not prepared:
        print(f"{action}: 0 conversation(s)")
    else:
        print(f"{action}: {len(prepared)} conversation(s)")
        for item in prepared:
            print(f"- {item.session_id}: {item.source.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
