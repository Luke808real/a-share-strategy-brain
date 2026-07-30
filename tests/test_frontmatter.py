from __future__ import annotations

import shutil

from tools.vaultlib import (
    case_paths,
    read_frontmatter,
    validate_rule_catalog,
    validate_vault,
)


def test_three_success_case_frontmatters_parse(vault_root_path):
    cases = case_paths(vault_root_path)

    assert len(cases) == 3
    assert {read_frontmatter(path)["code"] for path in cases} == {
        "002640",
        "600199",
        "002891",
    }
    assert all(
        read_frontmatter(path)["outcome"] == "success" for path in cases
    )


def test_chinese_case_content_is_utf8(vault_root_path):
    path = (
        vault_root_path
        / "02_Cases"
        / "Success"
        / "002640-2026-07-27.md"
    )

    content = path.read_text(encoding="utf-8")

    assert "跨境通" in content
    assert "不能得出的结论" in content


def test_illegal_rule_status_fails_validation(vault_root_path, tmp_path):
    original = (
        vault_root_path / "01_Strategy" / "RULE_CATALOG.md"
    ).read_text(encoding="utf-8")
    path = tmp_path / "RULE_CATALOG.md"
    path.write_text(
        original.replace("| FROZEN |", "| INVALID_STATUS |", 1),
        encoding="utf-8",
    )

    _, errors = validate_rule_catalog(path)

    assert any("invalid rule status" in error for error in errors)


def test_duplicate_rule_id_fails_validation(vault_root_path, tmp_path):
    lines = (
        vault_root_path / "01_Strategy" / "RULE_CATALOG.md"
    ).read_text(encoding="utf-8").splitlines()
    header_index = next(
        index for index, line in enumerate(lines)
        if line.startswith("| rule_id |")
    )
    path = tmp_path / "RULE_CATALOG.md"
    path.write_text(
        "\n".join(
            (
                lines[header_index],
                lines[header_index + 1],
                lines[header_index + 2],
                lines[header_index + 2],
            )
        )
        + "\n",
        encoding="utf-8",
    )

    _, errors = validate_rule_catalog(path)

    assert any("duplicate rule_id" in error for error in errors)


def test_candidate_rule_cannot_be_marked_frozen(vault_root_path, tmp_path):
    copied = tmp_path / "vault"
    shutil.copytree(vault_root_path, copied)
    catalog = copied / "01_Strategy" / "RULE_CATALOG.md"
    content = catalog.read_text(encoding="utf-8")
    catalog.write_text(
        content.replace(
            "| MA30_OVERHEAD | MA30高悬 | 风险候选 | PROPOSED |",
            "| MA30_OVERHEAD | MA30高悬 | 风险候选 | FROZEN |",
        ),
        encoding="utf-8",
    )

    errors = validate_vault(copied)

    assert any(
        "candidate MA30_OVERHEAD is incorrectly marked FROZEN" in error
        for error in errors
    )
