"""Recalculate the frozen strategy manifest from local Git objects."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
from typing import Any, Sequence

try:
    from .check_strategy_drift import (
        evaluate_strategy_drift,
        strategy_file_hashes_at_commit,
    )
    from .vaultlib import read_yaml, vault_root, write_yaml
except ImportError:
    from check_strategy_drift import (
        evaluate_strategy_drift,
        strategy_file_hashes_at_commit,
    )
    from vaultlib import read_yaml, vault_root, write_yaml


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def update_baseline_manifest(root: Path) -> dict[str, Any]:
    path = root / "01_Strategy" / "BASELINE_MANIFEST.yaml"
    manifest = read_yaml(path)
    code_root = (
        root / Path(str(manifest["code_repo_relative_path"]))
    ).resolve()
    strategy_version = str(manifest["strategy_version"])
    strategy_tag = str(manifest["strategy_repo_tag"])
    content_commit = str(manifest["strategy_content_commit"])
    integration_commit = str(
        manifest["strategy_main_integration_commit"]
    )

    tag_commit = _git(code_root, "rev-parse", f"{strategy_tag}^{{}}")
    if tag_commit != content_commit:
        raise ValueError(
            f"{strategy_tag} resolves to {tag_commit}, expected {content_commit}"
        )
    ancestor = subprocess.run(
        (
            "git",
            "merge-base",
            "--is-ancestor",
            content_commit,
            integration_commit,
        ),
        cwd=code_root,
        check=False,
    )
    if ancestor.returncode != 0:
        raise ValueError(
            f"{content_commit} is not an ancestor of {integration_commit}"
        )
    content_tree = _git(code_root, "rev-parse", f"{content_commit}^{{tree}}")
    integration_tree = _git(
        code_root,
        "rev-parse",
        f"{integration_commit}^{{tree}}",
    )
    if content_tree != integration_tree:
        raise ValueError(
            "content and integration commits do not have the same tree"
        )

    updated = {
        **manifest,
        "schema_version": "2.0",
        "strategy_version": strategy_version,
        "strategy_repo_tag": strategy_tag,
        "strategy_content_commit": content_commit,
        "strategy_main_integration_commit": integration_commit,
        "strategy_tree_sha": content_tree,
        "baseline_relation": "MERGE_EQUIVALENT_TREE",
        "strategy_file_hashes": strategy_file_hashes_at_commit(
            code_root,
            content_commit,
        ),
        # Compatibility aliases for existing Vault integrations.
        "frozen_strategy_version": strategy_version,
        "frozen_tag": strategy_tag,
        "frozen_commit": content_commit,
    }
    state = evaluate_strategy_drift(root, manifest=updated)
    updated["status"] = state["drift_status"]
    write_yaml(path, updated)
    return updated


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Recalculate 01_Strategy/BASELINE_MANIFEST.yaml"
    )
    parser.add_argument("--root", type=Path, default=vault_root())
    args = parser.parse_args(argv)
    try:
        manifest = update_baseline_manifest(args.root.resolve())
    except (KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Baseline manifest update failed: {exc}")
        return 1
    print(
        "Baseline manifest updated: "
        f"version={manifest['strategy_version']}, "
        f"content={manifest['strategy_content_commit']}, "
        f"integration={manifest['strategy_main_integration_commit']}, "
        f"tree={manifest['strategy_tree_sha']}, "
        f"status={manifest['status']}"
    )
    return 0 if manifest["status"] == "CURRENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
