"""Validate and ingest one structured Agent case without promoting it."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

try:
    from .agentlib import agent_case_paths, validate_agent_note
    from .vaultlib import (
        content_sha256,
        read_frontmatter,
        read_text,
        vault_root,
    )
    from .chatlib import with_content_hash
except ImportError:
    from agentlib import agent_case_paths, validate_agent_note
    from vaultlib import content_sha256, read_frontmatter, read_text, vault_root
    from chatlib import with_content_hash


def ingest_agent_case(
    root: Path,
    source: Path,
    *,
    dry_run: bool = False,
) -> Path:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    errors = validate_agent_note(root, source, verify_hash=False)
    if errors:
        raise ValueError("\n".join(errors))
    data = read_frontmatter(source)
    if data["type"] != "case_intake":
        raise ValueError("ingest_agent_case only accepts case_intake")
    if data["case_status"] != "captured":
        raise ValueError("Agent intake must begin with case_status=captured")
    normalized = with_content_hash(read_text(source))
    content_hash = content_sha256(normalized)
    known_ids: set[str] = set()
    known_hashes: set[str] = set()
    for path in agent_case_paths(root):
        existing = read_frontmatter(path)
        known_ids.add(str(existing["case_id"]))
        known_hashes.add(str(existing["content_hash"]))
    duplicate_errors: list[str] = []
    if str(data["case_id"]) in known_ids:
        duplicate_errors.append(f"duplicate case_id: {data['case_id']}")
    if content_hash in known_hashes:
        duplicate_errors.append(f"duplicate content_hash: {content_hash}")
    if duplicate_errors:
        raise ValueError("\n".join(duplicate_errors))
    destination = (
        root
        / "08_AgentExchange"
        / "Incoming"
        / f"{data['case_id']}.md"
    )
    if destination.exists():
        raise FileExistsError(destination)
    if not dry_run:
        destination.write_text(normalized, encoding="utf-8")
    return destination


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and ingest one Agent case into Incoming"
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        destination = ingest_agent_case(
            vault_root(),
            args.source,
            dry_run=args.dry_run,
        )
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 1
    prefix = "would write" if args.dry_run else "wrote"
    print(f"{prefix}: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
