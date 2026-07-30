"""Validate the complete local strategy Vault."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

try:
    from .vaultlib import case_paths, validate_vault, vault_root
except ImportError:
    from vaultlib import case_paths, validate_vault, vault_root


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate strategy Vault")
    parser.add_argument("--root", type=Path, default=vault_root())
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors = validate_vault(root)
    if errors:
        print(f"Vault validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Vault validation passed: "
        f"{len(case_paths(root))} case(s), no broken links or rule conflicts."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
