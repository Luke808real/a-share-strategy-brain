"""Explicitly purge one conversation and non-frozen derived drafts."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

try:
    from .build_case_index import write_case_index
    from .build_context_delta import write_context_delta
    from .build_context_pack import rebuild_full_context
    from .chatlib import (
        load_import_manifest,
        locate_digest,
        locate_raw,
        write_import_manifest,
    )
    from .conversation_views import write_conversation_views
    from .vaultlib import case_paths, read_frontmatter, read_text, vault_root
except ImportError:
    from build_case_index import write_case_index
    from build_context_delta import write_context_delta
    from build_context_pack import rebuild_full_context
    from chatlib import (
        load_import_manifest,
        locate_digest,
        locate_raw,
        write_import_manifest,
    )
    from conversation_views import write_conversation_views
    from vaultlib import case_paths, read_frontmatter, read_text, vault_root


class SessionDependencyError(ValueError):
    pass


def _derived_notes(root: Path, session_id: str) -> tuple[Path, ...]:
    paths: list[Path] = []
    for path in case_paths(root):
        data = read_frontmatter(path)
        if str(data.get("source_session_id")) == session_id:
            paths.append(path)
    requests = root / "03_Decisions" / "Requests"
    for path in sorted(requests.glob("*.md")) if requests.exists() else ():
        try:
            data = read_frontmatter(path)
        except ValueError:
            continue
        if str(data.get("source_session_id")) == session_id:
            paths.append(path)
    return tuple(paths)


def dependency_report(root: Path, session_id: str) -> tuple[str, ...]:
    dependencies: list[str] = []
    master = root / "01_Strategy" / "STRATEGY_MASTER.md"
    if session_id in read_text(master):
        dependencies.append(f"{master}: frozen strategy truth references session")
    catalog = root / "01_Strategy" / "RULE_CATALOG.md"
    for line in read_text(catalog).splitlines():
        if session_id in line and "| FROZEN |" in line:
            dependencies.append(f"{catalog}: FROZEN rule references session")
    for path in sorted((root / "03_Decisions").glob("ADR-*.md")):
        data = read_frontmatter(path)
        if (
            data.get("status") in {"ACCEPTED", "FROZEN"}
            and session_id in read_text(path)
        ):
            dependencies.append(f"{path}: accepted/frozen ADR references session")
    for path in _derived_notes(root, session_id):
        data = read_frontmatter(path)
        if data.get("type") == "stock_case" and data.get("case_status") == "confirmed":
            dependencies.append(f"{path}: confirmed case depends on session")
        if data.get("type") == "change_request" and data.get("status") == "accepted":
            dependencies.append(f"{path}: accepted change request depends on session")
    return tuple(dependencies)


def purge_session(root: Path, session_id: str, confirmation: str) -> tuple[Path, ...]:
    if confirmation != session_id:
        raise ValueError("--confirm must exactly match --session-id")
    dependencies = dependency_report(root, session_id)
    if dependencies:
        raise SessionDependencyError(
            "purge stopped because protected dependencies exist:\n- "
            + "\n- ".join(dependencies)
        )
    try:
        raw = locate_raw(root, session_id)
    except FileNotFoundError:
        raw = None
    try:
        digest = locate_digest(root, session_id)
    except FileNotFoundError:
        digest = None
    if raw is None and digest is None:
        raise FileNotFoundError(f"session not found: {session_id}")

    deletions = list(_derived_notes(root, session_id))
    if raw is not None:
        deletions.append(raw)
    if digest is not None:
        deletions.append(digest)
    for directory in (
        root / "06_Conversations" / "Processed",
        root / "07_Inbox" / "ChatGPT",
    ):
        for path in directory.glob("*.md"):
            try:
                data = read_frontmatter(path)
            except ValueError:
                continue
            source_id = data.get("session_id", data.get("conversation_id"))
            if str(source_id) == session_id:
                deletions.append(path)
    unique = tuple(sorted(set(deletions), key=lambda path: path.as_posix()))
    for path in unique:
        path.unlink()

    manifest = load_import_manifest(root)
    manifest["sessions"] = [
        item
        for item in manifest["sessions"]
        if str(item["session_id"]) != session_id
    ]
    batches = []
    for item in manifest["import_batches"]:
        conversation_ids = [
            value
            for value in item.get("conversation_ids", [])
            if str(value) != session_id
        ]
        if conversation_ids:
            updated = dict(item)
            updated["conversation_ids"] = conversation_ids
            batches.append(updated)
    manifest["import_batches"] = batches
    write_import_manifest(root, manifest)
    write_case_index(root)
    write_conversation_views(root)
    rebuild_full_context(root)
    write_context_delta(root)
    return unique


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Purge one session after protected dependency checks"
    )
    parser.add_argument("--session-id", required=True)
    parser.add_argument(
        "--confirm",
        required=True,
        help="must exactly repeat the session ID",
    )
    args = parser.parse_args(argv)
    try:
        deleted = purge_session(
            vault_root(),
            args.session_id,
            args.confirm,
        )
    except (FileNotFoundError, SessionDependencyError, ValueError) as exc:
        print(str(exc))
        return 1
    print(f"purged {args.session_id}: {len(deleted)} file(s)")
    for path in deleted:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
