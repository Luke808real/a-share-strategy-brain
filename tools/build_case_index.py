"""Build the deterministic case index from case frontmatter."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

try:
    from .vaultlib import case_paths, read_frontmatter, vault_root
except ImportError:
    from vaultlib import case_paths, read_frontmatter, vault_root


def build_case_index_text(root: Path) -> str:
    rows: list[tuple[str, str, str, str, str, str, str]] = []
    for path in case_paths(root):
        data = read_frontmatter(path)
        observation_date = data["observation_date"]
        date_text = (
            observation_date.isoformat()
            if hasattr(observation_date, "isoformat")
            else str(observation_date)
        )
        tags = ", ".join(sorted(str(tag) for tag in data.get("tags", [])))
        link = path.relative_to(root).with_suffix("").as_posix()
        rows.append(
            (
                str(data["code"]),
                date_text,
                str(data["outcome"]),
                str(data["case_status"]),
                str(data["strategy_version"]),
                tags,
                f"[[{link}]]",
            )
        )
    rows.sort(key=lambda row: (row[1], row[0], row[6]))
    lines = [
        "# 案例索引",
        "",
        "> 本文件由 `python tools/build_case_index.py` 确定性生成。",
        "",
        "| 股票代码 | 日期 | outcome | case_status | strategy_version | tags | 文件 |",
        "|---|---|---|---|---|---|---|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def write_case_index(root: Path, output: Path | None = None) -> Path:
    destination = output or root / "02_Cases" / "CASE_INDEX.md"
    if not destination.is_absolute():
        destination = root / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_case_index_text(root), encoding="utf-8")
    return destination


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rebuild CASE_INDEX.md")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    print(write_case_index(vault_root(), args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
