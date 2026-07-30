"""Validate Agent Exchange schemas, documents and human-gating invariants."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

try:
    from .agentlib import (
        agent_case_paths,
        change_request_paths,
        duplicate_values,
        reasoning_digest_paths,
        validate_agent_note,
    )
    from .build_reasoning_index import (
        build_implementation_queue_text,
        build_reasoning_index_text,
    )
    from .vaultlib import (
        case_paths,
        parse_rule_catalog,
        read_frontmatter,
        read_text,
        vault_root,
    )
except ImportError:
    from agentlib import (
        agent_case_paths,
        change_request_paths,
        duplicate_values,
        reasoning_digest_paths,
        validate_agent_note,
    )
    from build_reasoning_index import (
        build_implementation_queue_text,
        build_reasoning_index_text,
    )
    from vaultlib import (
        case_paths,
        parse_rule_catalog,
        read_frontmatter,
        read_text,
        vault_root,
    )


def validate_agent_exchange(root: Path) -> list[str]:
    errors: list[str] = []
    schema_directory = root / "08_AgentExchange" / "Schemas"
    for name in (
        "case_intake.schema.json",
        "reasoning_digest.schema.json",
        "strategy_change_request.schema.json",
    ):
        path = schema_directory / name
        try:
            parsed = json.loads(read_text(path))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: {exc}")
            continue
        if parsed.get("additionalProperties") is not False:
            errors.append(f"{path}: additionalProperties must be false")

    notes = (
        *agent_case_paths(root),
        *reasoning_digest_paths(root),
        *change_request_paths(root),
    )
    identities: list[str] = []
    hashes: list[str] = []
    for path in notes:
        errors.extend(validate_agent_note(root, path))
        try:
            data = read_frontmatter(path)
        except ValueError:
            continue
        identity = next(
            (
                str(data[field])
                for field in (
                    "case_id",
                    "digest_id",
                    "change_request_id",
                )
                if field in data
            ),
            "",
        )
        identities.append(identity)
        hashes.append(str(data.get("content_hash", "")))
        if data.get("created_by") == "chatgpt":
            for field in ("case_status", "status"):
                if str(data.get(field, "")).upper() in {
                    "ACCEPTED",
                    "FROZEN",
                }:
                    errors.append(
                        f"{path}: Agent cannot create ACCEPTED/FROZEN state"
                    )
    for value in duplicate_values(identities):
        errors.append(f"Agent Exchange: duplicate stable ID {value}")
    for value in duplicate_values(hashes):
        errors.append(f"Agent Exchange: duplicate content_hash {value}")

    for path in agent_case_paths(root):
        data = read_frontmatter(path)
        parent = path.parent.name
        allowed = {
            "Incoming": {"captured", "reviewed", "validated"},
            "Processed": {"observed"},
            "Rejected": {"rejected"},
        }[parent]
        if data.get("case_status") not in allowed:
            errors.append(
                f"{path}: case_status {data.get('case_status')!r} "
                f"is invalid in {parent}"
            )

    rows, catalog_errors = parse_rule_catalog(
        root / "01_Strategy" / "RULE_CATALOG.md"
    )
    errors.extend(catalog_errors)
    known_rules = {row["rule_id"] for row in rows}
    formal_case_ids = {
        path.stem for path in case_paths(root)
    }
    formal_case_ids.update(
        str(read_frontmatter(path).get("source_case_id"))
        for path in case_paths(root)
        if read_frontmatter(path).get("source_case_id")
    )
    exchange_case_ids = {
        str(read_frontmatter(path)["case_id"]) for path in agent_case_paths(root)
    }
    for path in change_request_paths(root):
        data = read_frontmatter(path)
        unknown_rules = sorted(set(data["source_rule_ids"]) - known_rules)
        if unknown_rules:
            errors.append(
                f"{path}: unknown source_rule_ids {', '.join(unknown_rules)}"
            )
        unknown_cases = sorted(
            set(data["source_cases"])
            - exchange_case_ids
            - formal_case_ids
        )
        if unknown_cases:
            errors.append(
                f"{path}: unknown source_cases {', '.join(unknown_cases)}"
            )

    reasoning_index = (
        root / "06_Conversations" / "REASONING_INDEX.md"
    )
    if reasoning_index.is_file() and read_text(
        reasoning_index
    ) != build_reasoning_index_text(root):
        errors.append(f"{reasoning_index}: index is stale")
    implementation_queue = (
        root / "05_Codex" / "IMPLEMENTATION_QUEUE.md"
    )
    if implementation_queue.is_file() and read_text(
        implementation_queue
    ) != build_implementation_queue_text(root):
        errors.append(
            f"{implementation_queue}: implementation queue is stale"
        )
    return sorted(set(errors))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Agent Exchange")
    parser.add_argument("--root", type=Path, default=vault_root())
    args = parser.parse_args(argv)
    errors = validate_agent_exchange(args.root.resolve())
    if errors:
        print(f"Agent Exchange validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Agent Exchange validation passed: "
        f"{len(agent_case_paths(args.root.resolve()))} case intake(s), "
        f"{len(reasoning_digest_paths(args.root.resolve()))} reasoning digest(s), "
        f"{len(change_request_paths(args.root.resolve()))} change request(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
