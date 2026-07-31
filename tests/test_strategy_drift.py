from __future__ import annotations

from pathlib import Path
import subprocess

import pytest
import yaml

from tools.check_strategy_drift import (
    evaluate_strategy_drift,
    strategy_file_hashes_at_commit,
)


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@pytest.fixture
def equivalent_merge_baseline(tmp_path):
    code = tmp_path / "code"
    vault = tmp_path / "vault"
    code.mkdir()
    (vault / "01_Strategy").mkdir(parents=True)
    git(code, "init", "-b", "main")
    git(code, "config", "user.name", "Baseline Test")
    git(
        code,
        "config",
        "user.email",
        "baseline.test" + "@" + "invalid.example",
    )
    (code / "README.md").write_text("# Code\n", encoding="utf-8")
    git(code, "add", "README.md")
    git(code, "commit", "-m", "base")
    base = git(code, "rev-parse", "HEAD")

    git(code, "switch", "-c", "feature")
    (code / "config").mkdir()
    (code / "SPEC.md").write_text("# Spec\n", encoding="utf-8")
    (code / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
    (code / "config" / "strategy.yaml").write_text(
        "strategy_version: '0.1.0'\n",
        encoding="utf-8",
    )
    git(code, "add", "SPEC.md", "DECISIONS.md", "config/strategy.yaml")
    git(code, "commit", "-m", "content")
    content = git(code, "rev-parse", "HEAD")
    git(code, "tag", "-a", "phase-2b3", "-m", "phase-2b3", content)

    git(code, "switch", "main")
    git(code, "merge", "--no-ff", "feature", "-m", "integrate")
    integration = git(code, "rev-parse", "HEAD")
    tree = git(code, "rev-parse", f"{content}^{{tree}}")
    manifest = {
        "schema_version": "2.0",
        "knowledge_repository": "test/brain",
        "code_repository": "test/code",
        "code_repo_relative_path": "../code",
        "strategy_version": "phase-2b3",
        "strategy_repo_tag": "phase-2b3",
        "strategy_content_commit": content,
        "strategy_main_integration_commit": integration,
        "strategy_tree_sha": tree,
        "baseline_relation": "MERGE_EQUIVALENT_TREE",
        "strategy_file_hashes": strategy_file_hashes_at_commit(code, content),
        "status": "CURRENT",
    }
    path = vault / "01_Strategy" / "BASELINE_MANIFEST.yaml"
    path.write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )
    return {
        "vault": vault,
        "code": code,
        "manifest": manifest,
        "base": base,
        "content": content,
        "integration": integration,
        "tree": tree,
    }


def test_different_content_and_merge_sha_with_same_tree_is_current(
    equivalent_merge_baseline,
):
    item = equivalent_merge_baseline

    assert item["content"] != item["integration"]
    assert git(item["code"], "rev-parse", f"{item['integration']}^{{tree}}") == (
        item["tree"]
    )
    assert evaluate_strategy_drift(item["vault"])["drift_status"] == "CURRENT"


def test_merge_commit_containing_content_commit_is_current(
    equivalent_merge_baseline,
):
    item = equivalent_merge_baseline

    completed = subprocess.run(
        (
            "git",
            "merge-base",
            "--is-ancestor",
            item["content"],
            item["integration"],
        ),
        cwd=item["code"],
        check=False,
    )

    assert completed.returncode == 0
    assert evaluate_strategy_drift(item["vault"])["drift_status"] == "CURRENT"


def test_different_main_tree_is_drift(equivalent_merge_baseline):
    item = equivalent_merge_baseline
    readme = item["code"] / "README.md"
    readme.write_text("# Changed tree\n", encoding="utf-8")
    git(item["code"], "add", "README.md")
    git(item["code"], "commit", "-m", "change tree")
    changed_main = git(item["code"], "rev-parse", "HEAD")
    item["manifest"]["strategy_main_integration_commit"] = changed_main

    state = evaluate_strategy_drift(
        item["vault"],
        manifest=item["manifest"],
    )

    assert state["drift_status"] == "TREE_DRIFT"


def test_wrong_tag_target_is_drift(equivalent_merge_baseline):
    item = equivalent_merge_baseline
    git(
        item["code"],
        "tag",
        "-f",
        "-a",
        "phase-2b3",
        "-m",
        "wrong target",
        item["base"],
    )

    state = evaluate_strategy_drift(item["vault"])

    assert state["drift_status"] == "TAG_DRIFT"


def test_main_not_containing_content_is_drift(equivalent_merge_baseline):
    item = equivalent_merge_baseline
    git(item["code"], "reset", "--hard", item["base"])
    git(item["code"], "commit", "--allow-empty", "-m", "unrelated main")
    unrelated_main = git(item["code"], "rev-parse", "HEAD")
    item["manifest"]["strategy_main_integration_commit"] = unrelated_main

    state = evaluate_strategy_drift(
        item["vault"],
        manifest=item["manifest"],
    )

    assert state["drift_status"] == "CONTENT_NOT_IN_MAIN"


def test_tracked_worktree_change_is_dirty(equivalent_merge_baseline):
    item = equivalent_merge_baseline
    (item["code"] / "SPEC.md").write_text(
        "# Dirty spec\n",
        encoding="utf-8",
    )

    state = evaluate_strategy_drift(item["vault"])

    assert state["drift_status"] == "DIRTY_WORKTREE"
