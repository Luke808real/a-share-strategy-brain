"""Artifact inventory and manifest helpers for deterministic context sync."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
from typing import Any

try:
    from .agentlib import (
        agent_case_paths,
        change_request_paths,
        reasoning_digest_paths,
    )
    from .chatlib import reviewed_digests
    from .vaultlib import (
        candidate_rule_ids,
        case_paths,
        content_sha256,
        git_head,
        read_frontmatter,
        read_text,
        read_yaml,
        write_yaml,
    )
except ImportError:
    from agentlib import (
        agent_case_paths,
        change_request_paths,
        reasoning_digest_paths,
    )
    from chatlib import reviewed_digests
    from vaultlib import (
        candidate_rule_ids,
        case_paths,
        content_sha256,
        git_head,
        read_frontmatter,
        read_text,
        read_yaml,
        write_yaml,
    )


def baseline_status(root: Path) -> str:
    text = read_text(root / "05_Codex" / "CURRENT_PHASE.md")
    match = re.search(r"冻结策略版本：`([^`]+)`", text)
    return match.group(1) if match else "UNKNOWN"


def code_baseline_state(root: Path) -> dict[str, str]:
    manifest = read_yaml(root / "01_Strategy" / "BASELINE_MANIFEST.yaml")
    relative = Path(str(manifest["code_repo_relative_path"]))
    code_root = (root / relative).resolve()
    base = {
        "code_repository": str(manifest["code_repository"]),
        "frozen_strategy_version": str(manifest["frozen_strategy_version"]),
        "frozen_tag": str(manifest["frozen_tag"]),
        "frozen_commit": str(manifest["frozen_commit"]),
    }
    if not (code_root / ".git").exists():
        return {
            **base,
            "observed_branch": "UNAVAILABLE",
            "observed_commit": "UNAVAILABLE",
            "drift_status": "CODE_REPOSITORY_UNAVAILABLE",
        }
    head = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=code_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    branch = subprocess.run(
        ("git", "branch", "--show-current"),
        cwd=code_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() or "DETACHED"
    dirty = bool(
        subprocess.run(
            ("git", "status", "--porcelain"),
            cwd=code_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    commit_drift = head != str(manifest["frozen_commit"])
    if commit_drift and dirty:
        drift = "COMMIT_DRIFT_AND_DIRTY"
    elif commit_drift:
        drift = "COMMIT_DRIFT"
    elif dirty:
        drift = "DIRTY_WORKTREE"
    else:
        drift = "CLEAN_AT_BASELINE"
    return {
        **base,
        "observed_branch": branch,
        "observed_commit": head,
        "drift_status": drift,
    }


def artifact_state(root: Path) -> dict[str, Any]:
    sessions = {
        str(read_frontmatter(path)["session_id"]): content_sha256(read_text(path))
        for path in reviewed_digests(root)
    }
    cases = {
        path.relative_to(root).as_posix(): content_sha256(read_text(path))
        for path in case_paths(root)
    }
    candidate_path = root / "04_Research" / "Candidate-Rules.md"
    rules = sorted(candidate_rule_ids(candidate_path))
    adrs = {
        path.relative_to(root).as_posix(): content_sha256(read_text(path))
        for path in sorted(
            (root / "03_Decisions").glob("ADR-[0-9][0-9][0-9]-*.md")
        )
    }
    todo_path = root / "04_Research" / "Research-Backlog.md"
    baseline_paths = (
        root / "01_Strategy" / "STRATEGY_MASTER.md",
        root / "05_Codex" / "CURRENT_PHASE.md",
    )
    baseline_text = "\n".join(read_text(path) for path in baseline_paths)
    reasoning = {
        path.relative_to(root).as_posix(): content_sha256(read_text(path))
        for path in reasoning_digest_paths(root)
        if read_frontmatter(path).get("review_status")
        in {"human_reviewed", "accepted"}
    }
    pending_intakes = {
        path.relative_to(root).as_posix(): content_sha256(read_text(path))
        for path in agent_case_paths(root)
        if path.parent.name == "Incoming"
    }
    approved_requests = {
        path.relative_to(root).as_posix(): content_sha256(read_text(path))
        for path in change_request_paths(root)
        if read_frontmatter(path).get("status")
        == "approved_for_implementation"
    }
    code_state = code_baseline_state(root)
    code_state_text = "\n".join(
        f"{key}={value}" for key, value in sorted(code_state.items())
    )
    return {
        "sessions": dict(sorted(sessions.items())),
        "cases": dict(sorted(cases.items())),
        "rules": rules,
        "candidate_rules_hash": content_sha256(read_text(candidate_path)),
        "adrs": dict(sorted(adrs.items())),
        "todo_hash": content_sha256(read_text(todo_path)),
        "baseline_hash": content_sha256(baseline_text),
        "strategy_baseline_status": baseline_status(root),
        "reasoning_digests": dict(sorted(reasoning.items())),
        "pending_agent_intakes": dict(sorted(pending_intakes.items())),
        "approved_change_requests": dict(sorted(approved_requests.items())),
        "code_baseline_hash": content_sha256(code_state_text),
        "code_drift_status": code_state["drift_status"],
    }


def empty_sync_manifest() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "last_full_pack_hash": "",
        "last_delta_pack_hash": "",
        "last_included_session_id": None,
        "included_session_ids": [],
        "included_session_hashes": {},
        "included_case_files": {},
        "included_rule_ids": [],
        "candidate_rules_hash": "",
        "included_adr_files": {},
        "generated_from_commit": "",
        "strategy_baseline_status": "UNKNOWN",
        "todo_hash": "",
        "baseline_hash": "",
        "included_reasoning_digests": {},
        "included_agent_intakes": {},
        "included_change_requests": {},
        "code_baseline_hash": "",
        "code_drift_status": "UNKNOWN",
    }


def load_sync_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_sync_manifest()
    data = read_yaml(path)
    default = empty_sync_manifest()
    default.update(data)
    if not isinstance(default["included_session_ids"], list):
        raise ValueError(f"{path}: included_session_ids must be a list")
    for field in (
        "included_session_hashes",
        "included_case_files",
        "included_adr_files",
        "included_reasoning_digests",
        "included_agent_intakes",
        "included_change_requests",
    ):
        if not isinstance(default[field], dict):
            raise ValueError(f"{path}: {field} must be a mapping")
    return default


def manifest_from_state(
    root: Path,
    state: dict[str, Any],
    *,
    last_full_pack_hash: str,
    last_delta_pack_hash: str,
) -> dict[str, Any]:
    session_ids = sorted(state["sessions"])
    return {
        "schema_version": "1.0",
        "last_full_pack_hash": last_full_pack_hash,
        "last_delta_pack_hash": last_delta_pack_hash,
        "last_included_session_id": session_ids[-1] if session_ids else None,
        "included_session_ids": session_ids,
        "included_session_hashes": state["sessions"],
        "included_case_files": state["cases"],
        "included_rule_ids": state["rules"],
        "candidate_rules_hash": state["candidate_rules_hash"],
        "included_adr_files": state["adrs"],
        "generated_from_commit": git_head(root),
        "strategy_baseline_status": state["strategy_baseline_status"],
        "todo_hash": state["todo_hash"],
        "baseline_hash": state["baseline_hash"],
        "included_reasoning_digests": state["reasoning_digests"],
        "included_agent_intakes": state["pending_agent_intakes"],
        "included_change_requests": state["approved_change_requests"],
        "code_baseline_hash": state["code_baseline_hash"],
        "code_drift_status": state["code_drift_status"],
    }


def write_sync_manifest(root: Path, data: dict[str, Any]) -> Path:
    path = root / "exports" / "CHAT_SYNC_MANIFEST.yaml"
    write_yaml(path, data)
    return path
