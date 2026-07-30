from __future__ import annotations

from pathlib import Path
import socket
from typing import NoReturn

import pytest


@pytest.fixture(autouse=True)
def block_all_socket_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*args: object, **kwargs: object) -> NoReturn:
        raise AssertionError("network access is forbidden in Vault tests")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)


@pytest.fixture
def vault_root_path() -> Path:
    return Path(__file__).resolve().parents[1]
