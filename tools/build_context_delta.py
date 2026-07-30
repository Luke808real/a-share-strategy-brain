"""Build the deterministic context delta since a sync manifest."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Any, Sequence

try:
    from .context_sync import (
        artifact_state,
        code_baseline_state,
        empty_sync_manifest,
        load_sync_manifest,
        manifest_from_state,
        write_sync_manifest,
    )
    from .vaultlib import (
        content_sha256,
        read_frontmatter,
        read_text,
        vault_root,
    )
except ImportError:
    from context_sync import (
        artifact_state,
        code_baseline_state,
        empty_sync_manifest,
        load_sync_manifest,
        manifest_from_state,
        write_sync_manifest,
    )
    from vaultlib import content_sha256, read_frontmatter, read_text, vault_root


def _changed(current: dict[str, str], prior: Any) -> tuple[str, ...]:
    previous = prior if isinstance(prior, dict) else {}
    return tuple(
        key for key, value in sorted(current.items()) if previous.get(key) != value
    )


def _session_block(root: Path, session_id: str) -> str:
    path = root / "06_Conversations" / "Digests" / f"{session_id}.md"
    data = read_frontmatter(path)
    body = re.sub(
        r"\A---\r?\n.*?\r?\n---\r?\n",
        "",
        read_text(path),
        count=1,
        flags=re.DOTALL,
    ).strip()
    return (
        f"### {session_id}\n\n"
        f"> Source: [[{path.relative_to(root).with_suffix('').as_posix()}]]；"
        f"review_status={data['review_status']}\n\n{body}"
    )


def _case_block(root: Path, relative: str) -> str:
    path = root / relative
    data = read_frontmatter(path)
    return (
        f"- [[{path.relative_to(root).with_suffix('').as_posix()}]]："
        f"{data['code']} {data['name']}，{data['observation_date']}，"
        f"outcome={data['outcome']}，case_status={data['case_status']}"
    )


def _rule_lines(root: Path, rule_ids: Sequence[str]) -> str:
    text = read_text(root / "04_Research" / "Candidate-Rules.md")
    lines = text.splitlines()
    output: list[str] = []
    wanted = set(rule_ids)
    for line in lines:
        match = re.match(r"^- `([A-Z][A-Z0-9_]*)`", line)
        if match and match.group(1) in wanted:
            output.append(line)
    return "\n".join(output)


def _adr_block(root: Path, relative: str) -> str:
    path = root / relative
    data = read_frontmatter(path)
    return (
        f"- [[{path.relative_to(root).with_suffix('').as_posix()}]]："
        f"{data['adr_id']}，status={data['status']}，{data['title']}"
    )


def build_context_delta_text(
    root: Path,
    previous: dict[str, Any],
) -> str:
    state = artifact_state(root)
    new_sessions = _changed(
        state["sessions"], previous.get("included_session_hashes", {})
    )
    changed_cases = _changed(
        state["cases"], previous.get("included_case_files", {})
    )
    old_rules = set(previous.get("included_rule_ids", []))
    new_rules = tuple(rule for rule in state["rules"] if rule not in old_rules)
    changed_adrs = _changed(
        state["adrs"], previous.get("included_adr_files", {})
    )
    changed_reasoning = _changed(
        state["reasoning_digests"],
        previous.get("included_reasoning_digests", {}),
    )
    changed_intakes = _changed(
        state["pending_agent_intakes"],
        previous.get("included_agent_intakes", {}),
    )
    changed_requests = _changed(
        state["approved_change_requests"],
        previous.get("included_change_requests", {}),
    )
    code_baseline_changed = (
        state["code_baseline_hash"]
        != previous.get("code_baseline_hash", "")
    )
    todo_changed = state["todo_hash"] != previous.get("todo_hash", "")
    baseline_changed = (
        state["baseline_hash"] != previous.get("baseline_hash", "")
        or state["strategy_baseline_status"]
        != previous.get("strategy_baseline_status", "")
    )
    has_delta = any(
        (
            new_sessions,
            changed_cases,
            new_rules,
            changed_adrs,
            changed_reasoning,
            changed_intakes,
            changed_requests,
            code_baseline_changed,
            todo_changed,
            baseline_changed,
        )
    )
    lines = [
        "# LLM Context Delta",
        "",
        "> 仅包含相对同步清单的新增或修改项；不包含Raw会话、截图或未审核Digest。",
    ]
    if not has_delta:
        lines.extend(["", "## 无增量", "", "当前输入与同步清单一致。", ""])
        return "\n".join(lines)

    lines.extend(["", "## 新增或修改的已审核会话", ""])
    lines.append(
        "\n\n".join(_session_block(root, value) for value in new_sessions)
        or "无。"
    )
    lines.extend(["", "## 新增或修改案例", ""])
    lines.append(
        "\n".join(_case_block(root, value) for value in changed_cases) or "无。"
    )
    lines.extend(["", "## 新Candidate Rules", ""])
    lines.append(_rule_lines(root, new_rules) or "无。")
    lines.extend(["", "## 新增或修改ADR", ""])
    lines.append(
        "\n".join(_adr_block(root, value) for value in changed_adrs) or "无。"
    )
    lines.extend(["", "## 当前待办", ""])
    lines.append(
        read_text(root / "04_Research" / "Research-Backlog.md").strip()
        if todo_changed
        else "无变化。"
    )
    lines.extend(["", "## 策略基线状态", ""])
    lines.append(
        (
            f"- 冻结基线：`{state['strategy_baseline_status']}`\n"
            "- 详见 [[01_Strategy/STRATEGY_MASTER]] 与 "
            "[[05_Codex/CURRENT_PHASE]]。"
        )
        if baseline_changed
        else "无变化。"
    )
    lines.extend(["", "## 新增或修改的已审核推理摘要", ""])
    lines.append(
        "\n".join(
            f"- [[{Path(value).with_suffix('').as_posix()}]]"
            for value in changed_reasoning
        )
        or "无。"
    )
    lines.extend(["", "## 新增或修改的待审核Agent Intake", ""])
    lines.append(
        "\n".join(
            f"- [[{Path(value).with_suffix('').as_posix()}]]："
            "尚未进入正式策略摘要。"
            for value in changed_intakes
        )
        or "无。"
    )
    lines.extend(["", "## 新增或修改的获批Change Request", ""])
    lines.append(
        "\n".join(
            f"- [[{Path(value).with_suffix('').as_posix()}]]"
            for value in changed_requests
        )
        or "无。"
    )
    lines.extend(["", "## 代码仓库基线与drift", ""])
    if code_baseline_changed:
        code_state = code_baseline_state(root)
        lines.append(
            "\n".join(
                (
                    f"- 代码仓库：`{code_state['code_repository']}`",
                    f"- 冻结commit：`{code_state['frozen_commit']}`",
                    f"- 当前commit：`{code_state['observed_commit']}`",
                    f"- 当前分支：`{code_state['observed_branch']}`",
                    f"- drift状态：`{code_state['drift_status']}`",
                )
            )
        )
    else:
        lines.append("无变化。")
    lines.append("")
    return "\n".join(lines)


def write_context_delta(
    root: Path,
    *,
    since_manifest: Path | None = None,
    rebuild_full: bool = False,
) -> Path:
    sync_path = root / "exports" / "CHAT_SYNC_MANIFEST.yaml"
    if rebuild_full:
        previous = empty_sync_manifest()
    else:
        source = since_manifest or sync_path
        if not source.is_absolute():
            source = root / source
        previous = load_sync_manifest(source)
    text = build_context_delta_text(root, previous)
    destination = root / "exports" / "LLM_CONTEXT_DELTA.md"
    destination.write_text(text, encoding="utf-8")
    current = load_sync_manifest(sync_path)
    state = artifact_state(root)
    manifest = manifest_from_state(
        root,
        state,
        last_full_pack_hash=str(current.get("last_full_pack_hash", "")),
        last_delta_pack_hash=content_sha256(text),
    )
    write_sync_manifest(root, manifest)
    return destination


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build LLM_CONTEXT_DELTA.md")
    parser.add_argument("--since-manifest", type=Path)
    parser.add_argument(
        "--rebuild-full",
        action="store_true",
        help="treat the baseline as empty and include every eligible artifact",
    )
    args = parser.parse_args(argv)
    try:
        print(
            write_context_delta(
                vault_root(),
                since_manifest=args.since_manifest,
                rebuild_full=args.rebuild_full,
            )
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
