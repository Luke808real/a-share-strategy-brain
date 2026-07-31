"""Validate the frozen strategy baseline against the local code repository."""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import subprocess
from typing import Any, Sequence

try:
    from .vaultlib import read_yaml, vault_root
except ImportError:
    from vaultlib import read_yaml, vault_root


STRATEGY_FILES = ("SPEC.md", "config/strategy.yaml", "DECISIONS.md")


def _git(
    root: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        check=check,
        capture_output=True,
        text=True,
    )


def _rev_parse(root: Path, ref: str) -> str | None:
    completed = _git(root, "rev-parse", "--verify", ref, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else None


def _observed_main(root: Path) -> str | None:
    return (
        _rev_parse(root, "refs/remotes/origin/main")
        or _rev_parse(root, "refs/heads/main")
        or _rev_parse(root, "HEAD")
    )


def strategy_file_hashes_at_commit(
    code_root: Path,
    commit: str,
) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in STRATEGY_FILES:
        completed = subprocess.run(
            ("git", "show", f"{commit}:{relative}"),
            cwd=code_root,
            check=True,
            capture_output=True,
        )
        hashes[relative] = sha256(completed.stdout).hexdigest()
    return hashes


def _manifest_value(
    manifest: dict[str, Any],
    current: str,
    legacy: str,
) -> str:
    value = manifest.get(current, manifest.get(legacy, ""))
    return str(value)


def evaluate_strategy_drift(
    root: Path,
    *,
    manifest: dict[str, Any] | None = None,
) -> dict[str, str]:
    data = manifest or read_yaml(
        root / "01_Strategy" / "BASELINE_MANIFEST.yaml"
    )
    relative = Path(str(data["code_repo_relative_path"]))
    code_root = (root / relative).resolve()
    strategy_version = _manifest_value(
        data,
        "strategy_version",
        "frozen_strategy_version",
    )
    strategy_tag = _manifest_value(data, "strategy_repo_tag", "frozen_tag")
    content_commit = _manifest_value(
        data,
        "strategy_content_commit",
        "frozen_commit",
    )
    integration_commit = str(
        data.get("strategy_main_integration_commit", content_commit)
    )
    expected_tree = str(data.get("strategy_tree_sha", ""))
    relation = str(data.get("baseline_relation", "EXACT_COMMIT"))
    expected_hashes = {
        str(key): str(value)
        for key, value in dict(data.get("strategy_file_hashes", {})).items()
    }
    base = {
        "code_repository": str(data["code_repository"]),
        "strategy_version": strategy_version,
        "strategy_repo_tag": strategy_tag,
        "strategy_content_commit": content_commit,
        "strategy_main_integration_commit": integration_commit,
        "strategy_tree_sha": expected_tree,
        "baseline_relation": relation,
        # Compatibility keys consumed by older context-pack readers.
        "frozen_strategy_version": strategy_version,
        "frozen_tag": strategy_tag,
        "frozen_commit": content_commit,
    }
    if not (code_root / ".git").exists():
        return {
            **base,
            "observed_branch": "UNAVAILABLE",
            "observed_commit": "UNAVAILABLE",
            "observed_main_commit": "UNAVAILABLE",
            "observed_tag_commit": "UNAVAILABLE",
            "observed_main_tree": "UNAVAILABLE",
            "drift_status": "CODE_REPOSITORY_UNAVAILABLE",
        }

    head = _rev_parse(code_root, "HEAD") or "UNAVAILABLE"
    branch_result = _git(code_root, "branch", "--show-current")
    branch = branch_result.stdout.strip() or "DETACHED"
    observed_main = _observed_main(code_root) or "UNAVAILABLE"
    observed_tag = (
        _rev_parse(code_root, f"refs/tags/{strategy_tag}^{{}}")
        or "UNAVAILABLE"
    )
    content_tree = (
        _rev_parse(code_root, f"{content_commit}^{{tree}}") or "UNAVAILABLE"
    )
    main_tree = (
        _rev_parse(code_root, f"{observed_main}^{{tree}}")
        if observed_main != "UNAVAILABLE"
        else None
    ) or "UNAVAILABLE"
    dirty = bool(
        _git(
            code_root,
            "status",
            "--porcelain",
            "--untracked-files=no",
        ).stdout.strip()
    )
    ancestor = (
        _git(
            code_root,
            "merge-base",
            "--is-ancestor",
            content_commit,
            observed_main,
            check=False,
        ).returncode
        == 0
        if observed_main != "UNAVAILABLE"
        else False
    )
    try:
        observed_hashes = strategy_file_hashes_at_commit(
            code_root,
            observed_main,
        )
    except subprocess.CalledProcessError:
        observed_hashes = {}

    if dirty:
        drift = "DIRTY_WORKTREE"
    elif relation != "MERGE_EQUIVALENT_TREE":
        drift = "BASELINE_RELATION_UNSUPPORTED"
    elif observed_main != integration_commit:
        drift = "MAIN_COMMIT_DRIFT"
    elif observed_tag != content_commit:
        drift = "TAG_DRIFT"
    elif not ancestor:
        drift = "CONTENT_NOT_IN_MAIN"
    elif (
        content_tree != expected_tree
        or main_tree != expected_tree
        or content_tree != main_tree
    ):
        drift = "TREE_DRIFT"
    elif observed_hashes != expected_hashes:
        drift = "FILE_HASH_DRIFT"
    else:
        drift = "CURRENT"
    return {
        **base,
        "observed_branch": branch,
        "observed_commit": head,
        "observed_main_commit": observed_main,
        "observed_tag_commit": observed_tag,
        "observed_content_tree": content_tree,
        "observed_main_tree": main_tree,
        "drift_status": drift,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the strategy code baseline for drift"
    )
    parser.add_argument("--root", type=Path, default=vault_root())
    args = parser.parse_args(argv)
    state = evaluate_strategy_drift(args.root.resolve())
    for key in (
        "strategy_version",
        "strategy_repo_tag",
        "strategy_content_commit",
        "strategy_main_integration_commit",
        "strategy_tree_sha",
        "baseline_relation",
        "observed_branch",
        "observed_commit",
        "observed_main_commit",
        "observed_tag_commit",
        "observed_main_tree",
        "drift_status",
    ):
        print(f"{key}={state[key]}")
    return 0 if state["drift_status"] == "CURRENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
