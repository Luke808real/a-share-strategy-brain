from __future__ import annotations

from datetime import date

import pytest

from tools.build_case_index import build_case_index_text
from tools.new_case import create_case
from tools.new_change_request import create_change_request


def test_case_index_contains_three_success_cases(vault_root_path):
    output = build_case_index_text(vault_root_path)

    assert output.count("[[02_Cases/Success/") == 3
    assert "002640" in output
    assert "600199" in output
    assert "002891" in output


def test_new_case_never_overwrites_existing_note(
    vault_root_path,
    tmp_path,
):
    template_directory = tmp_path / "02_Cases" / "Templates"
    template_directory.mkdir(parents=True)
    template_directory.joinpath("CASE_TEMPLATE.md").write_text(
        (
            vault_root_path
            / "02_Cases"
            / "Templates"
            / "CASE_TEMPLATE.md"
        ).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    kwargs = {
        "root": tmp_path,
        "code": "002640",
        "name": "跨境通",
        "observation_date": date(2026, 7, 27),
        "outcome": "success",
    }
    path = create_case(**kwargs)
    original = path.read_text(encoding="utf-8")

    with pytest.raises(FileExistsError, match="case already exists"):
        create_case(**kwargs)

    assert path.read_text(encoding="utf-8") == original
    assert "跨境通" in original


def test_change_request_uses_stable_non_ascii_safe_filename(
    vault_root_path,
    tmp_path,
):
    template_directory = tmp_path / "05_Codex"
    template_directory.mkdir(parents=True)
    template_directory.joinpath("CHANGE_REQUEST_TEMPLATE.md").write_text(
        (
            vault_root_path
            / "05_Codex"
            / "CHANGE_REQUEST_TEMPLATE.md"
        ).read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    path = create_change_request(
        root=tmp_path,
        title="增加MA30高悬风险",
        status="proposed",
        created_date=date(2026, 7, 30),
    )

    assert path.name.startswith("2026-07-30-change-")
    assert "增加MA30高悬风险" in path.read_text(encoding="utf-8")
