from __future__ import annotations

import io
from collections.abc import Iterator

import pytest
from rich.console import Console

import griphtui as gui
from griphtui import prompts


def make_console() -> tuple[Console, io.StringIO]:
    buf = io.StringIO()
    return Console(file=buf, force_terminal=False, width=120, highlight=False), buf


def fake_keys(seq: list[str]) -> Iterator[str]:
    for k in seq:
        yield k


def test_text_returns_input(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    monkeypatch.setattr(console, "input", lambda _prompt="": "hello")
    assert gui.text("name", console=console) == "hello"


def test_text_uses_default_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    monkeypatch.setattr(console, "input", lambda _prompt="": "")
    assert gui.text("name", default="anon", console=console) == "anon"


def test_confirm_yes(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["y"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    assert gui.confirm("go?", console=console) is True


def test_confirm_no(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["n"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    assert gui.confirm("go?", console=console) is False


def test_confirm_enter_uses_default(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    assert gui.confirm("go?", default=False, console=console) is False


def test_select_returns_value(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["down", "down", "enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    value = gui.select(
        "pick",
        [("One", 1), ("Two", 2), ("Three", 3)],
        console=console,
    )
    assert value == 3


def test_select_wraps_around(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["up", "enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    value = gui.select("pick", [("A", "a"), ("B", "b")], console=console)
    assert value == "b"


def test_select_empty_raises() -> None:
    with pytest.raises(ValueError):
        gui.select("pick", [])


def test_multiselect_returns_preselected(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    selected = gui.multiselect(
        "pick",
        [("A", "a", True), ("B", "b", False), ("C", "c", True)],
        console=console,
    )
    assert selected == ["a", "c"]


def test_multiselect_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["space", "down", "space", "enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    selected = gui.multiselect(
        "pick",
        [("A", "a", False), ("B", "b", False)],
        console=console,
    )
    assert selected == ["a", "b"]


def test_multiselect_empty_returns_empty() -> None:
    assert gui.multiselect("pick", []) == []
