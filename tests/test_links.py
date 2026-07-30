from __future__ import annotations

import socket

import pytest

from tools.vaultlib import validate_internal_links, validate_vault


def test_broken_internal_link_fails_validation(tmp_path):
    note = tmp_path / "note.md"
    note.write_text("# Note\n\n[[missing/target]]\n", encoding="utf-8")

    errors = validate_internal_links(tmp_path)

    assert errors
    assert "broken internal link" in errors[0]


def test_complete_vault_has_no_validation_errors(vault_root_path):
    assert validate_vault(vault_root_path) == []


def test_tests_forbid_socket_network():
    with pytest.raises(AssertionError, match="network access is forbidden"):
        socket.create_connection(("example.com", 80))
