from __future__ import annotations

import io
from collections.abc import Iterator
from typing import Never

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
    keys = iter(["h", "e", "l", "l", "o", "enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    assert gui.text("name", console=console) == "hello"


def test_text_uses_default_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
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


def test_multiselect_requires_blocks_until_dependency_selected(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["down", "space", "up", "space", "down", "space", "enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    selected = gui.multiselect(
        "pick",
        [
            gui.Option("A", "a"),
            gui.Option("B", "b", requires={"a"}),
        ],
        console=console,
    )
    assert selected == ["a", "b"]


def test_multiselect_excludes_blocks_conflicting_option(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["space", "down", "space", "enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    selected = gui.multiselect(
        "pick",
        [
            gui.Option("A", "a"),
            gui.Option("B", "b", excludes={"a"}),
        ],
        console=console,
    )
    assert selected == ["a"]


def test_multiselect_required_selection_cannot_be_deselected(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["space", "enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    selected = gui.multiselect(
        "pick",
        [
            gui.Option("A", "a", selected=True),
            gui.Option("B", "b", selected=True, requires={"a"}),
        ],
        console=console,
    )
    assert selected == ["a", "b"]


def test_multiselect_empty_returns_empty() -> None:
    assert gui.multiselect("pick", []) == []


def test_multiselect_resolves_dependency_reasons() -> None:
    opts = prompts._normalize_multiselect_options(
        [
            gui.Option("Core", "core"),
            gui.Option("Analytics", "analytics", requires={"core"}),
            gui.Option("Legacy", "legacy", excludes={"core"}),
        ]
    )

    states = prompts._resolve_multiselect_states(opts, [False, False, False])
    assert states[1].reason == "Depends on Core"

    states = prompts._resolve_multiselect_states(opts, [True, False, False])
    assert states[0].selected is True
    assert states[2].reason == "Conflicts with Core"


def test_multiselect_selected_requirement_reports_required_by() -> None:
    opts = prompts._normalize_multiselect_options(
        [
            gui.Option("Core", "core"),
            gui.Option("Analytics", "analytics", requires={"core"}),
        ]
    )

    states = prompts._resolve_multiselect_states(opts, [True, True])
    assert states[0].disabled is True
    assert states[0].reason == "Required by Analytics"


def test_multiselect_excludes_disable_reverse_direction() -> None:
    opts = prompts._normalize_multiselect_options(
        [
            gui.Option("Core", "core"),
            gui.Option("Legacy", "legacy", excludes={"core"}),
        ]
    )

    states = prompts._resolve_multiselect_states(opts, [False, True])
    assert states[0].disabled is True
    assert states[0].reason == "Conflicts with Legacy"


def test_multiselect_row_styles_keep_active_disabled_rows_highlighted() -> None:
    glyph_style, label_style = prompts._multiselect_row_styles(
        active=True,
        state=prompts._OptionState(selected=False, disabled=True, reason="Depends on Core"),
    )

    assert glyph_style == "bright_black dim"
    assert label_style == "bright_black"


def test_multiselect_row_styles_fade_disabled_selected_glyph() -> None:
    glyph_style, label_style = prompts._multiselect_row_styles(
        active=False,
        state=prompts._OptionState(selected=True, disabled=True, reason="Required by Analytics"),
    )

    assert glyph_style == "cyan dim"
    assert label_style == "dim"


def test_multiselect_row_suffix_shows_reason_only_when_active() -> None:
    suffix = prompts._multiselect_row_suffix(
        active=True,
        state=prompts._OptionState(selected=False, disabled=True, reason="Depends on Core"),
        hint="static hint",
    )
    assert suffix == "Depends on Core"

    suffix = prompts._multiselect_row_suffix(
        active=False,
        state=prompts._OptionState(selected=False, disabled=True, reason="Depends on Core"),
        hint="static hint",
    )
    assert suffix == "static hint"


def test_multiselect_row_suffix_uses_hint_when_no_reason() -> None:
    suffix = prompts._multiselect_row_suffix(
        active=True,
        state=prompts._OptionState(selected=False, disabled=False),
        hint="static hint",
    )
    assert suffix == "static hint"


def test_multiselect_unknown_dependency_raises() -> None:
    with pytest.raises(ValueError, match="unknown value"):
        prompts._normalize_multiselect_options(
            [
                gui.Option("A", "a"),
                gui.Option("B", "b", requires={"missing"}),
            ]
        )


def test_multiselect_duplicate_values_with_rules_raise() -> None:
    with pytest.raises(ValueError, match="unique values"):
        prompts._normalize_multiselect_options(
            [
                gui.Option("A", "a"),
                gui.Option("B", "a", excludes={"a"}),
            ]
        )


def test_multiselect_invalid_preselected_conflict_raises() -> None:
    with pytest.raises(ValueError, match="conflicting selection"):
        gui.multiselect(
            "pick",
            [
                gui.Option("A", "a", selected=True),
                gui.Option("B", "b", selected=True, excludes={"a"}),
            ],
        )


def test_multiselect_invalid_preselected_missing_requirement_raises() -> None:
    with pytest.raises(ValueError, match="without its requirements"):
        gui.multiselect(
            "pick",
            [
                gui.Option("A", "a"),
                gui.Option("B", "b", selected=True, requires={"a"}),
            ],
        )


def test_multiselect_string_rule_values_must_be_wrapped() -> None:
    with pytest.raises(ValueError, match="wrap single strings"):
        prompts._normalize_multiselect_options(
            [
                gui.Option("A", "a"),
                gui.Option("B", "b", requires="a"),
            ]
        )


def _raise_interrupt(**_: object) -> Never:
    raise KeyboardInterrupt


def test_text_cancel_returns_sentinel(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    monkeypatch.setattr(prompts, "read_key", _raise_interrupt)
    result = gui.text("name", console=console)
    assert gui.is_cancel(result)


def test_text_cancel_after_partial_input_returns_sentinel(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["a", "b", "c"])

    def read_key(**_: object) -> str:
        try:
            return next(keys)
        except StopIteration as exc:
            raise KeyboardInterrupt from exc

    monkeypatch.setattr(prompts, "read_key", read_key)
    result = gui.text("name", console=console)
    assert gui.is_cancel(result)


def test_confirm_cancel_returns_sentinel(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    monkeypatch.setattr(prompts, "read_key", _raise_interrupt)
    result = gui.confirm("go?", console=console)
    assert gui.is_cancel(result)


def test_select_cancel_returns_sentinel(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    monkeypatch.setattr(prompts, "read_key", _raise_interrupt)
    result = gui.select("pick", [("A", "a"), ("B", "b")], console=console)
    assert gui.is_cancel(result)


def test_multiselect_cancel_returns_sentinel(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    monkeypatch.setattr(prompts, "read_key", _raise_interrupt)
    result = gui.multiselect("pick", [("A", "a"), ("B", "b")], console=console)
    assert gui.is_cancel(result)


def test_password_cancel_returns_sentinel(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    monkeypatch.setattr(prompts, "read_key", _raise_interrupt)
    result = gui.password("secret", console=console)
    assert gui.is_cancel(result)


def test_text_validate_rejects_then_accepts(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["a", "b", "enter", "a", "b", "c", "d", "enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    result = gui.text(
        "name",
        validate=lambda s: "too short" if len(s) < 3 else None,
        console=console,
    )
    assert result == "abcd"


def test_text_validate_skipped_when_falling_back_to_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console, _ = make_console()
    keys = iter(["enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    result = gui.text(
        "name",
        default="anon",
        validate=lambda s: "nope" if s == "anon" else None,
        console=console,
    )
    assert result == "anon"


def test_password_validate_rejects_then_accepts(monkeypatch: pytest.MonkeyPatch) -> None:
    console, _ = make_console()
    keys = iter(["a", "enter", "a", "b", "c", "d", "enter"])
    monkeypatch.setattr(prompts, "read_key", lambda **_: next(keys))
    result = gui.password(
        "pw",
        validate=lambda s: "too short" if len(s) < 3 else None,
        console=console,
    )
    assert result == "abcd"
