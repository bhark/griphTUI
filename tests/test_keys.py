from __future__ import annotations

import sys
from collections.abc import Iterator

import pytest

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="POSIX-only key tests")


class FakeStdin:
    def __init__(self, seq: list[str]) -> None:
        self._it: Iterator[str] = iter(seq)

    def fileno(self) -> int:
        return 0

    def read(self, n: int) -> str:
        return next(self._it)


@pytest.fixture
def patched_tty(monkeypatch: pytest.MonkeyPatch):
    from griphtui import _keys

    monkeypatch.setattr("termios.tcgetattr", lambda _fd: None)
    monkeypatch.setattr("termios.tcsetattr", lambda *_a, **_k: None)
    monkeypatch.setattr("tty.setraw", lambda _fd: None)

    def install(seq: list[str]) -> None:
        monkeypatch.setattr(_keys.sys, "stdin", FakeStdin(seq))

    return install


def test_read_key_export() -> None:
    from griphtui._keys import read_key

    assert callable(read_key)


def test_posix_parses_enter(patched_tty) -> None:
    from griphtui import _keys

    patched_tty(["\r"])
    assert _keys._read_key_posix(nav=True) == "enter"


def test_posix_parses_arrow_up(patched_tty) -> None:
    from griphtui import _keys

    patched_tty(["\x1b", "[A"])
    assert _keys._read_key_posix(nav=True) == "up"


def test_posix_vim_nav(patched_tty) -> None:
    from griphtui import _keys

    patched_tty(["j"])
    assert _keys._read_key_posix(nav=True) == "down"


def test_posix_nav_disabled_returns_literal(patched_tty) -> None:
    from griphtui import _keys

    patched_tty(["j"])
    assert _keys._read_key_posix(nav=False) == "j"
