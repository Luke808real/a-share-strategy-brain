from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


def init_repo(path: Path) -> None:
    subprocess.run(("git", "init", "-b", "main"), cwd=path, check=True)
    subprocess.run(
        ("git", "config", "user.name", "Bridge Test"),
        cwd=path,
        check=True,
    )
    subprocess.run(
        (
            "git",
            "config",
            "user.email",
            "bridge.test" + "@" + "invalid.example",
        ),
        cwd=path,
        check=True,
    )
    (path / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(("git", "add", "README.md"), cwd=path, check=True)
    subprocess.run(
        ("git", "commit", "-m", "initial"),
        cwd=path,
        check=True,
        capture_output=True,
    )


def test_bridge_pull_stops_on_dirty_worktree(vault_root_path, tmp_path):
    root = tmp_path / "vault"
    tools = root / "tools"
    tools.mkdir(parents=True)
    shutil.copy2(
        vault_root_path / "tools" / "github_bridge_pull.sh",
        tools / "github_bridge_pull.sh",
    )
    init_repo(root)
    (root / "README.md").write_text("# Dirty\n", encoding="utf-8")

    completed = subprocess.run(
        (str(tools / "github_bridge_pull.sh"),),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "working tree is dirty" in completed.stderr


def test_bridge_publish_without_confirm_never_commits(
    vault_root_path,
    tmp_path,
):
    root = tmp_path / "vault"
    tools = root / "tools"
    tests = root / "tests"
    tools.mkdir(parents=True)
    tests.mkdir()
    shutil.copy2(
        vault_root_path / "tools" / "github_bridge_publish.sh",
        tools / "github_bridge_publish.sh",
    )
    for name in (
        "validate_agent_exchange.py",
        "validate_vault.py",
        "scan_sensitive_content.py",
    ):
        (tools / name).write_text(
            "print('test check passed')\n",
            encoding="utf-8",
        )
    (tests / "test_smoke.py").write_text(
        "def test_smoke():\n    assert True\n",
        encoding="utf-8",
    )
    init_repo(root)
    before = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    (root / "README.md").write_text("# Preview only\n", encoding="utf-8")

    completed = subprocess.run(
        (str(tools / "github_bridge_publish.sh"),),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    after = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert completed.returncode == 0
    assert "preview only" in completed.stdout
    assert after == before
