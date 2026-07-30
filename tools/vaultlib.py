"""Shared Markdown/YAML helpers for the local strategy Vault."""

from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
import re
from typing import Any

import yaml


RULE_STATUSES = frozenset(
    {
        "OBSERVED",
        "PROPOSED",
        "ACCEPTED",
        "REJECTED",
        "FROZEN",
        "DEPRECATED",
    }
)
CASE_STATUSES = frozenset({"observed", "confirmed", "watching", "rejected"})
CASE_OUTCOMES = frozenset({"success", "failure", "watching"})
OUTCOME_DIRECTORIES = {
    "success": "Success",
    "failure": "Failure",
    "watching": "Watching",
}
FRONTMATTER_PATTERN = re.compile(
    r"\A---\r?\n(?P<body>.*?)\r?\n---(?:\r?\n|\Z)",
    re.DOTALL,
)
WIKI_LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")
CANDIDATE_ID_PATTERN = re.compile(
    r"^- `([A-Z][A-Z0-9_]*)`(?:\s|$)",
    re.MULTILINE,
)


def vault_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_frontmatter(path: Path) -> dict[str, Any]:
    match = FRONTMATTER_PATTERN.match(read_text(path))
    if match is None:
        raise ValueError(f"{path}: missing YAML frontmatter")
    parsed = yaml.safe_load(match.group("body"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return parsed


def case_paths(root: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    for directory in OUTCOME_DIRECTORIES.values():
        paths.extend((root / "02_Cases" / directory).glob("*.md"))
    return tuple(sorted(paths, key=lambda item: item.as_posix()))


def _as_iso_date(value: Any) -> str | None:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            return None
    return None


def validate_case_file(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = read_frontmatter(path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [str(exc)]

    required = {
        "type",
        "code",
        "name",
        "observation_date",
        "outcome",
        "case_status",
        "strategy_version",
        "confidence",
        "data_source",
        "tags",
    }
    missing = sorted(required - set(data))
    if missing:
        errors.append(f"{path}: missing case fields {', '.join(missing)}")
        return errors
    if data["type"] != "stock_case":
        errors.append(f"{path}: type must be stock_case")
    if re.fullmatch(r"\d{6}", str(data["code"])) is None:
        errors.append(f"{path}: code must contain exactly six digits")
    if _as_iso_date(data["observation_date"]) is None:
        errors.append(f"{path}: observation_date must be YYYY-MM-DD")
    if data["outcome"] not in CASE_OUTCOMES:
        errors.append(f"{path}: invalid outcome {data['outcome']!r}")
    if data["case_status"] not in CASE_STATUSES:
        errors.append(f"{path}: invalid case_status {data['case_status']!r}")
    if not isinstance(data["strategy_version"], str) or not data["strategy_version"]:
        errors.append(f"{path}: strategy_version must be non-empty")
    if data["confidence"] not in {"low", "medium", "high"}:
        errors.append(f"{path}: confidence must be low, medium or high")
    if not isinstance(data["tags"], list) or any(
        re.fullmatch(r"[A-Z][A-Z0-9_]*", str(tag)) is None
        for tag in data["tags"]
    ):
        errors.append(f"{path}: tags must be uppercase stable identifiers")

    expected_directory = OUTCOME_DIRECTORIES.get(str(data["outcome"]))
    if expected_directory is not None and path.parent.name != expected_directory:
        errors.append(
            f"{path}: outcome {data['outcome']} belongs in {expected_directory}"
        )
    expected_name = (
        f"{data['code']}-{_as_iso_date(data['observation_date'])}.md"
        if _as_iso_date(data["observation_date"]) is not None
        else None
    )
    if expected_name is not None and path.name != expected_name:
        errors.append(f"{path}: expected stable filename {expected_name}")
    try:
        path.relative_to(root)
    except ValueError:
        errors.append(f"{path}: case is outside the Vault")
    return errors


def parse_rule_catalog(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    lines = read_text(path).splitlines()
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.strip().startswith("| rule_id |")
        ),
        None,
    )
    if header_index is None:
        return [], [f"{path}: missing rule catalog table"]
    headers = [cell.strip() for cell in lines[header_index].strip("|").split("|")]
    required_headers = {
        "rule_id",
        "名称",
        "适用层级",
        "状态",
        "输入字段",
        "判断语义",
        "影响setup_stage",
        "影响is_entry_candidate",
        "代码实现",
        "对应测试",
        "来源决策",
    }
    errors: list[str] = []
    missing_headers = sorted(required_headers - set(headers))
    if missing_headers:
        errors.append(
            f"{path}: missing rule columns {', '.join(missing_headers)}"
        )

    rows: list[dict[str, str]] = []
    for line in lines[header_index + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            errors.append(f"{path}: malformed rule row {line}")
            continue
        rows.append(dict(zip(headers, cells, strict=True)))
    return rows, errors


def validate_rule_catalog(path: Path) -> tuple[dict[str, str], list[str]]:
    rows, errors = parse_rule_catalog(path)
    rule_ids = [row.get("rule_id", "") for row in rows]
    duplicates = sorted(
        rule_id
        for rule_id, count in Counter(rule_ids).items()
        if rule_id and count > 1
    )
    if duplicates:
        errors.append(f"{path}: duplicate rule_id(s): {', '.join(duplicates)}")

    statuses: dict[str, str] = {}
    for row in rows:
        rule_id = row.get("rule_id", "")
        status = row.get("状态", "")
        if re.fullmatch(r"[A-Z][A-Z0-9_]*", rule_id) is None:
            errors.append(f"{path}: invalid rule_id {rule_id!r}")
        if status not in RULE_STATUSES:
            errors.append(
                f"{path}: invalid rule status {status!r} for {rule_id}"
            )
        if rule_id:
            statuses[rule_id] = status
    return statuses, errors


def candidate_rule_ids(path: Path) -> tuple[str, ...]:
    return tuple(CANDIDATE_ID_PATTERN.findall(read_text(path)))


def _link_target_exists(source: Path, target: str, root: Path) -> bool:
    clean = target.split("|", 1)[0].split("#", 1)[0].strip()
    if not clean or "://" in clean:
        return True
    raw = Path(clean)
    candidates = [root / raw, source.parent / raw]
    for candidate in candidates:
        if candidate.suffix:
            if candidate.exists():
                return True
        else:
            if candidate.with_suffix(".md").exists() or candidate.is_dir():
                return True
    return False


def validate_internal_links(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*.md")):
        for target in WIKI_LINK_PATTERN.findall(read_text(path)):
            if not _link_target_exists(path, target, root):
                errors.append(f"{path}: broken internal link [[{target}]]")
    return errors


def validate_vault(root: Path) -> list[str]:
    required_files = (
        "README.md",
        "00_INDEX.md",
        "CHATGPT_PROJECT_INSTRUCTIONS.md",
        "01_Strategy/STRATEGY_MASTER.md",
        "01_Strategy/RULE_CATALOG.md",
        "01_Strategy/STATE_MACHINE.md",
        "01_Strategy/CHANGELOG.md",
        "01_Strategy/GLOSSARY.md",
        "02_Cases/CASE_INDEX.md",
        "02_Cases/Templates/CASE_TEMPLATE.md",
        "02_Cases/Templates/DAILY_REVIEW_TEMPLATE.md",
        "03_Decisions/DECISION_INDEX.md",
        "03_Decisions/ADR_TEMPLATE.md",
        "04_Research/Blogger-Observations.md",
        "04_Research/Candidate-Rules.md",
        "04_Research/Success-Case-Features.md",
        "04_Research/Research-Backlog.md",
        "05_Codex/CURRENT_PHASE.md",
        "05_Codex/NEXT_PROMPT.md",
        "05_Codex/IMPLEMENTATION_LOG.md",
        "05_Codex/CHANGE_REQUEST_TEMPLATE.md",
        "06_Conversations/CONVERSATION_INDEX.md",
    )
    errors = [
        f"{root / relative}: required file is missing"
        for relative in required_files
        if not (root / relative).is_file()
    ]
    for path in sorted(root.rglob("*.md")):
        if (
            "Templates" in path.parts
            or path.name.endswith("_TEMPLATE.md")
            or path.name == "ADR_TEMPLATE.md"
        ):
            continue
        if read_text(path).startswith("---"):
            try:
                frontmatter = read_frontmatter(path)
            except (ValueError, yaml.YAMLError) as exc:
                errors.append(str(exc))
                continue
            if frontmatter.get("type") == "strategy_decision":
                adr_id = str(frontmatter.get("adr_id", ""))
                status = str(frontmatter.get("status", ""))
                if re.fullmatch(r"ADR-\d{3}", adr_id) is None:
                    errors.append(f"{path}: invalid adr_id {adr_id!r}")
                if status not in RULE_STATUSES:
                    errors.append(f"{path}: invalid ADR status {status!r}")
                if _as_iso_date(frontmatter.get("decision_date")) is None:
                    errors.append(
                        f"{path}: decision_date must be YYYY-MM-DD"
                    )
    for path in case_paths(root):
        errors.extend(validate_case_file(path, root))

    catalog_path = root / "01_Strategy" / "RULE_CATALOG.md"
    if catalog_path.is_file():
        statuses, catalog_errors = validate_rule_catalog(catalog_path)
        errors.extend(catalog_errors)
        for path in case_paths(root):
            try:
                case = read_frontmatter(path)
            except (ValueError, yaml.YAMLError):
                continue
            for tag in case.get("tags", []):
                if tag not in statuses:
                    errors.append(f"{path}: unknown case tag {tag}")
        candidates_path = root / "04_Research" / "Candidate-Rules.md"
        if candidates_path.is_file():
            for rule_id in candidate_rule_ids(candidates_path):
                if rule_id not in statuses:
                    errors.append(
                        f"{candidates_path}: unknown candidate rule {rule_id}"
                    )
                elif statuses[rule_id] not in {"OBSERVED", "PROPOSED"}:
                    errors.append(
                        f"{candidates_path}: candidate {rule_id} is incorrectly "
                        f"marked {statuses[rule_id]}"
                    )

    errors.extend(validate_internal_links(root))

    case_index = root / "02_Cases" / "CASE_INDEX.md"
    if case_index.is_file():
        indexed = {
            target.split("|", 1)[0].split("#", 1)[0]
            for target in WIKI_LINK_PATTERN.findall(read_text(case_index))
            if target.startswith("02_Cases/")
        }
        actual = {
            path.relative_to(root).with_suffix("").as_posix()
            for path in case_paths(root)
        }
        missing_index_entries = sorted(actual - indexed)
        stale_index_entries = sorted(indexed - actual)
        if missing_index_entries:
            errors.append(
                f"{case_index}: missing cases {', '.join(missing_index_entries)}"
            )
        if stale_index_entries:
            errors.append(
                f"{case_index}: references absent cases "
                f"{', '.join(stale_index_entries)}"
            )

    master = root / "01_Strategy" / "STRATEGY_MASTER.md"
    if master.is_file():
        for target in WIKI_LINK_PATTERN.findall(read_text(master)):
            clean = target.split("|", 1)[0].split("#", 1)[0]
            if clean.startswith("03_Decisions/ADR-") and not (
                root / f"{clean}.md"
            ).is_file():
                errors.append(f"{master}: references missing ADR {clean}")
    return sorted(set(errors))
