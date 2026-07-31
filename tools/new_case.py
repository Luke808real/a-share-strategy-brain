"""Create a stock case from the Vault template without overwriting files."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
from typing import Sequence

try:
    from .vaultlib import OUTCOME_DIRECTORIES, vault_root
except ImportError:
    from vaultlib import OUTCOME_DIRECTORIES, vault_root


def create_case(
    *,
    root: Path,
    code: str,
    name: str,
    observation_date: date,
    outcome: str,
    strategy_version: str = "phase-2b3",
    confidence: str = "medium",
    data_source: str = "manual",
    source_case_id: str | None = None,
    source_session_id: str | None = None,
    source_digest: str | None = None,
) -> Path:
    if re.fullmatch(r"\d{6}", code) is None:
        raise ValueError("code must contain exactly six digits")
    if outcome not in OUTCOME_DIRECTORIES:
        raise ValueError(f"unsupported outcome: {outcome}")
    if confidence not in {"low", "medium", "high"}:
        raise ValueError("confidence must be low, medium or high")
    template_path = root / "02_Cases" / "Templates" / "CASE_TEMPLATE.md"
    template = template_path.read_text(encoding="utf-8")
    replacements = {
        "{{code}}": code,
        "{{name}}": name,
        "{{observation_date}}": observation_date.isoformat(),
        "{{outcome}}": outcome,
        "{{strategy_version}}": strategy_version,
        "{{confidence}}": confidence,
        "{{data_source}}": data_source,
        "{{source_case_id}}": (
            f'"{source_case_id}"' if source_case_id else "null"
        ),
        "{{source_session_id}}": (
            f'"{source_session_id}"' if source_session_id else "null"
        ),
        "{{source_digest}}": (
            f'"{source_digest}"' if source_digest else "null"
        ),
    }
    content = template
    for marker, value in replacements.items():
        content = content.replace(marker, value)

    destination = (
        root
        / "02_Cases"
        / OUTCOME_DIRECTORIES[outcome]
        / f"{code}-{observation_date.isoformat()}.md"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"case already exists: {destination}")
    destination.write_text(content, encoding="utf-8")
    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create one stock case note")
    parser.add_argument("--code", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--date", required=True, type=date.fromisoformat)
    parser.add_argument(
        "--outcome",
        required=True,
        choices=tuple(OUTCOME_DIRECTORIES),
    )
    parser.add_argument("--strategy-version", default="phase-2b3")
    parser.add_argument(
        "--confidence",
        choices=("low", "medium", "high"),
        default="medium",
    )
    parser.add_argument("--data-source", default="manual")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = create_case(
            root=vault_root(),
            code=args.code,
            name=args.name,
            observation_date=args.date,
            outcome=args.outcome,
            strategy_version=args.strategy_version,
            confidence=args.confidence,
            data_source=args.data_source,
        )
    except (ValueError, FileExistsError) as exc:
        print(str(exc))
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
